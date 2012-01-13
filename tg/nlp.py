#!/usr/bin/env python
# Filename: nlp.py
# Copyright (c) 2010-2011 Hobson Lane
# All rights reserved.

# Written by Hobson Lane <hobson@totalgood.com>
# NLP = Natural Language Processing

# This module used the decimal.py module as a model for syntax and style.
# This module should be replaced by similar functionality in nltk.py module, when available.
# Also, diflib is much better at this

"""
This is a Python 2.3 implementation of basic natural language processing functions
for the TotalGood Food project:

	  http://totalgood.com/food

The purpose of this module is to identify statistical features in natural English language.
The objects that contain these statsitics can be compared and differenced like sets.

Here are some example usages:

>>> x=Features('The quick brown fox jumped over the lazy dog.')
>>> y=Features('The lazy brown dog was overpassed by the hyperactive red fox.')
>>> print x.similarity(y)
0.636363636364
>>> print y.similarity(x)
0.636363636364

>>> print are_names(['column 1','Column2','Name Three','Four has a really long column name, with a little punctuation.','5','Six','5.1234'])
[0.8846283599999999, 0.9410939999999999, 0.97, 0.34301916, 0.0088462836, 1.0, 8.403969420000001e-05]
"""

version = 0.2

#__all__ = [
#	# One main class
#	'Features',
#	# Contexts
#	# 'DefaultContext',
#	# Exceptions
#	#'NLPFeaturesException',
#	# Constants
#	'SCALE',
#	'SPACE','PUNC', 'LETTER', 'DIGIT', 
#	'TYPICAL_NAME_LEN', 'YES', 'NO', 'NUMSTR',
#	'PK_NAMES','PK_TEXT'
#	# Functions
#	'essence', 'cleanpunc', 'variablize','is_number','is_float','is_integer','is_int','round_str','are_names','are_all_names'
#]
 
# might be nice to implement contexts (a la decimal.py) if more than one way of doing phrase feature algebra is necessary,
# deep copy implementation would necessitate importing copy module
# import copy as _copy

try:
	from os import linesep as eol
except ImportError:
	eol = '\n'

try: 
	from string import punctuation as PUNC, whitespace as SPACE, ascii_letters as LETTER, printable as PRINTABLE
except ImportError:
	#SPACE = ' \t\v\r\n\f\a\b' # \a and \b (ascii bell and ascii backspace) are not included in the standard string.whitespace definition
	#PUNC = '!@#$%^&*()-_+=~`:";\'<>?,./{}|[]\\'
	SPACE = '\t\n\x0b\x0c\r '
	PUNC = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
	LETTER = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
#	PRINTABLE = SPACE + PUNC + LETTER
	PRINTABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'
# warnHL: list(set(list(x))) changes the order of x!
DIGIT = '0123456789'
BADPUNC = list(set(PUNC).difference(set("'-./:_"))) # allow dots dashes and underscores in column headers and names (maybe even slashes)
BADPUNC.sort() # new list must have been allocated memory for sort in-place to work
BADPUNC = ''.join(BADPUNC)
WORDSPACE = SPACE + '-._' # additional word dividers besides whitespace
NAMELETTER = ' '+DIGIT+LETTER+'._' # some names/variables use underscores and digits and dots
NONNAMELETTER = list(set([chr(x) for x in range(256)]).difference(set(NAMELETTER)))
NONNAMELETTER.sort()  # new list must have been allocated memory for sort in-place to work
NONNAMELETTER = ''.join(NONNAMELETTER)
NONPRINTABLE = list(set([chr(x) for x in range(256)]).difference(set(PRINTABLE)))
NONPRINTABLE.sort()  # new list must have been allocated memory for sort in-place to work
NONPRINTABLE = ''.join(NONPRINTABLE)

def dedupe_whitespace(s,spacechars=' '):
	"""Merge whitespace characters (replace repeated whitespace characters with a single whitespace character).

	See Also: 
		cleanpunc, standardize_whitespace

	Example:
    >>> output = dedupe_whitespace('Black\t\tGround')  #doctest: +REPORT_NDIFF
    >>> output == 'Black\tGround'
    True
    """
	for w in spacechars:
		s = re.sub(r"("+w+"+)", w, s)
	return s

def standardize_whitespace(s,spacechars=SPACE):
	"""Merge all whitespaces into a single space with user-defined whitespace character list.

	Example:
	>>> print standardize_whitespace("Hello   World! What\t\t\tdo\t \t \tyou think?")  #doctest: +REPORT_NDIFF
	Hello World! What do you think?
	"""
	w_list='|'.join(['('+w+'+)' for w in spacechars])
	s = re.sub(r"("+w+"+)", " ", s)
	return s.strip()

# actHL: convert this to set subtraction like NONPRINTABLE = ''.join(set([chr(x) for x in range(256)]).difference(set(PRINTABLE)))
def non_list_of_characters(s=LETTER):
	"""Produce a list of characters that is the negative set of letters provided.
	
	The returned character array (string) is the list of all characters NOT in the input."""
	chr_array = []
	for c in range(256):
		if chr(c) not in s:
			chr_array.append(chr(c))
	return(''.join(chr_array)) 


# unfortunately this produces a list that includes a lot of hex characters (unprintables) that are unlikely to ever appear in an ASCII text file or CSV file when binary values not converted to hex characters
NONLETTER = non_list_of_characters(s=LETTER)
TYPICAL_NAME_LEN = 10
YES = [True,1,'1','true','True','y','Y','yes','Yes'] # floating value of 1.0 should probably not be considered "yes"
NO = [False,0,'0','false','False','n','N','no','No'] # floating value of 0.0 should probably not be considered "no"
NUMSTR = ['Null','null','NULL','None','none','NONE','Void','void','VOID','N/A','n/a','not applicable','Not Applicable','Invalid','invalid', 'INVALID','Inf','INF','inf','NaN','NAN','+inf','+INF','+Inf','-inf','-INF','-Inf']
EMPTYSTR = ['',' ',"\t","''",'""','?'] # might also consider whitespace strings or single whitespace characters as Null or empty values for numbers
PK_NAMES = ['code','Code','cd','Cd','no','No','Number','number','num','Num','id','Id','ID','#','pk','PK','key','Key','seq','Seq','sequence','Sequence'] # the last word in a primary key column name
PK_TEXT = ['primary key','key','primary id','primary identifier','key #','key number','primary number','primary #','primary no','unique id','unique identifier','identifying code','identifying number','code number','identification code','identificaiton number','serial number','identifier','code','id','number','record number','record','entry number','entry','#','entry #','identifying #','unique number','unique #','unique no','identifying no','id no','id number'] # case-insensitive phrases and words indicative of a primary key or foreign key in a description or help_text field

# value given is number multiplied by the nonstandard units to convert into SI units
# TODO: split this dict in two or three: 
#  1. canonical abreviations with conversion factors to SI
#  2. synonyms for noncanonical units and abreviations
#  3. list of cononical abreviations for fundamental units
#  4. list of canonical abreviations that compose a compound unit (speed = m/s)
UNIT_CONVERSIONS = [
                    ('m',[ (['meter','meters'],1),
                           (['yard','yards','yd','yds'],2.54*12*3/100),
                           (['inch','inches','in'],0.0254),
                         ] ),
                    ('s',[ (['second','seconds','sec'],1),
                           (['minute','min','minutes'],1.0/60),
                           (['hour','hours','hr','h'],1.0/3600),
                           (['day','days','dy','d'],1.0/3600/24),
                           (['month','months','mo'],1.0/3600/24/365.25*12),
                           (['year','years','yr','y'],1.0/3600/24/365.25),
                         ] ),
                   ]
UNIT_PREFIXES = [(['n','nano'],            0.000000001),
                 (['u',u"\u00B5",'micro'], 0.000001),
                 (['m','milli'],           0.001),
                 (['c','centi'],           0.01),
                 (['d','deci'],            0.1),
                 (['D','deca'], 10),
                 (['k','kilo'], 1000),
                 (['M','mega'], 1000000),
                 (['G','giga'], 1000000000),
                 (['T','tera'], 1000000000000),
                ]

#import django.db as db
#import nltk.tokenize as tok
import re

PARAGRAPH_EXAMPLE=" \t The quick brown fox jumped over the lazy dog.  Did you know that the previous sentence contains all the letters of the English alphabet only once ??  I bet you did !!! this passage contains intentionally nonstandard spacing near punctuation and at the beginning and end of the string.  Unfortunately doctext can't handle newlines and carriage-returns in test value strings (inconsistent leading whitespace)."

def essence(s=''):
	"""Reduce a sentence to it's essence, without punctuation, for comparison to other similar sentences without confusion by case and trailing or leading punctuation.  
	
	EXAMPLES:
	>>> essence(PARAGRAPH_EXAMPLE)
	"the quick brown fox jumped over the lazy dog.  did you know that the previous sentence contains all the letters of the english alphabet only once ??  i bet you did !!! this passage contains intentionally nonstandard spacing near punctuation and at the beginning and end of the string.  unfortunately doctext can't handle newlines and carriage-returns in test value strings (inconsistent leading whitespace"
	"""
	return s.strip().strip(PUNC+SPACE).lower()

# some code patterns taken from http://www.python-forum.org/pythonforum/viewtopic.php?f=3&t=21474
def dec2base(dec,base):
	"""Convert a decimal number to a list of decimal numbers representing the value for a new 'base'
	
	Useful for generating column labels of the form A,...,Z,AA,AB...,AZ,BA,... as in Excel 
	if used in combination with chr:
	
	Examples:
	>>> x = dec2base( 14543 , ord('Z')-ord('A')+1 )
	>>> print x
	[21, 13, 9]
	>>> print ''.join([ chr(x0+ord('A')) for x0 in x ])
	VNJ
	
	Also useful for creating numeric instead of string arrays for binary number similar to bin(dec):
	
	>>> dec2base(5,2)
	[1, 0, 1]
	>>> dec2base(21*26**2 + 13*26 + 9, 26)
	[21, 13, 9]
	"""
	newnum = [] # list of digits listed from MSB to LSB
	if dec==0:
		return [0]
	while dec>0:
		dec, rem = divmod(dec, base)
		newnum.insert(0, rem)
	return newnum

#needs to be internationalized, use whatever Excel uses to number its columns in different locals
# actHL: alphabet_offset parameter not used properly or ill-conceived
def number2alpha(i,alphabet_length=ord('Z')-ord('A'),alphabet_offset=ord('A')):
	"""Create an excel-style column label from a column index, 
	
	For example:
	i = 0,1,2,... becomes
			A,B,C,...,Z,AA,AB...,AZ,BA,BB,...
	"""
	digits = dec2base(i,alphabet_length)
	return ''.join([chr(int(x+alphabet_offset)) for x in digits])
	
def create_name(i=None, prefix='Column', offset=1, unique_names=[]):
	"""Create a name based on an integer count, usually the column number for the label
	
	Usage:
	create_name(i=None, prefix='', offset=1, unique_names=[]):
	i = column number (1 offset, unless specified otherwise below)
	offset = numbering offset for columns, e.g. if offset=0 then columns are 0,1,2...N
	unique_names = list of previously created names that cannot be used again
	"""
	if len(unique_names):
		assert(False) # actHL: Not implemented
	if not is_int(i,include_nan=False,include_empty=False):
		raise ValueError
	return(str(prefix)+str(i-int(offset)))
	#return(str(prefix)+number2alpha(i,alphabet_length=ord('z')-ord(offset.lower()),alphabet_offset=ord(offset)))

# actHL: Not implemented
#def unique_names(indexes,prefix=''):
#	un = [] # actHL: at what point should the list be converted to a set?
#	for i in indexes:
#		un.append(create_name(i,un),unique_names=un)
#	return un
	
# actHL: Not implemented
def create_names(indexes,prefix='Column'):
	print 'creating names from a list of indexes'
	n = [] # actHL: at what point should the list be converted to a set?
	for i in indexes:
		print i
		print n
		n.append(create_name(i,prefix))
	return n

def remove_prefix(s,p,case_sensitive=True,in_place=False):
	"""Removes the specified prefix in-place."""
	return clean_prefix(s,p,case_sensitive,in_place)

def clean_prefix(s,p,case_sensitive=True,in_place=False):
	"""Removes the specified prefix in-place."""
	if in_place:
		s2 = s		 # just copy the reference (pointer) the original string
	else:
		s2 = copy.copy(s)	# copy the string contents into a new string
	if (    ( case_sensitive and s2.startswith(p) )
	    or ( not case_sensitive and s2.lower().startswith(p.lower()) ) 
	   ):
		s2 = s2[len(p):]
	return s2
	
	# actHL: if there's no change, then input pointer returned as output, this may not be what user wants for in_place=False
	return s 
	
def find_prefix(strings,case_sensitive=True):
	"""Identifies a common prefix among strings."""
	s0 = strings[0].strip()
	if not case_sensitive:
		s0 = s0.lower()
	imin = len(s0)
	for s in strings:
		if not case_sensitive:
			s1 = s.lower()
		else:
			s1=s
		# actHL: remove the kluge that adds 'Q' and 'Z' suffix to get the indexing right for strings that are the same length as the prefix
		for ((i,c1),c2) in zip(enumerate(s0+'Q'),s1.strip()+'Z'):
			if c1 != c2:
				break
		imin = min(imin,i)
	return strings[0].strip()[0:imin]

def clean_suffix(s,suf,case_sensitive=True):
	"""Removes the specified suffix in-place."""
	if (    ( case_sensitive and s.endswith(suf) )
	     or ( not case_sensitive and s.lower().endswith(suf.lower()) ) 
	   ):
		s = s[:-len(suf)]
	return s

from sys import stderr,stdout,stdin
import difflib
import numpy as np
import copy
import nltk

def distance(obj1,obj2,string_distance_metric='',distance_mode=2, case_sensitive=0, normalize = True):
	"""Distance metric for dictionaries using nltk.metrics.distance... for strings within the dict.
	
	Treats numbers as strings. 
	
	obj1 and obj2 are the dictionaries to be compared
	string_distance_metric = name of distance metric to use for strings (UNUSED)
	distance_mode = which norm to use, e.g.. 2 = a 2-norm or squared distance sqrt(sum((v1-v2)^2)/N)
		This distance mode is used for the numerical vectors that result from the distance
		metric applied to all the strings within the dictionaries. 
		 (UNUSED)
	case_sensitive = 0 if no case sensitivity, 1 if fully case sensitive
	                -anything in between determines the blending alpha for case insensitive and sensitive matches
  actHL: Alternatively, function could be designed to take a norm of vectors
	composed of numerical values extracted from distance between values. Strings
	could be distanced separately and then the results combined based on some
	quantiative scale factor between the string distance metric and the numerical
	distance metric.
	"""
	import nltk
	if not type(obj1)==type(obj2):
		raise TypeError
	# if it's a scalar, just convert it to a string and do a string difference
	case_sensitive = min(max(case_sensitive,0),1)
	if not is_iter(obj1):
		o1 = str(obj1)
		o2 = str(obj2)
		N = 1
		if normalize:
			N = max(max(len(o1),len(o2)),1)
		# normalize the distance metric for individual strings for their length (e.g. 0<distance<1)
		return (     case_sensitive  * nltk.metrics.distance.edit_distance(str(o1)        , str(o2)         )/N
		        + (1-case_sensitive) * nltk.metrics.distance.edit_distance(str(o1).lower(), str(o2.lower()) )/N
		       )
	# probably need some global variable to keep track of the depth down the tree and use that as a coefficient in the distance summing process
	# right now, grandchildren have just as much weight as grandparents
	# if you get this far, the objects are both iterable objects, so the only question is if they are dictionaries
	# all iterables, except dictionaries can be treated identically
	if not isinstance(obj1,dict):
		d = []
		for o1,o2 in zip(obj1,obj2):
			d.append(distance(o1,o2))
		return d
	
	# crude way to deal with dictionaries
	return distance(str(obj1),str(obj2))
	
	# so the objects must be dictionaries
	c1 = 1.0
	c2 = 1.0
	if case_sensitive > 0: 
		c1 = 0.0
	elif case_sensitive < 0:
		c2 = 0.0
	# actHL: need a way to recursively dive into nested dictionaries and lists
	d=[]
	# actHL: need some technique for "aligning" vectors of strings to find the best match
	#   this to assist in associating the keys from one dictionary with those of the other
	#   so they can be distanced along with the values
	k2 = obj2.keys()
	for (k,v) in obj1.items():
		if isinstance(v,dict):
			d.append(dict_distance(obj1,obj2,string_distance_metric,distance_mode,case_sensitive))
		elif k in k2:
			# actHL: need to have separate branch to deal with numerical values, e.g. abs(v1-v2)/abs(v1+v2)
			d.append((  c1*nltk.metrics.distance.edit_distance(str(v),str(obj2[k])) # case-sensitive edit distance
			          + c2*nltk.metrics.distance.edit_distance(str(v).lower(),str(obj2[k]).lower()))  # case-insensitive edit distance
			          /(c1+c2) )  # isolation or averaging of the 2 metrics
		# actHL: find similar keys in the second dictionary, 
		# actHL: e.g. find the most similar key to k1 in obj2 that isn't also in obj1
		else:
			# actHL: need to deal with normalize==False separately
			d.append(1); # if the key doesn't exist in the second dictionary then it's value is a maximal distance from that key-value in the 1st dictionary

# TODO: Use numpy or list comprehensions and or list slicing
def add_column(list_of_lists, value='',column_name=False):
	"""Add a list of lists column to the right and fill with the value indicated."""
	if isinstance(value,list):
		v = copy.deepcopy(value) # deepcopy in case the new column values are deep objects themselves
	else:
		v = [value]
	for i,row in enumerate(list_of_lists):
		if not isinstance(row,list):
			row = [row]
		if i == 0 and not column_name==False:
			row += column_name
		else:
			row += v
		list_of_lists[i]=row
	# unnecessary as lists are passed by reference and list_of_lists has been augmented in place
	return list_of_lists

# TODO: Use numpy or list comprehensions and or list slicing
def remove_column(list_of_lists,column_number=-1,value=None,check_none=False):
	"""Remove a column if it contains the value indicated, or remove it regardless if value='' or None."""
	# del_count = 0
	# check_per = 200
	# print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
	for i,row in enumerate(list_of_lists):
		if isinstance(row,list) and abs(column_number)<len(row):
			if value == None or row[column_number] == value: # or (len(value)==0 and (row[column_number]==None or len(row[column_number]) == 0)):
				# print str(del_count)
				# del_count += 1
				# if del_count % check_per == 0:
				#	print 'Deleting row ' + str(del_count) + ' and column ' + str(column_number) + ' for value "' + str(value) + '"'
				del row[column_number]
				list_of_lists[i]=row
	# it's not necessary to return the list of lists since all lists are passed by reference already
	return list_of_lists # actHL: should do it in-place so no return is required

def has_len(obj):
	try:
		l=len(obj)
		return l
	except TypeError: 
		return False

def is_iter(obj):
	# actHL: might be better to do a try: list(obj) except TypeError:, 
	# because __getitem__ attribute still might not comply with iterator requriements (e.g. start at [0])
#	if hasattr(obj,'__iter__') or hasattr(obj,'__getitem__'):
#		return True
	if isinstance(obj,(list,dict,set,tuple)): # TODO: add collections.deque, collections.defaultdict
		return True
	return False

def is_float(s,include_nan=False,include_empty=False):
	if include_nan and s in NUMSTR:
		return True
	if include_empty and s in EMPTYSTR:
		return True
	if isinstance(s,bool): 
		return False
	try:
		float(s)
		return True
	except (ValueError, TypeError): # typeerror for None objects
		return False

def is_number(s,include_nan=False,include_empty=False):
	return is_float(s,include_nan=include_nan)

# whether the string can be parsed into two values (start and end) plus an optional string for the units (e.g. "Mon-Fri", "1 to 7 meters")
def is_range(s):
	raise(RuntimeError("Not yet implemented"))
	return s


def is_int(s,include_nan=False,include_empty=False):
	if include_nan and isinstance(s,str) and s in NUMSTR:
		return True
	if include_empty and  isinstance(s,str) and s in EMPTYSTR:
		return True
	if isinstance(s,bool): 
		return False
	try:
		int(s)
		return True
	except (ValueError, TypeError): # typeerror for None objects
		return False

def is_integer(s,include_nan=False,include_empty=False):
	return is_int(s=s,include_nan=include_nan,include_empty=include_empty)
	
# used to produce FDA database format strings?
def round_str(s,N=0,include_nan=False,include_empty=False):
	if not is_number(s,include_nan=False,include_empty=False):
		return False
	return format(float(s), '.'+str(N)+'f')

# This is to deal with the fact that list has to be created in memory with separate statement before sort() can be performed on it
def sort_characters(s,order=True):
	"""Sort the characters in a string as if they are a list of characters.
	
	If order is set to False then the characters are sorted in decreasing \"value.\"
	
	Don't try \"''.join(list(s).sort())\" or it will fail!
	You must allocate memory for the list before sorting or joining.
	"""
	l=list(s)
	l.sort()
	if not order:
		l.reverse()
	return ''.join(l)

def swap_if(a,b,c=''):
	if (a==b):
		return c
	return a

def swap_if_not(a,b,c=''):
	if (a!=b):
		return c
	return a

def swap_if_in(a,b,c=''):
	if (a in b):
		return c
	return a

def swap_if_not_in(a,b,c=''):
	if (a not in b):
		return c
	return a

def make_printable(s,substitute='~',nochange=PRINTABLE,change=''):
	"""Substitute all nonprintable characters with a surrogate (presumably printable) character."""
	if isinstance(substitute,str) and isinstance(nochange,str):
		s2 = substitute
		if len(change)>0:
			if len(s2)==1:
				s2 = substitute*len(change)
			table = str.maketrans(change,s2)
		else:
			if not len(s2)==1:
				return ValueError
			table_list = [swap_if_not_in(chr(c),nochange,s2) for c in range(256)]
			table = ''.join(table_list)
		return s.translate(table)
	raise ValueError

def contains(s,characters=PUNC):
	N=0
	for ch0 in characters:
		N1 = s.count(ch0)
		N += N1
	return N

def count(s,characters=PUNC):
	return contains(s,characters)

def count_unique(s,characters=PUNC):
	N=0
	Nunique=0
	for ch0 in characters:
		N1 = s.count(ch0)
		N += N1
		Nunique += bool(N1)
	return (N,Nunique)

# actHL: need to use the any() or all() operators and list comprehensions or a "map" list filter
def are_all_names(s,confidence=.8):
	if len(s)>0:
		c = are_names(s=s)
		c_all = np.cumprod(c)[-1]
		if c_all>confidence:
			return True
		return False
	else:
		return is_name(s=s)

import operator
def is_list_of_lists(x):
	"""Based on 2007 comment by Vincent Legoll at http://effbot.org/zone/python-list.htm"""
	if not isinstance(x, list): return False
	return reduce(operator.__and__, map(lambda z: isinstance(z, list), x))

def contains_only_lists(l):
	return len(l) == len([x for x in l if isinstance(x,list)])

def are_names(s,delete_last_empty=True):
	name_confidence_factors = {'not_is_title':.94, 'not_is_alpha':.95, 'contains_digit':0.98,
	                           'per_letter':+0.80, 'per_space':-0.04, 'per_punc':-0.11, 'per_digit':-0.05}
	if delete_last_empty and len(s[-1])==0:
		s=s[:-1]
	c=[]
	for x in s:
		xs = x.strip(PUNC)
		if len(xs)<=0:
			c0=0
		else:
			c0=1
			# character type criteria
			# does string contain punctuation not at the beginning or end
			c0 *= max(1     -.01*contains(xs,PUNC)  ,0.01)
			# 0 letters -> 0.01%, 1 letter ->  90%, 2+ letters -> 100%
			c0 *= min( 0.01 +.89 * count(xs,LETTER) ,1.00 )
			# 50% space -> 87.5%, 30% space ->  95.5%, 10% space -> 99.5%, ...
			c0 *= max( 1.00 -.50 * (count(xs,WORDSPACE)/max(count(xs,LETTER),0.01))**2 ,0.10 )
			# 0 unprint -> 100%, 1 unprint ->  80%, 2 unprint -> 20%, 3+ -> 0%
			c0 *= max( 1.00 -.20 * (count(xs,NONPRINTABLE)**2) ,0.01 )
			# 0 nonnames-> 100%, 1  nonnames ->  90%, 2  nonnames -> 80%, ...
			c0 *= max( 1.00 -.05 * count(xs,NONNAMELETTER) ,0.01 )
			# 0 digit -> 100%, 1 digit ->  98%, 2 punc -> 96%, ...
			c0 *= max( 1.00 -.01 * count(xs, DIGIT) ,0.01 )
			# 50% digit -> 87.5%, 30% digit ->  95.5%, 10% digit -> 99.5%, ...
			c0 *= max( 1.00 -.50 * (count(xs.rstrip(DIGIT),DIGIT)/max(count(xs,LETTER),0.01))**2 ,0.10 )
			if contains(xs,DIGIT):
				c0 *= name_confidence_factors['contains_digit'];
			if not xs.istitle():
				c0 *= name_confidence_factors['not_is_title'];
			if not xs.isalpha():
				c0 *= .97
			# length criteria
			if len(xs)>TYPICAL_NAME_LEN*2 or len(xs)<TYPICAL_NAME_LEN*0.5:
				# actHL: need to plot and understand this complex nonlinear function that adjusts confidence based on length of string
				c0 *= 1-min(abs(1-len(xs)/TYPICAL_NAME_LEN)/2,.6)
		c.append(c0)
	return c
	
def cleanpunc(s=''):
	"""Delete any spaces before periods or question marks at the end of a sentence. Reduce double spaces between sentences to single spaces. 

	EXAMPLES:
	>>> cleanpunc(s=PARAGRAPH_EXAMPLE)
	" \\t The quick brown fox jumped over the lazy dog. Did you know that the previous sentence contains all the letters of the English alphabet only once? I bet you did! this passage contains intentionally nonstandard spacing near punctuation and at the beginning and end of the string. Unfortunately doctext can't handle newlines and carriage-returns in test value strings (inconsistent leading whitespace)."
	"""
	# This may mess up a word like "&#!1"
	return re.sub(r'\s*([;,!?.])[;,!?.]*\s+',r'\1 ',s)

def str_replace(s,c='',i=0):
	"""Replace a character in string s at position i with character c"""
	if len(c)==1 and type(c)==str:
		return s[:i]+c[0]+s[i+1:]
	return s

def titlize(s=''):
	"""Capitalize all letters within a string that are preceded by non-letter (space, punctuation, etc)
	
	unlike str.title() nlp.titlize does not lower the case of letters that are already
	capitalized, even those within a word (e.g. acronyms and allcaps words).
	"""
	s2=s;
	capit=False
	for i,c in enumerate(s):
		if c not in LETTER:
			capit=True
		elif capit:
			capit=False
			s2=str_replace(s2,c.upper()[0],i) # c just points back to the original character in the string, right?
	return s2
	
def variablize(s=''):
	"""Convert filename to a form suitable for use as a variable name or SQL table name or column name
	>>> variablize(PARAGRAPH_EXAMPLE)
	'TheQuickBrownFoxJumpedOverTheLazyDog'
	"""
	# [0:255] ensures variable name, file name, or dictionary key is truncated to reasonable length
	# actHL: need to make sure acronyms aren't uncapitalized
	return titlize(s.split('.')[0]).translate(None,NONLETTER)[0:256]

def filename2modelname(filename,prefix='NLPModel'):
	"""Create a variable name suitable as a table name for django models using a filename string."""
	print 'filename2modelname --------------------------'
	return variablize(prefix) + variablize(filename)

def similarity(s1='',s2='',ignorechars=PUNC+SPACE):
	return difflib.SequenceMatcher(lambda x: x in ignorechars,s1,s2).ratio()
	
class Features(object):
	"""
	Here is an interesting example that should one day return a value near 0.9:

	>>> x=Features('The quick brown fox jumped over the lazy dog.')
	>>> y=Features('The sleeping dog was hurdled quickly by the golden fox.')
	>>> x.similarity(y)
	0.47619047619047616
	>>> y.similarity(x)
	0.47619047619047616
	
	SEE ALSO:
		1. nltk.metrics.distance -- does more and does it better
	"""
	# Intended to identify the similarity in passages/phrases/paragraphs/sentences/words for
	# 1. totalgood Food: identify the target of foreign keys when interpreting the schema of FDA databases
	# 2. determine the best connections/relations between recipt ingredients & FDA "food items"
	s = '' # retain local copy of string that created the feature set
	wordlist = [] # retain an ordered list of the tokens (words, punctuation, etc)
	wordset = set() # retain an unordered set of words and tokens
	sequences = [] # an ordered list of word pairs, triplets, etc
	sequencesets = [] # an unordered set of word pairs triplets, etc
	N = 0
	MAX_SEQUENCE_LENGTH = 2
	def __init__(self,s):
		from warnings import warn
		self.s = s
		# don't use split() which only works for words delimitted by either whitespace or a user-designated single character
		self.wordlist = nltk.word_tokenize(self.s)
		# actHL: better to use regular expressions that this inaccurate assumption that all solitary s's are the result of a splitup possive word ending in 's, 
		#        otherwise the text could coneivably contain things like 's' or "s" and trigger this crudeposessive fix
		# deal with possessive words that were garbled due to apostrophe splitting
		#    [1:] slice ensures that i-1 is a valid index ("'s" can't be the first word!)
		for i,word in enumerate(self.wordlist[1:]): 
			if word.lower()=='s':
				self.wordlist[i-1]='\''.join(wordlist[i-1:i])
				del self.wordlist[i]
		self.wordset = set(self.wordlist)
		self.N = len(self.wordset)
		self.sequences = [[]]*len(self.wordlist)
		self.sequencesets = []
		for i,word in enumerate(self.wordlist[:-1]):
			newword=word
			self.sequences[i]=[word]
			seq=[]
			for j in range(1,min(self.MAX_SEQUENCE_LENGTH,len(self.wordlist)-i)):
				newword += self.wordlist[i+j]
				seq.append(newword)
			self.sequences.append(seq)
			self.sequencesets.append(set(seq))
		# TODO:
		# 1. break down wordlist into lexemes by getting rid of suffixes and prefixes
		# 2. assign numerical ids to each word and it's associated WordNet synset
		# 3. use nltk.wordnet.similarity.path_similarity() on all combinations of word pairs 
		#    from each phrase, windowing at some position offset.
		# 4. build a matrix of word positions relative to each other (adjacency matrix) and do similarity math on the matrices for the 2 phrases
	# TODO: accept more than one type of object as an argument (word, phrase, Feature)
	#	def similarity(self,s=''):
	#		f=Features(s)
	#		return len(self.wordset.symmetric_difference(f.wordset))/self.N/f.N
	def set(self):
		return self.wordset
	def list(self):
		return self.wordlist
	def __cmp__(self,other):
		self.wordset-other.wordset
		
	# Naive Bayes similarity
	def similarity(self,f): # TODO: enforce argument type (e.g. f=Features)
		return(1.0-float(len(self.wordset.symmetric_difference(f.wordset)))/(self.N+f.N))
		#sim = sim + (1.0-float(len(self.pairset.symmetric_difference(f.wordset)))/(self.N+f.N))/2
		
# trying to develop a class to use to identify the similarity in passages/phrases/paragraphs/sentences/words 
# immediate need is to identify the target of foreign keys when interpreting the schema of FDA databases
# obviously it will also be useful for determining the best connections/relations between the ingredients in the recipe database and the FDA "food items"
# does menaing have order? should it be a sequence or a set?
#class Meaning: # really a set of meanings, the atom of meaning might have it's own object and this class might be a set of them
#	def __eq__(self,other_meaning):
#		# above some threshold of similarity, two passages are deemed to have the same meaning
#	def __gt__:
#		# one passage encompasses the meaning of another if it is a superset of facts/assertions/meanings
#	def __lt__:
#		# one passage encompasses the meaning of another if it is a superset of facts/assertions/meanings
#	def __cmp__(self,other_meaning):
#		# for use in sort function

import re
#import _sre
#import sre_compile
#import sre_parse

# re has something called an re._sre.SRE_pattern object, but I can't find it in the docstrings

class NLRE_Pattern(): #_sre.SRE_Pattern):
	"""Natural language regular expressions to match, search, and "comprehend" English phrases.
	
	Regular expression syntax is intended to be a superset of GNU regular expressions (re).
	Vocabulary unique to nlre expressions is removed before passing the expression to an re object.
	Current implementation was not optimized for efficiency, accuracy, or even repeatability.
	"""
	def __init__(self, pattern='', flags=[]):
		self.re_pattern = self.compile(pattern,flags)
		
	def compile(self, pattern, flags):
		"""Compile the parent regular expression after translating the nlre into re"""
		return re.compile(pattern, flags)
		pass
	
	def match(self, pattern, string, flags=0):
		"""Try to apply the pattern at the start of the string, returning
		a match object, or None if no match was found."""
		return self._compile(pattern, flags).match(string)

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()



