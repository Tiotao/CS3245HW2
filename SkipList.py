import math

class Node:
	def __init__(self, data=None):
		self.next = None	# next node
		self.skip = None	# the target node of the skip pointer (if has)
		self.data = int(data)
	
	def append_node(self, node):
		self.next = node

	def has_next(self):
		return self.next != None

	# if the node has a skip pointer
	def has_skip(self):
		return self.skip != None

	def __repr__(self):
		return "Node: " + str(self.data)

class SkipList:
	def __init__(self, array=None):
		
		self.length = 0
		self.skip = False

		if array == None:
			self.head = None	# first node in the list	
			self.tail = None	# last node in the list

		else:
			array.sort()
			for i in array:
				node = Node(i)
				self.append(node)


	def __len__(self):
		return self.length

	# if skip pointers are created for this list
	def is_skipped(self):
		return self.skip


	# get a specific node according to its index
	def get_node(self, index):
		current = self.head
		while index > 0 :
			current = current.next
			index = index - 1
		return current

	# append a node after the last node of the list
	def append(self, node):
		if len(self) == 0:
			self.head = node
			self.tail = node
		else:
			self.tail.append_node(node)
			self.tail = node

		self.length = self.length + 1

	# calculate the skip distance of the list
	def skip_distance(self):
		list_length = len(self)
		skipDis = math.floor(math.sqrt(list_length))
		return skipDis

	# connect two nodes by adding skip pointers from current node to target node. input: index! not node!
	def connect(self, current_index, target_index):
		current_node = self.get_node(current_index)
		target_node = self.get_node(target_index)
		current_node.skip = target_node

	# create skip pointes for the entire list
	def build_skips(self):
		if self.is_skipped():
			self.clearSkips()
		else:
			distance = self.skip_distance()
			current = 0
			target = 0 + distance
			while target < self.length:
				self.connect(current, target)
				current = target
				target = target + distance
			self.skip = True
		return self

	# clear skip pointers for the entire list
	def clear_skips(self):
		if self.skip == True:
			current = self.head
			while current.has_next():
				if current.has_skip():
					current.skip = None
				current = current.next
			self.skip = False
		return self

	def to_list(self):
		result = []
		current = self.head
		while current.has_next():
			result.append(current.data)
			current = current.next
		result.append(self.tail.data)
		return result

	# return two arrays. one with all nodes, another with skip pointers
	def display(self):
		first = []
		second = []
		current = self.head
		while current.has_next():
			if current.has_skip():
				second.append((current.data, current.skip.data))
			first.append(current.data)
			current = current.next
		first.append(self.tail.data)
		return { "all_nodes": first, "skips": second }
