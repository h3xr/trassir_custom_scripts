import os
import time
from datetime import datetime
from contextlib import suppress

import jsonc
import asyncio
from dotenv import load_dotenv
from colorama import Back, Style
from aiohttp import ClientSession
from prettytable import PrettyTable


# Загружаем переменные окружения
load_dotenv()


async def main():
    ip = os.getenv('SERVER_IP')
    port = os.getenv('SERVER_WEB_PORT')
    username = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')

    try:
        await create_session(ip, port, username, password)
    except KeyboardInterrupt:
        await ClientSession.close()


async def create_session(ip, port, username, password):
    """ 
    Получение SID по ссылке https://[IP]:[PORT]/login?username=username&password=password 
    Время жизни одного SID = 15 минут 
    """
    url = f'https://{ip}:{port}'

    async with ClientSession() as session:
        while True:
            async with session.get(f'{url}/login', params = {'username': username, 'password': password}, 
                               verify_ssl=False) as response:
                if response.status == 200:
                    
                    # Обработка данных
                    data = jsonc.loads(await response.text())
                    session_start_time = time.time()
                    
                    try:
                        if data['success'] != 0:
                            sid = data['sid']
                            cam_list = await get_ip_cameras_list(session, sid, url)
                            await get_ip_cameras_info(session, sid, url, cam_list, session_start_time)
                        else:
                            await session.close()
                            print(data['error_code'])
                            raise KeyboardInterrupt
                    except KeyError:
                        await session.close()
                        return 'Нет данных'     
                else:
                    print(f"Ошибка при запросе данных: {response.status}")


async def get_ip_cameras_list(session, sid, url) -> list:
    """ 
    Ссылка на запрос списка камер: https://[IP]:[PORT]/settings/ip_cameras/?sid=[SID] 
    """
    async with session.get(f'{url}/settings/ip_cameras/', params={'sid': sid}, verify_ssl=False) as response:
        if response.status == 200:
            # Убираем комментарии из json ответа
            data = jsonc.loads(await response.text())   

            cam_list = data['subdirs']

            # Чистим лишнее
            cam_list.remove('ip_camera_add')
            return cam_list      
        else:
            print(f"Ошибка при запросе данных: {response.status}")
    

async def get_ip_cameras_info(session, sid, url, cam_list, session_start_time) -> dict:
    """
    Функция получения данных о камерах
    Создание session - сессия aiohttp
    Получение списка камер. Осуществление обхода по требуемым характеристикам каждой камеры
    """
    cam_info = {}
    tasks_cams = []
    tasks_ch = []
    semaphore = asyncio.Semaphore(10)

    # 60 * 15 = 900 сек -> Обновление SID
    session_stop_time = session_start_time + 60 * 15

    # Цикл запросов к конечным точкам. Цикл необходимо прерывать каждые 15 минут для обновления SID 
    while time.time() < session_stop_time:
        for cam in cam_list:
            task = asyncio.ensure_future(fetch_cams(semaphore, session, sid, url, cam, cam_info))
            tasks_cams.append(task)
        results = [await res for res in asyncio.as_completed(tasks_cams)]

        if cam_info:
            for cam in cam_info:
                ch_guid = cam_info[cam][2]
                task = asyncio.ensure_future(fetch_channels(semaphore, session, sid, url, cam, ch_guid, cam_info))
                tasks_ch.append(task)
            results_ch = [await res for res in asyncio.as_completed(tasks_ch)]
        else:
            pass

        # Рисуем таблицу
        draw_table(cam_info)
        
        # Таймер сна между опросом
        await asyncio.sleep(int(os.getenv('CHECK_STATE_TIMER')))


async def fetch_cams(semaphore, session, sid, url, cam, cam_info):
    """
    Формирование задач сбора информации по endpoints камер
    Обноление списка камер
    """
    # Список конечных точек сбора информации по камерам
    endpoints = [f'{url}/settings/ip_cameras/{cam}/name',
                 f'{url}/settings/ip_cameras/{cam}/connection_ip',
                 f'{url}/settings/ip_cameras/{cam}/channel00_guid']

    async with semaphore:
        tasks = []
        
        for endpoint in endpoints:
            # Формируем задачи
            tasks.append(get_data(session, endpoint, sid))

        # Добавляем в словарь список с полученными данными
        cam_info[cam] = await asyncio.gather(*tasks, return_exceptions=True)


async def fetch_channels(semaphore, session, sid, url, cam, ch_guid, cam_info):
    """
    Формирование задач сбора информации по endpoints каналов
    Обноление списка камер
    """
    # Список конечных точек сбора информации по каналам
    endpoints = [f'{url}/settings/channels/{ch_guid}/flags/signal']
    
    async with semaphore:
        tasks = []

        for endpoint in endpoints:
            # Формируем задачи
            tasks.append(get_data(session, endpoint, sid))

        # Добавляем во вложенный список в словаре информацию о флаге канала
        cam_info[cam].extend(await asyncio.gather(*tasks, return_exceptions=True))
        

async def get_data(session, endpoint, sid):
    """
    Получение данных из json по endpoints
    """
    async with session.get(endpoint, params = {'sid': sid}, verify_ssl=False) as response:
        if response.status == 200:
            # Обработка данных
            data = jsonc.loads(await response.text())
            return data['value']
        else:
            print(f"Ошибка при запросе данных: {response.status}")
        

def draw_table(cam_info):
    """ 
    Сортировка полученных значений по IP камеры. 
    Отображение в виде таблицы, используя PrettyTable 
    """
    os.system('cls' if os.name == 'nt' else 'clear')

    table = PrettyTable()
    table.field_names = ["Название камеры", "GUID", "IP", "GUID Канала", "Статус канала"]

    for i in cam_info:
        table.add_row([cam_info[i][0], 
                       i, 
                       cam_info[i][1], 
                       cam_info[i][2],
                       Back.GREEN + 'Online ' + Style.RESET_ALL 
                            if cam_info[i][3] == 1 
                                else Back.RED + 'Offline' + Style.RESET_ALL,
                                ])
    table.sortby = 'IP'
    print(table.get_string(title=str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))))


async def kill_tasks():
    """
    Закрытие запланированных задач asyncio 
    """
    pending = asyncio.all_tasks()
    for task in pending:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task 
    loop.stop()
    

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())   
    except KeyboardInterrupt:
        print('\nПрограмма завершена !')
        loop.run_until_complete(kill_tasks())
        loop.close()