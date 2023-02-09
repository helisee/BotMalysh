import bot_malysh.db
import configparser
from io import BytesIO
import json
import matplotlib.pyplot as plt
import os
import sys
import random
import requests
import time
import unicodedata
import vk_api

from PIL import Image
from bot_malysh import utils, db
from bot_malysh.db import User
from pathlib import Path
from pdf2image import convert_from_path, convert_from_bytes, exceptions
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
_PDFDOC_MINSIZE = 159000
_PDFDOC_MAXSIZE = 180000

settings = dict(one_time=True)
mkeyboard = VkKeyboard(**settings)
settings_keyboard = VkKeyboard(**settings)

tomain_label = '🗄 На главную'
settings_label = '⚙ Настройки'
mkeyboard.add_callback_button(label=settings_label, color=VkKeyboardColor.POSITIVE, payload="{\"type\": \"settings_key\"}")
mkeyboard.add_line()
_snackbar_msg = "{\"type\": \"show_snackbar\", \"text\": \"Клик клик клик\n                                              Бот Малыш {´◕ ◡ ◕｀}\"}"
mkeyboard.add_callback_button(label='Клик', color=VkKeyboardColor.POSITIVE, payload=_snackbar_msg)

settings_keyboard.add_callback_button(label='✏ Сменить ник', color=VkKeyboardColor.SECONDARY, payload="{\"type\": \"change_nickname_key\"}")
settings_keyboard.add_line()
settings_keyboard.add_callback_button(label=tomain_label, color=VkKeyboardColor.NEGATIVE, payload="{\"type\": \"tomain_key\"}")

_root = utils.get_project_root()
_config = configparser.ConfigParser()
_config_file_path = f'{_root}/settings.ini'
_config.read(_config_file_path)
#считывание и запись параметров
#блок загрузки параметров бота с ./settings.ini
_access_token=_config["BotMalysh"]["access_token"]
_group_id = _config["BotMalysh"]["group_id"]
_token = _config["BotMalysh"]["token"]

last_message = {}
nickname_change_state = {}
nickname_len = 20

hello_event_msgs = ['/start','привет','прив','првиет','привте','ghbdtn','даров','дарова','здаров','здарова']
hello_reply_msgs = ['Привет','Прив','Ась','Даров','Дарова','Здаров','Здарова', 'Да-да, приветик', 'Приветик, пупсик <3']

def run():
	#print('VK listener started')
	#print(f'token={_token}\ngroup_id={_group_id}')

	vk_session = vk_api.VkApi(token=_token)
	vk = vk_session.get_api()

	longpoll = VkBotLongPoll(vk_session, _group_id)
	db.db(rf'{_root}/malysh.db3', vk)
	# начало слушателя
	for event in longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			message_new_handler(event=event, vk=vk)
			nikitma_module(event=event , vk=vk)
		elif event.type == VkBotEventType.MESSAGE_EVENT:
			message_event_handler(event=event, vk=vk)
		elif event.type == VkBotEventType.MESSAGE_REPLY:
			message_reply_handler(event=event)
			#last_message[event.obj.]
		elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
			message_typing_state_handler(event=event)
		elif event.type == VkBotEventType.GROUP_JOIN:
			group_join_handler(event=event)
		elif event.type == VkBotEventType.GROUP_LEAVE:
			group_leave_handler(event=event)

def message_new_handler(event, vk):
	msg = event.object.message['text']
	user = db.db.get_user(event.obj.message["from_id"])
	vkmsg_date = event.object.message['date']
	for key, value in db.db.users.items():
		print(f"От {value.nickname} сообщение\n{event.obj.message['text']}")

	print(f"Время соообщения: {user.last_msg_timestamp}\nТекущее время:    {int(time.time())}")
	if int(user.last_msg_timestamp)+8600 <= int(time.time()) or (msg.lower() in hello_event_msgs): 
		result = vk.messages.send(
			user_id=str(event.obj.message["from_id"]),
			random_id=get_random_id(),
			peer_id=event.obj.message["peer_id"],
			keyboard=mkeyboard.get_keyboard(),
			message=random.choice(hello_reply_msgs),
			#'&#12288;' - символ пробела
			chat_id=event.obj.chat_id
			)
		#vk.messages.delete(message_ids=result, delete_for_all=1)
		user.set_last_msg_timestamp(vkmsg_date)

	if bool(nickname_change_state):
		if bool(nickname_change_state[event.obj.message["from_id"]]):
			new_nickname = msg.split()[0][0:12]
			user.set_nickname(new_nickname)

			result = vk.messages.send(
				user_id=user.user_id,
				random_id=get_random_id(),
				peer_id=event.obj.message["peer_id"],
				keyboard=settings_keyboard.get_keyboard(),
				message=f'Отлично, @id{user.user_id}(Вы) сменили ник на @id{user.user_id}({new_nickname})',
				chat_id=event.obj.chat_id
			)
			nickname_change_state.pop(event.obj.message["from_id"], None)

	attachments=event.object.message['attachments']
	if bool(attachments):
		print('attachments selected')
		for attachment in attachments:
			doc=attachment['doc']
			# отсеивание форматов и веса документа
			# полагаем, что формат чека pdf, а размер от 159000 до 180000
			if doc["ext"] == "pdf" and int(doc["size"]) > _PDFDOC_MINSIZE and int(doc["size"]) < _PDFDOC_MAXSIZE:
				url=doc['url']
				title=doc['title']
				print('Документ: ', title)
				response = requests.get(url)
				directory = f"{_root}\\cache\\doc"

				if not os.path.exists(directory):
					os.makedirs(directory)
				doc_path = f"{directory}\\{title}"
				print(doc_path)

				poppler_path = "C:\\poppler-0.68.0\\bin"
			#try:
				f = open(doc_path, "wb")
				f.write(response.content)

				#size = image.size
				A4_WIDTH = 210
				A4_HEIGHT = 297
				pdf_width = 320
				in_one_sheet = 5
				image_width = pdf_width * in_one_sheet
				image_height = int(pdf_width / A4_WIDTH * A4_HEIGHT);  # высота сгенерированного изображения (пропорции А4 210x297)
				mainimg = Image.new("RGB", (image_height, image_width), "white")

				with open(doc_path, 'rb') as f:  # The mode is r+ instead of r
					images = convert_from_bytes(f.read(), poppler_path = poppler_path)
					image = images[0]
					
					user_imgs = UserController.add_image(user.user_id, image)
					i = 0
					for img in user_imgs:
						mainimg.paste(img, (i * pdf_width, 0, img.size[0], img.size[1]))
				
				mainimg.show()
			#except:
				#print("Файл не сохранился")
			#else:
				#print(f"Файл {title} сохранён")

"""			try:
			except NotImplementedError:
				pass
			except exceptions.PDFPopplerTimeoutError:
				pass
			except exceptions.PDFInfoNotInstalledError:
				pass
			except exceptions.PDFPageCountError:"""


	#else:
		#print('None attachments')

def message_event_handler(event, vk):
	if event.object.payload.get('type') == 'settings_key':
		result = vk.messages.sendMessageEventAnswer(
			access_token=_access_token,
			event_id=event.object.event_id,
			user_id=event.object.user_id,
			peer_id=event.object.peer_id,
			event_data=''
			)
		result = vk.messages.send(
			user_id=str(event.object.user_id),
			random_id=get_random_id(),
			peer_id=event.object.peer_id,
			keyboard=settings_keyboard.get_keyboard(),
			message=settings_label,
			chat_id=event.obj.chat_id
			)
		#vk.messages.delete(message_ids=result, delete_for_all=1)
	elif event.object.payload.get('type') == 'tomain_key':
		result = vk.messages.sendMessageEventAnswer(
			access_token=_access_token,
			event_id=event.object.event_id,
			user_id=event.object.user_id,
			peer_id=event.object.peer_id,
			event_data=''
			)
		result = vk.messages.send(
			user_id=str(event.object.user_id),
			random_id=get_random_id(),
			peer_id=event.object.peer_id,
			keyboard=mkeyboard.get_keyboard(),
			message=tomain_label,
			chat_id=event.obj.chat_id
			)
		#vk.messages.delete(message_ids=result, delete_for_all=1)
	elif event.object.payload.get('type') == 'change_nickname_key':
		nickname_change_state[event.object.user_id] = True
		result = vk.messages.sendMessageEventAnswer(
			access_token=_access_token,
			event_id=event.object.event_id,
			user_id=event.object.user_id,
			peer_id=event.object.peer_id,
			event_data=''
			)
		result = vk.messages.send(
			user_id=str(event.object.user_id),
			random_id=get_random_id(),
			peer_id=event.object.peer_id,
			keyboard=VkKeyboard.get_empty_keyboard(),
			message=f'✏ Введите свой новый ник\n⚠ Ограничение по количеству символов: {nickname_len}',
			chat_id=event.obj.chat_id
			)
	elif event.object.payload.get('type') == 'show_snackbar':
		result = vk.messages.sendMessageEventAnswer(
			access_token=_access_token,
			event_id=event.object.event_id,
			user_id=event.object.user_id,
			peer_id=event.object.peer_id,
			event_data=json.dumps(event.object.payload)
			)

def message_reply_handler(event):
	print('message reply')

def message_typing_state_handler(event):
	user = db.db.get_user(event.obj["from_id"])
	print(f'{user.nickname} пишет ...')

def group_join_handler(event):
	print('group join')

def group_leave_handler(event):
	print('group leave')

def edit_message(peer_id, message_id, message, keyboard=None):
	return vk.messages.edit(peer_id=peer_id, message_id=message_id, message=message, keyboard=keyboard)

def nikitma_module(event, vk):
	# ·	Никитма – описание мини-языка
	# ·	никита)  = Привет - регистроНЕзависимый
	# ·	НИКИТА(А) = Бл*  - регистрозависимый ;;; (А) - математический период
	# ·	никит = Эй - регистроНЕзависимый
	# ·	[Нн]екитА = Что – регистрозависимый ;;;  [Пп] = П или п
	# ·	никитишь = делаешь - регистроНЕзависимый
	# ·	никита? = Как дела? - регистроНЕзависимый
	# ·	китя = спасибо - регистроНЕзависимый
	# ·	оникитенно = отлично = регистроНЕзависимый
	# ·	[Нн]еКит = ничего - регистрозависимый
	# ·	никитую = работаю - регистроНЕзависимый

	##  lower()
	#  .strip()
	# 'Нефтяк!


	msg = event.object.message['text']
	user = db.db.get_user(event.obj.message["from_id"])
	if msg == '':
		return
	elif msg.lower() == 'никита)':
		vk.messages.send(
			user_id=user.user_id,
			message='Никита)',
			random_id=get_random_id()
		)
	elif msg.strip()[0].find('НИКИТАА') > -1:
		vk.messages.send(
			user_id=user.user_id,
			message='Не ругайся',
			random_id=get_random_id()
		)
	elif msg.lower() == 'никит':
		vk.messages.send(
			user_id=user.user_id,
			message='НекитА?',
			random_id=get_random_id()
		)
	elif msg == 'НекитА' or msg == 'некитА':
		vk.messages.send(
			user_id=user.user_id,
			message='НеКит',
			random_id=get_random_id()
		)
	elif msg.lower() == 'никитишь':
		vk.messages.send(
			user_id=user.user_id,
			message=random.choice(['Угу', 'Да', 'Никитую']),
			random_id=get_random_id()
		)
	elif msg == 'НекитА никитишь?' or msg == 'некитА никитишь?':
		vk.messages.send(
			user_id=user.user_id,
			message='Никитую',
			random_id=get_random_id()
		)
	elif msg == 'НеКит' or msg == 'неКит':
		vk.messages.send(
			user_id=user.user_id,
			message='Ну ладно',
			random_id=get_random_id()
		)
	elif msg.lower() == 'никита?':
		vk.messages.send(
			user_id=user.user_id,
			message='Оникитенно',
			random_id=get_random_id()
		)
		vk.messages.send(
			user_id=user.user_id,
			message='А у тебя никита?',
			random_id=get_random_id()
		)
	elif msg.lower() == 'оникитенно':
		vk.messages.send(
			user_id=user.user_id,
			message='Я рад',
			random_id=get_random_id()
		)
	elif msg.lower() == 'ты никитявый' or msg.lower() == 'никитявый':
		vk.messages.send(
			user_id=user.user_id,
			message='Китя <3\nТы тозе)',
			random_id=get_random_id()
		)


class UserController(object):
	users = {}	

	@classmethod
	def add_image(self, user_id, img):
		if not user_id in self.users:
			self.users[user_id] = UserImages()
		user_imgs = self.users[user_id].add(img)
		return user_imgs

class UserImages:
	imgs = []
	count = 0
	_imgs_max_size = 5

	def __init__(self):
		self.imgs = []
		self.count = 0

	def add(self, img):
		
		if len(self.imgs) < self._imgs_max_size:
			pass
		else: 
			self.imgs.clear()
		self.imgs.append(img)
		return self.imgs