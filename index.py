
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from os import walk
import sys

PATH = "D:\\training\\"
DICT_DIR = 'D:\\dictionary.txt'
POSTING_DIR = 'D:\\postings.txt'

from config import *
# TODO: use args

def index():
	print 'start indexing'	
	masterDict = {}

	filenames = []
	for (root, dirs, files) in walk(PATH):
		filenames.extend(files)
	
	total = len(filenames)
	curr = 0
	for filename in filenames:
		words = tokenize_files(filename)
		tokens = stemming_words(words)
		for t in tokens:
			key = str(t)
			if key in masterDict:
				if not int(filename) in masterDict[key]:
					masterDict[key].append(int(filename))
			else:
				masterDict[key] = [int(filename)]
		curr += 1
		sys.stdout.write("\r" + ("%.2f" % (100.0 * curr / total)) + '%')
		sys.stdout.flush()

	f = open(DICT_DIR, 'w')
	f.write(str(masterDict))
	print "\nindex finished"
	f.close()




def tokenize_files(filename):
	fileDir = PATH + filename
	f = open(fileDir, 'r')
	fileString = f.read().lower()
	f.close()

	sentences = sent_tokenize(fileString)
	words = []
	for s in sentences:
		words = words + word_tokenize(s)
	return words

def stemming_words(words):
	stemmer = PorterStemmer()
	tokens = []
	for w in words:
		tokens.append(stemmer.stem(w))
	return tokens
	


index()