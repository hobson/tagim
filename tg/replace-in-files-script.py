#!/usr/bin/env python
# -*- coding: ascii -*-
# :filename:  replace-in-files-script.py

import tg.utils

"""
Replace string in multiple files, like sed -e 's/<from>/<to>/g' *

:author: 'Hobson Lane (hobson@totalgood.com)'
:copyright: 'Copyright (c) 2012 Hobson Lane'
:license: 'Creative Commons BY-NC-SA' 
:vcs_id: '$Id$'
:version: '0.01'

Examples:
    >>> import subprocess
    >>> # from a bash shell prompt: replace-in from_text to_text
    >>> subprocess.call('replace-in',['filename','from text','to_text'])
    >>> # from a bash shell prompt: replace-in '' from_text to_text
    >>> subprocess.call('replace-in',['','from text','to_text'])

Requirements:
    optparse.OptionParser
    os.path

Copyright:
    Copyright 2012 Hobson Lane dba TotalGood

"""

version = '0.01'

def parse_args():
    from optparse import OptionParser

    p = OptionParser(usage="%prog [options] [path1] [path2] ...[pathN]", add_help_option=True)
    p.add_option('-p','--path',
                 default='./',
                 help='Path to folder or file to do the replacement in.',
                )
    p.add_option('-i','--interactive',
                 action = 'store_true',
                 help='Whether to interractively prompt for confirmation of every file replacement.',
                )
    p.add_option('-d','--dryrun','--dry-run',
                 action = 'store_true',
                 help='Do not alter any file content.',
                )
    p.add_option('-n','--non-interactive','--force',
                 action = 'store_true',
                 help='Whether to force replacement without promptin the user.',
                )
    p.add_option('-b','--bin','--binary',
                 action = 'store_true',
                 help='Replace string in binary files in addition to text files (ascii, unicode, etc).',
                )
    p.add_option('-x','-e','--ext','--extension','--extensions',
                 dest='ext',
                 default=None,
                 help='Regular expression for extensions of files to do search/replace in.',
                )
    p.add_option('-f','--from','--from-txt','--from-text',
                 dest='fromtxt',
                 default='',
                 help='Regular expression for the string to be replaced.',
                )
    p.add_option('-t','--to',
                 default='',
                 help='Raw, litereal string to replace "from" string with.',
                )
    p.add_option('-v','--verbose',
                 default=False,
                 action='store_true',
                 help='Verbosely print details of every string replaced in every file.',
                )
    p.add_option('-q','--quiet',
                 default=False,
                 action='store_true',
                 help="Don't print anything except errors and warnings.",
                )
    o,a = p.parse_args()
    return o,a

if __name__ == "__main__":
    import os.path
    o,a = parse_args()
    if len(a)==3:
        # TODO: extract extension & use in `utils.replace_in_files(extensions=<...>)`
        if o.path=='./': # TODO: DRY this using the default argument from the ArgParser object
            o.path=a[0]
        if len(o.fromtxt)<1:
            o.fromtxt=a[1]
        if len(o.to)<1:
            o.to=a[2]
    elif len(a)==2:
        if len(o.fromtxt)<1:
            o.fromtxt=a[0]
        if len(o.to)<1:
            o.to=a[1]
    elif len(a)==1:
        if len(o.fromtxt)<1:
            o.fromtxt=a[0]
    print o
    if ( 
            not isinstance(o.fromtxt,str) or not len(o.fromtxt)>=1
         or not isinstance(o.to,str)      or not len(o.to)     >=0
         or not isinstance(o.path,str)    or not len(o.path)    >=1
       ):
        raise ValueError('Need to supply a from and to string to do a replacement')
    import tg.utils as ut
    ut.replace_in_files(search_pattern      = o.fromtxt, 
                        replacement_pattern = o.to, 
                        dir_name            = o.path, 
                        extensions          = o.ext, 
                        interactive         = (o.interactive and not o.non_interactive), 
                        verbose             = o.verbose,
                        dry_run              = o.dryrun,
                       )
    import sys
    sys.exit(0)
    
    if len(o.path)<1:
        o.path=chr(0).join(a) # these are already split into an array, so this is unnecessary
    paths = o.path.split(chr(0))

    #results = []
    for p in paths:
        if not os.path.exists(p):
            path = os.path.normpath(which(p))
        else:
            path = os.path.normpath(p)

        if path and not o.unreal:
            path = os.path.realpath(path)
        if path and not o.abs:
            path = os.path.abspath(path)
        if path and o.norm:
            path = os.path.normcase(path)
        if path and o.base:
            path = os.path.basename(path)
        if path and o.dir:
            path = os.path.split(path)[0]
        if path and o.strip:
            path, ext = os.path.splitext(path)
        if path and o.ext:
            ext, path = os.path.splitext(path)
        #result.append(path)
        # TODO: BUG: pipes may not work output doesn't work (e.g. resolve --run cat tagim | grep tag)
        # TODO: BUG: built-in commands like cat don't work (e.g. resolve --run cat tagim)
        #			 which('cat') works fine and points to /bin/cat
        if path and o.run and which(o.run):
            output = subprocess.Popen([o.run,'{0}'.format(path)], stdout=subprocess.PIPE).communicate()[0]
        else:
            print path # std out

