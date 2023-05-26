#Скрипт отображения текста при движении
#05.2023

'''
<parameters>
	<title>Set Text on Motion Detect</title>
	<version>1.0</version>
	<parameter>
		<id>CHANNELS</id>
		<name>Каналы для тревоги</name>
		<type>objects</type>
	</parameter>
	<parameter>
		<id>CUSTOM_TEXT</id>
		<name>Текст на экране</name>
		<type>string</type>
		<value>ДВИЖЕНИЕ!</value>
	</parameter>
	<parameter>
		<id>DELAY</id>
		<name>Длительность отображения текста (сек.)</name>
		<type>integer</type>
		<value>8</value>
		<min>1</min>
		<max>100</max>
	</parameter>
	<parameter>
		<id>FONT_COLOR</id>
		<name>Цвет текста</name>
		<type>string</type>
		 <value>FF2D02</value>
	</parameter>
		<parameter>
		<id>FONT_SIZE</id>
		<name>Размер текста (px)</name>
		<type>integer</type>
		<value>100</value>
		<min>1</min>
		<max>300</max>
	</parameter>
	<parameter>
		<id>X</id>
		<name>X</name>
		<type>integer</type>
		<value>30</value>
		<min>1</min>
		<max>100</max>
	</parameter>
	<parameter>
		<id>Y</id>
		<name>Y</name>
		<type>integer</type>
		<value>70</value>
		<min>1</min>
		<max>100</max>
	</parameter>
</parameters>
'''

GLOBALS = globals()
CHANNELS = GLOBALS.get("CHANNELS", "")
FONT_COLOR = GLOBALS.get("FONT_COLOR", "")
FONT_SIZE = GLOBALS.get("FONT_SIZE", "")
X = GLOBALS.get("X", "")
Y = GLOBALS.get("Y", "")
CUSTOM_TEXT = GLOBALS.get("CUSTOM_TEXT", "")
DELAY = GLOBALS.get("DELAY", "")


if CHANNELS:
	CHANNELS = CHANNELS.split(",")
else:
	raise ValueError("Выберите каналы!")
	
if not CUSTOM_TEXT:
	raise ValueError("Введите текст тревоги!")


class MotionText():
	def __init__(self, ev):
		self.ev = ev
		self.check()

	def check(self):
		for name in CHANNELS:
			if self.ev.origin == object(name).guid:
				self.view_text(True)
			else:
				pass

	def view_text(self, fl):
		if fl:
			alert(self.ev.type, 10000)
			text_set(self.ev.origin, CUSTOM_TEXT, X, Y, FONT_SIZE, 90, 15,  FONT_COLOR)
			timeout(1000 * DELAY, lambda: self.view_text(False))
		else:
			text_set(self.ev.origin, ' ', X, Y, FONT_SIZE, 90, 15,  FONT_COLOR)

# text_set(object('Камера 1').guid, 
# 		  	'текст', 
#			'перемещение по горизонтали', 
#			'перемещение по вертикали', 
#			'размер', 
#			'обрезка текста снизу', 
#			'чем меньше значение, тем больше текст', 
#			'FF2D02 - цвет')

activate_on_events("Motion Start", "", MotionText)
