
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from os import walk

PATH = "D:\\training\\"
DICT_DIR = 'D:\\dictionary.txt'
POSTING_DIR = 'D:\\postings.txt'

def index():
	
	masterDict = {}

	filenames = []
	for (root, dirs, files) in walk(PATH):
		filenames.extend(files)
	
	for filename in filenames:
		words = tokenizeFiles(filename)
		tokens = stemmingWords(words)
		for t in tokens:
			key = str(t)
			if key in masterDict:
				if not int(filename) in masterDict[key]:
					masterDict[key].append(int(filename))
			else:
				masterDict[key] = [int(filename)]

	f = open(DICT_DIR, 'w')
	f.write(str(masterDict))
	print 'index finished'




def tokenizeFiles(filename):
	fileDir = PATH + filename
	f = open(fileDir, 'r')
	fileString = f.read().lower()
	
	sentences = sent_tokenize(fileString)
	words = []
	for s in sentences:
		words = words + word_tokenize(s)
	return words

def stemmingWords(words):
	stemmer = PorterStemmer()
	tokens = []
	for w in words:
		tokens.append(stemmer.stem(w))
	return tokens
	


index()