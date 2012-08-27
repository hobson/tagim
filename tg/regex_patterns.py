#!/usr/bin/env python
# Filename: tg/patterns.py
"""Regular expression patterns for interpreting date, time, GPS position, and numerical values in strings

Examples:
	from tg.regex_patterns import POINT_PATTERN;  POINT_PATTERN.findall("1.5d 50' 30" S 5.5 deg 23.4567 min 156.1 m")

Depends On:
	re
	tg ((c) Hobson Lane dba TotalGood)

TODO:
	POINT_PATTERN still can't interpret triplet of floats as lat/lon/alt rather than deg/min/sec unless units are provided
	Exponential notation for float or point should require a number or +- immediately preceeding the E
	  otherwise it can confuse the N/S/E/W interpretation of E. 
	  Geographic E should always be followed by a whitespace or punctuation, wherease exponent E shouldn't.
	Examples:
	>>> mo = POINT_PATTERN.match("1d 50 min 30 sec S 5 deg 23.4567 min 156.1 m")
	>>> for m in ml:
	>>>     print "http://maps.google.com/q?{1},{2}".format(m.latitude,m.longitude)
	http://maps.google.com/q?-1.91,5.35
"""
# Filename: tg/patterns.py

# eliminates insidious integer division errors, otherwise '(1.0 + 2/3)' gives 1.0 (in python <3.0)
from __future__ import division

version = '0.7'
import re
try:
    import geopy
except ImportError:
    geopy = False
import os.path

# Unicode characters for symbols that appear in coordinate strings.
DEGREE = unichr(176) # ascii 167 = unicode 176 ?
PRIME = unichr(8242)
DOUBLE_PRIME = unichr(8243)
ASCII_DEGREE = ''
ASCII_PRIME = "'"
ASCII_DOUBLE_PRIME = '"'
LATIN1_DEGREE = chr(176)
HTML_DEGREE = '&deg;'
HTML_PRIME = '&prime;'
HTML_DOUBLE_PRIME = '&Prime;'
XML_DECIMAL_DEGREE = '&#176;'
XML_DECIMAL_PRIME = '&#8242;'
XML_DECIMAL_DOUBLE_PRIME = '&#8243;'
XML_HEX_DEGREE = '&xB0;'
XML_HEX_PRIME = '&x2032;'
XML_HEX_DOUBLE_PRIME = '&x2033;'
ABBR_DEGREE = 'deg'
ABBR_ARCMIN = 'arcmin'
ABBR_ARCSEC = 'arcsec'
ABBR_N = 'n|north'
ABBR_S = 's|south'
ABBR_E = 'e|east'
ABBR_W = 'w|west'
FOUR_WINDS = '(ABBR_N|ABBR_S|ABBR_E|ABBR_W)'
FOUR_WINDS_POS = 'ABBR_N|ABBR_E'
FOUR_WINDS_NEG = 'ABBR_S|ABBR_W'
FOUR_WINDS_LAT = 'ABBR_N|ABBR_S'
FOUR_WINDS_LON = 'ABBR_E|ABBR_W'

DEGREES_FORMAT = "%(degrees)d%(deg)s %(minutes)d%(arcmin)s %(seconds)s%(arcsec)s"
UNICODE_SYMBOLS = {'deg': DEGREE, 'arcmin': PRIME, 'arcsec': DOUBLE_PRIME}
ASCII_SYMBOLS = {'deg': ASCII_DEGREE, 'arcmin': ASCII_PRIME, 'arcsec': ASCII_DOUBLE_PRIME}
LATIN1_SYMBOLS = {'deg': LATIN1_DEGREE, 'arcmin': ASCII_PRIME, 'arcsec': ASCII_DOUBLE_PRIME}
HTML_SYMBOLS = {'deg': HTML_DEGREE, 'arcmin': HTML_PRIME, 'arcsec': HTML_DOUBLE_PRIME}
XML_SYMBOLS = {'deg': XML_DECIMAL_DEGREE, 'arcmin': XML_DECIMAL_PRIME, 'arcsec': XML_DECIMAL_DOUBLE_PRIME}
ABBR_SYMBOLS = {'deg': ABBR_DEGREE, 'arcmin': ABBR_ARCMIN, 'arcsec': ABBR_ARCSEC}

# should I use QUANT PATTERNS or UTIL PATTERNS
UTIL_PATTERNS = dict(
	# HL: added sign, spacing, & exponential notation: 1.2E3 or +1.2 e -3
	FLOAT           = r'[+-]?\d+(?:\.\d+)?(?:\s?[eE]\s?[+-]?\d+)?', 
	FLOAT_NONEG     =  r'[+]?\d+(?:\.\d+)?(?:\s?[eE]\s?[+-]?\d+)?', 
	FLOAT_NOSIGN    =      r'\d+(?:\.\d+)?(?:\s?[eE]\s?[+-]?\d+)?', 
	# HL: added sign and exponential notation: +1e6 -100 e +3
	INT             = r'[+-]?\d+(?:\s?[eE]\s?[+]?\d+)?', 
	INT_NONEG       =  r'[+]?\d+(?:\s?[eE]\s?[+]?\d+)?', 
	INT_NOSIGN      =      r'\d+(?:\s?[eE]\s?[+]?\d+)?', # HL: exponents should always be allowed a sign
	SEP             = r'\s*[,;\s]\s*', 
	EOL             = r'(?:\r\n|\n|\r)',
	QUOTE           = r"""(?P<quote>(?P<quoter>['"])(?P<quoted>.*?)(?P=quoter))""", # named parameters could through regexes that use \1 off
	)
if geopy:
	UTIL_PATTERNS['DEGREE_SYM']          = geopy.format.DEGREE
	UTIL_PATTERNS['PRIME_SYM']           = geopy.format.PRIME
	UTIL_PATTERNS['DOUBLE_PRIME_SYM']     = geopy.format.DOUBLE_PRIME
else:
	UTIL_PATTERNS['DEGREE_SYM'      ]    = u'\xb0'   #chr(167) # ASCII or unicode? which can be used in RE patterns?
	UTIL_PATTERNS['PRIME_SYM'       ]    = u'\u2032'
	UTIL_PATTERNS['DOUBLE_PRIME_SYM']    = u'\u2033'
UTIL_PATTERNS['DEGREE'] = r'['                   +UTIL_PATTERNS['DEGREE_SYM']      +r'Dd\s][Ee]?[Gg]?', # HL: matches some typos, whitespace equivalent to deg sym
UTIL_PATTERNS['ARCMIN'] = r'(?:arc|Arc|ARC)?['   +UTIL_PATTERNS['PRIME_SYM']       +r"'Mm][Ii]?[Nn]?", 
UTIL_PATTERNS['ARCSEC'] = r'(?:arc|Arc|ARC)?\-?['+UTIL_PATTERNS['DOUBLE_PRIME_SYM']+r'"Ss]?[Ee]?[Cc]?', 

# TODO: Implement patterns for paths
#   1. identify quoted and unquoted path names, with or without backslash-escaped spaces
#   2. process escapes properly according to OS (backslash for linux)
#   3. contribute these path patterns to the os.path python module/library
PATH_PATTERNS = dict(
	# http://techtavern.wordpress.com/2009/04/06/regex-that-matches-path-filename-and-extension/
	LIN      = r"""(?P<PathPattLinQuote>['"]?)""" \
	           + r'(?P<PathPattLinBase>.*/)?' \
	           + r'(?P<PathPattLinFile>$|(.+?)(?:([.][^.]*$)|$))' \
	           + r'(?P=PathPattLinQuote)',
	# see http://stackoverflow.com/questions/5452655/python-regex-to-match-text-in-single-quotes-ignoring-escaped-quotes-and-tabs-n
	#LIN_PATH      = "(['\"]?)[-_A-Za-z/.]+(\0)", # not at all precise/accurate or complete
	WIN      = r'',
	DOS      = r'',
	MAC      = r'',
	ANY          = r'['+os.path.sep+r']*', # add in colon (os.curdir) for DOS drive designations
	)

# TODO: cosolidate with UTIL_PATTERNS.FLOAT and others
QUANT_PATTERNS = dict(
	# HL: added some less common field/column separators: colon, vertical_bar
	SEP                  = r'\s*[\s,;\|:]\s*', 
	DATE_SEP             = r'\s*[\s,;\|\-\:\_\/]\s*',
	# based on DATE_SEP (with \s !!) ORed with case insensitive connecting words like "to" and "'till"
	RANGE_SEP            = r"(?i)\s*(?:before|after|then|(?:(?:un)?(?:\')?til)|(?:(?:to)?[\s,;\|\-\:\_\/]{1,2}))\s*", 
	TIME_SEP             = r'\s*[\s,;\|\-\:\_]\s*',
	# HL: added sign, spacing, & exponential notation: 1.2E3 or +1.2 e -3
	FLOAT                = r'[+-]?\d+(?:\.\d+)?(?:\s?[eE]\s?[+-]?\d+)?', 
	FLOAT_NONEG          =  r'[+]?\d+(?:\.\d+)?(?:\s?[eE]\s?[+-]?\d+)?', 
	FLOAT_NOSIGN         =      r'\d+(?:\.\d+)?(?:\s?[eE]\s?[+-]?\d+)?', 
	# HL: got rid of exponential notation with an E and added x10^-4 or *10^23
	FLOAT_NOE            = r'[+-]?\d+(?:\.\d+)?(?:\s?[xX*]10\s?\^\s?[+-]?\d+)?', 
    FLOAT_NONEG_NOE      =  r'[+]?\d+(?:\.\d+)?(?:\s?[xX*]10\s?\^\s?[+-]?\d+)?', 
    FLOAT_NOSIGN_NOE     =      r'\d+(?:\.\d+)?(?:\s?[xX*]10\s?\^\s?[+-]?\d+)?', 
	# HL: added sign and exponential notation: +1e6 -100 e +3
	INT                  = r'[+-]?\d+(?:\s?[eE]\s?[+]?\d+)?',
	INT_NONEG            =  r'[+]?\d+(?:\s?[eE]\s?[+]?\d+)?',
	INT_NOSIGN           =      r'\d+(?:\s?[eE]\s?[+]?\d+)?', # HL: exponents should always be allowed a sign 
	INT_NOSIGN_2DIGIT    = r'\d\d',
	INT_NOSIGN_4DIGIT    = r'\d\d\d\d',
	INT_NOSIGN_2OR4DIGIT = r'(?:\d\d){1,2}',
	YEAR                 = r'(?i)(?:1[0-9]|2[012]|[1-9])?\d?\d(?:\s?AD|BC)?',  # 2299 BC - 2299 AD, no sign
	MONTH                = r'[01]\d',   # 01-12
	DAY         = r'[0-2]\d|3[01]',     # 01-31
	HOUR        = r'[0-1]\d|2[0-4]',    # 01-24
#	MONTH                = r'[01]?\d',   # 1-12 and 01-09
#	DAY         = r'[0-2]?\d|3[01]',    #  1-31 and 01-09
#	HOUR        = r'[0-1]?\d|2[0-4]',   #  1-24 and 01-09
	MINUTE      = r'[0-5]\d',           # 00-59
	SECOND      = r'[0-5]\d(?:\.\d+)?', # 00-59
	)
for k,v in {'DEGREE':'DEGREE','ARCMIN':'PRIME','ARCSEC':'DOUBLE_PRIME'}.items():
    QUANT_PATTERNS[k+'_SYM'] = UTIL_PATTERNS[v+'_SYM']
    QUANT_PATTERNS[k       ] = UTIL_PATTERNS[k]

#WARN: each of the lat/lon/alt elements needs to stop and not worry about armin/arcsec as soon as they get a decimal point, especially if no arcmin or arcsec units are given
#TODO: to avoid ambiguity just require arcmin/arcsec units indicators rather than allowing a sequence of floats to be interpreted as d,m,s
POINT_PATTERN = re.compile(r"""
	(?P<latitude>
		(?P<latitude_degrees>%(FLOAT_NOE)s)[ ]?(?:%(DEGREE)s[ ]*
			(?:(?P<latitude_arcminutes>%(FLOAT_NONEG_NOE)s)[ ]?%(ARCMIN)s[ ]*)?
			(?:(?P<latitude_arcseconds>%(FLOAT_NONEG_NOE)s)[ ]?%(ARCSEC)s[ ]*)?
		)?\s*(?P<latitude_direction>[NS])?
	)
	%(SEP)s
	(?P<longitude>
		(?P<longitude_degrees>%(FLOAT_NOE)s[ ]?(?:%(DEGREE)s[ ]*
			(?:(?P<longitude_arcminutes>%(FLOAT_NONEG_NOE)s)[ ]?%(ARCMIN)s[ ]*)?
			(?:(?P<longitude_arcseconds>%(FLOAT_NONEG_NOE)s)[ ]?%(ARCSEC)s[ ]*)?
		)?\s*(?P<longitude_direction>[EW])?) )
	(?:
		%(SEP)s
			(?P<altitude>
				(?P<altitude_distance>-?%(FLOAT)s)[ ]*
				(?P<altitude_units>km|m|mi|ft|nm|nmi|mile|kilometer|meter|feet|foot|nautical[ ]mile)[s]?)
	)?
	\s*$""" % QUANT_PATTERNS, re.X | re.I) # HL: added case insensitivity which seemed to break things




DATE_PATTERN = re.compile(r"""
		(?P<y>%(YEAR)s)%(DATE_SEP)s
		(?P<mon>%(MONTH)s)%(DATE_SEP)s
		(?P<d>%(DAY)s)
""" % QUANT_PATTERNS, re.X)

# FIXME: parse the AM/PM bit
TIME_PATTERN = re.compile(r"""
		(?P<h>%(HOUR)s)%(TIME_SEP)s
		(?P<m>%(MINUTE)s)%(TIME_SEP)s
		(?P<s>%(SECOND)s) 
""" % QUANT_PATTERNS, re.X)

DATETIME_PATTERN = re.compile(r'(?P<date>'+DATE_PATTERN.pattern+
                              r')(?:'+QUANT_PATTERNS['DATE_SEP']+
                              r')?(?P<time>'+TIME_PATTERN.pattern+r')', re.X)
                              
#DATETIME_PATTERN = re.compile(r'(?P<date>'+DATE_PATTERN.pattern+r')(?:%(DATE_SEP)s)?(?P<time>'+TIME_PATTERN.pattern+r')' % QUANT_PATTERNS, re.X)

DATE_OR_TIME_PATTERN = re.compile(r"""
	(?P<date>"""
	+DATE_PATTERN.pattern+
r""")|
	(?:%(DATE_SEP)s)?
	(?P<time>"""
	+TIME_PATTERN.pattern+
r""")
""" % QUANT_PATTERNS, re.X)

#DATE_ANDOR_TIME_PATTERN = re.compile(r"""
#	(?P<date>"""
#	+DATE_PATTERN.pattern+
#r""")?
#	(?:%(DATE_SEP)s)?
#	(?P<time>"""
#	+TIME_PATTERN.pattern+
#r""")|(?:
#	(?P<time>"""
#	+TIME_PATTERN.pattern+
#r""")?
#	(?:%(DATE_SEP)s)?
#	(?P<date>"""
#	+DATE_PATTERN.pattern+
#r"""))
#""" % QUANT_PATTERNS, re.X)


RANGE_PATTERN = re.compile(r"""
	(?P<left>%(FLOAT)s)
	(?:%(RANGE_SEP)s)
	(?P<right>%(FLOAT)s)
""" % QUANT_PATTERNS, re.X)

def _test():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  _test()
