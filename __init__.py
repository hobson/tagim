# -*- coding: utf-8 -*-

"""
Module containing tagim script for tagging images with GPS position, dates, comments, tags, etc
"""

# get_version() function and PEP compliance of format copied from pinax.__init__.py
VERSION = (0, 8, 1)  # , "a", 0)  # following PEP 386
DEV_N = 1


def get_version():
    """
    Compose a version number string for the tagim module.
    """
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "f":
        version = "%s%s%s" % (version, VERSION[3], VERSION[4])
        if DEV_N:
            version = "%s.dev%s" % (version, DEV_N)
    return version

__version__ = get_version

__test__ = {}


def test():
    """
    Run all tests found in the tagim.__init__ script
    """
    import doctest
    doctest.testmod(verbose=True)


if __name__ == "__main__":
    test()

