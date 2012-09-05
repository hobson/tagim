#!/usr/bin/env python
# Filename: tagim.py
"""Tag an image file with GPS position or date values, or comment and tag text

Examples:
	tagim -t 'kinariver quality6' -w -q -g '5d 31.152m N, 118d 33.801m E' -i '/home/hobs/Photos/2011_01_20 Kina River/IMG_5203.JPG'

Depends On:
	optparse, pyexiv2, sys, desktop, os, geopy, re, datetime
	tg ((c) Hobson Lane dba TotalGood)

TODO:
	Add command line options to trigger e-mailing, blog posting, and/or web2.0 sharing of the image.
	Refresh desktop photo after a rotate.
	Allow manual refresh
	Allow quiet output of just filename and double-quiet output of nothing but errors and tripple quiet no output.
	Make sure catalog is being updated to include more recent photos.
	Use file system monitoring system (see recoll user manual) to trigger database updates
	Use a databasing system to keep track of which files have been shown and to index the tags and comments for searching.
"""

import os, sys
if __name__ == "__main__":
    try:
        modDir=os.path.dirname(os.path.realpath(__file__))
        runningDir=os.path.split(modDir)[0]
    except NameError:
        # py2exe
        runningDir=os.path.dirname(sys.argv[0])
        modDir=runningDir
    sys.path.insert(0, os.path.join(modDir, "libtagim"))
    sys.path.insert(0, os.path.join(os.path.join(modDir, ".."), "libtagim"))
    import tagimgui
    try:
        import tagimgui.forms
    except ImportError, e:
        if "tagimgui.forms" in str(e): # tagimqt?
            raise Exception("Error in tagimgui.forms. Visit totalgood.com for information on this error message.")
        else:
            raise
    tagimgui.run()

