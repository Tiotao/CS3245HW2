from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import *

PATH = "D:\\training\\"
DICT_DIR = 'D:\\dictionary.txt'
POSTING_DIR = 'D:\\postings.txt'
QUERY_DIR = 'D:\\query.txt'
OUT_DIR = 'D:\\output.txt'

from config import *
# TODO: use args

def read_query():
	query_file = file(QUERY_DIR, 'r')
	queries = []
	for line in query_file:
		queries.append(parse_query(line))

	query_file.close()

	out_file = file(OUT_DIR, 'w')
	for query in queries:
		out_file.write(str(query) + '\n')

	out_file.close()

def parse_query(raw):
	operators = ('AND', 'OR', 'NOT', '(', ')')
	parsed = []

	# the following steps split the input string into list of operators and operands
	raw_atoms = raw.split()
	atoms = []

	# some special treatment for ( and ) without surrounding spaces on one side
	for atom in raw_atoms:
		if atom[0] == '(':
			atoms.append('(')
			atom = atom[1:]
		if atom[-1] == ')':
			atoms.append(atom[:-1])
			atoms.append(')')
		else:
			atoms.append(atom)

	# buffer, which is a reserved word...
	buff = []
	for atom in atoms:
		# we've found an operator, everything accumulated in buffer are joined by 'AND' in ()
		if atom in operators:
			if len(buff) > 2:
				parsed.append('(')
				# Do not add the last 'AND'
				parsed.extend(buff[:-1])
				parsed.append(')')
			else:
				parsed.extend(buff[:-1])
			parsed.append(atom)
			buff = []
		else:
			buff.append(stemming_word(atom))
			buff.append('AND')

	# add the remaining buffer content
	if len(buff) > 2:
		parsed.append('(')
		# Do not add the last 'AND'
		parsed.extend(buff[:-1])
		parsed.append(')')
	else:
		parsed.extend(buff[:-1])
	return parsed

stemmer = PorterStemmer()
def stemming_word(word):
	return stemmer.stem(word.lower())

read_query()