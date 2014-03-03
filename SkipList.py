import math

class Node:
	def __init__(self, data=None):
		self.next = None
		self.skip = None
		self.data = int(data)
	
	def appendNode(self, node):
		self.next = node

	def hasNext(self):
		return self.next != None

	def hasSkip(self):
		return self.skip != None

	def __repr__(self):
		return "Node: " + str(self.data)

class SkipList:
	def __init__(self, array=None):
		
		self.length = 0

		if array == None:
			self.head = None
			self.tail = None

		else:
			for i in array:
				node = Node(i)
				self.append(node)


	def __len__(self):
		return self.length

	def getNode(self, index):
		current = self.head
		while index > 0 :
			current = current.next
			index = index - 1
		return current


	def append(self, node):
		if len(self) == 0:
			self.head = node
			self.tail = node
		else:
			self.tail.appendNode(node)
			self.tail = node

		self.length = self.length + 1

	def skipDistance(self):
		listLength = len(self)
		skipDis = math.floor(math.sqrt(listLength))
		return skipDis

	def connect(self, current, target):
		currentNode = self.getNode(current)
		targetNode = self.getNode(target)
		currentNode.skip = targetNode

	def buildSkips(self):
		distance = self.skipDistance()
		current = 0
		target = 0 + distance
		while target < self.length:
			self.connect(current, target)
			current = target
			target = target + distance

	def display(self):
		
		first = []
		second = []
		current = self.head
		while current.hasNext():
			if current.hasSkip():
				second.append((current.data, current.skip.data))
			first.append(current.data)
			current = current.next
		first.append(self.tail.data)
		return { "all_nodes": first, "skips": second }




