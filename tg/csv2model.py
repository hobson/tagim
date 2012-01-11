#!/usr/bin/env python
"""tg.csv2model.py"""

import csv
import numpy as np
import json
import types
import os
from os import linesep as eol
import re
from sys import stderr,stdout,stdin
import copy
#import rateit.fdamodels as fdam
#from settings import PROJECT_ROOT
PROJECT_ROOT='/home/hobs/newsite/'
#import rateit.utils.nlp as nlp
import tg.nlp as nlp
# python debugger
import pdb

def make_same_type_as(obj1,obj2):
  return type(obj2)(obj1)


class fda_dialect(csv.Dialect):
  """CSV dialect used to read the csv (*.txt) files for fdaimporter.
  
  If quoting=QUOTE_NONNUMERIC csv file reading will fail on columns in the
  Nutrient description table which contains the unquoted ascii character 'C'
  in the last column."""
  delimiter = '^'
  quotechar = '~'
  escapechar = None
  doublequote = False
  skipinitialspace = False
  lineterminator = '\r\n'
  quoting = csv.QUOTE_MINIMAL #QUOTE_NONNUMERIC # 

class nasdaq_dialect(csv.Dialect):
  """CSV dialect used to read the csv (*.txt) files for fdaimporter.
  
  """
  delimiter = ','
  quotechar = '"'
  escapechar = None
  doublequote = False
  skipinitialspace = False
  lineterminator = '\r\n'
  quoting = csv.QUOTE_ALL # QUOTE_NONNUMERIC # QUOTE_ALL # QUOTE_MINIMAL # QUOTE_NONE

class oo_dialect(csv.Dialect):
  """CSV dialect used to read the csv (*.txt) files for open office on linux.
  
  """
  delimiter = ','
  quotechar = '"'
  escapechar = None
  doublequote = False
  skipinitialspace = False
  lineterminator = '\n'
  quoting = csv.QUOTE_MINIMAL # QUOTE_NONNUMERIC # QUOTE_ALL # QUOTE_MINIMAL # QUOTE_NONE

class kaggle_dialect(csv.Dialect):
  """CSV dialect used to read the csv files for Kaggle.com competitions.

  The only Kaggle project csv files tested are Claims.csv, etc in the predict hospital stay prediction competition.
  
  """
  delimiter = ','
  quotechar = '"'
  escapechar = None
  doublequote = False
  skipinitialspace = False
  lineterminator = '\r\n'
  quoting = csv.QUOTE_MINIMAL # QUOTE_NONNUMERIC # QUOTE_ALL # QUOTE_MINIMAL # QUOTE_NONE

class MetaGet:
  """Preprocess tabular data in text files (CSV, TSV, or TXT) gleaning meta data and normalizing data
  """
  def get_row_params(self, row):
    types=[]
    lengths=[]
    if isinstance(row,list) and len(row) > 0:
      for col,f in enumerate(row):
        #ignore blank last rows
        if col==len(row)-1 and len(f)<=0:
          break;
        fs = str(f).strip().strip("!?,;:.'\" \t")
        if isinstance(f,str) and not nlp.is_number(f,include_nan=True, include_empty=True):
          types.append(str) # 'A'
        elif nlp.is_integer(fs,include_nan=True, include_empty=True):
          types.append(int) # 'I'
        elif nlp.is_float(fs,include_nan=True, include_empty=True):
          types.append(float) # 'F'
        else:
          types.append(None) #unknown type
        lengths.append(len(str(f)))
    else:
      stderr.write('Row passed was not a nonzero-length list, so unable to determine the column data types.\n')
      exit(1)
    print 'looks like the types and lengths were...'
    print types
    print lengths
    return (types,lengths)

class Importer:
  """Methods for defining relationships between database tables stored in flat csv
  (*.txt) files and then using those relationships to create json files for importing
  into django as models in a model file.
  
  
  """
  appname = 'tgfinance'
  csv_models_file = 'csv_models.py'
  numfiles = 0
  # TODO: Delete these defaults if they don't matter -- they're overwritten in __init__()
  overwrite=False # whether to overwrite existing schema files
  refine=False    # whether to attempt automatic table relationship connection during schema composition
  verbosity = 1
  fda_revision_number = ''
  MAX_PREPROCESS_ROWS=1000000 # maximum number of rows to read in a CSV file to determine the data type and field name for each column
  MAX_CSV_ROWS=10000000 # 10 million rows maximum per CSV file read
  MAX_CSV_FILES=1000 # 1000 CSV files maximum per csv_read() call
  #PROJECT_ROOT=''
  csv_models_path = None
  file_names = [] # used in read_tables, read_schemas, etc
  file_model_names = []
  schemas={}
  
  # schema for .table files that are from cutting and pasting FDA tables describing FDA CSV file schemas (schema of a schema)
  num_table_fields_before_asterisk_split =  5
  num_table_fields_after_asterisk_split =  6
  schema_keys=        ['column_name' ,'field_type','column_width' ,'is_key'       ,'is_null'    ,'is_blank'   ,'verbose_name','help_text']
  field_order=        [0             ,1           ,2              ,3              ,4            ,4            ,0             ,'5:']
  # the type of the default field determines the type of field output in schema file, which in turn affects type of database field (currently only detected for column_widths)
  default_fields=     [''            ,''          ,0.0            ,''              ,0            ,0            ,''            ,'']
  # not suitable for str.translate() or str.replace() 
  schema_translations=[{}            ,{}          ,{}             ,{'Y':1,'N':0}  ,{'Y':1,'N':0},{'Y':1,'N':0},{}            ,{}] 
    
  def __init__(self, 
              csv_path=os.path.join(PROJECT_ROOT,appname,'fixtures'),
              revno=fda_revision_number, models_file=csv_models_file,
              overwrite=False, refine=False, verbosity=1,file_names=[]):
    """Initialize an object to convert fda database text files to python data model script files.
    """
    self.clear_csv()
    self.overwrite=overwrite
    self.refine=refine
    self.verbosity=verbosity
    self.file_names=file_names
    project_root = csv_path.rpartition(os.path.join(self.appname,'fixtures'))
    if len(project_root[2])==0:
      project_root=project_root[0]
    else:
      project_root=None
    if not project_root:
      if csv_path:
          project_root = str(csv_path)+'/..'
      elif os.getenv('HOME'):
          project_root = os.getenv('HOME')
      else:
          project_root = '/home/hobs'
    if not csv_path:
      if os.path.exists(os.path.join(project_root,'fixtures')):
          csv_path = os.path.join(project_root,'fixtures')
      else:
          csv_path = project_root
#    if not revno:
#      revno = 'sr22'
    self.full_path = os.path.join(csv_path,revno) # this will take care of any extra trailing slashes in csv_path
    if self.verbosity:
      stderr.write('The path "{0}" will be used when searching for .csv (.txt), .table, and .schema files.\n'.format(self.full_path))
    if not models_file:
      models_file = self.csv_models_file
    self.csv_models_path = os.path.join(project_root,self.appname,models_file)
    csv.field_size_limit(2000) # sr22.pdf says the longest field is 200 characters, but some of my verbose help text comments in the schema could use 500 char or more
    for fn in self.file_names:
      print "filename:" + str(fn)
      self.file_model_names.append(nlp.filename2modelname(filename=fn,prefix='CSV'))

  def get_fda_file_names(self, path):
    return self.get_file_names(path,is_upper=True)

  def consolidate_schemas(self):
    """Homogenize the schemase used for all csv_data tables in memory. Incomplete! Nonworking!
    
    Started this to deal with the OTCBB schema discrepancy with the others (AMEX, NASDAQ, NYSE)
    so that when the unsharded table is converted to a numpy array the .shape() function works properly.
    But I was used a dictionary with the schema values as the keys and the number of schemas 
    that contain them as the value (votes). Then I got confused. Schema values can sometimes be floats
    or other values innapropriate as keys. And fields like the float for column width should be 
    consolidated differently (take the maximum) than things like column names (where voting makes sense)
    or types (where chosing the most inclusive one makes sense)."""
    sks = self.schemas.values()[0].keys()
    schema_counter = {}
    for schema_key in sks: # for each key within the first schema
      for test_schema in self.schemas.values(): # for each schema that you want to check
        if test_schema.has_key(schema_key): # if the schema we're testing has the key we want to check
          if schema_counter.has_key(schema_key): # if the counter has already recorded the existence of this particular key
            if schema_counter[schema_key].has_key(test_schema[schema_key]): # if the counter has already counted at least one schema value for this key
              schema_counter[schema_key][test_schema[schema_key]] += 1 # increase the count
            else:
              schema_counter[schema_key][test_schema[schema_key]]  = 1
          else:
            schema_counter[schema_key]={test_schema[schema_key]:1} # initialize a dictionary to hold the number of votes for each schema entry
        else:
          pass # schema_counter[schema_key]=self.schemas.values()  ...
    return

  def add_schema_column(self, schema={}, new_column_name='', field_type='A', column_width=1, in_place=True):
    if in_place:
      s = schema
    else:
      s = copy.deepcopy(schema)
    s['column_name'][-1]=new_column_name
    types = s['field_type'][:]
    types.append(field_type)
    lengths = s['column_width']
    lengths.append(column_width)
    self.update_schema(schema=s, types=types, lengths=lengths, filename=s['file_name'])
    return s

  def unshard(self, shard_column_name='ShardID'):
    MAX_SHARD_SCHEMA_DISCREPANCY = 10
    if self.schemas.items():
      # this should create a new copy of the schema in the first position in memory (but dictionary order is undefined)
      (fmn,schema) = self.schemas.items()[0] 
    else: 
      # no schemas to process (and presumably no associated csv_data) 
      return None
    shard_model_names = []
    for k,s in self.schemas.items():
      if nlp.distance(schema,s) < MAX_SHARD_SCHEMA_DISCREPANCY:
        shard_model_names.append(k)
    print shard_model_names
    prefix = nlp.find_prefix(shard_model_names)
    print prefix
    new_csv_data=np.array([[]])
    for i,smn in enumerate(shard_model_names):
      print i, smn, self.csv_data.keys()
      if smn in self.csv_data:
        print smn
        shard_field_value = nlp.remove_prefix(smn,prefix)
        # remove the last column whenever it is empty (only if its value is an empty string, '', not just a None value)
        self.csv_data[smn]=nlp.remove_column(self.csv_data[smn], column_number=-1, value='') 
        print 'LENGTH for ' + smn + ' = ' + str(len(self.csv_data[smn][1]))
        # add a new column to hold the name of the table that was combined to create the bigger table so no information is lost
        self.csv_data[smn]=nlp.add_column(self.csv_data[smn],value=shard_field_value,column_name=shard_column_name)
        # update it's schema
        self.schemas[smn] = self.add_schema_column(schema=self.schemas[smn], new_column_name=shard_column_name, column_width=16)
        cd = self.csv_data[smn]
        print cd[0][0]
        print cd[0][:]
        print 'LENGTH for ' + smn + ' = ' + str(len(cd[0]))
        #print cd
        c = np.array(copy.deepcopy(cd))
        pdb.set_trace()
        #print c
        print 'LENGTH for c = ' + str(len(c[0]))
        print c.shape
        if not new_csv_data:
          #new_schema['ignore_first_row']=True
          new_csv_data = copy.deepcopy(c)
        else:
          if self.schemas[smn]['ignore_first_row']:
            c=np.delete(c,0,0) # delete c's 0th element, 0th dimension (c's 1st row)
          print c.shape
          if len(c.shape)>1:
            M = min(c.shape[1],new_csv_data.shape[1])+1
            print 'min width is {0} from c shape of {1} and new_csv_data.shape of {2}'.format(M,c.shape[1],new_csv_data.shape[1])
            new_csv_data = np.vstack((new_csv_data[:,:M],c[:,:M]))
          print new_csv_data.shape
        print 'LENGTH for ' + smn + ' = ' + str(len(self.csv_data[smn][1]))
    print new_csv_data.shape
    # actHL: probably better to just augment the existing schema and replace self.csv_data, but this works too...
    #self.clear_csv()
    self.set_csv(new_csv_data,filename=prefix) #,schema={}) #schema=new_schema)
    # actHL: consider and add_csv function instead of set_csv()

  def clear_csv(self):
    self.file_names=[]
    self.file_model_names=[]
    self.schemas={}
    self.csv_data={} # actHL: should pay attention to the ignore_first_row flag within schema
    self.json_data={} # dict of dicts = {model_name:{field names:field values}} ready for json.dumps()

  def set_csv(self, list_of_lists, filename, preprocess_rows=MAX_PREPROCESS_ROWS, prefix='',schema={}):
    it = iter(list_of_lists)
    if not schema:
      schema = self.table2schema(table=it, filename=filename, preprocess_rows=preprocess_rows)
    schema = self.check_schema(schema=schema)
    fmn    = nlp.filename2modelname(filename=filename,prefix=prefix)
    self.file_names.append(filename)  # strings are immutable, so no need to protect against linking (referencing) with slice notation
    self.file_model_names.append(fmn) # strings are immutable, so no need to protect against linking (referencing) with slice notation
    self.schemas.update({fmn:copy.deepcopy(schema)}) # HL: it's probably OK to pass schema by refernce because a new one is created with every call to table2schema
    self.csv_data.update({fmn: []}) # dict of lists list, or list of {field names: field values}'s ready csv.writer()
    # warnHL: if you don't use the slice notation at the end of a list, the list links by reference instead of copies
#    self.csv_data[fmn].append(schema['column_name'][:]) # write the column labels into row 0 (in memory only)
    self.csv_data[fmn]=list_of_lists # actHL: should pay attention to the ignore_first_row flag within schema
    self.json_data.update({fmn: {}}) # dict of dicts = {model_name:{field names:field values}} ready for json.dumps()
    return schema

  def find_files(self, path = '',is_upper=False):
    self.get_file_names(path,is_upper)

  def get_file_names(self, path = '',is_upper=False):
    if not (len(path)):
      path = self.full_path;
    ls=os.listdir(path)
    self.file_names=[]
    self.numfiles=0
    for fn in ls:
      (f,e)=os.path.splitext(fn);
      if ( os.path.isfile(os.path.join(path,fn)) 
            and (e.upper() in ['.TXT','.CSV']) 
            and (not is_upper or f.isupper()) ):
        self.file_names.append(fn)
        self.numfiles=self.numfiles+1
    for fn in self.file_names:
      self.file_model_names.append(nlp.filename2modelname(filename=fn,prefix='CSV'))
    return self.file_names

  def check_schemas(self):
    for fmn,schema in self.schemas.items():
      schema = self.check_schema(schema=schema)

  def write_schemas(self):
    """Write *.txt.schema files for the schemas currently held in memory."""
    self.check_schemas()
    for fmn,schema in self.schemas.items():
      schema_path=os.path.join(self.full_path,str(schema['file_name'])+'.schema')
      with open(schema_path,'w') as outfile:
        csvw = csv.writer(outfile,dialect=nasdaq_dialect) 
        for schema_key in self.schema_keys: # ordered list of schema keys?
          csvw.writerow(schema[schema_key])

  def get_row_params(self, row):
    types=[]
    lengths=[]
    if isinstance(row,list) and len(row) > 0:
      for col,f in enumerate(row):
        #ignore blank last rows
        if col==len(row)-1 and len(f)<=0:
          break;
        fs = str(f).strip().strip("!?,;:.'\" \t")
        if isinstance(f,str) and not nlp.is_number(f,include_nan=True, include_empty=True):
          types.append('A')
        elif nlp.is_integer(fs,include_nan=True, include_empty=True):
          types.append('I')
        elif nlp.is_float(fs,include_nan=True, include_empty=True):
          types.append('F')
        else:
          types.append('U') #unknown type
        lengths.append(len(str(f)))
    else:
      stderr.write('Unable to read the first line of the csv file to look for schema information (field names)\n')
      exit(1)
    print 'looks like the types and lengths were...'
    print types
    print lengths
    return (types,lengths)

  def update_row_params(self,row,types=[],lengths=[],check_width=False):
    # guess the types and lengths without any hints from previous rows:
    (types2,lengths2)=self.get_row_params(row)
    for i in range(min(len(types),len(types2))):
      # if nonnumerical strings found in a number column, change it to a string (ASCII) column
      if not types[i]=='A': # current type is integer, float or unknown
        if   types2[i]=='A': # new type is ascii
          types[i]='A' # take the new type
        elif types2[i]=='F': # new type is float
          types[i]='F' # relabel the unknown or integer column as a float
        elif types2[i]=='I' and types[i]=='U': # new type is int and old type was unknown
          types[i]='I' # relabel the unknown or integer column as a float
      # increase the string length or number of digits (precision) as needed
      if lengths2[i] > lengths[i]:
        lengths[i]=max(lengths[i],int(lengths2[i]+2)) # add an extra couple places for good measure
    if check_width and not (N<=len(row) and (len(types2)==N) and (len(lengths2)==N) and (len(lengths)==N)):
      stderr.write("Inconsistent row lengths in csv file: row passed:{0} len(types):{1} len(lengths):{2} len(lengths2):{3}\n".format(len(row),N,len(lengths),len(types2),len(lengths2)))
      assert(N<=len(row) and (len(types2)==N) and (len(lengths2)==N) and (len(lengths)==N))
    return (types,lengths) # actHL return of lists is not required since types and lengths lists are passed by reference and have been modified in place

  #   schema_keys=        ['column_name' ,'field_type','column_width' ,'is_key'       ,'is_null'    ,'is_blank'   ,'verbose_name','help_text'
  def update_schema(self, schema={}, types=[], lengths=[], filename=''):
    if not types and not lengths:
      return schema
    if not lengths:
      lengths = []
      for t in types:
        if t == 'F':
          lengths.append(15.15)
        else:
          lengths.append(128)
    if not types:
      types = []
      for l in lengths:
        if nlp.is_float(l):
          types.append('F')
        else:
          types.append('A')
    # column_names (schema_keys[0]) should have already been set, so no need to set it here
    schema.update({self.schema_keys[1]:types}) # assume the first row is a good example of the data types
    schema.update({self.schema_keys[2]:lengths}) # assume the first row is a good example of the data types
    schema.update({self.schema_keys[3]:list(np.concatenate([[1,], np.zeros(len(types)-1, dtype=np.int)]))}) # assume first column is the primary key
    schema.update({self.schema_keys[4]:list(np.concatenate([[0,],  np.ones(len(types)-1, dtype=np.int)]))}) # assume first column is the primary key
    schema.update({self.schema_keys[5]:schema[self.schema_keys[4]]}) # assume all but the primary key are allowed to be blank 
    schema.update({self.schema_keys[6]:schema[self.schema_keys[0]]}) # assume verbose name and field name are the same
    schema.update({self.schema_keys[7]:schema[self.schema_keys[6]]}) # assume help text and verbose name are the same
    schema.update({'numcols': len(schema[self.schema_keys[0]])})
    schema.update({'file_name': filename})
    return schema

  def check_schema(self, schema):
    for fieldnum,colwidth in enumerate(schema['column_width']):
        if isinstance(colwidth,float) and colwidth.is_integer():
          schema['column_width'][fieldnum]=int(colwidth)
    for j in range(1,len(self.schema_keys)):
        N1 = len(schema[self.schema_keys[j]])
        N2 = schema['numcols']
        if N1 != N2:
          # actHL: figure out how to properly raise an exception in django
          stderr.write('The '+self.schema_keys[j]+' row (row '+str(j)
                      +') has an invalid number of fields (columns). Is '
                      +str(N1)+'; should be '+str(N2)+'.\n')
          # actHL: and truncate the schema or update the numcols
    return schema # pass-by-reference probably obviates this return statement


  def get_column_names(self, row, confidence_threshold = .3, prefix = 'Column', numbering_offset = 1):
    """Extrace column names from a list of strings (usually from the first row of a csv file).
    
    Strings are cleaned of punctuation and "variablized" to form column names 
    suitable as file names, variable names, or dictionary keys.
    
    row = list of strings to be converted to column names
    
    confidence_threshold = fractional confidence threshold (0 to 1) which name must meet
      before it is accepted rather than generating a filler name of the form
      Column123
    
    If confidence_threshold is less than or equal to 0, no check of the 
    column name form is performed,
    i.e. bad names like "a#@?!" will be accepted as "A".
    
    If row contains an empty string at the end it is ignored
    
    If row is a number it is taken as the number of columns 
    for which names are to be generated, 
    e.g. Column1, Column2, ... ColumnN
    
    
    Options include
    """
    if isinstance(row,(int,float)) or (
         isinstance(row,str) and is_number(row,include_nan=False,include_empty=False) ):
      row=range(int(round(float(row))))
    fieldnames=[]
    if len(row) > 0:
      for i,f in enumerate(row):
        fs = nlp.variablize(str(f).strip().strip("!?,;:.'\""))
         # get rid of the last field (column) if it's empty (usually caused by a comma or tab or field separator at the end of a row)
        print i,f,fs
        if fs in fieldnames or (i<len(row)-1 and len(fs)<=0):
          # this filler name has to be created twice, 1st time here is for duplicate field names or for the special case of an empty column header at the end of the first row
          print 'column name already exists:' + str(fs)
          fieldnames.append(nlp.create_name(i, prefix, numbering_offset,unique_names=[])) #unqiue_names=fieldnames)
          print 'new name:' + str(fieldnames[-1])
          # this won't work if a previous column header contained ColumnN as it's name (might happen if user used zero-offset column numbering)
        elif len(fs)>0:
          fieldnames.append(fs)
      if confidence_threshold>0:
        confidences = nlp.are_names(fieldnames)
        for i,c in enumerate(confidences):
          if c < confidence_threshold:
            # this filler name has to be created twice, second time here is for unsatisfactory confidence
            fieldnames[i]=prefix+str(i+numbering_offset) # one-offset column number labeling as backup
    else:
      stderr.write('Unable to read the first line of the csv file to look for schema information (field names)\n')
    return fieldnames

          
  def read_schema(self, infile):
    # qHL: should the schema use the nasdaq_dialect or something more standard like csv with commas and quotes?
    # qHL: should the schema reader use a dictreader like the others?
    csvr = csv.reader(infile,dialect=nasdaq_dialect)
    j=0 # default_fields and schema_keys index 
    schema={}
    for row in csvr: # actHL: consider an enumerate(csvr) to get rid of j=0 j+=1 etc
      # This retyping is required only for 'column_width' 
      # Its type (integer or float) is used as a flag for the value type for each column
      # A better csv dialect would obviate this, since the schema value types would be preserved
      # rather than all becoming strings.
      for k,r in enumerate(row):
        row[k]=type(self.default_fields[j])(r) # default schema entries
      schema.update({self.schema_keys[j]:row})
      j += 1
    return (schema)

  def table2schema(self, table, filename, preprocess_rows=MAX_PREPROCESS_ROWS):
    """Convert a list of lists (table) into a schema based on the column headers, data types, and column widths of the data"""
    try:
      schema={'first_row': table.next()[:],
              'ignore_first_row': False }
    except StopIteration: 
      schema={'first_row': [],
            'ignore_first_row': False }
    schema['column_name']=nlp.create_names(range(len(schema['first_row'][:])),prefix='Column'), # assume that the first row contains data rather than column labels
    # Check to see if first row contains things that look like column labels with reasonable confidence
    if schema['first_row'] and nlp.are_all_names(schema['first_row'],confidence=.1):
      schema['column_name']= self.get_column_names(row=schema['first_row'][:]) # column_name (field name)
      schema['ignore_first_row']=True 
    print 'First row in schema read: {0}'.format(schema['first_row'])
    schema['numcols']=len(schema['column_name'])
    types=['U']*schema['numcols']
    lengths=[1]*schema['numcols']
    if schema['first_row'] and not schema['ignore_first_row']: 
      (types,lengths) = self.update_row_params(row=schema['first_row'][:],types=types,lengths=lengths)
    # types list may still contains some 'U'nknowns at this point, because some None or empty field values might have been processed in the first non-header row
    for rowcount,r in enumerate(table): 
      # actHL: since types and lengths are passed by reference, really no need to assign as an output tuple
      (types,lengths) = self.update_row_params(row=r,types=types,lengths=lengths) 
      if rowcount > preprocess_rows: # don't process more than 1000K rows in a CSV file looking for the widest fields in each column
        break
        
    print 'First row middle schema read: {0}'.format(schema['first_row'])
    for i,l in enumerate(lengths):
      if types[i].upper()=='F':
        lengths[i]=float(str(l)+'.'+str(l)) # create a decimal width for floating point field values
        lengths[i]=float(nlp.round_str(lengths[i],2)) # never need more than 2 digits to express number of decimal places in floating point value
    if types and lengths:
      schema = self.update_schema(schema,types=types,lengths=lengths,filename=filename)
    print 'First row after schema read: {0}'.format(schema['first_row'])
    return(schema)

  def read_schemas(self, preprocess_rows=MAX_PREPROCESS_ROWS):
    """Read *.txt.schema files into memory.
    
    Schema files describe the format and relationships for a csv or delimmited text file."""
    if self.verbosity:
      stderr.write('Reading schemas associated with csv files: '+str(self.file_names)+"\n")
    for ((file_index, fn), fmn) in zip(enumerate(self.file_names),self.file_model_names):
      schema_path=os.path.join(self.full_path,fn+'.schema')
      csv_path=os.path.join(self.full_path,fn)
      if os.path.isfile(schema_path):
        if self.verbosity:
          stderr.write('Found schema file: '+str(schema_path)+"\n")
        with open(schema_path,'Ur') as infile: # U turns all eols into \n, r = read mode
          if self.verbosity: stderr.write("Opened {0}\n".format(schema_path));
          schema = self.read_schema(infile)
      elif os.path.isfile(csv_path):
        if self.verbosity:
          stderr.write('Using csv file to create schema: '+str(csv_path)+"\n")
        with open(csv_path,'Ur') as infile:
          try:
            sniffed_dialect = csv.Sniffer().sniff(infile.read(16000),",\t|")
          except:
            sniffed_dialect = oo_dialect
          infile.seek(0)
          if sniffed_dialect: 
            csvr = csv.reader(infile,dialect=sniffed_dialect())
          else:
            csvr = csv.reader(infile,dialect=oo_dialect)
          print 'Trying to figure out the schema from the table itself.'
          schema = self.table2schema(table=csvr, filename=fn, preprocess_rows=preprocess_rows)
      schema = self.check_schema(schema=schema)
      self.schemas.update({fmn:schema})

  def write_models(self,append=True):
    """Write a models.py file with one model for each of the schemas currently held in memory.
    
    Also write source code for Managers, if implied by the set of is_key fields in a schema."""
    if self.verbosity:
      stderr.write("Composing python script to represent the {0} schemas currently loaded in memory...\n"
          .format(len(self.schemas)))
    ind='  ' # indentation characters
    s=''
    s += '#!/usr/bin/env python' + eol
#    s += '# -*- coding: UTF-8 -*-' + eol  # required to avoid pep0263 error when python tries to load model.py script containing unicode characters in string literals
    s += '"""' + eol + 'Models auto-generated from ' + self.full_path + '*.schema' + eol + '"""' + eol
    s += 'from django.db import models' + eol + 'from django.utils.translation import ugettext_lazy as _'
    s += eol + eol
    for fmn,schema in self.schemas.items():
      fn=schema['file_name']
      schema_path=os.path.join(self.full_path,fn+'.schema')
      s_doctext = ind + '"""' + eol + ind + fmn + ' model auto-generated from ' + schema_path + \
                  '.' + eol + ind + '"""' + eol
      s_c = s_manager = s_unique_together = '' # warnHL: Dont try this with an empty list (e.g. x=y=[]) !!!
      for j in range(0,schema['numcols']):
        s_is_key = s_max_length = ''
        s_c += ind + schema['column_name'][j]+' = models.'
        if isinstance(schema['is_key'][j],str) and (
           len(schema['is_key'][j])>1 and schema['is_key'][j] not in nlp.NO ):
          s_field_type = 'ForeignKey( \''+schema['is_key'][j]+'\', related_name=\'' \
                          + fmn + '2' + schema['is_key'][j] + schema['column_name'][j] + '\', '
          s_max_length = 'max_length='+str(int(schema['column_width'][j]))+', '
        elif schema['field_type'][j]=='A':
          s_field_type = 'CharField( ' 
          s_max_length = 'max_length='+str(int(schema['column_width'][j]))+', '
        elif isinstance(schema['column_width'][j],int) or (
               isinstance(schema['column_width'][j],float) and schema['column_width'][j].is_integer() ): # is_integer() works for floats only
          s_field_type = 'IntegerField( '
          s_max_length = '' # actHL: not sure if a max_length attribute makes sense for a IntegerField
        else:
          s_field_type = 'FloatField( '
          s_max_length = '' # actHL: does max_length attribute (precision?) makes sense for FloatField?
        # identify columns for natural key (unique_together model meta attribute)
        # actHL: Currently only looks for more than 2 foreign keys
        #        May need other conditions, like includes a local key instead of just foreign keys
        #        Might be better to have explicit schema tag
         # actHL: consider adding a name=column_)name field
        # don't do "bool(['schema'is_key']) because that will be true for any nonzero length text field
        if schema['is_key'][j] in nlp.YES and (j==0): # key is 1st column then must be suitable primary key
          s_is_key = 'primary_key=True, '
        # actHL: Could use tables FDAAbbreviations & FDAOtherAbbrev to translate column names into verbose names
        s_c += s_field_type + 'verbose_name=_(\''+schema['verbose_name'][j]+'\'), ' 
        # actHL: prohibit primary key of Null (null=True)?
        s_c += s_max_length + s_is_key + 'null=' + str(bool(schema['is_null'][j])) 
         # actHL: prohibit users entering a blank pk field (blank=True)? key automatically generated?
        s_c += ', blank='+str(bool(schema['is_blank'][j]))
        s_c += ', help_text=_('+`schema['help_text'][j].decode('utf-8')`+') )'+eol 
      unique_together = []; unique_together_equality = []; unique_together_self = [];
      for j in range(len(schema['is_key'])):
        if ( isinstance(schema['is_key'][j],str) and ( len(schema['is_key'][j])>1 
             and schema['is_key'][j] not in nlp.NO ) ) or schema['is_key'][j] in nlp.YES:
          unique_together.append(schema['column_name'][j])          
          unique_together_equality.append("{0}={0}".format(unique_together[-1]))
          unique_together_self.append("self.{0}".format(unique_together[-1]))
      if len(unique_together)>1:  
        # this allows you to use natural keys in the text files for serialized models:
        s_manager = "class {0}Manager(models.Manager):".format(fmn) + eol
        s_manager += ind + "def get_by_natural_key(self, "
        s_manager += ', '.join(unique_together) + '):' + eol
        s_manager += ind + ind + 'return self.get( '
        s_manager += ', '.join(unique_together_equality) +' )' + eol + eol
        s_unique_together = eol + ind + 'def natural_key(self):' + eol
        s_unique_together += ind + ind + 'return (' + ', '.join(unique_together_self) + ')' + eol
        s_unique_together += ind + "class Meta:" + eol + ind + ind + \
                            'unique_together = ((\'' + '\', \''.join(unique_together) + '\'),)' +eol
      s_c += s_unique_together
      s_c += ind + 'def __unicode__(self):' + eol
      # actHL: need to identify columns that are best as summary/title/key for each row in each table
      #    1st two columns might be only part of the key in a many-to-many relationships table like Footnote
      #    and 3 columns may be too long a text line for easy display and reading
      s_c += ind + ind
      # actHL: why does _() (translation) in a model output a proxy object rather than a unicode 
      #s_c += 'return str(_(self.' + ')) + " : " + str(_(self.'.join(schema['column_name'][0:3]) + '))'
      # ansHL: seems to be a problem with some other aspect of the models or unicode method
      s_c += 'return str(self.' + ') + " : " + str(self.'.join(schema['column_name'][0:3]) + ')'
      s_c += eol + eol
      s += s_manager
      s += 'class ' + fmn + '(models.Model):' + eol
      s += s_doctext
      if s_manager:
        s += ind + 'objects=' + fmn + 'Manager()' + eol
      s += s_c
    if self.verbosity:
      stderr.write("Writing python file: "+self.csv_models_path+"\n")
    file_mode = 'a'
    if not append:
      file_mode = 'w'
    with open(self.csv_models_path,file_mode) as outfile:
      outfile.write(s)
      if self.verbosity:
        stderr.write('Python script file encoding was:' + str(outfile.encoding) +"\n")
      
  def read_tables(self):
    """Read *.txt.table files and form a schema in memory for each table file.\
    
    This is extremely brittle translation of table files (created by cutting and 
    pasting text from FDA database documentation in sr22.pdf) into *.txt.schema files.
    Cut-and-paste must be done with Adobe Acrobat reader to gedit or similar text editor. 
    The gnome document viewer application garbles tables--shuffling the text order."""
    if self.verbosity:
      stderr.write('Reading {0} table files... \n'.format(len(self.file_names)))
    valid_fields=False # flag to indicate when the first line containing a valid set of fields has been read
    #lre = re.compile(r'['+nlp.SPACE+']+') # use this to perform split if custom whitespace character definition is required
    for i,fn in enumerate(self.file_names):
      fmn=self.file_model_names[i] # actHL: should be stored in the schemas dictionary of dictionaries
      table_path=os.path.join(self.full_path,fn+'.table')
      schema_path=os.path.join(self.full_path,fn+'.schema')
      if (os.path.isfile(schema_path) and not self.overwrite):
        stderr.write('Warning: {0} already exists and overwrite option not enabled. Skipping schema.\n'.format(schema_path))
        continue
      if not os.path.isfile(table_path): 
        continue
      with open(table_path,'Ur') as infile: # U turns all eols into \n, r = read mode
        if self.verbosity:
          stderr.write('Opened {0}\n'.format(table_path))
        for l in infile: 
          l=l.strip() # leading and trailing whitespace (including \r \n, regardless of eol for locale)
          if nlp.similarity(nlp.essence(l),nlp.essence('Field name Type Description')) > 0.7:
            if self.verbosity:
              print 'Found a header row: "{0}"\n  so skipping to next line...'.format(l)
            continue # header row detected, skip it
          # find or develop a regular expression language for tokenizing text lines into variables like this does manually:\
          fields=list(self.default_fields) # without the "list()" method, assignment only creates a pointer with fields pointing to the same memory as self.default_fields
          #s=lre.split(l,self.num_table_fields_before_asterisk_split-1)  # use this to spit on custom whitespace characters
          s=l.split(None,self.num_table_fields_before_asterisk_split-1) # careful, if you specify a whitespace character then a different algorithm runs
          # The following is unnecessary, a check of the field contents and formating occurs below
          # All this would do is prevent some blank table rows being generated with helptext containing the short, invalid text lines from the file
          if not self.schemas.has_key(fmn):
            self.schemas.update({fmn:{}})
            for k in self.schema_keys:
              self.schemas[fmn].update({k:[]})
          if len(s)<self.num_table_fields_before_asterisk_split:
            if valid_fields==False:
              stderr.write('Warning (csv2models.Importer.read_tables()): Row {0}, number of fields insufficient (<{1}), skipping to next line.'.format(
                len(s),self.num_table_fields_before_asterisk_split))
              stderr.write( 'The faulty table line was: "{0}"'.format(l))
            else:
              self.schemas[fmn]['help_text'][-1]=self.schemas[fmn]['help_text'][-1]+' '+l.strip(nlp.SPACE+eol)
            continue                      
          # actHL: need some way of specifying generically this syntax where more than one schema field is contained in a single space-delimitted token      
          if s[2][0].isdigit() and s[2].endswith('*'):
            # insert synthetic field between second number and the asterisk (primary key indicator)
            # create a new Y/N token to represent the presence or absence of this asterisk
            s[2:3]=[s[2].rstrip('*'),'Y']
          else:
            s[2:3]=[s[2],'N']
          for j in range(len(self.field_order)):
            # if self.field_order[j]<len(s) doesn't work because sometimes self.field_order is a slice
            cmd='s['+str(self.field_order[j])+']'
            s2=eval(cmd)
            # actHL: find a more elegant slice or iterator method rather than an if-else
            if isinstance(s2,list): 
              fields[j] = ' '.join(s2)
            else:
              fields[j] = s2
          if fields[0][0].isalpha() and fields[0][0].isupper() and (fields[1]=='A' or fields[1]=='N') and fields[2][0].isdigit() and (fields[3]=='Y' or fields[3]=='N') and (fields[4]=='Y' or fields[4]=='N') and (fields[5]=='Y' or fields[5]=='N'): # and len(fields[7])>10:
            # actHL: automate this with a loop over some translation definitions for strings into fields, like Y/N into 1/0 etc, colname coes with schema_key[0] etc
            valid_fields=True
            for j in range(len(self.schema_keys)):
              for k,v in self.schema_translations[j].items():
                fields[j]=fields[j].replace(k,str(v)) # actHL: should take into account the type of the variable being translated into, somehow
              self.schemas[fmn][self.schema_keys[j]].append(type(self.default_fields[j])(fields[j]))
          else: # line is a continuation of the help text rather than a new column description
            self.schemas[fmn]['help_text'][-1]=self.schemas[fmn]['help_text'][-1]+' '+l.strip(nlp.SPACE+eol)      
        self.schemas[fmn].update({'numcols': len(self.schemas[fmn][self.schema_keys[0]])}) # not necesary, but convenient
        self.schemas[fmn].update({'file_name': fn}) # necessary because the "variablize" conversion (title case, no punc) is not reversible
        #self.schemas[fmn].update({'model_name': fn}) # not necessary because the keys of the schemas dict are the file_model_names
        #self.schemas[fmn].update({'table_name': fn}) # not necessary because table_names are just the keys of the schemas dict .lower()ed
        
  def tables2schemas(self):
    """Read *.txt.table files, refine the resulting schemas in memory, and then write
    those schemas to *.txt.schema files."""
    self.read_tables()
    if self.refine:
      self.refine_schemas()
    self.write_schemas()

  def schemas2models(self):
    """Read *.txt.schema files, and then write the corresponding django models into 
    an csv_models.py file."""
    self.read_schemas()
    self.check_schemas()
    self.write_models()

  def tables2models(self):
    """Read *.txt.table files, refine the reulstin schemas in memory, then write the
    corresponding django models into an csv_models.py file."""
    self.read_tables()
    if self.refine:
      self.refine_schemas()
    self.check_schemas
    self.write_models()
      
  def refine_schemas(self):
    """Try to discern relationships between tables by looking for primary key
    and column name and column help text similarities. Encode those relationships
    as the target foreign key table in the "is_key" element within the schemas
    to replace the True/False 1/0 value there currently"""
    if self.verbosity:
      stderr.write('Refining {0} schemas... \n'.format(len(self.schemas.items())))
    # find all foreign key references even if the column is not labeled 'is_key' because the FDA doesn't label the footnotes column for the NDB No as a primary key, though maybe it should
#    Ncols=[]
#    for schema in self.schemas:
#      Ncols.append(schema['numcols'])
    Nkeys={}
    Ncols={}
    # count the keys before they begin being modified
    for k,schema in self.schemas.items():      
      Nkeys[k] = schema['is_key'].count(True)  
      Ncols[k] = len(schema['is_key'])  # already available within the schema   
    for k,schema in self.schemas.items():
      if self.verbosity:
        stderr.write('Refining schema '+str(k) + '\n')
      for i,schema_is_key in enumerate(schema['is_key']):
        max_target_likelihood = 0.0
        source_likelihood = 0.3*(Nkeys[k]-1)
        source_likelihood += 0.5*bool(schema_is_key)
        source_likelihood -= 0.5*bool(schema['is_blank'][i])
        target_likelihoods = []
        for fsk,foreign_schema in self.schemas.items():
#      actHL this is a kluge to catch the footnote table in the FDA database
#      footnote_table_columns = 4
#      if (Nkeys==1 and schema['is_key'][0]==1 and schema['numcols']>=max(Ncols)):
#        continue
#          if foreign_schema['numcols']....:
#          if fsk == k or schema['column_name'][i]!=foreign_schema['column_name'][0]:
#            target_likelihood = 0.0
#          else:
          target_likelihood = source_likelihood 
          if fsk==k and i==0 and Nkeys[k]==1:
            target_likelihood += .5
          target_likelihood += 0.5*( schema['column_name'][i] == foreign_schema['column_name'][0] )
          target_likelihood += nlp.similarity(nlp.essence(schema['help_text'][i][0:32]),nlp.essence(foreign_schema['help_text'][0][0:32]))
          target_likelihood += 0.2*( schema['field_type'][i] == foreign_schema['field_type'][0] )
          target_likelihood += 0.5*foreign_schema['numcols']/(2*Nkeys[fsk]+1) # +1 to help avoid divide by zero
          # assumes that the key for each table is the first column, which is not the general case, but works for the FDA schema 
          if self.verbosity:
            stderr.write(str(k)+'.'+str(schema['column_name'][i]) +'->'+str(fsk)+'.'+str(foreign_schema['column_name'][0]) + ' likelihood='+str(target_likelihood)+'\n')
          if target_likelihood > max_target_likelihood:
            max_target_likelihood = target_likelihood
            max_target_key = fsk
          target_likelihoods.append(target_likelihood);
        if self.verbosity:
          stderr.write('max likelihood='+str(max_target_likelihood)+'='+str(max(target_likelihoods))+'\n')
        if max_target_key == k:
          schema['is_key'][i] = 1 # actHL: should already be 1
        elif max_target_likelihood>1 :
          schema['is_key'][i]=str(max_target_key) #+'.'+schema['column_name']

  def write_csv(self,N=MAX_CSV_ROWS,M=MAX_CSV_FILES,overwrite=False,suffix='.from_csv2model',retain_header=True,quote_null=False):
    """Writes CSV files based on models held in lists and dictionaries in memory
    
    CSV data must have been previously imported with read_csv() or set_csv() method calls.
    N = the maximum number of rows to read from the csv file
    M = the maximum number of files to read data from
    Created json files are loadable with the django command "python manage.py loaddata".
    If schemas for the *.txt files are not currently in memory, 
    then search for *.txt.schema files in the same directory as the data and use them."""
    verbosity_step = 100000 # how many lines to skip before displaying status text message
    if (len(self.schemas)<1): 
      stderr.write("No schemas found in memory, so unable to format CSV files for writing to disk.\n")
      return
    self.check_schemas()
    for ((filenum,fmn),schema) in zip(enumerate(self.schemas),self.schemas.itervalues()):
      if filenum>M:
        break
      csv_path = os.path.join(self.full_path,schema['file_name'])
      if (os.path.isfile(csv_path) and 
          (not overwrite or not fmn in self.csv_data.keys() or not len(self.csv_data[fmn])>1)):
        stderr.write('Warning: {0} already exists and overwrite argumnet set to false. Skipping csv file.\n'.format(csv_path))
        continue
      with open(csv_path,'w') as outfile: # w=write, U=universal (not possible for write mode)
        if self.verbosity:
          print 'Column names for csv file being written ({0}): {1}'.format(schema['file_name'],schema['column_name'])
        cw = csv.writer(outfile,dialect=oo_dialect)
        cw.writerows(self.csv_data[fmn])

  
# actHL: should accept a list of file names and only process those rather than reading the list from schemas
  def read_csv(self,N=MAX_CSV_ROWS,M=MAX_CSV_FILES,change_first_row=False):
    """Imports CSV data into django models by first loading the CSV data into lists in memory.
    
    N = the maximum number of rows to read from the csv file
    M = the maximum number of files to read data from
    Created json files are loadable with the django command "python manage.py loaddata".
    If schemas for the *.txt files are not currently in memory, 
    then search for *.txt.schema files in the same directory as the data and use them."""
    verbosity_step = 100000 # how many lines to skip before displaying status text message
    if (len(self.file_names)<1):
      self.find_files()
    if (len(self.schemas)<1):
      self.read_schemas()
    self.check_schemas()
    for ((filenum,fmn),schema) in zip(enumerate(self.schemas),self.schemas.itervalues()):
      if filenum>M:
        break
      self.json_data.update({fmn: []}) # dict of dicts = {model_name:{field names:field values}} ready for json.dumps()
      # warnHL: slice copy notation ([:]) prevents schema column names from being linked by reference to the first csv data row
      if change_first_row:
        self.csv_data.update({fmn: [schema['column_name'][:]]}) # dict of lists or list of {field names: field values} ready csv.writer()
      else:
        if schema['ignore_first_row']:
          self.csv_data[fmn]=[schema['first_row'][:]]
        else:
          self.csv_data.update([[]])
      with open(os.path.join(self.full_path,schema['file_name']),'Ur') as infile: # r=read, u=universal treatement of eol characters so that they are translated into \n's regardless
        #dr = csv.DictReader(infile,fieldnames=schema['column_name'],dialect=nasdaq_dialect)
        cr = csv.reader(infile,dialect=nasdaq_dialect)
        pk_needed = schema['is_key'].count(1)!=1
        if self.verbosity:
          print 'Column names for json file ({0}): {1}'.format(schema['file_name'],schema['column_name'])
        row={};
        if schema['ignore_first_row']:
          row=cr.next() # skip a row
        for pk,row in enumerate(cr):
          if pk>N:
            break
          if self.verbosity and pk % verbosity_step == 0:
            print 'Reading csv rows {0:08d}-{1:08d}'.format(pk+1, pk+verbosity_step )
          csv_row=[]
          for colnum,nm in enumerate(schema['column_name']):
            if (len(nm)<=0):
              continue
            #obj = row.get(nm)
            obj = row[colnum]
            colwidth = schema['column_width'][colnum]
            # make sure all numerical fields have None (null) value instead of empty strings ("")
            # HL: also all string fields set to None
            if schema['field_type'][colnum] in ['I','F','N']: # is this column supposed to store a number
              if isinstance(colwidth,(float,int)):
                if not isinstance( obj , (float,int) ) and not (nlp.is_number(obj,include_nan=True, include_empty=False)):
                  if schema['is_null'][colnum] in nlp.YES: # or obj in nlp.NUMSTR:
                    obj=None
                  else:
                    obj=type(colwidth)(0)
            # is the csv field an ascii string and is the column width a valid (integer) number of characters?
            elif schema['field_type'][colnum]=='A' and isinstance(obj,str):
              colwidth=int(colwidth) # actHL: check that colwidth is already an integer
              # does the text in the csv field exceed the allowed column_width (django model max_length tag)
              if len(obj)>colwidth:
                if self.verbosity:
                  stderr.write("Warning (csv2models.csv2json()): Column {0}, row {1} in {2} is {3} long, so truncated to {4}.\n".format(
                    colnum, pk, fmn, len(obj), colwidth))
                obj=str(obj[:max(colwidth-1,0)]) # actHL: shouldn't this list be converted to a string or ''.join() ed ?
            csv_row += [obj]
          print csv_row[:]
          row_dict = dict(zip(schema['column_name'][:],csv_row[:]))
          json_row = {}
          # pop delete's the first column from the row dictionary (so it isn't used as a json "field" item)
          # and the popped value is used as the primary key ("pk") for the json entry or row_dict
          if pk_needed: # have to generate a new key for the json entry because no single column acts as the primary key in the csv file
            json_row["pk"] = pk+1 # enumerate function is handling the incrementing of pk, but it will start at zero unless increased by 1 here
          else: # 
            json_row["pk"] = row_dict.pop(schema['column_name'][schema['is_key'].index(1)]) # remove the part of the row_dict that is supposed to be the primary key
          try:
            row_dict.pop(None)
          except KeyError:
            pass
          try:
            row_dict.pop('')
          except KeyError:
            pass
          json_row["model"] = str(self.appname)+'.'+fmn.lower()
          json_row["fields"] = row_dict # the rest of the row_dict makes up the various field values for that json_row
          # accumulate all the data in a single list before writing to file so that indentation and terminating punctuation comes out right
          # this won't work for data sets larger than RAM
          self.json_data[fmn].append(json_row)
          self.csv_data[fmn].append(csv_row)
        print 'First row of csv: {0}'.format(self.csv_data[fmn][0])

  def write_json(self,records_per_file=10000): # break up json data into records_per_file 
    # HL: don't allow less than 100 records per file otherwise you may create more than 1K files
    rpf = max(records_per_file, 1000) # make sure records_per file isn't zero or impractically small
    max_files = 500
    for fmn, schema in self.schemas.items():
      # some files may end up with more records per file than others if records_per_file is small
      rpf = max( rpf, int( len(self.json_data[fmn]) / max_files)+1)
      for fnum in range( int( len(self.json_data[fmn]) / rpf ) + 1 ):
        # actHL: might be better to indicate the record number range in the file name
        fn = os.path.join(self.full_path, str(schema['file_name']) + '.{0:03d}'.format(fnum) + '.json')
        with open(fn,'w') as outfile:
          if self.verbosity:
            print "Writing json file '{0}' ...".format(fn)
          # actHL: is it OK to rely on slice bounds checking?
          outfile.write(json.dumps(self.json_data[fmn][fnum*rpf:(fnum+1)*rpf-1],indent=2))#,cls=NullFloatEncoder)) 

  def csv2json(self):
    self.read_csv()
    self.write_json()

