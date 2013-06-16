Tagim
======

Tagim is a command-line tool for EXIF-tagging and manipulation of images.

Example Usage:

>>> # tag the current desktop background image (wallpaper) and display the path of the image being tagged.
>>> tagim 'by Hobson' 'in Mexico' 'boat' 'technical7' 'quality5'  # doctest: +ELLIPSIS
Image file name: ...
>>> # change the desktop wallpaper image to the next random image from the queue.
>>> tagim -n
Image file name: ...
>>> # tag the current desktop background image (wallpaper) and display the path of the image being tagged.
>>> tagim 'by Shantaram, in India, story, art9' 'quality8'  # doctest: +ELLIPSIS
Image file name: ...
>>> # change the desktop wallpaper image to the image previously used for the wallpaper
>>> tagim -i -2 -b
Image file name: ...
>>> tagim -t 'kinariver quality6' -w -q -g '5d 31.152m N, 118d 33.801m E' -i '/home/hobs/Pictures/2011_01_20 Kina River/IMG_5203.JPG'   # doctest: +ELLIPSIS
Image file name: '/home/hobs/Pictures/2011_01_20 Kina River/IMG_5203.JPG'...
>>> # send the image to Hobson, with the provided subject and body
>>> tagim -t 'quality10, interest5, artistic5, family6, by Hobson'-i '/home/hobs/Photos/2011_01_20 Kina River/IMG_5203.JPG' --email=hobson@totalgood.com --subject='Check out this photo of the Kinabitungan River monkeys' --body="Hey Hobson, thought you'd like this photo."
Image file name: '/home/hobs/Pictures/2011_01_20 Kina River/IMG_5203.JPG'...

Features
--------

    * e-mail an image (optionally reducing in size) to a specified e-mail address
    * Chron job to update catalog and shuffle the images periodically 
    * Trigger indexing of photos based on file system monitor (OS-dependent)
    * in-place image rotation with -r <degrees> (clockwise = positive)


TODO
-----

* Top Priority
    * Persistent settings
        - Threshold values for tags like "public" or "interest" that prohibit or allow upload to blog or web2.0 share
        - default tag values for all images (if empty and not specified otherwise) 
    * Database (sqlite): to store image catalog and keep track of which files have been shown
    * Database (sqlite?): to index text in tags and comments, with queries implementable directly in tagim

* Backlog
    * Automatically augment the filename of photos that have non-human-readable strings with natural language snippet
        - High priority for tags like location and people names and dates and unusual/rare words
        - Secondary priority from abbreviate strings from tags and comments
    * Post blog article (e-mail default address in secure settings)
    * web2.0 share to Google+, Facebook, and other APIs
    * Quiet output of filename (needs cleanup)
    * Double-quiet to output only fatal errors 
    * Tripple-quiet to only output fatal errors to a log file
    * Chron job or service to update catalog ever few times an image is shuffled across the background
    * Secure settings (env variables) or OS key-chain for e-mail & blog and web2.0 credentials
    * Trigger indexing of photos based on file system monitor (OS-depedent)
    * Database: which files have been shown, index tags and comments, query language output (directly through tagim?)
    * Allow user to set persistent thresholds for values or tags like "public" or "interest" for auto-upload to blog or web2.0 share
    * Automatically modify the filename of numbered photos with natural language snippet (from tags, comments)
        + High priority for tags like location and people names and dates and unusual/rare words
