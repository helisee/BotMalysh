import configparser
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
from bot_malysh import utils

def run():
	print('VK listener started')

	""" блок загрузки параметров бота с ./settings.ini
	"""
	_config = configparser.ConfigParser()
	_root = utils.get_project_root()
	_config_file_path = f'{_root}\\settings.ini'
	_config.read(_config_file_path)

	""" считывание и запись параметров
	"""
	_group_id = _config["BotMalysh"]["group_id"]
	_token = _config["BotMalysh"]["token"]

	print(f'token={_token}\ngroup_id={_group_id}')

	vk_session = vk_api.VkApi(token=_token)
	vk = vk_session.get_api()

	longpoll = VkBotLongPoll(vk_session, _group_id)

	""" начало слушателя
	"""
	for event in longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			message_new_handler(event)
		elif event.type == VkBotEventType.MESSAGE_REPLY:
			message_reply_handler(event)
		elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
			message_typing_state_handler(event)
		elif event.type == VkBotEventType.GROUP_JOIN:
			group_join_handler(event)
		elif event.type == VkBotEventType.GROUP_LEAVE:
			group_leave_handler(event)

def message_new_handler(event):
	print('message new')

def message_reply_handler(event):
	print('message reply')

def message_typing_state_handler(event):
	print('message typing state')

def group_join_handler(event):
	print('group join')

def group_leave_handler(event):
	print('group leave')
