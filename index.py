from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from nltk.corpus import stopwords
from os import walk
import sys, json
from SkipList import SkipList
import cPickle as pickle
import getopt
import config


#######################################################################
# Sample command:
#	python index.py -i D:\training\ -d dictionary.txt -p postings.txt
#######################################################################


#######################################################################
# Read filenames - Creating posting lists - Generate outputs
#######################################################################

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
	
	# init stdout
	curr = 0
	
	# init tokens list (sorted) and the list length
	sorted_keys = sorted(dict.iterkeys())
	total = len(sorted_keys)
	
	# init content for dictionary file
	dict_content = ""

	# init content for postings file
	# header: json of all filenames in the corpus
	posting_header = json.dumps(filenames) + '\n'
	posting_f = open(posting_file, 'wb')
	posting_f.write(posting_header)
	
	# preparing content to be written into files
	for key in sorted_keys:
		skiplist_pos = pickle_and_write(dict[key], posting_f)
		dict_line = "%(token)s %(length)s %(start)s %(end)s\n"%{'token':str(key), 'length':str(len(dict[key])), 'start':str(skiplist_pos[0]), 'end':str(skiplist_pos[1])}
		dict_content = dict_content + dict_line
		curr += 1
		sys.stdout.write("\rprocessing: " + ("%.2f" % (100.0 * curr / total)) + '%')
		sys.stdout.flush()

	# finished writing positing file 
	posting_f.close()

	# write into dictionary file
	dict_f = open(dict_file, 'wb')
	dict_f.write(str(dict_content))
	dict_f.close()

# build SkipList for every tokens from its posting array, build skips.
# pickled each SkipList into string and write into posting files. 
# return starting and ending position of the SkipList in the positng file
def pickle_and_write(posting_array, posting_f):
	skip_list = SkipList(posting_array).build_skips()
	skip_list_pickled = pickle.dumps(skip_list)
	skip_list_start = posting_f.tell()
	posting_f.write(skip_list_pickled + '\n')
	skip_list_end = posting_f.tell()
	return skip_list_start, skip_list_end


#######################################################################
# Generating Posting SkipLists
#######################################################################

# returns a dictionary
# key: tokens
# value: posting array
def generate_posting_array_dict(filenames):

	# init stdout 
	curr = 0

	# init empty posting array 
	posting_array_dict = {}
	
	# totol length of files to be processed 
	total = len(filenames)
	for filename in filenames:
		# genearate tokenized and stemmed (stopwords and numbers can be filtered by option) from a file
		tokens = generate_tokens(str(filename))
		# store tokens and filnames into posting_array_dict
		# append filenames at end of the posting array if token key existed in the dictionary
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


#######################################################################
# Tokenization and Stemming 
#######################################################################

# generate array of tokens from file
def generate_tokens(filename):
	words = tokenize_sentences(filename)
	tokens = stemming_words(words)
	if config.ELIMINATE_STOP_WORDS:
		tokens = filter_stopwords(tokens)
	if config.ELIMINATE_NUMBERS:
		tokens = filter_numbers(tokens)
	return tokens

# tokenize sentences in a file into array of words
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

#######################################################################
# Optimisation (options available in config.py)
# filter stopwords
# filter numbers
#######################################################################

stop = stemming_words(stopwords.words('english'))
def filter_stopwords(words):
	return [i for i in words if i not in stop]

def filter_numbers(words):
	return [i for i in words if i.isdigit()]


#######################################################################
# Main
#######################################################################

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
