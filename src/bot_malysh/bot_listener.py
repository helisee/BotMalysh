import configparser
from bot_malysh import utils

def run():
	print('VK listener started')

	_config = configparser.ConfigParser()
	_root=utils.get_project_root()
	_config_file_path=f'{_root}\\settings.ini'
	print(_config_file_path)
	_config.read(_config_file_path)
	_group_id=_config["BotMalysh"]["group_id"]
	_token=_config["BotMalysh"]["token"]

	print(f'token={_token}\ngroup_id={_group_id}')