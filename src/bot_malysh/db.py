import sqlite3
import vk_api
import time
from pathlib import Path


class db(object):
	conn = None
	cursor = None
	users = {}
	session_api = None

	@classmethod
	def __init__(self, db_path, session_api):
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()
		self.session_api = session_api

	@classmethod
	def execute(self, request):
		self.cursor.execute(request)

	@classmethod
	def add_user(self, user_id):
		self.users[user_id] = User(self.session_api, user_id)

	@classmethod
	def get_user(self, user_id):
		tmp_user = self.users.get(user_id)
		if tmp_user == None:
			self.add_user(user_id)
			return self.users[user_id]
		else:
			return tmp_user 

class User:
	
	user_id=0
	nickname=None
	last_msg_timestamp=None

	def __init__(self, session_api, user_id):
		self.user_id = user_id
		self.last_msg_timestamp = int(time.time())
		
		#если нет такого айдишника, то вносим запись в бд
		if self.exists_user():
			# обращение к api через users_id
			users = session_api.users.get(user_ids = (self.user_id))
			self.nickname = users[0]['first_name']
			request = f"INSERT INTO users (user_id, nickname, last_msg_timestamp) VALUES ({self.user_id}, \"{self.nickname}\", \"{self.last_msg_timestamp}\")"
			db.execute(request)
		else:
			self.nickname = self.get_nickname()
			request = f"SELECT last_msg_timestamp FROM users WHERE user_id={self.user_id}"
			db.execute(request)
			self.last_msg_timestamp = db.cursor.fetchall()[0][0]
			#self.set_last_msg_timestamp(self.last_msg_timestamp)
			#request = f"UPDATE users SET last_msg_timestamp = '{self.last_msg_timestamp}' WHERE user_id = {self.user_id}"
			#db.execute(request)
		db.conn.commit()
 
	def exists_user(self):
		request=f'SELECT EXISTS (SELECT user_id FROM users WHERE user_id={self.user_id})'
		db.execute(request)
		db.conn.commit()
		return (db.cursor.fetchall()[0][0] == 0)

	def set_nickname(self, nickname):
		request = f"UPDATE users SET nickname = '{nickname}' WHERE user_id = {self.user_id}"
		print(f'db.Users.{self.user_id}.set_nickname')
		db.execute(request)
		db.conn.commit()

	def get_nickname(self):
		#print(f"1get_nickname: {self.nickname}")
		if self.nickname == None:
			request = f"SELECT nickname FROM users WHERE user_id = {self.user_id}"
			db.execute(request)
			self.nickname = db.cursor.fetchall()[0][0]
			
			#print(f"2get_nickname: {self.nickname}")
			db.conn.commit()
		return self.nickname

	def edit_nickname(self, new_nickname):
		self.nickname = new_nickname
		request = f"UPDATE users SET nickname = '{self.nickname}' WHERE user_id = {self.user_id}"
		db.execute(request)
		db.conn.commit()

	def set_last_msg_timestamp(self, last_msg_timestamp):
		self.last_msg_timestamp = last_msg_timestamp
		request = f"UPDATE users SET last_msg_timestamp = '{self.last_msg_timestamp}' WHERE user_id = {self.user_id}"
		db.execute(request)
		db.conn.commit()
 
 	#def get_last_msg_timestamp_from_db(self):
 		#request = 
#def main():
#	db.__init__(rf'{Path(__file__).parent.parent.parent}/malysh.db3')
	
	#user = User(2);
	#request = 'SELECT nickname from users WHERE user_id = 1'
	#db.execute(request)
	#print(db.cursor.fetchall()[0][0])

#if __name__ == "__main__":
#    main()