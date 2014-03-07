This is the README file for A0099314Y's and A0099332Y's submission

== General notes about this assignment ==

< explain your approach to indexing, and how are dict and postings written to disk>


When it comes to searching, we do the following:

First, read queries line by line and tokenize it.

Then, we optimise the order of the terms AND chains to prioritise
terms that results in shorter postings list. We do this by first
locating all subqueries in parenthesis, identify the AND chains, and
sort the operands based on estimated postings size. We then run the
same algorithm on the entire query, ignoring subqueries in
parenthesis.

After the order of operands has been optimised, we convert the
expression to reverse polish notation using shunting-yard algorithm.
The benefit is that during evaluation, the order of operation is
extremely simple as all parenthesis has been removed and we don't need
to consider operator precedence. Another benefit is that using reverse
polish notation, we can guarentee that we are keeping at most 2
postlings list in memory at the same time.

We then evaluate the RPN expressing, look up the postings list if we
see a token, and process them using either intersect, union, or
complement operation for AND, OR and NOT operator.

== Files included with this submission ==
.
|-- ESSAY.txt        answer to essay question
|-- MyList.py        wrapper class for skiplist and native list
|-- README.txt       this file
|-- SkipList.py      implements a skip list for postings file storage
|-- config.py        configuration switches for testing
|-- dictionary.txt   indexed dictionary  
|-- index.py         python script for indexing 
|-- postings.txt     indexed postings file
`-- search.py        python script for searching


== Statement of individual work ==

Please initial one of the following statements.

[x] I, A0099314Y, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[x] I, A0099332Y, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

== References ==

Appreciation towards the classmates on IVLE forum that helped each other
to check the correctness of the output.

Shunting-yard algorithm
 - https://igor.io/2013/12/03/stack-machines-shunting-yard.html
python: most elegant way to intersperse a list with an element 
 - http://stackoverflow.com/a/5656097/1903464