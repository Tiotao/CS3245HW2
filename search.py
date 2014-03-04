from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *
import re, random

PATH = "D:\\training\\"
DICT_DIR = 'D:\\dictionary.txt'
POSTING_DIR = 'D:\\postings.txt'
QUERY_DIR = 'D:\\query.txt'
OUT_DIR = 'D:\\output.txt'

from config import *
# TODO: use args


def search():
	queries = read_queries()
	result = []
	for query in queries:
		result.append(process(query))
	output(result)

def read_queries():
	query_file = file(QUERY_DIR, 'r')
	queries = []
	for line in query_file:
		queries.append(parse_query(line))

	query_file.close()

	return queries


def parse_query(raw):
	operators = ('AND', 'OR', 'NOT', '(', ')')
	operators_re = '(AND|OR|NOT|\(|\))'

	# split the words from operators
	raw_atoms = re.split(operators_re, raw)
	atoms = []
	for atom in raw_atoms:
		if atom in operators:
			atoms.append(atom)
		else:
			# tokenize input
			words = word_tokenize(atom)
			if len(words) > 1:
				atoms.append('(')
				for i in range(len(words) - 1):
					atoms.append(normalise_word(words[i]))
					atoms.append('AND')
				atoms.append(normalise_word(words[-1]))
				atoms.append(')')
			elif len(words) == 1:
				atoms.extend(words)
	return atoms

def output(result):
	out_file = file(OUT_DIR, 'w')
	for line in result:
		out_file.write(' '.join(map(str, line)) + '\n')

	out_file.close()

# process all AND queries into nested arrays,
# so A OR B AND C OR D becomes [A, [B, C], D]
def fold(query):
	result = []
	buff = []
	for atom in query:
		if atom == 'AND':
			continue
		elif atom == 'OR':
			result.append(buff)
			buff = []
		else:
			buff.append(atom)
	result.append(buff)
	return result

def process(query):
	query = fold(query)
	ORs = []
	for ANDs in query:
		if len(ANDs) == 1:
			ORs.append(lookup(ANDs[0]))
		else:
			res = reduce(intersect, ANDs, master)
			ORs.append(res)

	
	result = reduce(union, ORs, [])

	return result

master = range(100)

def union(l1, l2):
	if type(l1) is not list:
		l1 = lookup(l1)
	if type(l2) is not list:
		l2 = lookup(l2)
	i = 0;
	j = 0;
	result = []

	while i < len(l1) and j < len(l2):
		if l1[i] == l2[j]:
			result.append(l1[i])
			i += 1
			j += 1
		elif l1[i] < l2[j]:
			result.append(l1[i])
			i += 1
		else:
			result.append(l2[j])
			j += 1

	# add remaining, one of the following is actually empty
	result += l1[i:]
	result += l2[j:]
	return result

def intersect(l1, l2):
	if type(l1) is not list:
		l1 = lookup(l1)
	if type(l2) is not list:
		l2 = lookup(l2)

	i = 0;
	j = 0;
	result = []

	while i < len(l1) and j < len(l2):
		if l1[i] == l2[j]:
			result.append(l1[i])
			i += 1
			j += 1
		elif l1[i] < l2[j]:
			i += 1
		else:
			j += 1

	return result

dict = {
	'A' : [1, 2, 3, 4, 5],
	'B' : [4, 5, 6, 7, 8],
	'C' : [5, 6, 7, 8, 9],
	'D' : [8, 9]
}

# TODO: implement
def lookup(word):
	if word in dict:
		return dict[word]
	else:
		return []


stemmer = PorterStemmer()

# case folding, stemming
def normalise_word(word):
	return stemmer.stem(word.lower())

search()