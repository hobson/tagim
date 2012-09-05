# -*- coding: utf-8 -*-

# ******************************************************************************
#
# Copyright (C) 2011-2012 Olivier Tilloy <hobson@totalgood.com>
#
# This file is part of the tagim distribution.
#
# tagim is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# tagim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tagim; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, 5th Floor, Boston, MA 02110-1301 USA.
#
# Author: Hobson Lane <hobson@totalgood.com>
#
# ******************************************************************************

"""
Module containing tagim script for tagging images with GPS position, dates, comments, tags, etc

Examples:
    tagim -t 'kinariver quality6' -w -q -g '5d 31.152m N, 118d 33.801m E' -i '/home/hobs/Photos/2011_01_20 Kina River/IMG_5203.JPG'
    tagim -t 'quality10, interest5, artistic5, family6, by Hobson'-i '/home/hobs/Photos/2011_01_20 Kina River/IMG_5203.JPG' --email=hobson@totalgood.com --subject='Check out this photo of the Kinabitungan River monkeys' --body="Hey Hobson, thought you'd like this photo."

Depends On:
    optparse, pyexiv2, os, sys, desktop, re, datetime
    geopy, nltk
    tg ((c) Hobson Lane dba TotalGood)

TODO:
    * Facilitate blog posting (e-mail default address in secure settings)
    * web2.0 share
    * Quiet output of filename only suitable for xargs
    * Double-quiet output of errors only
    * Tripple quiet no output (errors sent to a log file?)
    * Chron job or service to update catalog ever few times an image is shuffled across the background
    * Secure settings/key-chain for e-mail & blog and web2.0 passwords
    * Trigger indexing of photos based on file system monitor (OS-depedent)
    * Database: which files have been shown, index tags and comments, query language output (directly through tagim?)
    * Allow user to set persistent thresholds for values or tags like "public" or "interest" for auto-upload to blog or web2.0 share
    * Automatically modify the filename of numbered photos with natural language snippet (from tags, comments)
        + High priority for tags like location and people names and dates and unusual/rare words
"""

# get_version() function and PEP compliance of format copied from pinax.__init__.py
VERSION = (0, 1, 0, "a", 0) # following PEP 386
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

