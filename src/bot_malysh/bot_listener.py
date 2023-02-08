import bot_malysh.db
import vk_api
import configparser
import json
import os
import random
import requests
import time
import unicodedata

from bot_malysh import utils, db
from bot_malysh.db import User
from pathlib import Path
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

nickname_change_state = {}
nickname_len = 20

hello_event_msgs = ['/start','привет','прив','ghbdtn','даров','дарова','здаров','здарова']
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
		elif event.type == VkBotEventType.MESSAGE_EVENT:
			message_event_handler(event=event, vk=vk)
		elif event.type == VkBotEventType.MESSAGE_REPLY:
			message_reply_handler(event=event)
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
				keyboard=mkeyboard.get_keyboard(),
				message=f'Отлично, @id{user.user_id}(Вы) сменили ник на @id{user.user_id}({new_nickname})',
				chat_id=event.obj.chat_id
			)
			nickname_change_state.pop(event.obj.message["from_id"], None)

	attachments=event.object.message['attachments']
	if bool(attachments):
		print('attachments selected')
		# print(attachments)
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
				open(f'{directory}\\{title}', "wb").write(response.content)
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
			message='&#12288;',
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
			message='&#12288;',
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
			keyboard=mkeyboard.get_keyboard(),
			message=f'Введите свой новый ник ✏\n⚠ Ограничение по количеству символов: {nickname_len}',
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