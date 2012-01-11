#!/usr/bin/env python
# Filename: tg/os.py
# Copyright (c) 2010-2011 Hobson Lane, dba TotalGood
# All rights reserved.

# Written by Hobson Lane <hobson@totalgood.com>
# OS = Operating System

version = 0.1

class UserEnv:
	def __init__(self,username='hobs'):
		import os
		self.user=os.getenv('USER')
		if not self.user:
			self.user=username
		self.home=os.getenv('HOME')
		if not self.home:
			self.home=os.path.join(os.path.sep+'home',user)
	def __repr__(self):
		return "USER='"+self.user+"' && HOME='"+self.home+"'"

def user_home():
	import os
	user=os.getenv('USER')
	if not user:
		user='hobs'

	home=os.getenv('HOME')
	if not home:
	  home=os.path.join(os.path.sep+'home',user)

	return (user,home)

def basic_arguments(p):
	from optparse import OptionParser
	if p and isinstance(p,OptionParser):
		p.add_option('-v', '--verbose',
			dest='verbose', default=True,
			action='store_true',
			help='Print status messages.', )
		p.add_option('--debug',
			dest='debug', default=False,
			action='store_true',
			help='Print debug information.', )
		p.add_option('-q', '--quiet',
			dest='verbose', default=True,
			action='store_false', 
			help="Don't print status messages.")
		return p
	else:
		import warning.warn;
		warning.warn('Basic options (arguments) were not added to the OptionParser object because no object named "p" exists in the local namespace.')

def android_path():
	# any android devices mounted in "usb storage" mode and return a list of paths to their sdcard root
	# not currently implemented
	return '/media/83E2-0FEC' # this just happens to be the label for my android t-mobile G2 flashed with cyanogen mod
	
# not real sure why you can't just call 'assert expected==actual, message'
# http://stackoverflow.com/questions/1179096/suggestions-for-python-assert-function
def validate(expected, actual=True, type='==', message='', trans=(lambda x: x)):
	m = { '==': (lambda e, a: e == a),
		  '!=': (lambda e, a: e != a),
		  '<=': (lambda e, a: e <= a),
		  '>=': (lambda e, a: e >= a), }
	assert m[type](trans(expected), trans(actual)), 'Expected: %s, Actual: %s, %s' % (expected, actual, message)
def validate_str(expected, actual=True, type='', message=''):
	assert_validation(expected, actual, type, message, trans=str)

def zero_if_none(x):
	if not x:
		return 0
	return x

# unlike math.copysign, this may return +1 for -0.0 (on systems that have negative zero)
def sign(f):
	s = type(f)(1)
	if f<0:
		s *= -1
	return s

def make_same_type_as(obj1,obj2):
  return type(obj2)(obj1)

import collections
# accepted answer http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python/2158532#215853
def flatten(list_o_lists):
    """Flatten all dimensions of a multi-dimensional iterable (list/array, tuple, dict, etc) to 1-D, except for member strings.
    
    BASED ON:
      http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python/2158532#215853
    
    >>> l1 = list(flatten(UNIT_CONVERSIONS))
    >>> [(s in l1) for s in ('inches','m','furlongs','stone')]
    [True, True, False, False]
    """
    for el in list_o_lists:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for subel in flatten(el):
                yield subel
        else:
            yield el

# more complicated, but effective answer (doesn't seem like it would work for other iterables like dict and set, but seems to
# http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python/2158532#215853
flatten_lists = lambda *n: (e for a in n
    for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    
 

## TODO: there should be a clever way to do this with a recursive function and a static variable to hold the accumulated list of dimensions
#def __size__(x): 
#  l = nlp.has_len(x)
#  TG_NLP_SIZE_DIMENSION_LIST[-1]=max(TG_NLP_SIZE_DIMENSION_LIST[-1],l)
#  
#  for x0 in x:
#    l=max(nlp.has_len(x),l)
#  
#def size(x):
#  """Calculate the shape (size) of a multi-dimensional list"""
#  HL_SIZE_DIMENSION_LIST = [0] # reset the dimension list
#  return __size__(x)


