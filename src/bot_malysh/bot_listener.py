import configparser
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import requests
import os
from vk_api.utils import get_random_id
from bot_malysh import utils, db
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

_PDFDOC_MINSIZE = 159000
_PDFDOC_MAXSIZE = 180000

settings = dict(one_time=True)
mkeyboard = VkKeyboard(**settings)
_snackbar_msg = "{\"type\": \"show_snackbar\", \"text\": \"Клик клик клик\n                                              Бот Малыш {´◕ ◡ ◕｀}\"}"
mkeyboard.add_callback_button(label='Клик', color=VkKeyboardColor.POSITIVE, payload=_snackbar_msg)

_config = configparser.ConfigParser()
_root = utils.get_project_root()
_config_file_path = f'{_root}\\settings.ini'
_config.read(_config_file_path)
#считывание и запись параметров
#блок загрузки параметров бота с ./settings.ini
_group_id = _config["BotMalysh"]["group_id"]
_token = _config["BotMalysh"]["token"]
_access_token=_config["BotMalysh"]["access_token"]

def run():
	#print('VK listener started')
	#print(f'token={_token}\ngroup_id={_group_id}')

	vk_session = vk_api.VkApi(token=_token)
	vk = vk_session.get_api()

	longpoll = VkBotLongPoll(vk_session, _group_id)

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
	r = vk.messages.send(
		user_id=str(event.obj.message["from_id"]),
		random_id=get_random_id(),
		peer_id=event.obj.message["peer_id"],
		keyboard=mkeyboard.get_keyboard(),
		message='Привет, @id0(кожаный мешок)',
		chat_id=event.obj.chat_id
		)
	
	

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
	r = vk.messages.sendMessageEventAnswer(
		access_token=_access_token,
		event_id=event.object.event_id,
		user_id=event.object.user_id,
		peer_id=event.object.peer_id,
		event_data=json.dumps(event.object.payload)
		)

def message_reply_handler(event):
	print('message reply')

def message_typing_state_handler(event):
	print('message typing state')

def group_join_handler(event):
	print('group join')

def group_leave_handler(event):
	print('group leave')
