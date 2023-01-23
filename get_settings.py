-import configparser
from pathlib import Path

def main():
	_config = configparser.ConfigParser()
	_root = Path(__file__).parent
	print(_root)
	_config_file_path = f'{_root}\\settings.ini'
	print(_config_file_path)
	_config.read(_config_file_path)
	
	# считывание и запись параметров
	_group_id = _config["BotMalysh"]["group_id"]
	_token = _config["BotMalysh"]["token"]
	
	print(f'token={_token}\ngroup_id={_group_id}')

if __name__ == '__main__':
	main()