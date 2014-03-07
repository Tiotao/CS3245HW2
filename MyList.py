import math

class MyList:
	"""
	This file is a wrapper over SkipList and native list 
	to provide a common API for easier manipulation over
	retireved postings and intermediate result
	"""
	def __init__(self, lst):
		self.data = lst
		self.length = len(lst)
		self.is_list = type(lst) is list
		if self.is_list:
			self.current = 0
			if self.length > 0:
				self.current_data = lst[0]
		else:
			self.current = self.data.get_node(0)
			if self.length > 0:
				self.current_data = self.current.data

	def __len__(self):
		return self.length

	def current_val(self):
		return self.current_data

	def has_next(self):
		if self.is_list:
			return self.current +1 < self.length
		else:
			return self.current.next != None

	def next(self):
		if not self.has_next():
			return False # return false on failed operation
		if self.is_list:
			self.current += 1
			self.current_data = self.data[self.current]
		else:
			self.current = self.current.next
			self.current_data = self.current.data
		return True

	def has_skip(self):
		if self.is_list:
			return False
			return self.has_next()
		else:
			return self.current.has_skip()

	def skip_val(self):
		if self.is_list:
			return self.data[min(self.length - 1, int(math.sqrt(self.length)) + self.current)]
		return self.current.skip.data

	def skip(self):
		if self.is_list:
			idx = min(self.length - 1, int(math.sqrt(self.length)) + self.current)
			self.current = idx
			self.current_data = self.data[idx] 
		else:
			self.current = self.current.skip
			self.current_data = self.current.data

	def to_list(self):
		if self.is_list:
			return self.data
		else:
			return self.data.to_list()