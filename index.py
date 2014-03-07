from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from nltk.corpus import stopwords
from os import walk
import sys, json
from SkipList import SkipList
import cPickle as pickle
import getopt

import config


# Sample command:

# python index.py -i C:\Users\Yiwen\AppData\Roaming\nltk_data\corpora\reuters\training\ -d dictionary.txt -p postings.txt
# python index.py -i D:\training\ -d dictionary.txt -p postings.txt


def index(docs_dir, dict_file, posting_file):
	print 'start indexing'	

	filenames = []
	for (root, dirs, files) in walk(docs_dir):
		files = [ int(x) for x in files ]
		filenames.extend(files)
	filenames.sort()

	posting_array_dict = generate_posting_array_dict(filenames)

	print "\nstart processing output"

	generate_output(filenames, posting_array_dict, dict_file, posting_file)

	print "\nmission completed :)"


def generate_output(filenames, dict, dict_file, posting_file):
	
	# initialize iterations

	curr = 0
	sorted_keys = sorted(dict.iterkeys())
	total = len(sorted_keys)
	

	# initialize content for postings and dictionary

	dict_content = ""
	
	posting_header = json.dumps(filenames) + '\n'
	
	posting_f = open(posting_file, 'wb')
	posting_f.write(posting_header)
	
	for key in sorted_keys:

		posting_array = dict[key]
		skip_list = SkipList(posting_array).build_skips()
		skip_list_pickled = pickle.dumps(skip_list)
		skip_list_start = posting_f.tell()
		posting_f.write(skip_list_pickled + '\n')
		skip_list_end = posting_f.tell()

		dict_line = "%(token)s %(length)s %(start)s %(end)s\n"%{'token':str(key), 'length':str(len(dict[key])), 'start':str(skip_list_start), 'end':str(skip_list_end)}
		dict_content = dict_content + dict_line
		
		curr += 1
		sys.stdout.write("\rprocessing: " + ("%.2f" % (100.0 * curr / total)) + '%')
		sys.stdout.flush()

	posting_f.close()

	dict_f = open(dict_file, 'wb')
	dict_f.write(str(dict_content))
	dict_f.close()


def generate_posting_array_dict(filenames):
	posting_array_dict = {}
	curr = 0
	total = len(filenames)
	for filename in filenames:
		tokens = generate_tokens(str(filename))
		for t in tokens:
			key = str(t)
			if key in posting_array_dict:
				if not filename in posting_array_dict[key]:
					posting_array_dict[key].append(filename)
			else:
				posting_array_dict[key] = [filename]

		curr += 1
		sys.stdout.write("\rindexing: " + ("%.2f" % (100.0 * curr / total)) + '%')
		sys.stdout.flush()

	return posting_array_dict

def generate_tokens(filename):
	words = tokenize_sentences(filename)
	tokens = stemming_words(words)
	if config.ELIMINATE_STOP_WORDS:
		tokens = filter_stopwords(tokens)
	return tokens

def tokenize_sentences(filename):
	file_dir = docs_dir + str(filename)
	f = open(file_dir, 'r')
	file_string = f.read().lower()
	f.close()

	sentences = sent_tokenize(file_string)
	words = []
	for s in sentences:
		words = words + word_tokenize(s)
	return words

stemmer = PorterStemmer()
def stemming_words(words):
	tokens = []
	for w in words:
		tokens.append(stemmer.stem(w))
	return tokens

stop = stemming_words(stopwords.words('english'))
def filter_stopwords(words):
	return [i for i in words if i not in stop]

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"

docs_dir = dict_file = posting_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        docs_dir = a
    elif o == '-d':
        dict_file = a
    elif o == '-p':
        posting_file = a
    else:
        pass # no-op
if docs_dir == None or dict_file == None or posting_file == None:
    usage()
    sys.exit(2)

index(docs_dir, dict_file, posting_file)
