[Описание работы SDK Trassir 4.2](https://trassir.com/software-updates/file/TrassirManual_en_SDK_4.2.pdf)  
[Описание работы SDK Trassir 4.4.16.0](https://www.dssl.ru/upload/iblock/3e0/sdk_ru.pdf)  
[Техническая документация ПО Trassir](https://www.dssl.ru/support/tech/documentation/po-trassir/)


Запрос SID (длительность жизни SID 15 минут)
```
https://[server_ip_address]:[port]/login?username=[username]&password=[password]
```

Данные о каналах
```
https://[server_ip_address]:[port]/settings/channels/?sid=[session_id]
```

Данные о конкретном канале
```
https://[server_ip_address]:[port]/settings/channels/[GUID]/?sid=[session_id]
```

Флаг доступности канала
```
https://[server_ip_address]:[port]/settings/channels/[GUID]/flags/signal?sid=[session_id]
```

Данные о камерах
```
https://[server_ip_address]:[port]/settings/ip_cameras/?sid=[session_id]
```

Данные о конкретной камере
```
https://[server_ip_address]:[port]/settings/ip_cameras/[CAM_GUID]/?sid=[session_id]
```

Запрос имени (названия) камеры
```
https://[server_ip_address]:[port]/settings/ip_cameras/[CAM_GUID]/name?sid=[session_id]
```

Данные о Connection IP
```
https://[server_ip_address]:[port]/settings/ip_cameras/[CAM_GUID]/connection_ip?sid=[session_id]
```

Запрос GUID канала камеры
```
https://[server_ip_address]:[port]/settings/ip_cameras/[CAM_GUID]/channel00_guid?sid=[session_id]
```