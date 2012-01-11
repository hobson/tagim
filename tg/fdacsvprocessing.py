#!/usr/bin/env python

import csv
import json
import rateit.fdamodels as fdam
import types
import os
import re
from os import linesep as eol
from settings import PROJECT_ROOT
from sys import stderr,stdout,stdin
import rateit.utils.nlp as nlp

from csv2model import *
  
class FDAImporter(Importer):
  """Methods for defining relationships between database tables stored in flat csv
  (*.txt) files and then using those relaitonships to create json files for importing
  into django as models in a model file called fdamodels.py."""
  appname = 'rateit'
  fda_models_file = ''
  numfiles = 1
  # cleanupHL: not sure if these matter as they are oerwritten by defaults during __init__()
  force=False # whether to force overwrite of existing schema files
  refine=False # whether to attempt automatic table relationship conneciton during schema composition
  verbosity = 1
  fda_revision_number = ''
  file_path = os.path.join(PROJECT_ROOT,appname,'fixtures/')
  fda_models_path = ''
  full_path = file_path
  file_names = []
  file_model_names = []
  model_names = []
  column_names = []
  column_widths=[]
  is_key=[]
  is_blank=[]
  is_null=[]
  verbose_name=[]
  help_text=[]
  schemas={}
  num_table_fields_before_asterisk_split =  5
  num_table_fields_after_asterisk_split =  6
  schema_keys=        ['column_name' ,'field_type','column_width' ,'is_key'       ,'is_null'    ,'is_blank'   ,'verbose_name','help_text']
  field_order=        [0             ,1           ,2              ,3              ,4            ,4            ,0             ,'5:']
  default_fields=     [''            ,''          ,0.0            ,''              ,0            ,0            ,''            ,''] # the type of the default field determines the type of the field output in the schema file, which in turn can affect the type of the database field (currently only detected for column_widths)
  schema_translations=[{}            ,{}          ,{}             ,{'Y':1,'N':0}  ,{'Y':1,'N':0},{'Y':1,'N':0},{}            ,{}] # not suitable for str.translate() or str.replace()
    
  def __init__(self, csv_path=file_path, revno=fda_revision_number, models_file=fda_models_file,
               force=False, refine=False, verbosity=1):
    """Initialize the fda database to model conversion object.
    
    Options include
    """
    #print 'refine='+str(refine)
    #print 'force='+str(force)
    self.force=force
    self.refine=refine
    self.verbosity=verbosity
#    print 'Force={0}'.format(self.force)
    if not csv_path:
      csv_path = os.path.join(PROJECT_ROOT,'fixtures/')
    if not revno:
      revno = 'sr22'
    if not models_file:
      models_file = 'fdamodels.py'
    self.full_path = os.path.join(csv_path,revno)
    if self.verbosity:
      print('The path "{0}" will be used when searching for .csv (.txt), .table, and .schema files'.format(self.full_path))
    self.fda_models_path = os.path.join(PROJECT_ROOT,self.appname,models_file)
    csv.field_size_limit(1000) # sr22.pdf says the longest field is 200 characters, but some of my verbose help text comments in the schema could use 500 char or more
    ls=os.listdir(self.full_path)
    self.file_names=[]
    self.numfiles=0
    for fn in ls:
      (f,e)=os.path.splitext(fn);
      if os.path.isfile(os.path.join(self.full_path,fn)) and (e=='.txt' or e=='.TXT') and f.isupper():
        self.file_names.append(fn)
        self.numfiles=self.numfiles+1
    self.model_names=[]
    unordered_model_names=[]
    table_model_names=[]
    for Ifn in range(len(self.file_names)):
      self.file_model_names.append('FDA'+nlp.variablize(self.file_names[Ifn]))
    self.fda_data={} # actHL: come up with an approach that doesn't require storage of ALL FDA tables in memory
    # actHL: Should incrementally load portions of a table and write that portion to a modestly sized json file
    #        (<2 MB). 2 MB can probably be loaded into a database or memory in less than a minute on most PCs

  def check_schemas(self):
    for fmn,schema in self.schemas.items():
      for fieldnum,colwidth in enumerate(schema['column_width']):
        if isinstance(colwidth,float) and colwidth.is_integer():
#            print "Warning ({0}.check_schemas()): ".format(str(self.check_schemas.im_class)) + \
#            "Schema '{0}' field {1} column_width field is a float type but the value is an exact integer.".format(fmn,fieldnum) + eol + \
#            "Column width value was converted to an integer. " + \
#            "You may want to check that this is appropriate for the field data type for that column and if it is, issue the manage.py fixschemas command."
          schema['column_width'][fieldnum]=int(colwidth)

  def write_schemas(self):
    """Write *.txt.schema files for the schemas currently held in memory."""
    self.check_schemas()
    for fmn,schema in self.schemas.items():
      schema_path=os.path.join(self.full_path,str(schema['file_name'])+'.schema')
      with open(schema_path,'w') as outfile:
        csvw = csv.writer(outfile,dialect=fda_dialect) 
        for schema_key in self.schema_keys: # ordered list of schema keys?
          csvw.writerow(schema[schema_key])

  def read_schemas(self):
    """Read *.txt.schema files into memory.
    
    Schema files describe the format and relationships for a csv or delimmited FDA database file."""
    if self.verbosity:
      print('Reading schemas associated with csv files: '+str(self.file_names))
    for ((i, fn), fmn) in zip(enumerate(self.file_names),self.file_model_names):
      schema_path=os.path.join(self.full_path,fn+'.schema')
      if os.path.isfile(schema_path):
        with open(schema_path,'Ur') as infile:
          if self.verbosity:
            print('Opened {0}'.format(schema_path))
          csvr = csv.reader(infile,dialect=fda_dialect) # should the schema use the fda_dialect or something more standard like csv with commas and quotes?
          j=0        
#          if not self.schemas.has_key(fmn):
#            self.schemas.update({fmn:{}})
#            for k in self.schema_keys:
#              self.schemas[fmn].update({k:[]})
          schema={}
          for row in csvr:
             # This retyping is required only for 'column_width' 
             # It's type (integer or float) is used as a flag for the value type for each column
             # A better csv dialect would obviate this, since the schema value types would be preserved
             # rather than all becoming strings.
            for i,r in enumerate(row):
              row[i]=type(self.default_fields[j])(r)
            schema.update({self.schema_keys[j]:row})
            j=j+1
          schema.update({'numcols': len(schema[self.schema_keys[0]])})
          schema.update({'file_name': fn})
          for j in range(1,len(self.schema_keys)):
            if len(schema[self.schema_keys[j]]) != schema['numcols']:
              # actHL: figure out how to properly raise an exception in django
              stderr.write(self.schemas[fmn])
              stderr.write('The ' + self.schema_keys[j] + 'row of the '+fmn+' schema (row '+str(j)+') has an invalid number of fields (columns).')
              #continue(2) need some way to continue the outer loop rather than this inner check loop
          self.schemas.update({fmn:schema})

  def write_models(self):
    """Write fdamodels.py file with one model for each of the schemas currently held in memory.
    
    Also write source code for Managers, if implied by the set of is_key fields in a schema."""
    if self.verbosity:
      print('Composing python script to represent the {0} schemas currently loaded in memory...'
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
               isinstance(schema['column_width'][j],float) and schema['column_width'][j].is_integer() ):
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
      print('Writing python file: '+self.fda_models_path)
    with open(self.fda_models_path,'w') as outfile:
      outfile.write(s)
      if self.verbosity:
        print 'Python script file encoding was:' + str(outfile.encoding)
      
  def read_tables(self):
    """Read *.txt.table files and form a schema files in memory for each table file.\
    
    This is extremely brittle translation of .table files (created by cutting and 
    pasting text from FDA database documentation in sr22.pdf) into *.txt.schema files.
    Cut-and-paste must be done with Adobe Acrobat reader to gedit or similar text editor. 
    The gnome document viewer application garbles tables--shuffling the text order."""
    if self.verbosity:
      print('Reading {0} table files... '.format(len(self.file_names)))
    valid_fields=False # flag to indicate when the first line containing a valid set of fields has been read
    #lre = re.compile(r'['+nlp.SPACE+']+') # use this to perform split if custom whitespace character definition is required
    for i,fn in enumerate(self.file_names):
      fmn=self.file_model_names[i] # actHL: should be stored in the schemas dictionary of dictionaries
      table_path=os.path.join(self.full_path,fn+'.table')
      schema_path=os.path.join(self.full_path,fn+'.schema')
      if (os.path.isfile(schema_path) and not self.force):
        print('Warning: {0} already exists and "--force" (overwrite) option not enabled. Skipping schema.'.format(schema_path))
        continue
      if not os.path.isfile(table_path): 
        continue
      with open(table_path,'Ur') as infile:
        if self.verbosity:
          print('Opened {0}'.format(table_path))
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
              print 'Warning (fdacsvprocessing.fdaimporter.read_tables()): Row {0}, number of fields insufficient (<{1}), skipping to next line.'.format(
                len(s),self.num_table_fields_before_asterisk_split)
              print 'The faulty table line was: "{0}"'.format(l)
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
    an fdamodels.py file."""
    self.read_schemas()
    self.check_schemas()
    self.write_models()

  def tables2models(self):
    """Read *.txt.table files, refine the reulstin schemas in memory, then write the
    corresponding django models into an fdamodels.py file."""
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
      print('Refining {0} schemas... '.format(len(self.schemas.items())))
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
        print('Refining schema '+str(k))
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
            print(str(k)+'.'+str(schema['column_name'][i]) +'->'+str(fsk)+'.'+str(foreign_schema['column_name'][0]) + ' likelihood='+str(target_likelihood))
          if target_likelihood > max_target_likelihood:
            max_target_likelihood = target_likelihood
            max_target_key = fsk
          target_likelihoods.append(target_likelihood);
        if self.verbosity:
          print('max likelihood='+str(max_target_likelihood)+'='+str(max(target_likelihoods)))
        if max_target_key == k:
          schema['is_key'][i] = 1 # actHL: should already be 1
        elif max_target_likelihood>1 :
          schema['is_key'][i]=str(max_target_key) #+'.'+schema['column_name']

# actHL: should accept a list of file names and only process those rather than reading the list from schemas
  def read_csv(self):
    """Facilitate data importing into django by creating json files based on the FDA csv files (e.g. sr22/*.txt). 
    
    Created json files are loadable with the django command "python manage.py loaddata".
    If schemas for the *.txt files are not currently in memory, 
    then search for *.txt.schema files in the same directory as the data and use them."""
    verbosity_step = 100000 # how many lines to skip before displaying status text message
    if (len(self.schemas)<1):
      self.read_schemas()
    self.check_schemas()
    for ((filenum,fmn),schema) in zip(enumerate(self.schemas),self.schemas.itervalues()):
      self.fda_data.update({fmn: []}) # list of dicts or list of {field names: field values} ready for output to json file using json.dumps()
      with open(os.path.join(self.full_path,schema['file_name']),'Ur') as infile: # r=read, u=universal treatement of eol characters so that they are translated into \n's regardless
        dr = csv.DictReader(infile,fieldnames=schema['column_name'],dialect=fda_dialect)
        pk_needed = schema['is_key'].count(1)!=1
#        print infile
        if self.verbosity:
          print 'Column names for json file ({0}): {1}'.format(schema['file_name'],schema['column_name'])
#        print fda_dialect
#        print dr.dialect
#        print dr
        for pk,row in enumerate(dr):
          if self.verbosity and pk % verbosity_step == 0:
            print 'Reading csv rows {0:08d}-{1:08d}'.format(pk+1, min(pk+verbosity_step, len(dr)) )
          for colnum,nm in enumerate(schema['column_name']):
            obj = row.get(nm)
            colwidth = schema['column_width'][colnum]
            # make sure all numerical fields have None (null) value instead of empty strings ("")
            if schema['field_type'][colnum]=='N': # is this column supposed to store a number
              if isinstance(colwidth,(float,int)):
                # Database field type is float (column_width type used as flag),
                # so if field value is not a float, there there must be a blank 
                # in the column (or an invalid string), so replace it with <None>
                # to be interpreted as a <null> float in json (javascript)
                if not isinstance( obj , (float,int) ):  # or (isinstance(obj,str) and len(obj)<1)):
                  if schema['is_null'][colnum] in nlp.YES:
                    row[nm]=None
                  else:
                    row[nm]=type(colwidth)(0)                
            # is the csv field an ascii string and is the column width a valid (integer) number of characters?
            if schema['field_type'][colnum]=='A' and isinstance(obj,str):
              colwidth=int(colwidth) # actHL: check that colwidth is already an integer
              # does the text in the csv field exceed the allowed column_width (django model max_length tag)
              if len(obj)>colwidth:
                if self.verbosity:
                  print "Warning (fdacsvprocessing.csv2json()): Column {0}, "
                "row {1} in csv file is string of length {2} so it was "
                "truncated to {3}.column_width={4}.".format(
                   colnum, pk, fmn, colwidth)
                row[nm]=obj.truncate(colwidth)
          json_row = {}
          # pop delete's the first column from the row dictionary (so it isn't used as a json "field" item)
          # and the popped value is used as the primary key ("pk") for the json entry or row
          if pk_needed: # have to generate a new key for the json entry because no single column acts as the primary key in the csv file
            json_row["pk"] = pk # enumerate function is handling the incrementing of pk, but it will start at zero unless increased by 1 here
          else: # 
            json_row["pk"] = row.pop(schema['column_name'][schema['is_key'].index(1)])
          json_row["model"] = str(self.appname)+'.'+fmn.lower()
          json_row["fields"] = row
          # accumulate all the data in a single list before writing to file so that indentation and terminating punctuation comes out right
          # this won't work for data sets larger than RAM
          # print(str(json_row) + eol)
          self.fda_data[fmn].append(json_row)

  def write_json(self,records_per_file=10000): # break up json data into records_per_file 
    # HL: don't allow less than 100 records per file otherwise you may create more than 1K files
    rpf = max(records_per_file, 1000) # make sure records_per file isn't zero or impractically small
    max_files = 500
    for fmn, schema in self.schemas.items():
      # some files may end up with more records per file than others if records_per_file is small
      rpf = max( rpf, int( len(self.fda_data[fmn]) / max_files)+1)
      for fnum in range( int( len(self.fda_data[fmn]) / rpf ) + 1 ):
        # actHL: might be better to indicate the record number range in the file name
        fn = os.path.join(self.full_path, str(schema['file_name']) + '.{0:03d}'.format(fnum) + '.json')
        with open(fn,'w') as outfile:
          if self.verbosity:
            print "Writing json file '{0}' ...".format(fn)
          # actHL: is it OK to rely on slice bounds checking?
          outfile.write(json.dumps(self.fda_data[fmn][fnum*rpf:(fnum+1)*rpf-1],indent=2))#,cls=NullFloatEncoder)) 

  def csv2json(self):
    self.read_csv()
    self.write_json()

