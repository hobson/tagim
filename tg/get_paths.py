#!/usr/bin/env python
from urllib2 import unquote, quote

delim = '\n'
delims = '\n' + chr(0)
uri_type = 'file://'
quote_char = '"'
stripit = False


def test(examples=None):
    if examples is None:
        examples = ['file:///media/sda1/ssd/home/hobs/Pictures/ofHobsonLinks/Isla%20Mujeres%20to%20Panama%20052.jpg']
    for example in examples:
        stdout.write(get_path(example) + delim)


def get_path(string, stripit=stripit, quote_char=quote_char):
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
    stripped = string.strip()
    if quote_char:
        stripped = string.strip(quote_char)
    if not stripped.startswith(uri_type):
        return uri_type + quote(stripped)
    return string


def normalize_path(path):
    return os.path.normpath(os.path.abspath(os.path.expandvars(os.path.expanduser(get_paths.get_path(path)))))


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
