#!/usr/bin/env python
# Filename: recollq.py
"""Execute a recoll query and launch gedit or firefox on the first decent match.

	Examples:
	# this will find and gedit a text file containing the indicated search terms
	>>> recollq 'bitcoin mtgox txt google trend'

	Dependencies:
	recoll (python API to linux recoll app)
	argparse

	TODO:
	1. Add option to filter out some common red herrings like .bash_history (or hobs's .bash_history_forever)
	2. Add option to provide colorized/highlighted search result text abstracts like 
	   recoll or google desktop, and select on to launch
	3. add quiet and verbose options

	Copyright:
	((c) Hobson Lane dba TotalGood)
"""

import recoll
from argparse import ArgumentParser

p = ArgumentParser(description=__doc__.strip())
p.add_argument(
	'-u','--url','-b','--basic',
	action='store_true',
	help='Output urls without size, type, title, or abstract',
	)
p.add_argument(
	'-f','--file',
	action='store_true',
	help='Output filename without size, type, title, or abstract',
	)
p.add_argument(
	'-t','--title',
	action='store_true',
	help='Output filename without size, type, title, or abstract',
	)
p.add_argument(
	'-p','--path',
	action='store_true',
	default=True,
	help='Output path without size, type, title, or abstract',
	)
p.add_argument(
	'-v','--verbose',
	action='store_true',
	help='Output an abstract, relevance and other details',
	)
p.add_argument(
	'-q','--quiet',
	action='store_true',
	# action='store_false',
	# dest='verbose',
	help='Output urls without size, type, title, or abstract.',
	)
p.add_argument(
	'-n','--num',
	type=int,
	default = 1,
	help='Limit the maximum number of results.')
p.add_argument(
	'-a','--ascending',
	action='store_true',
	help='Sort the results in ascending alphabetical order by their titles.')
p.add_argument(
	'-d','--descending',
	action='store_true',
	help='Sort the results in descending alphabetical order by their filenames.')
p.add_argument(
	'terms', 
	#metavar='SEARCH_TERMS',
	type=str,
	nargs = '+', # other options '*','+', 2
	default = None,
	help='Recoll query (search) terms.')
o = p.parse_args()
#print o

o.num = max(o.num,1)

db=recoll.connect()
q=db.query()
if (o.descending and not o.ascending) or (o.ascending and not o.descending):
	q.sortby(field='filename', ascending=o.ascending)
N=q.execute(' '.join(o.terms))

for i in range(min(N,o.num)):
	s=q.fetchone()
	if o.title:
		print s.title
	if o.file:
		print "'"+s.filename+"'"
	if o.url:
		print "'"+s.url+"'"
	if o.path:
		print "'"+s.url[7:]+"'"
	if o.verbose:
		print '({0}) {1} MB {2}'.format(s.relevancyrating,float(s.dbytes)/1000000.0,str(s.mtime)) #,s.author)

