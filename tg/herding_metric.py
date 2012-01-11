#!/usr/bin/env python
#
#  Copyright (c) 2011, Hobson Lane dba TotalGood (hobson@totalgood.com)
#
#  license: All Rights Reserved

"""
This is the "herding_metric" module.

It contains a class called herding_metric that imports historical financial data and analyzes it 
to determine the likelihood of a precipitous fall in prices for the financial data imported.

Sample Usage
>>> import tg.herding_metric as hm
>>> h = hm.herd()
>>> h.read_symbol_lists()
>>> print h.value(months=12)
3.0
>>> print h.trend(days=20)
2.5
>>> """

import urllib
import csv
import numpy as np
import json
import types
import os
from os import linesep as eol
import re
from sys import stderr,stdout,stdin
#import rateit.fdamodels as fdam
from settings import PROJECT_ROOT
#import rateit.utils.nlp as nlp
import tg.stockquote as sq
import tg.nlp as nlp
import tg.csv2model as csm

class herd:

  def __init__(self, symbols = ['GOOG','IBM'],
                start_date = '20110412', end_date = '20110415', months = 12,
                sector = None,
                csv_path = None, models_file='',
                force=False, refine=False, verbosity=1, 
                file_names=[]):
    """Initialize the herding metric object.
    
    Options include
      csv_path    = os.path.join(PROJECT_ROOT,appname,'fixtures'),
      models_file = csv_models_file,
      force       = False
      refine      = False
      verbosity   = 1, 
      file_names  = []
    """
    self.csi = csm.Importer()
    self.symbols = symbols

  def read_symbol_lists(self):
    return self.read_symbol_list()
    
  def read_symbol_list(self):
    try:
      from settings import PROJECT_ROOT
    except:
      PROJECT_ROOT = '/home/hobs/newsite/'
    import tg.csv2model as csm 
    self.csi=csm.Importer(PROJECT_ROOT+'/tgfinance/fixtures')
    self.csi.find_files()
    self.csi.read_schemas()
    print self.csi.schemas
    self.csi.read_csv()
    print self.csi.schemas
    print self.csi.csv_data.keys()
    print self.csi.csv_data.values()[2][0]
    print self.csi.csv_data.values()[2][1]
    print self.csi.csv_data.values()[3][0]
    print self.csi.csv_data.values()[3][1]
    self.csi.unshard()
    print self.csi.csv_data.keys()
    print self.csi.schemas
    self.xs = np.array(self.csi.csv_data.values()[0])
    print self.xs.shape
    self.exchanges=self.xs[0,1:,-1].tolist()
    self.symbols=self.xs[0,1:,0].tolist()
    self.fullsymbols=[':'.join(x) for x in zip(self.exchanges,self.symbols)]
    
    
    #csi.write_models()
    #csi.write_json()

  def get_all(self, start_date='20110412', end_date='20110415'): # ,'IBM','APL'
      """ Gather up historical stock quote data into a list of lists.
      
      Each row is a list ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Clos']
      Quotes (rows) for each date are in a quote list
      Quote lists for each symbol are in a dictionary list, i.e.:
        quote_data_for_symbol = [symbol_name][date_index][parameter_index]
      """
      if not end_date:
        end_date = '20110412'
      self.end_date = end_date
      if not start_date:
        start_date = '19300101'
      self.start_date = start_date
      if not symbols:
        symbols = ['GOOG'] #,'IBM','APL']
      self.symbols = symbols
      print symbols
      print len(self.symbols)
      for symbol in self.symbols:
        data = sq.get_history(symbol, start_date, end_date) 
        print len(data)
        # a prefix can be used to identify a group of models to be automatically registered for the admin interface
        self.csi.set_csv(data,filename='YahooQuotes'+symbol+'.CSV',prefix='')
      print self.csi.schemas
      print self.csi.csv_data
      self.csi.write_csv(overwrite=True)
      # json data has not been created, that requires:
      #self.csi.read_csv()
      #self.csi.write_json()
      self.csi.write_models(append=True)


