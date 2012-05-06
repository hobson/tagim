#!/usr/bin/env python

def get_status(file):
    with open(file) as fp:
        return fp.readline()

import os

f = get_status(os.path.expanduser('~/.bashrc'))
print 'you only get one line'
print f
print f


with open('no-file-here') as fp:
    print fp.readline()
except:
    print 'whatever'
    

