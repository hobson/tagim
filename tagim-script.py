#!/usr/bin/env python
# Filename: tagim.py
"""Tag an image file with GPS position or date values, or comment and tag text

Examples:
    tagim -t 'kinariver quality6' -w -q -g '5d 31.152m N, 118d 33.801m E' -i '/home/hobs/Photos/2011_01_20 Kina River/IMG_5203.JPG'

Depends On:
    optparse, pyexiv2, sys, desktop, os, geopy, re, datetime
    tg ((c) Hobson Lane dba TotalGood)

TODO:
    * Post blog article (e-mail default address in secure settings)
    * web2.0 share
    * Quiet output of filename (needs cleanup)
    * Double-quiet output of only errors 
    * Tripple quiet no output (errors sent to a log file?)
    * Chron job or service to update catalog ever few times an image is shuffled across the background
    * Secure settings/key-chain for e-mail & blog and web2.0 passwords
    * Trigger indexing of photos based on file system monitor (OS-depedent)
    * Database: which files have been shown, index tags and comments, query language output (directly through tagim?)
    * Allow user to set persistent thresholds for values or tags like "public" or "interest" for auto-upload to blog or web2.0 share
    * Automatically modify the filename of numbered photos with natural language snippet (from tags, comments)
        + High priority for tags like location and people names and dates and unusual/rare words
"""

# eliminates insidious integer division errors, otherwise '(1.0 + 2/3)' gives 1.0 (in python <3.0)
from __future__ import division
# TODO: optionparser deprecated
from optparse import OptionParser
import tg.tagim as tagim
from warnings import warn
from tg.utils import *  # zero_if_none, sign, running_as_root
from tg.gtkutil import get_background_path
import os
import pyexiv2
import sys

version = '0.8'

# TODO: 'optparse.OptionParser' deprecated, refactor to 'argparse.ArgumentParser' and do something about reverse compatability
#p = argparse.ArgumentParser(
#            description='sum the integers at the command line')
#        parser.add_argument(
#            'integers', metavar='int', nargs='+', type=int,
#            help='an integer to be summed')
#        parser.add_argument(
#            '--log', default=sys.stdout, type=argparse.FileType('w'),
#            help='the file where the sum should be written')
#        args = parser.parse_args()
#        args.log.write('%s' % sum(args.integers))
#        args.log.close()

p = OptionParser(usage="%prog [options] [tag1] [tag2] ...[tagN]", add_help_option=True)

p.add_option('--date', '--datetime', '--time',
             dest='date', default=None,
             help='Date and time the image was taken, in ISO format, YY-MM-DD hh:mm:ss',)
p.add_option('-i', '--image', '--filename', '--image_file', '--image_filename',
             '--path', '--image_path',
             dest='image_filename', default=None,
             help='Image file whose EXIF or IPTC tags should be modified. If an integer is given instead of a valid path, then it is presumed to be the number of "frames" to rewind the slideshow to find the image requested. Image tags are edited, but the referenced image is not displayed on the desktop background.', )
p.add_option('-m', '--mirror', '--flip', '--transpose',
             dest='flip', default=0,
             help='Whether and how to mirror or flip or transpose the image. 1 = horizontally left to right, 2 = vertically top to bottom.',)
p.add_option('-g', '--gps', '-l', '--location',
             dest='gps', default=None,
             help='GPS location of the scene in the image, to be added to EXIF tags for the image.',)
p.add_option('--go', '--og', '--cg', '--mg', '--gc', '--ogps', '--mgps', '--cgps',
             '--overwrite-gps', '--overwritegps', '--overwrite_gps', '--gps-overwrite',
             '--gpsoverwrite', '--gps_overwrite', '--move-gps', '--change-gps', '--change_gps',
             '--changegps',
             dest='overwritegps', default=False,
             action='store_true',
             help='Overwrite the gps position, even if one already appears to be present in the file.',)
p.add_option('-r', '--rotate', '--rot',
             dest='angle', default=None,
             help='Rotation angle in clockwise degrees.',)
p.add_option('-o', '--overwrite',
             dest='append', default='True',
             action='store_false',
             help='Overwrite existing comments and tags in the user comment meta data field of the image file.',)
p.add_option('--edit', '--open', '--show',
             dest='show', default=False,
             action='store_true',
             help='Show the image for editing in a shotwell window.',)
p.add_option('-n', '--next', '--new', '--shuffle',
             dest='shuffle', default=False,
             action='store_true',
             help='Reload another random image for the desktop background (shuffle the deck and chose the next photo).',)
p.add_option('-u', '--update', '--refresh-catalog', '--update-catalog', '--catalog', '--refresh',
             dest='update', default=False,
             action='store_true',
             help='Find all photos in the default photo directory and build a catalog for use with --shuffle (-n).',)
p.add_option('-b', '-d', '--background', '--desktop', '--desktopbackground', '--desktop-background', '--desktop_background',
             dest='background', default=False,
             action='store_true',
             help='Whether to change the background image to reflect the image identified by --filename or --image.')
p.add_option('--ubuntu', '--splash', '--splash-screen',
             dest='splash', default=False,
             action='store_true',
             help='Whether to change the bootup background image (splash screen) to reflect the image identified by --filename or --image.')
p.add_option('-t', '--tag',
             dest='tag', default='',
             help='Tags to add to image.')
p.add_option('--test-module',
             default=False,
             action='store_true',
             help='Test tagim module and exif parsing algorithms (which rely on the pyexiv2 module).')
p.add_option('--test',
             default=False,
             action='store_true',
             help='Test the tagim script and tagim exif parsing algorihms.')
p.add_option('-c', '--comment',
             dest='comment', default='',
             help='User comment text to add to image EXIF Comment meta field (not EXIF.Photo.UserComment field).')
p.add_option('--dry-run', '--display', '--dryrun', '--dry_run',
             dest='dry_run', default=False,
             action='store_true',
             help='Display new EXIF data without writing it to the image file (see --write).',)
p.add_option('-w', '--write',
             dest='dry_run', default=False,
             action='store_false',
             help='Write new EXIF data to image file (see --dry-run).',)
p.add_option('-v', '--verbose',
             dest='verbose', default=True,
             action='store_true',
             help='Print status messages.',)
p.add_option('--debug',
             dest='debug', default=False,
             action='store_true',
             help='Print status messages.',)
p.add_option('-q', '--quiet',
             dest='verbose', default=True,
             action='store_false',
             help='Don\'t print status messages.')
p.add_option('--comment-field',
             dest='comment_field_name', default=None,
             help='NOT IMPLEMTNED: EXIF field name for storing comment text rather than the standard image comment field used by Gimp and Photoshop, e.g. "EXIF.Photo.UserComment". ')
p.add_option('--tag-field',
             dest='tag_field_name', default=None,
             help='NOT IMPLEMENTED: intended to redirect tag text to a field other than a specially encoded line at the end of the comment field.')
p.add_option('-s', '--send', '--share', '--send-email', '--send_email', '--share-email', '--email', '--email-to', '--email_to', '--to',
             dest='email_to',
             default=None,
             help='Send the modified or tagged image to the e-mail address specified.',)
p.add_option('-p', '--password', '--pass', '--pw', '--email-password', '--email-pw', '--email-pass',
             dest='email_pw',
             default=None,
             help="The plaintext password for your gmail account.",)
p.add_option('--email-user', '--email_user',
             dest='email_user',
             default='hobsonlane@gmail.com',
             help="The email address or user name for your smtp email server account (e.g. name@gmail.com)")
p.add_option('--title', '--subject', '--caption', '--heading', '--email-subject', '--email_subject', '--subject',
             dest='title',
             default='',
             help="The email subject line, caption, heading, or title for the image.")
p.add_option('--by', '--by-line', '--photographer',
             default='',
             help="The photographer (or possibly the painter or sculptor or actor that is the subject of the photo?). The copyright holder's personal name?")
p.add_option('--copyright',  # TODO: implement an appropriate tag udpated or incorporate into Comment tag
             default='',
             help="The copyright line including year and copyright holder's name")
p.add_option('--license',  # TODO: implement an appropriate tag udpated or incorporate into Comment tag
             default='',
             help="The copyright license, if any, under which the work can be copied, downloaded, shared, and/or viewed.")
p.add_option('--email-resolution', '--email_resolution', '--email-res', '--email_res', '--resolution', '--res',
             dest='email_res',
             default=None,
             help="Size of the image to be e-mailed (shrink if necessary)--number of pixels along the maximum dimension (length or width, whichever is larger).")
p.add_option('--email-from', '--email_from', '--from',
             dest='email_from',
             #default ='knowledge@totalgood.com',
             default=None,
             help="The email address in the ReplyTo: and From: fields of the email you want to send out with this image.")
p.add_option('--email-body', '--body',
             dest='email_body',
             #default ='knowledge@totalgood.com',
             default=None,
             help="Email body text to send instead of the image EXIF comments.")
p.add_option('--email-server', '--email_server', '--email-url', '--email_url', '--email-smtp', '--email_smtp',
             dest='email_server',
             default='smtp.gmail.com',
             help="The smtp email server URL (e.g. smtp.gmail.com or localhost)")

(o, a) = p.parse_args()

if o.email_pw:
    warn("Make sure you invoked "+p.get_prog_name()+" in such a way that history won't record this command (with a plaintext password) in the history file. It would be much  better if you didn't supply the password on the command line and instead allowed this script to securely prompt you for it later.")  # ,UserWarning) #,RuntimeWarning)

if not o.email_from:
    o.email_from = o.email_user

lat_label = 'Exif.GPSInfo.GPSLatitude'
lon_label = 'Exif.GPSInfo.GPSLongitude'
ref_suffix = 'Ref'

#exiv2 -M"set Exif.GPSInfo.GPSLatitude 4/1 15/1 33/1" \
#-M"set Exif.GPSInfo.GPSLatitudeRef N" image.jpg
#Sets the latitude to 4 degrees, 15 minutes and 33 seconds north. The Exif
#standard  stipulates  that the GPSLatitude tag consists of three Rational
#numbers for the degrees, minutes and seconds of the latitude and GPSLati
#tudeRef  contains  either  'N' or 'S' for north or south latitude respec
#tively.

if len(o.tag) < 1:
    o.tag = ' '.join(a)

if o.debug:
    print('Command line options being used by ' + sys.argv[0] + ':')
    print(o)

if o.test_module:
    tagim.test()

if o.test_module:
    import doctest
    doctest.testmod()

if o.update:
    tagim.update_image_catalog()

if o.shuffle:
    #cl = home + os.path.join(os.path.sep+'bin','cron.hourly','shuffle_background_photo')
    #os.system(cl)
    o.image_filename = tagim.shuffle_background_photo(o.image_filename)


sequencenum = None
if not o.image_filename:
    if o.background:
        warn("You have requested to set the desktop background to the image that is already used for the desktop background (the default input image), so nothing to be done!")  # ,UserWarning) #,RuntimeWarning)
        o.background = False
    # strip removes trailing (and leading?) \r\n characters, so filenames with leading or trailing spaces will be corrupted
    o.image_filename = os.path.normpath(tagim.image_path_from_log().strip())  # .strip('"')
else:
    try:
        sequencenum = int(o.image_filename)
    except ValueError:
        pass

if isinstance(sequencenum, int) and not os.path.isfile(o.image_filename):
    o.image_filename = tagim.image_path_from_log(sequencenum)
print o.image_filename
if not os.path.isfile(o.image_filename):
    o.image_filename = get_background_path()
print o.image_filename
if not os.path.isfile(o.image_filename):
    raise IOError("Error: Couldn't find the image file at '{0}'".format(o.image_filename))
else:
    print repr(o.image_filename)

if o.verbose:
    print "Image file name: '{0}'".format(o.image_filename)

if o.angle or int(o.flip):
    if not o.angle:
        o.angle = 0.0
    if not o.flip:
        o.flip = 0
    im = tagim.rotate_image(o.image_filename, angle=round(float(o.angle), 2), flip=int(o.flip))
    p = tagim.image_path_from_log()
    print 'path tagim.image_path(): ' + p + "\n"
    print 'path o.image_filename: ' + o.image_filename + "\n"
    if o.image_filename == p:
        tagim.shuffle_background_photo(o.image_filename)  # update the desktop image to the file that was rotated

# need these even if not o.verbose
im = pyexiv2.ImageMetadata(o.image_filename)
im.read()
exif = im.exif_keys
iptc = im.iptc_keys
xmp = im.xmp_keys

old_comment = ''
clean_comment = ''
tags = ''  # initialize the tags variable before extracting the existing tags from the image and appending any new ones

if o.comment_field_name:
    if o.comment_field_name in exif:
        old_comment = exif[o.comment_field_name]
else:
    old_comment = im.comment

# TODO: extract By-line, Title, and other tags embedded in the Comment, in addition to the "Tags" tag
#       so that Title: and By: can always precede the Tags: and "Comment:" tags within the EXIF Comment field
if o.append:
    (tags, clean_comment) = tagim.extract_tags(old_comment)
else:
    clean_comment = ''
    tags = ''

new_comment = clean_comment

if len(new_comment) > 0:
    new_comment += '\n'
new_comment += o.comment

# TODO: find out if there is an EXIF or EXIV tag for the title that should be used instead
# TODO: process the image filename and parent folder(s) name(s) to see if together they would make an appropriate default, natural language title
if len(o.title.strip()):
    new_comment = new_comment.strip('\r\n\t')  # TODO: strip spaces too? put outside of if condition and do only once?
    if len(new_comment) > 0:
        new_comment += '\n'  # find out whether \r\n is specified as line feed in EXIF standard for multi-line text fields
    new_comment += 'Title: ' + o.title.strip()

# TODO: find out if there is an EXIF or EXIV tag for the by-line that should be used instead
if len(o.by.strip()):
    new_comment = new_comment.strip('\r\n\t')  # TODO: strip spaces too? put outside of if condition and do only once?
    if len(new_comment) > 0:
        new_comment += '\n'  # find out whether \r\n is specified as line feed in EXIF standard for multi-line text fields
    new_comment += 'By: ' + o.by.strip()

# TODO: delete unneccessary (ugly) '\n' newline characters:
if len(tags) > 0 or len(o.tag) > 0:
    new_comment = new_comment.strip('\r\n\t')  # TODO: strip spaces too? put outside of if condition and do only once?
    if len(new_comment) > 0:
        new_comment += '\n'  # find out whether \r\n is specified as line feed in EXIF standard for multi-line text fields
    new_comment += 'Tags: '
if len(tags) > 0:
    new_comment += tags.strip()
if len(o.tag) > 0 and len(tags) > 0:
    new_comment += ' '
if len(o.tag) > 0:  # TODO: remove this unnecessary check
    new_comment += o.tag.strip()

if o.comment_field_name and o.comment_field_name in im.keys():
    im[o.comment_field_name].value = new_comment
else:
    im.comment=new_comment

if o.gps:
    if o.overwritegps or (not o.append) or (not (lat_label in exif)) or (len(im[lat_label].value)<2):
        d=tagim.exif_gps_strings(o.gps) # produce a dictionary of key/values for gps location string
        if o.verbose:
            print "GPS tags added to EXIF for this file:" 
            import yaml
            print yaml.dump(d)

    else:
        warn('Though a GPS position string ('+o.gps+') was provided, the file ('+o.image_filename+') already has a GPS tag. To overwrite or change this GPS position, pass the --overwrite-gps option in addition to the --gps position string.')

if o.date and im.has_key(DATE_TAG_KEY):
    im[tg.tagim.DATE_TAG_KEY]=tagim.parse_date(o.date)

if o.verbose:
    if o.debug:
        tagim.display_meta_str(im)
    else:
        tagim.display_meta_ascii(im)

if o.show:
    clargs = ['"{0}"'.format(o.image_filename),'']
    cl = 'shotwell '+' '.join(clargs)
    if o.verbose:
      print 'cl: '+cl
    os.system(cl)

if o.background and os.path.exists(o.image_filename):
    tagim.shuffle_background_photo(o.image_filename)
    #tagim.set_image_path(o.image_filename)
    #warn("Desktop image description text file no longer matches the image displayed.") # ,UserWarning) #,RuntimeWarning)
    # TODO: need to also write to the ImageMagik "identify" text file

# in '/etc/lightdm/unity-greeter.conf' modify line in "[greeter]" section starting
# with 'background=/home/...' and insert the user-selected path (o.image)
if o.splash and os.path.exists(o.image_filename):
    import subprocess
    print 'file: '+__file__
    if running_as_root(quiet=True):
        subprocess.call(["python set_splash_background.py '"+o.image_filename+"'"])
        # tagim.set_splash_background(o.image_filename)
    else:
        subprocess.call(['gksudo',"python set_splash_background.py '"+o.image_filename+"'"])

if o.dry_run:
    print(o.image_filename) # just print out the file name in case tagim was just used to find out the file path for the desktop image
    # only useful in combination with -q
else:
    if o.tag or o.comment or o.date or o.gps: # or o.angle or o.flip: # but im.write() happens within tagim.rotate_image function already
        if o.verbose:
            print 'Writing meta data to file at ' + o.image_filename
        im.write()
    else: 
        if o.verbose:
            print 'No need to write meta data to file at ' + o.image_filename
    if o.email_to:
        if not o.email_body:
            # use the revised comment field, including tags as the body of the e-mail
            o.email_body = im.comment
        print 'Composing an email to',o.email_to,'from',o.email_from,'with attachment',o.image_filename,'using username',o.email_user,'on server',o.email_server
        print '          Email body:',o.email_body
        # TODO: add command line options for SMTP server selection and/or settings (--smpt=URL+port or --use-postfix or --use-local)
        import tg.mail
        if not o.email_pw:
            import getpass
            print "Please enter your password for your",o.email_user,"account at",o.email_server
            o.email_pw=getpass.getpass()
        # TODO: confirm the contents of the e-mail and preview the image before sending (python gtk dialog box with thumbnail? html page with email and embedded image?)
        tg.mail.send(to          = o.email_to,
                     password    = o.email_pw,
                     attachments = [o.image_filename],
                     from_addr   = o.email_from,
                     user        = o.email_user,
                     subject     = o.title if o.title else 'Attached tagim Image',
                     server      = o.email_server,
                     text        = o.email_body,
                     size        = o.email_res)


