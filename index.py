
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
from os import walk
import sys
from SkipList import SkipList
import pickle
import getopt


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

	output_content = generate_output_content(filenames, posting_array_dict)

	print "\nstart writing"

	write_output_file(output_content, dict_file, posting_file)

	print "\nmission completed :)"


def write_output_file(output_content, dict_file, posting_file):
	dict_f = open(dict_file, 'w')
	dict_f.write(str(output_content[0]))
	dict_f.close()
	posting_f = open(posting_file, 'w')
	posting_f.write(str(output_content[1]))
	posting_f.close()



def generate_output_content(filenames, dict):
	curr = 0
	all_index = ""

	for f in filenames:
		all_index = all_index + str(f) + " "
	dict_content = ""
	posting_content = all_index + '\n'
	start_line = 2
	sorted_keys = sorted(dict.iterkeys())
	total = len(sorted_keys)
	for key in sorted_keys:
		posting_array = dict[key]
		skip_list = SkipList(posting_array).build_skips()
		skip_list_pickled = pickle.dumps(skip_list)
		skip_list_start = start_line
		skip_list_end = start_line + skip_list_pickled.count('\n')
		dict_line = str(key) + " " + str(len(dict[key])) + " " + str(skip_list_start) + " " + str(skip_list_end) +  "\n"
		dict_content = dict_content + dict_line

		start_line = skip_list_end + 1
		posting_content = posting_content + skip_list_pickled + '\n'
		
		curr += 1
		sys.stdout.write("\rprocessing: " + ("%.2f" % (100.0 * curr / total)) + '%')
		sys.stdout.flush()

	return dict_content, posting_content

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

def stemming_words(words):
	stemmer = PorterStemmer()
	tokens = []
	for w in words:
		tokens.append(stemmer.stem(w))
	return tokens


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
        assert False, "unhandled option"
if docs_dir == None or dict_file == None or posting_file == None:
    usage()
    sys.exit(2)

index(docs_dir, dict_file, posting_file)
