#!/usr/bin/env python
# -*- coding: ascii -*-
"""
Follow links & relative paths to resolve the absolute canonical path to the specified file

Positional Arguments:
    filename
Flags:
    strip
    norm
    ext

__author__ = 'Hobson Lane (hobson@totalgood.com)'
__copyright__ = 'Copyright (c) 2012 Hobson Lane'
__license__ = 'version 3 of the GNU Affero General Public License' 
__vcs_id__ = '$Id$'
__version__ = '1.0'

TODO:
consider the 'New-style BSD' OS license, or the CC BY-NC-SA license, or the MIT license
consier the :: style doctest parameter and meta-data identification

Examples:
    >>> import subprocess

    From shell terminal (command line) prompt:
        resolve resolve
    >>> subprocess.call('resolve',['resolve'])
    '/home/hobs/bin/resolve.py'

    From shell terminal (command line) prompt:
        resolve -x resolve
    >>> subprocess.call('resolve',['-x','resolve.py'])
    '.py'

Requirements:
    optparse.OptionParser
    os.path

TODO:
    Add options to return portions of a path (extension, basename, folder)
    Parse and process more than one path
    Use the xarg options like -0 and -n to separate responses by newlines, Nulls, or spaces
    Verbose and quiet options

Copyright:
    Copyright 2012 Hobson Lane dba TotalGood

Acknowledgments:
    Portions based on http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python

"""

version = '0.1'



def which(program):
    """Find the executable that implements a command, similar to "which" program in Unix/Linux/Posix
    Based on http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    import os
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    if os.path.split(program) and is_exe(program):
        return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None
def test():
    """ Testing Docstring"""
    pass

#if __name__=='__main__':
#    test()



def test():
    """
    Examples: (can't seem to get these to work)
    doctest records the return value of the shell script rather than the sdtout output
    >>> import subprocess
    >>> subprocess.call(['resolve','resolve'])
    '/home/hobs/bin/resolve.py'
    >>> subprocess.call(['resolve','-x','resolve.py'])
    '.py'
    """
    import doctest
    doctest.testmod(verbose=True)

def parse_args():
    from optparse import OptionParser

    p = OptionParser(usage="%prog [options] [path1] [path2] ...[pathN]", add_help_option=True)
    p.add_option('-b','--base','--basename', '--file','--filename','-f',
                 dest='base', default=False,
                 action='store_true', 
                 help='Output just the base-name or file-name portion of the path'
                )
    p.add_option('-d','--dir','--directory', '--container','--containing','--folder',
                 default=False,
                 action='store_true', 
                 help='Output the containing folder or directory'
                )
    p.add_option('-u','--unreal','--unreal-path','--no-follow', '--dont-follow','--leave-links','--with-links',
                 default=False,
                 action='store_true', 
                 help="Don't follow links to resolve the real path."
                )
    p.add_option('-a','--abs','--absolute',
                 default=False,
                 action='store_true', 
                 help="Find absolute path."
                )
    p.add_option('-n','--norm','--case', '--normalize','--normalize-case',
                 dest='norm', default=False,
                 action='store_true', 
                 help='NOT IMPLEMENTED: Normalize the path case (no effect in Posix, but in Windows or Mac converts to all upper case or all lower case).'
                )
    p.add_option('-x','--ext','-e', '--extension',
                 dest='ext', default=False,
                 action='store_true', 
                 help='Output only the extension and not the filename or path.'
                )
    p.add_option('-s','--strip','--strip-ext','--strip-extension',
                 dest='strip', default=False,
                 action='store_true', 
                 help='Output the path and filename, but without the file name extension, also strip the dot (".") character in the extension.'
                )
    p.add_option('--run','--execute','--exec','--launch','--edit','--ed','--gedit',
                 default='',
                 help='Use the path as the first argument to a command (e.g. gedit).'
                )
    p.add_option('-p','--path',
                 dest='path', default='',
                 help='Path to resolve into a real, canonical path, following all links.'
                )
    o,a = p.parse_args()
    return o,a

if __name__ == "__main__":
    import os.path
    #import commands
    import subprocess # allows piping ouput
    from tg.utils import locate
    o,a = parse_args()

    if not o.path or len(o.path)<1:
        o.path=chr(0).join(a) # these are already split into an array, so this is unnecessary
    paths = o.path.split(chr(0))
    #results = []
    for p in paths:
        if os.path.exists(p):
            path = os.path.normpath(p)
        else:
            path = which(p)
        if p and not path or not os.path.exists(path):
            # TODO: append locate path generator to end of paths? Do something with the excess paths.
            path = next(locate(pattern=p))
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

