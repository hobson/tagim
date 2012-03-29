#!/usr/bin/env python

# do something like this to preprocess the Kaggle presick project medical insurance data files...
#FN="$1"
#OFN="$1.tsv"
#cp -f "$FN" "$OFN"
#sed -i -r -e 's/([01]?[0-9]+)-\s*([01]?[0-9]+) month[s]?/\1\t\2/g' "$OFN"
#sed -i -r -e 's/,/\t/g' "${OFN}"
#sed -i -r -e 's/\t7[+]/\t10/g' "$OFN"
#sed -i -r -e 's/\tY([1234])/\t\1\t/g' "$OFN"
#echo "$OFN"

import csv, tg.nlp, os, re

# stack overflow code to read a tab-delimitted text file separated into sections with lines like '#intensities'
def tsv2dict(filepath,retag=r'^[^0-9.].*$'):
	"""Read a tab-delimitted text file separated into sections with lines like '#intensities'
	
		Ignores obvious text lines that match a supplied or default regular expression.
	"""
	r=re.compile(retag)
	f = open(filepath, 'r')
	answer = {}
	name='data'
	maxcols = 0
	for line in f:
		ln = line.strip()
		mo = r.match(ln)
		mog= None
		if mo:
			mog=mo.group()
		if isinstance(mog,str):
			name = tg.nlp.variablize(mog)
			answer[name] = []
			maxcols = 0
		elif len(ln)>0:
			rw = ln.split('\t')
			maxcols = max(maxcols,len(rw))
			rw.extend(['']*(maxcols-len(rw)))
			answer[name].append(rw)
	f.close()
	return answer



datafolder = os.path.join(os.path.sep,'home','hobs','Desktop','presick','data','HHP_release3');
filenames = {'dih2':   'DaysInHospital_Y2.csv',
	         'dih3':   'DaysInHospital_Y3.csv',
	         'claims': 'Claims.csv'}
filenames = {'dih2':'DaysInHospital_Y2.csv'}

data=dict();
meta=dict();
names=dict();

def read(filename):
	print 'Opening "{0}"...\n'.format(filename);
	with open(fn,'r') as fp:
		print 'Creating csv reader for "{0}"...\n'.format(fn);
		csvr = csv.reader(fp, dialect=tg.nlp.kaggle_dialect)
		if csvr:
			data = [];
			meta = [];
			names = [];
			for r0,row in enumerate(csvr):
				data.append([]);
				for c,cell in enumerate(row):
					if r0>0:
						r1 = r0-1
						if tg.nlp.is_integer(cell):
							data[r1].append(  int(cell))
						elif tg.nlp.is_number(cell):
							data[r1].append(float(cell))
						else:
							data[r1].append(  str(cell))
					else:
						data[r1].append(int(cell))
				else:
					names.append(str(cell))
	return (data,meta,names)

# TODO:
def quantify(s,lookfor=['units'],ignore=['']): # look_for=['gps','range','units','list']
	"""UNFINISHED: Extract quantitative data from a string.
	
	value1 = first numerical value found in string (usually in a pair for a range)
	units  = string for the units of measure
	value2 = second numerical value found in a string list of numerical values
	
	TODO: treat look_for as a prioritization list, with all non-ignored searches at the bottom of the list
	"""
	if isinstance(lookfor,str):
		look_for = look_for.lower()
	else:
		look_for = map(str.lower,look_for)
	if ('gps' in look_for) or ('gps' in ignore):
		from tg.regex_patterns import POINT_PATTERN, DATETIME_PATTERN
		import geopy
		value1 = value2 = 0
		try:
			p = geopy.point.Point(s)
			value1 = p.latitude
			value2 = p.longitude
		except ValueError:
			mo = POINT_PATTERN.findall(s) # or .match(s)
			if mo: # and (mo.group('latitude_degrees' ) or mo.group('longitude_degrees' )):
				value1 = (float(zero_if_none(mo.group('latitude_degrees' )))
					 + float(zero_if_none(mo.group('latitude_arcminutes' )))/60.0
					 + float(zero_if_none(mo.group('latitude_arcseconds' )))/3600.0)
				value2 = (float(zero_if_none(mo.group('longitude_degrees'))) 
					 + float(zero_if_none(mo.group('longitude_arcminutes')))/60.0 
					 + float(zero_if_none(mo.group('longitude_arcseconds')))/3600.0)
	elif ('units' in lookfor)
		from tg.regex_patterns import VALUE_WITH_UNITS
	#if value1 
	
	
# TODO:
def prepro(filename,output_filename):
	"""Read through a text file to determine tabular data structure (meta)
	
		1. column delimiter or alignment
		2. # of columns stats (max, min, counts for each length)
		3. the data characteristics of each "cell"
			a. boolean, float, integer, string (before interpretation)
			b. whether string interpretation likely to work
			c. string interpretation results (new columns/values, units, types)
	"""
	print 'Opening "{0}"...\n'.format(filename);
	with open(fn,'r') as ifp:
		with open(output_filename,'w') as ofp:
			print 'Creating csv reader for "{0}"...\n'.format(fn);
			csvr = csv.reader(fp, dialect=tg.nlp.kaggle_dialect)
			if not csvr:
				return False
			meta = [];
			names = [];
			for r0,row in enumerate(csvr):
				data = [];
				for c,cell in enumerate(row):
					if r0>0:
						r1 = r0-1
						if tg.nlp.is_integer(cell):
							data[r1].append(  int(cell))
						elif tg.nlp.is_number(cell):
							data[r1].append(float(cell))
						else:
							data[r1].append(  str(cell))
					else:
						names.append(str(cell))
				return (data,meta,names)

def __main__():
	for k,v in filenames.items():
		fn = os.path.join(datafolder,v);
		(data[k],meta[k],names[k])=read(fn);

def test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()


# file formats:
#    Treemap (UMD): tab delimitted
#       line 1: double-quoted strings on first line: "Cause of, death"	"1981 Deaths, per 100,000" ...
#       line 2: unquoted variable type name (only 2 allowed): STRING	FLOAT
#    Eureka formulize: CSV
	
#import numpy as np
# from StringIO import StringIO
#dih2 = np.genfromtxt('HHP_release3/DaysInHospital_Y2.csv',delimiter=',',names=True)
#dih3 = np.genfromtxt('HHP_release3/DaysInHospital_Y3.csv',delimiter=',',names=True)
#claims = np.genfromtxt('HHP_release3/Claims.csv',delimiter=',',names=True)


