class UserController(object):
	users = {}	

	@classmethod
	def add_image(self, user_id, img):
		if not user_id in self.users:
			print("Instance user_id dict")
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
			self.count = 0
			self.imgs.clear()
		self.imgs.append(img)
		self.count = len(self.imgs)
		print(f'В imgs картинок: {self.count}')
		return self.imgs