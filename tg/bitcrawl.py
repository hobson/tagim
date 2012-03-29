#!/usr/bin/python
"""Crawls the web looking for quantitative information about bitcoin popularity.

	Examples (require Internet connection):
	# this will find and gedit a text file containing the indicated search terms
	>>> bitcrawl.py # takes about a minute
	329
	>>> bitcrawl.py # takes a sec
	329
	
	Dependencies:
		argparse -- ArgumentParser
		urllib
		urllib2

	TODO:
	1. Add option to filter out some common red herrings like .bash_history (or hobs's .bash_history_forever)
	2. Add option to provide colorized/highlighted search result text abstracts like 
	   recoll or google desktop, and select on to launch
	3. add quiet and verbose options
	4. deal with csv: http://www.google.com/trends/?q=bitcoin&ctab=0&geo=us&date=ytd&sort=0 , 
	      <a href='/trends/viz?q=bitcoin&date=ytd&geo=us&graph=all_csv&sort=0&scale=1&sa=N'>
	      other examples in comments below
	5. poll domain name registries to determine the number of domain names with "bitcoin" in them or beginning with "bit" or having "bit" and "coin" in them 
	6. build website and REST to share bitcoin trend info, several domain names saved at bustaname under shopper@tg username 
	      pairbit, bitpair, coinpair, paircoin, coorbit, bitcorr, bitcoinarbitrage, etc

	Copyright:
	((c) Hobson Lane dba TotalGood)

"""

FILENAME='/home/hobs/Notes/notes_repo/bitcoin popularity trend.txt'

def parse_args():
	# TODO: "meta-ize" this by only requiring number format specification in some common format 
	#       like sprintf or the string input functions of C or python, and then convert to a good regex
	# TODO: add optional units and suffix patterns
	URLs=dict([
				('http://bitcoincharts.com/about/markets-api/', 
					[ # TODO: make this a dict instead of a list, with the key acting as the variable/quantity name
					[r'<td class="label">Blocks</td><td>',          # (?<= ... )\s*
					 r'[0-9]{1,9}'                               ],  # (...)
					[r'<td class="label">Total BTC</td><td>',
					 r'[0-9]{0,2}[.][0-9]{1,4}[MmKkGgBb]' ], 
					[r'<td class="label">Difficulty</td><td>',
					 r'[0-9]{1,10}' ], 
					[r'<td class="label">Estimated</td><td>',
					 r'[0-9]{1,10}' ] ,
					[r'<td class="label">Network total</td><td>',
					 r'[0-9]{0,2}[.][0-9]{1,4}' ],
					[r'<td class="label">Blocks/hour</td><td>',
					 r'[0-9]{0,3}[.][0-9]{1,4}' ]
					],
				),
				('https://en.bitcoin.it/wiki/Trade', [[
					r'accessed\s',
					r'([0-9],)?[0-9]{3},[0-9]{3}' ]]
				), 
				('https://mtgox.com',                [[
					r'Weighted Avg:<span>',            # (?<= ... )\s*
					r'\$[0-9]{1,2}[.][0-9]{3,5}',    ]] # (...)
				), 
			])
	from argparse import ArgumentParser
	p = ArgumentParser(description=__doc__.strip())
	p.add_argument(
		'-b','--bitfloor','--bf',
		type    = int,
		nargs   = '?',
		default = 0,
		help    = 'Retrieve N prices from the order book at bitfloor.',
		)
	p.add_argument(
		'-u','--urls','--url',
		type    = str,
		nargs   = '*',
		default = URLs,
		help    = 'URL to scape data from.',
		)
	p.add_argument(
		'-p','--prefix',
		type    = str,
		nargs   = '*',
		default = '', 
		help    = 'HTML that preceeds the desired numerical text.',
		)
	p.add_argument(
		'-r','--regex','--regexp','--re',
		type    = str,
		nargs   = '*',
		default = '',
		help    = 'Python/Perl regular expression to capture numerical string only.',
		)
	p.add_argument(
		'-v','--verbose',
		action  = 'store_true',
		default = False,
		help    = 'Output an progress information.',
		)
	p.add_argument(
		'-q','--quiet',
		action  = 'store_true',
		default = False,
		help    = "Don't output anything to stdout, not even the numerical value scraped from the page. Overrides verbose.",
		)
	p.add_argument(
		'-t','--tab',
		action  = 'store_true',
		default = 'false',
		help    = "In the output file, precede numerical data with a tab (column separator).",
		)
	p.add_argument(
		'-n','--newline',
		action  = 'store_true',
		default = 'false',
		help    = "In the output file, after outputing the numerical value, output a newline.",
		)
	p.add_argument(
		'-s','--separator','-c','--column-separator',
		metavar = 'SEP',
		type    = str,
		default = '',
		help    = "In the output file, precede numberical data with the indicated string as a column separator.",
		)
	p.add_argument(
		'-m','--max','--max-results',
		metavar = 'N',
		type=int,
		default = 1,
		help    = 'Limit the maximum number of results.',
		)
	p.add_argument(
		'-f','--path','--filename',
		type    = str,
		#nargs  = '*', # other options '*','+', 2
		default = FILENAME,
		help    = 'File to append the numerical data to (after converting to a string).',
		)
	return p.parse_args()

#Historic Trade Data
#Trade data is available as CSV, delayed by approx. 15 minutes.
#http://bitcoincharts.com/t/trades.csv?symbol=SYMBOL[&start=UNIXTIME][&end=UNIXTIME]
#returns CSV:
#unixtime,price,amount
#Without start or end set it'll return the last few days (this might change!).
#Examples
#Latest mtgoxUSD trades:
#http://bitcoincharts.com/t/trades.csv?symbol=mtgoxUSD
#All bcmPPUSD trades:
#http://bitcoincharts.com/t/trades.csv?symbol=bcmPPUSD&start=0
#btcexYAD trades from a range:
#http://bitcoincharts.com/t/trades.csv?symbol=btcexYAD&start=1303000000&end=1303100000
#Telnet interface
#There is an experimental telnet streaming interface on TCP port 27007.
#This service is strictly for personal use. Do not assume this data to be 100% accurate or write trading bots that rely on it.

COOKIEFILE='/home/hobs/tmp/wget_cookies.txt'
#REFERRERURL='http://google.com'
#USERAGENT='Mozilla'

#!/usr/bin/env python

import urllib
import urllib2


class Bot:
	"""A browser session that follows redirects and maintains cookies."""
	def __init__(self):
		self.response    = ''
		self.params      = ''
		self.url         = ''
		redirecter  = urllib2.HTTPRedirectHandler()
		cookies     = urllib2.HTTPCookieProcessor()
		self.opener = urllib2.build_opener(redirecter, cookies)
#		build_opener creates an object that already handles 404 errors, etc, right?
#			except urllib2.HTTPError, e:
#				print "HTTP error: %d" % e.code
#			except urllib2.URLError, e:
#				print "Network error: %s" % e.reason.args[1]
	def GET(self, url):
		self.response = self.opener.open(url).read()
		return self.response
	def POST(self, url, params):
		self.url    = url
		self.params = urllib.urlencode(parameters)
		self.response = self.opener.open(url, self.params ).read()
		return 

def get_page(url):
	try:
		return urllib.urlopen(url).read()
	except:
		return ''

def get_next_target(page):
	start_link = page.find('<a href=')
	if start_link == -1: 
		return None, 0
	start_quote = page.find('"', start_link)
	end_quote = page.find('"', start_quote + 1)
	url = page[start_quote + 1:end_quote]
	return url, end_quote

def union(p,q):
	for e in q:
		if e not in p:
			p.append(e)

def get_all_links(page):
	links = []
	while True:
		url,endpos = get_next_target(page)
		if url:
			links.append(url)
			page = page[endpos:]
		else:
			break
	return links

def get_links(seed,max_depth=1,max_breadth=1e6,max_links=1e6):
	tocrawl = [seed]
	crawled = []
	depthtocrawl = [0]*len(tocrawl)
	depth = 0
	page = tocrawl.pop()
	depth = depthtocrawl.pop()
	links = 0
	while depth<=max_depth and links<max_links:
		links += 1
		if page not in crawled:
			i0=len(tocrawl)
			union(tocrawl, get_all_links(get_page(page)))
			crawled.append(page)
			for i in range(i0,len(tocrawl)):
				depthtocrawl.append(depth+1)
		if not tocrawl: break
		page  = tocrawl.pop(0) # FIFO to insure breadth first search
		depth = depthtocrawl.pop(0) # FIFO
	return crawled

def rest_json(url='https://api.bitfloor.com/book/L2/1'):
	import json
	b = HttpBot()
	data_str = b.GET(url)
	#print data_str
	data     = json.loads( data_str )
	#print data
	return data

def mine_data(url='',prefixes=r'',regexes=r''):
	print 'Mining URL "'+url+'" ...'
	if not url: 
	    return None
	page=Bot().GET(u)
	print 'Retrieved '+str(len(page))+' characters/bytes.'
	if isinstance(prefixes,list):
		for [prefix,regex] in prefixes:
			r = re.compile(r'(?<='+prefix+r')\s*'+r'(?P<quantity>'+regex+r')')
			mo = r.search(page)
			if mo:
				import pprint
				q = mo.group(mo.lastindex)
				print 'found the value:', q

if __name__ == "__main__":
	import re
	o = parse_args()

#	data = rest_json()
#	print type(data)
#	print data

#	example bot usage
#	signin_results   = bot.POST('https://example.com/authenticator', {'passwd':'foo'})
#	singoff_results  = bot.POST('https://example.com/deauthenticator',{})

	if type(o.urls)==dict:
		for u,r in o.urls.items():
			mine_data(u,r)
	elif type(o.urls)==list and len(o.urls)==len(o.prefix)==len(o.regex):
		for i,u in enumerate(o.urls):
			mine_data(u,o.prefix[i],o.regex[i])
	elif type(o.urls)==type(o.prefix)==type(o.regex)==str and len(o.urls)>1 and len(o.regex)>0 and len(o.prefix)>0:
		mine_data(o.urls,o.prefix,o.regex)
	else:
		raise ValueError('Invalid URL, prefix, or regex argument.')


	#links = get_links("https://en.bitcoin.it/wiki/Trade",1)
	#print len(set(links))

