from nltk.stem.porter import *
from nltk.corpus import stopwords
import re, getopt, json
import cPickle as pickle
from SkipList import SkipList
from MyList import MyList

import config

#######################################################################
# Read query - execute query - output result
#######################################################################

def search():
	queries = read_queries()
	for query in queries:
		try:
			result = evaluate(query)
		except Exception, e:
			result = []
		output(result)

def read_queries():
	query_file = file(QUERY_DIR, 'r')
	queries = []
	for line in query_file:
		try:
			query = parse_query(line.strip())
		except Exception, e:
			# if we determined a syntax error, read it as an empty query 
			query = []
		queries.append(query)

	query_file.close()

	return queries

def output(result):
	out_file.write(' '.join(map(str, result)) + '\n')


#######################################################################
# Parsing
#######################################################################

# operator precedence
operators = {
	'OR': 1,
	'AND': 10,
	'NOT': 100
}

precedence = operators

# number of operands for each operator
required_operands = {
	'OR': 2,
	'AND': 2,
	'NOT': 1
}
def parse_query(raw):
	"""
	Parse a raw query string into Reverse Polish Notation for easy evaluation
	"""
	# Add surrounding whitespaces to parenthesis 
	raw = re.sub("(\(|\))", r" \1 ", raw)
	# split the words from operators
	tokens = raw.split()
	
	find_and_optimise_parentheses_subquery(tokens)
	find_and_optimise_AND_subquery(tokens)

	return to_RPN(tokens)

def to_RPN(tokens):
	"""
	convert to reverse polish notation with shunting-yard algorithm
	"""
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
			try:
				while stack[-1] != '(':
					output.append(stack.pop())
			# if we do not find a left parenthesis,
			# there must be mismatched parentheses
			except IndexError, e:
				raise Exception("mismatched parenthesis")
			# throw away the left parenthesis
			stack.pop()
		# if token is an operator o1:
		elif token in operators:
			# as long as there is an operator o2 at the top of stack
			while (stack and stack[-1] in operators 
			# and either:
			# 1) the operator is left assosiative (i.e. not a NOT) and o1 and o2 has equal precedence
			# 2) o2 has higher precedence
			# we continue to pop o2 off the stack
			and (token != 'NOT' and precedence[token] == precedence[stack[-1]] 
				or precedence[token] < precedence[stack[-1]])):
				output.append(stack.pop())
			# after no more operators are on the top of the stack, we push o1 onto the stack
			stack.append(token)
		else:
			# it's a word token
			# we normalise it and add it to output queue
			output.append(normalise_word(token))

	while stack:
		if stack[-1] in ('(', ')'):
			raise Exception("mismatched parenthesis")
		output.append(stack.pop())

	return output


#######################################################################
# Optimisation
# This part is not very well written, but since the bottleneck is
# operation on large postings list, so some inefficient optimisation
# should be compensated by faster postings processing
#######################################################################


def find_and_optimise_parentheses_subquery(query):
	"""
	Identify all parentheses in the query, and optimise the inner query
	"""
	start = -1
	index = 0
	parentheses = []
	# locate all ( and )
	# +1 since we want content excluding surrounding ( and )
	left = [i+1 for i, x in enumerate(query) if x == '(']
	right = [i for i, x in enumerate(query) if x == ')']

	# for each subquery, optimise it
	for start, end in zip(left, right):
		find_and_optimise_AND_subquery(query[start:end])

def find_and_optimise_AND_subquery(query):
	"""
	Identify chains of AND queries and sort operands in ascending
	order of size of postings list.

	Notice that for a chain of AND queries, such as
	A AND B AND NOT C AND (X OR Y AND Z),
	this method sees the following operands:
	[A, B, NOT C, (X OR Y AND Z)]

	Therefore we explicitly invoke this function inside 
	find_and_optimise_parentheses_subquery
	to deal with nested queries inside parentheses, then we invoke this 
	function again on the entire query, so parentheses will be seen 
	as one operand
	"""
	start = end = 0
	index = 0
	skip = False
	while index < len(query):
		token = query[index]
		# treating (subquery) as one operand
		if token == '(':
			skip = True
		elif token == ')':
			skip = False
		elif not skip and token == 'OR':
			end = index
			# only optimise if there are more than 2 operands
			if (end - start) > 3:
				query[start:end] = optimise_AND_subquery(query[start:end])
			start = index + 1
		else:
			pass

		index += 1

	end = index
	if (end - start > 3):
		query[start:end] = optimise_AND_subquery(query[start:end]) 

def optimise_AND_subquery(query):
	"""
	Sort a chain of ANDs by ascending order of size of postings list.
	"""
	operands = []
	buff = []
	skip = False
	# break the query into list of operands, such as 
	# A AND B AND NOT C AND (X OR Y AND Z),
	# changed to
	# [A, B, NOT C, (X OR Y AND Z)]
	for token in query:
		if token == '(':
			buff.append(token)
			skip = True		
		elif token == ')':
			buff.append(token)
			skip = False
		elif not skip and token == 'AND':
			operands.append(buff)
			buff = []
		else:
			buff.append(token)
	operands.append(buff)

	# sort the list of operands
	optimised = sorted(operands, key=estimate_query)

	# reconstruct the operands by flatten and intersperse it with 'AND'
	return  intersperse(optimised, ['AND'])

def estimate_query(query):
	
	query = to_RPN(query)

	"""
	Estimate the size of a given query written in RPN
	"""
	stack = []
	for token in query:
		# if we see an operator, we take out the required operands from the stack
		# evaluate the result, and push it back to the stack
		if token in operators:
			# not enough operands
			if len(stack) < required_operands[token]:
				raise Exception("insufficient operands")
			else:
				operands = []
				for i in range(required_operands[token]):
					operands.append(stack.pop())
				stack.append(estimate_op(token, operands))
		# otherwise, we push the token, which is an operand, to the stack directly
		else:
			stack.append(token)

	if len(stack) == 1:
		return freq(stack[0])
	elif len(stack) == 0:
		return []
	else:
		print stack
		raise Exception("too many operands")


def estimate_op(operator, operands):
	if operator == 'NOT':
		return len(master_postings) - freq(operands[0])
	elif operator == 'AND':
		return min(freq(operands[0]), freq(operands[1]))
	else:
		return freq(operands[0]) + freq(operands[1])

#######################################################################
# Evaluation
#######################################################################

def evaluate(query):
	"""
	Evaluate a given query written in RPN
	"""
	stack = []
	for token in query:
		# if we see an operator, we take out the required operands from the stack
		# evaluate the result, and push it back to the stack
		if token in operators:
			# not enough operands
			if len(stack) < required_operands[token]:
				print stack, token
				raise Exception("insufficient operands")
			else:
				operands = []
				for i in range(required_operands[token]):
					operands.append(stack.pop())
				stack.append(apply_op(token, operands))
		# otherwise, we push the token, which is an operand, to the stack directly
		else:
			stack.append(token)

	if len(stack) == 1:
		return lookup(stack[0]).to_list()
	elif len(stack) == 0:
		return []
	else:
		print stack
		raise Exception("too many operands")

def apply_op(operator, operands):
	if operator == 'NOT':
		return complement(operands[0])
	elif operator == 'AND':
		return intersect(operands)
	else:
		return union(operands)

#######################################################################
# Set operations
#######################################################################

def complement(operand):
	postings = lookup(operand).to_list()
	result =  MyList([x for x in master_postings if x not in postings])
	del postings
	return result

def intersect(operands):
	first = lookup(operands[0])
	second = lookup(operands[1])

	result = []
	if len(first) == 0 or len(second) == 0:
		return MyList([]) 
	else:
		carry_on = True
	while carry_on:
		a = first.current_val()
		b = second.current_val()

		if a == b:
			result.append(a)
			carry_on &= first.next()
			carry_on &= second.next()
		elif a < b:
			if first.has_skip() and first.skip_val() <= b:
				first.skip()
			else:
				carry_on &= first.next()
		else:
			if second.has_skip() and second.skip_val() <= a:
				second.skip()
			else:
				carry_on &= second.next()
	del first
	del second
	return MyList(result)

def union(operands):
	first = lookup(operands[0]).to_list()
	second = lookup(operands[1]).to_list()

	i = j = 0
	result = []

	while i < len(first) and j < len(second):
		if first[i] == second[j]:
			result.append(first[i])
			i += 1
			j += 1
		elif first[i] < second[j]:
			result.append(first[i])
			i += 1
		else:
			result.append(second[j])
			j += 1

	# add remaining, one of the following is actually empty
	result.extend(first[i:])
	result.extend(second[j:])
	del first
	del second
	return MyList(result)

#######################################################################
# Utilities
#######################################################################

# return the size of the postings for a given token
def freq(word):
	if type(word) is int:
		return word
	elif word in dictionary:
		return dictionary[word]['freq']
	else:
		return 0

def lookup(word):
	if type(word) is str:
		if config.ELIMINATE_STOP_WORDS and is_stopword(word):
			return MyList(master_postings)
		elif config.ELIMINATE_NUMBERS and is_number(word):
			return MyList(master_postings)
		if word in dictionary:
			postings_file.seek(dictionary[word]['start'])
			raw = postings_file.read(dictionary[word]['size'])
			return MyList(pickle.loads(raw))
		else:
			return MyList([])
	else:
		return word

# http://stackoverflow.com/a/5656097/1903464
def joinit(iterable, delimiter):
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x

def intersperse(iterable, delimiter):
	lst =  list(joinit(iterable, delimiter))
	return [item for sublist in lst for item in sublist]

stemmer = PorterStemmer()
# case folding, stemming
def normalise_word(word):
	return stemmer.stem(word.lower())

stop = [normalise_word(i) for i in stopwords.words('english')]
def is_stopword(word):
	return word in stop

def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

#######################################################################
# Main
#######################################################################

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
QUERY_DIR = DICT_DIR = POSTING_DIR = OUT_DIR = None
for o, a in opts:
    if o == '-q':
        QUERY_DIR = a
    elif o == '-o':
    	OUT_DIR = a
    elif o == '-d':
        DICT_DIR = a
    elif o == '-p':
        POSTING_DIR = a
    else:
        pass # no-op
if QUERY_DIR == None or DICT_DIR == None or POSTING_DIR == None or OUT_DIR == None:
    usage()
    sys.exit(2)

out_file = file(OUT_DIR, 'w')
dict_file = file(DICT_DIR, 'r')
dictionary = {}
for line in dict_file:
	# format: token freq start_pos end_pos
	data = line.split()
	dictionary[data[0]] = {
		'freq':  int(data[1]),
		'start': int(data[2]),
		'size':   int(data[3]) - int(data[2])
	}

dict_file.close()
postings_file = file(POSTING_DIR, 'r')
# list of all docIDs
master_postings = postings_file.readline()
master_postings = json.loads(master_postings)

search()

out_file.close()
postings_file.close()