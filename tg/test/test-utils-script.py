#!/usr/bin/env python
from   settings2 import *
d2 = locals() # locals() returns a reference to the local namespace dict, so by the time it's printed it contains things like d1,d2,d3, os, s1, merge_settings

import copy
from tg.utils import merge_settings

import settings1 as s1
d1 = s1.__dict__

d3 = d2 #copy.deepcopy(s2) # can't deepcopy because modules contain the unsafe __new__ object/method


merge_settings(s1,d3,verbose=False)

assert max(len(d1),len(d2))<=len(d3)<=(len(d1)+len(d2))
msg = 'd1.keys = \n'+repr(sorted(d1.keys())) + '\n\nd2.keys = \n'+repr(sorted(d2.keys())) + '\n\nd3.keys = \n'+repr(sorted(d3.keys()))
assert set([d for d in d1.keys() if d==d.upper and not d.starts_with('__') and not d.ends_with('__')]).union(set(
            [d for d in d2.keys() if d==d.upper and not d.starts_with('__') and not d.ends_with('__')])) == set(
            [d for d in d3.keys() if d==d.upper and not d.starts_with('__') and not d.ends_with('__')]), msg
    

import settings1 as s1b
import settings2 as s2b
s3b = s1b 

merge_settings(s2b,s3b,verbose=False)

d1b = s1b.__dict__
d2b = s2b.__dict__
d3b = s3b.__dict__

assert max(len(d1b),len(d2b))<=len(d3b)<=(len(d1b)+len(d2b))
assert set([d for d in d1b.keys() if d==d.upper and not d.starts_with('__') and not d.ends_with('__')]).union(set(
            [d for d in d2b.keys() if d==d.upper and not d.starts_with('__') and not d.ends_with('__')])) == set(
            [d for d in d3b.keys() if d==d.upper and not d.starts_with('__') and not d.ends_with('__')]), msg

print 'Tests of tg.utils.py module passed.'
#from pprint import pprint



