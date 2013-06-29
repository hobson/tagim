#!/usr/bin/env python
from urllib2 import unquote, quote

delim = '\n'
delims = '\n' + chr(0)
uri_type = 'file://'
quote_char = '"'
stripit = False
import os.path
from os import environ


def test(examples=None):
    if examples is None:
        examples = ['file:///media/sda1/ssd/home/hobs/Pictures/ofHobsonLinks/Isla%20Mujeres%20to%20Panama%20052.jpg']
    for example in examples:
        stdout.write(get_path(example) + delim)


# uri2path
def get_path(string, stripit=stripit, quote_char=quote_char):
    """Convert URI to normal file system path, transforming indentation, quotes, and %-escaped characters, if necessary"""
    stripped = string.strip()
    if stripped.startswith(uri_type):
        indentation = ''
        if not stripit:
            i0 = string.find(uri_type)
            if i0 > 0:
                indentation = string[:i0]
        if string[-1] in delims:
            return indentation + quote_char + unquote(stripped)[7:] + quote_char + string[-1]
        else:
            return indentation + quote_char + unquote(stripped)[7:] + quote_char
    return string


def make_uri(string):
    """Convert a local file system path to a file://... URI, with %-escaped spaces and other special characters."""
    stripped = string.strip()
    if quote_char:
        stripped = string.strip(quote_char)
    if not stripped.startswith(uri_type):
        return uri_type + quote(stripped)
    return string


def normalize_path(path):
    """Return the canonical, real path to a file, followings symlinks, shell variables, tilde symbols, and normalizing double-slashes"""
    return expand_path(get_path(path, stripit=True, quote_char=''))


def expand_path(*path_elements):
    """return os.path.abspath(os.path.realpath(os.path.expandvars(os.path.expanduser(os.path.join(*paths)))))

    These examples may only work on a POSIX-like system:
    >>> path = expand_path('$HOME')
    >>> 'home' in path or 'User' in path
    True
    >>> path.startswith('/')
    True
    >>> expand_path('~') == expand_path('$HOME')
    True
    >>> path = expand_path('~nonusernamesure/ly', '$SHELL')
    >>> path.endswith('sh')
    True
    >>> '~nonusernamesure/ly' in path
    True
     """
    return os.path.realpath(os.path.normpath(os.path.abspath(os.path.realpath(os.path.expandvars(os.path.expanduser(os.path.join(*path_elements)))))))


def find_project_dir(project_homes=None, proj_subdirs=None, verbose=False):
    """Return the full, absolute path to a directory containing what looks like a source code project (git, svn, bzr repo or Django project)

    >>> find_project_dir(project_homes=['~/this_cant_possibly_exist/and/contain/a/project/$SHELL'], verbose=False)  # doctest: +ELLIPSIS
    >>> find_project_dir(project_homes=['~frank/ly/$SHELL'], verbose=False)
    >>> find_project_dir(project_homes=[''], verbose=True)
    """
    from sys import stderr

    if isinstance(project_homes, basestring):
        project_homes = [project_homes]

    workon_proj_file = environ.get('VIRTUALENVWRAPPER_PROJECT_FILENAME')  # typically '.project'
    workon_home = environ.get('WORKON_HOME')  # typically ~/.virtualenvs

    proj_name = os.path.basename(environ.get('VIRTUAL_ENV', ''))
    try:
        with open(expand_path(workon_home, proj_name, workon_proj_file), 'rUb') as fpin:
            found_path = fpin.read().strip('\n')
    except:
        found_path = None

    #environ['VENVWRAP_CURDIR_BEFORE_WORKON'] = os.path.abspath(os.path.curdir)

    proj_homes = (
        project_homes
        or environ.get('VENVWRAP_PROJECT_HOMES', '').split()
        or ['~/src', '~/flint-projects', '~/bin', '~/projects', '~/sublime-projects', '~'])

    proj_subdirs = (
        proj_subdirs
        or environ.get('VENVWRAP_PROJECT_HOMES_CONTAIN', '').split()
        or [os.path.join('django', '.git'), '.git', '.svn', '.bzr', 'readme.txt', 'README', 'README.md', 'CHANGELOG', 'VERSION'])

    while proj_homes:
        proj_home = proj_homes.pop()
        # take care of quoted paths from ENV variable
        proj_home = proj_home.strip("'").strip('"')
        proj_path = expand_path(proj_home, proj_name)
        if verbose:
            stderr.write('Checking to see if "%s" is a valid directory.\n' % proj_path)
        if not os.path.isdir(proj_path):
            continue
        for subdir in proj_subdirs:
            path = os.path.join(proj_path, subdir)
            if verbose:
                stderr.write('Looking for %s\n' % path)
            if os.path.exists(path):
                # remove the last directory from the path unless that would put you above the dir named for the project
                found_path_parent = os.path.split(path)[0]
                found_path = found_path_parent if len(found_path_parent) >= len(proj_path) else proj_path
                return found_path



if __name__ == "__main__":
    from sys import argv, stdout, stdin
    import os.path

    # TODO: check to see if it's a file and do like grep (read the file and process it as one argument per line)
    #       -0 and -1 option like xargs and grep to output "args" delimited by null or newline
    if len(argv) > 1:
        args = argv[1:]
        for arg in args:
            stdout.write(get_path(arg) + delim)
            if os.path.isfile(arg):
                raise RuntimeError('Not implemented.')
                exit(1)
    else:
        for line in stdin:
            stdout.write(get_path(line))
    exit(0)
