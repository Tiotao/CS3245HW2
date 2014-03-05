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
	for query in queries:
		result = (process(query))
		output(result)



def read_queries():
	query_file = file(QUERY_DIR, 'r')
	queries = []
	for line in query_file:
		queries.append(parse_query(line))

	query_file.close()

	return queries

# operator precedence
operators = {
	'OR': 1,
	'AND': 10,
	'NOT': 100,
	'+': 2,
	'-':2,
	'/':3,
	'*':3
}

def parse_query(raw):

	# Add surrounding whitespaces to parenthesis 
	raw = re.sub("(\(|\))", r" \1 ", raw)
	# split the words from operators
	tokens = raw.split()
	
	# convert to reverse polish notation
	# with shunting-yard algorithm
	
	output = []
	stack = []
	for token in tokens:
		# push left parenthesis to the stack
		if token == '(':
			stack.append(token)
		# if token is right parenthesis,
		# pop stack onto output until 
		# left parenthesis, which is ignored
		elif token == ')':
			while stack[-1] != '(':
				output.append(stack.pop())
			# throw away the left parenthesis
			stack.pop()
		elif token in operators:
			while stack and stack[-1] in operators and (token != 'NOT' and operators[token] == operators[stack[-1]] or operators[token] < operators[stack[-1]]):
				output.append(stack.pop())
			stack.append(token)
		else:
			output.append(token)

	while stack:
		output.append(stack.pop())

	return output


def output(result):
	out_file.write(' '.join(map(str, result)) + '\n')


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
	return query
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

out_file = file(OUT_DIR, 'w')
search()
out_file.close()