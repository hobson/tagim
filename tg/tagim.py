#!/usr/bin/env python
# Filename: tagim.py
"""Tag an image file with GPS position or date values, or comment and tag text

Examples:
    tagim -t 'kinariver quality6' -w -q -g '5d 31.152m N, 118d 33.801m E' -i '/home/hobs/Photos/2011_01_20 Kina River/IMG_5203.JPG'

Depends On:
    pyexiv2
    geopy.format
    geopy.point
    warnings.warn
    sys
    desktop
    tg.nlp
    PIL.Image
    re
    datetime
    commands
    subprocess

TODO:
    Add a functions to e-mail, blog, or web2.0 share an image file.
    Eliminate model_byline variable and content before release!!!
    this fails: tagim -i /home/hobs/photo...jpg --background  
                tagim hello world
            Error: Couldn't find the image file at 'Status=0 after copying user-designated image file at '/media/Win7/Users/Hobs/Documents/Photos/2008_10 MDR, Catalina, San Diego/IMG_3629.JPG' to dekstop background image location.'Image file name: 'Status=0 after copying user-designated image file at '/media/Win7/Users/Hobs/Documents/Photos/2008_10 MDR, Catalina, San Diego/IMG_3629.JPG' to dekstop background image location.'

"""

# eliminates insidious integer division errors, otherwise '(1.0 + 2/3)' gives 1.0 (in python <3.0)
from __future__ import division

import tg;
from tg.utils import zero_if_none, sign
from tg.regex_patterns import POINT_PATTERN, DATETIME_PATTERN
import tg.nlp as nlp

from warnings import warn
import pyexiv2

import os
import re

import commands # equivalent to subprocess?
import subprocess

version = '0.7'
(user,home) = tg.user_home();

# I can't imagine GPS positions ever needing to be recorded better
#  than a couple tenths of a milimeter (an arcsecond is about 1.7 meters)
MAX_RATIONALIZE_BITS = 31
MAX_RATIONALIZE_DENOMINATOR = 2**MAX_RATIONALIZE_BITS
MIN_RATIONALIZE_FLOAT = 10.0/float(MAX_RATIONALIZE_DENOMINATOR)

RATIONALIZE_DENOMINATOR_FACTOR = 2 # should be a power of 2 to avoid round off error in the conversion from a float to a fraction of integers
DATE_TAG_KEY = 'Exif.Photo.DateTimeOriginal'


# some hints from http://www.opanda.com/en/pe/help/gps.html 
#                 http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/GPS.html
#                 http://www.jofti.com/files/index.php?option=com_content&view=article&id=29:geo-tag-2&catid=11:blog&Itemid=9
# EXIF_GPSLatitudeRef EXIF_GPSLatitude EXIF_GPSLongitudeRef EXIF_GPSLongitude EXIF_GPSAltitudeRef EXIF_GPSAltitude EXIF_GPSTimeStamp EXIF_GPSSatellites EXIF_GPSStatus EXIF_GPSMeasureMode EXIF_GPSDOP EXIF_GPSSpeedRef EXIF_GPSSpeed EXIF_GPSTrackRef EXIF_GPSTrack EXIF_GPSImgDirectionRef EXIF_GPSImgDirection EXIF_GPSMapDatum EXIF_GPSDestLatitudeRef EXIF_GPSDestLatitude EXIF_GPSDestLongitudeRef EXIF_GPSDestLongitude EXIF_GPSDestBearingRef EXIF_GPSDestBearing EXIF_GPSDestDistanceRef 	EXIF_GPSDestDistance 

# HL: leave out all the "Ref" labels?
EXIF_GPS_LABEL  = ['LatitudeRef', 'Latitude', 'LongitudeRef', 'Longitude', 'AltitudeRef', 'Altitude',]
EXIF_GPS_LABEL += ['TimeStamp', 'Satellites', 'Status', 'MeasureMode', 'DOP', 'SpeedRef', 'Speed', 'TrackRef',]
EXIF_GPS_LABEL += ['Track', 'ImgDirectionRef', 'ImgDirection', 'MapDatum', 'DestLatitudeRef', 'DestLatitude',]
EXIF_GPS_LABEL += ['DestLongitudeRef', 'DestLongitude', 'DestBearingRef', 'DestBearing', 'DestDistanceRef', 'DestDistance',]

EXIF_GPS_REF_SUFFIX = 'Ref'
EXIF_GPS_PREFIX = 'GPS'
PYEXIV2_GPS_PREFIX = 'Exif.GPSInfo.'
EXIF_GPS_LAT_LABEL = PYEXIV2_GPS_PREFIX + EXIF_GPS_LABEL[1]
EXIF_GPS_LON_LABEL = PYEXIV2_GPS_PREFIX + EXIF_GPS_PREFIX+EXIF_GPS_LABEL[3]
EXIF_GPS_ALT_LABEL = PYEXIV2_GPS_PREFIX + EXIF_GPS_PREFIX+EXIF_GPS_LABEL[5]
EXIF_GPS_POS_LABELS = [EXIF_GPS_LAT_LABEL, EXIF_GPS_LON_LABEL, EXIF_GPS_ALT_LABEL]

#exiv2 -M"set Exif.GPSInfo.GPSLatitude 4/1 15/1 33/1" \
#-M"set Exif.GPSInfo.GPSLatitudeRef N" image.jpg
#Sets the latitude to 4 degrees, 15 minutes and 33 seconds north. The Exif
#standard stipulates that the GPSLatitude tag consists of three Rational
#numbers for the degrees, minutes and seconds of the latitude and GPSLati
#tudeRef contains either 'N' or 'S' for north or south latitude respec
#tively.

# describes the position of the 0th column and zeroth row, e.g. the point 0,0, <ref> http://sylvana.net/jpegcrop/exif_orientation.html </ref>
# the desktop wallpaper seems to not take this setting into account (shotwell does seem to), so after rotation to upright
# TODO: these belong in a public database and are probably unnecessary
EXIF_orientation_name    =[None , 'top left' , 'top rght', 'btm rght', 'btm left', 'left top', 'rght top', 'rght btm', 'left btm']
# degrees to rotate the image data before or after flipping
EXIF_orientation_angle   =[None ,      0     ,     0     ,     180   ,    180    ,     90    ,     90    ,    270    ,     270   ] 
# 0 = no flip/transpose required, 1 = flip horizontally, 2 = flip vertically
EXIF_orientation_flip    =[None ,      0     ,     1     ,      0   ,      1     ,      2    ,      0    ,     2     ,      0    ] 
# 0th array is list of camera models that don't report orientation, 1th is for cameras that do
EXIF_orientation_makes  = [['CANON','NIKON','OLYMPUS OPTICAL CO.,LTD'],['CANON','KODAK','SONY','PENTAX', 'HTC']] 
EXIF_orientation_models  = [['Canon PowerShot S300','COOLPIX L18','C740UZ'],['Canon EOS 450D','KODAK EASYSHARE M863 DIGITAL CAMERA','DSC-W80','PENTAX K10D', 'Android Dev Phone 1']] 
# whether or not to trust the GPS info from the camera
EXIF_gps_makes  = [['CANON','NIKON','OLYMPUS OPTICAL CO.,LTD','CANON','KODAK','SONY','PENTAX Corporation'],['HTC']] 
EXIF_gps_models  = [['Canon PowerShot S300','COOLPIX L18','C740UZ','Canon EOS 450D','KODAK EASYSHARE M863 DIGITAL CAMERA','DSC-W80','PENTAX K10D'],['Android Dev Phone 1']] 
# camera models and thier owners, a list in order from most likely photographer (byline) to least likely, for each camera
# TODO: this belongs in a database based on previously processed and bylined photos for an individual
# DEPLOY: RELEASE: delete this before deployment or release
model_byline = {'Canon PowerShot S300':['Hobson','Larissa'],'COOLPIX L18':['Catherine','Larissa','Hobson'],'C740UZ':['Diane','Hobson','Larissa'],'Canon EOS 450D':['Larissa','Hobson','Diane'],'KODAK EASYSHARE M863 DIGITAL CAMERA':['Hobson','Larissa'],'DSC-W80':['Hobson','Carlana','Dewey'],'PENTAX K10D':['Ryan']}

# Desktop Background (DBG) paths
DBG_PATH         = os.path.realpath(os.path.join(home, '.cache', 'gnome-control-center', 
                                    'backgrounds','desktop_background_image_copy.jpg'))
DBG_CATALOG_PATH = os.path.realpath(os.path.join(home, '.desktop_slide_show_catalog.txt'))
DBG_PHOTOS_PATH  = os.path.realpath(os.path.join(home, 'Desktop', 'Photos'))
DBG_LOG_PATH     = os.path.realpath(os.path.join(home, 
                                    '.desktop_background_refresh_photo_debug.log'))
DB_LOG_PATH      = os.path.realpath(os.path.join(home, 
                                    '.desktop_background_refresh_photo_catalog.log'))
DBG_DB_PATH      = os.path.realpath(os.path.join(DBG_PHOTOS_PATH, 
                                   '.tagim_photo_sqlite_database.db'))

def rotate_image(filename,angle=0.0,resample='bicubic',expand=True,flip=0):
    """Rotate and/or flip the image data within a jpeg file.

    Examples:
    >>> import filecmp, tg.utils
    >>> imp    = os.path.join(tg.utils.path_here()[0],  test.jpg)
    >>> imp90  = os.path.join(tg.utils.path_here()[0],test90.jpg)
    >>> imp90b = os.path.join(tg.utils.path_here()[0],test90.jpg)
    >>> os.copy(imp,imp90b)
    >>> rotate(imp90b,90,flip=0)
    >>> filecmp.cmp(imp90,imp90b,shallow=False)
    True
    >>> filecmp.cmp(imp,imp90b,shallow=False)
    False
    >>> filecmp.cmp(imp,imp90, shallow=False)
    False
    """
    from PIL import Image
    if not nlp.is_number(angle) or abs(float(angle))<=1e-6:
        angle = 0
    if not angle and flip not in [1,2]:
        return
    angle=float(angle)
    im = pyexiv2.ImageMetadata(filename)
    im.read()
    # every camera make has different compliance standards
    if resample==Image.NEAREST  or resample.lower().strip()=='nearest': 
        resample=Image.NEAREST
    elif resample==Image.BILINEAR or resample.lower().strip()=='bilinear': 
        resample=Image.BILINEAR
    else:
        resample=Image.BICUBIC
    # read in the filename using PIL and rotate it, then save it to the same file
    if angle:
        im3=Image.open(filename)
        im3.rotate(-1*angle,resample=resample,expand=expand).save(filename)
    if flip in [1,2]:
        im4=Image.open(filename)
        im4.transpose(int(Image.FLIP_LEFT_RIGHT)+flip-1).save(filename)
    # instantiate another object for writing to the image file's metadata to change the vertical/horizontal dimensions
    im2 = pyexiv2.ImageMetadata(filename)
    im2.read()
    im.copy(im2) # copy over all the image meta-data from the original image to the new one (in memory)
    im2["Exif.Photo.PixelXDimension"] = im3.size[0]
    im2["Exif.Photo.PixelYDimension"] = im3.size[1]
    im2.write()
    # these models require no adjustement of their orientation value, because it wasn't set in the first place, it should always be 1
    if im2['Exif.Image.Model'].value in EXIF_orientation_models[0]:
        im2['Exif.Image.Orientation'] = 1 # assume that the rotated image is now upright, with top-left equal to row,column 0,0 
        im2.write() # this saves the new orientation value, other EXIF tag changes have already been saved
        warn("Camera model isn't one that normally sets the Exif.Image.Orientation appropriately (no orientation sensor?). Writing a 1 to this field, which assumes the newly rotated image is upright.") # ,UserWarning # ,RuntimeWarning)
    # These models need to have their orientation value properly set by the camera (along with image dimensions)
    # So they should display properly in programs that check this, even if the bitmap is not rotated.
    # But since we are rotating the bitmap, we need to rotate the Exif.Image.Orientation value as well.
    elif im2['Exif.Image.Model'].value in EXIF_orientation_models[1]:
        if EXIF_orientation_angle[int(im2['Exif.Image.Orientation'].value)] not in [angle,angle-360,angle+360]:
            warn("The Exif.Image.Orientation tag doesn't match the current rotation of the image, assuming you were trying to rotate it upright, so the Exif.Image.Orientation field was left unchanged." )  # ,UserWarning # ,RuntimeWarning)
        if EXIF_orientation_flip[int(im2['Exif.Image.Orientation'].value)] != 0 :
            hv_text = [ '','horizontally','vertically']
            warn("The image needs to be flipped (mirrored) for the image orientation tag of " + hv_text[EXIF_orientation_flip[int(im2['Exif.Image.Orientation'])] % 2]
               + "to match the EXIF orientation tag in the image to the actual image data arrangement which is presumed to be upright and normalized after your requested rotation." ) # ,UserWarning # ,RuntimeWarning)
        im2['Exif.Image.Orientation'] = 1 # assume that the rotated image is now upright, with top-left equal to row,column 0,0 
    else:
        im2['Exif.Image.Orientation'] = 1 # assume that the rotated image is now upright, with top-left equal to row,column 0,0 
        warn("Unknown camera model, so don't know whether it normally sets the Exif.Image.Orientation appropriately (no orientation sensor?). So writing a 1 to this field, which assumes the newly rotated image is upright.") # ,UserWarning # ,RuntimeWarning)
    im2.write()

def display_meta(im):
    exif = im.exif_keys
    iptc = im.iptc_keys
    xmp  = im.xmp_keys

    print '-------------EXIF Data-------------------'
    for k in exif:
        # escape_unprintable(str(...  or s.encode('utf_8','backslashreplace')
        print "{0}: {1}".format(k,str(im[k].value))
    print '-----------------------------------------'
    print
    print '-------------IPTC Data-------------------'
    for k in iptc:
        print "{0}: {1}".format(k,str(im[k].value))
    print '-------------XMP Data-------------------'
    for k in xmp:
        print "{0}: {1}".format(k,str(im[k].value))
    print '-----------------------------------------'
    print
    print '------------- Comment -------------------'
    print im.comment
    print '-----------------------------------------'
    return (exif, iptc, xmp)

def extract_tags(comment_string):
    comment_string=comment_string.strip()
    # actHL: need an or in the re to capture 'Tags: ' field identifier as the only line in the comment and enforce '\nTags: ' identifier otherwise
    mo=re.search(r'(.*)(\n*Tags:\s*)(.*)(\n*.*)',comment_string) #(1).split(' ') #,flags=re.IGNORECASE).group(1)
    tags=[]
    if not mo:
        return (tags,comment_string)
    groups=mo.groups()
    if (len(groups)>2):
        tags = groups[2]
        comment_without_tags = str(groups[0])
        if (len(groups)>3):
            comment_without_tags += str(groups[3])
    return (tags,comment_without_tags)

def deg2dms(deg):
    deg = float(deg)
    assert isinstance(deg,float)
    neg = bool(deg<0)
    assert neg==True or neg==False
    d = int(abs(deg)) # int is like floor() but towards zero for negative values (floor is towards negative infinity)
    assert d>=0 
    assert d<=abs(float(deg))
    assert isinstance(d,int)
    m = int((float(deg) - d)*60)
    assert isinstance(m,int)
    s = ((float(deg) - d)*60 - m)*60
    assert isinstance(s,float)
    if neg:
        d=-d
        m=-m
        s=-s
    # both deg and the d,m,s set should have the sign of the deg value originally input
    assert abs( s/3600.0 + m/60.0 + d - deg) < 1e-3, "abs( (s)/3600.0 + {m}/60.0 + {d} + {deg}) = {val} !< 1e-3".format(s=s,m=m,d=d,deg=deg,val=abs(s/3600.0+m/60.0+d-deg))
    return (d,m,s)

# WARN: seems to fail for some floats if MAX_RATIONALIZE... is too big (1e9),
# perhaps due to the precision of the repeated multiplication by 10 which seems to destroy the last couple digits
def rationalize_float(f):
    den = long(1)
    num = f
    sgn = sign(f)
    num *= sgn
    assert num>=0, "{num}>=0".format(num=num)
    if (f and (f-0.0)<MIN_RATIONALIZE_FLOAT):
        warn("Float value ("+str(f)+") close to zero so rounding it to exactly zero, for simplicity and equality comparison.")
        return(0,1)
    # *= 10 makes the fraction easier to read in decimal, but introduces roundoff error due to the base 2 floating point math in the cpu
    while (abs(num-round(num))>(1.1/MAX_RATIONALIZE_DENOMINATOR)) and (den<.9*MAX_RATIONALIZE_DENOMINATOR):
        num *= RATIONALIZE_DENOMINATOR_FACTOR
        den *= RATIONALIZE_DENOMINATOR_FACTOR
    num = long(round(num))
    assert num>=0, "{num}>=0".format(num=num)
    den = long(round(den))
    assert den>0, "{den}>0".format(den=den)
    num *= sgn
    # assert less than 1 part per million error when converted back to a float from a rational pair
    if abs(f)>0:
        assert abs(f-float(num)/den)/abs(f)<=1e-6, '{val} = abs({f} - float({num})/{den})/{f} !<= 1e-6'.format(
                    f=f, num=num, den=den, val=abs(f - float(num)/den)/abs(f) )   
    # assert less than 2 parts of the MAX_RATIONALIZE_DENOMINATOR
        assert abs(f-float(num)/den)/abs(f)<=2.0/MAX_RATIONALIZE_DENOMINATOR, "{val} = abs({f} - {num}/{den})/{f} !<= 2/{max_den}".format(
                    f=f, num=num, den=den, val=abs(f - num/den)/abs(f), max_den = MAX_RATIONALIZE_DENOMINATOR )
    return (int(round(num)),int(round(den)))

def exif_gps_rationalize(deg):
    isneg = bool(deg<0)
    if isneg:
        deg *= -1.0
    assert deg==abs(deg), "{deg}==abs({deg})".format(deg=deg)
    (d,m,s)=deg2dms(deg)
    assert d==int(d), "{d}==int({d})".format(d=d)
    assert m==int(m), "{m}==int({m})".format(m=m)
    #print 'dms =',str(d),str(m),str(s)
    #import pyexiv2.utils
    #r = pyexiv2.utils.make_fraction(str(round(s,MAX_RATIONALIZE_DIGITS))) 
    # pyexiv2.utils.Rational requires the decimal to already be split into numerator and denomenator! It can't deal with floats or strings of floats!
    #import fractions
    #r = fractions.Fraction(str(round(s,MAX_RATIONALIZE_DIGITS)))
    #print r
    (s_num,s_den)= rationalize_float(s)
    #print s_num,s_den
    return  ("{d}/1 {m}/1 {s}/{den}".format(d=int(round(d)),m=int(round(m)),s=int(round(s_num)),den=s_den), isneg)

def location2latlon(location_string):
    import geopy
    lat = lon = alt = 0.0
    mo = POINT_PATTERN.match(location_string)
    try:
        p = geopy.point.Point(location_string)
        lat = p.latitude
        lon = p.longitude
        # TODO: need to trigger these warnings or messages only when "verbose" or "debug" global option is set
        print "geopy module point.Point() read the gps string, but is it valid?"
        print '('+str(lat)+','+str(lon)+') '+' == '+'"'+location_string+'" ?'
    except ValueError:
        if mo: # and (mo.group('latitude_degrees' ) or mo.group('longitude_degrees' )):
            lat = (float(zero_if_none(mo.group('latitude_degrees' )))
                 + float(zero_if_none(mo.group('latitude_arcminutes' )))/60.0
                 + float(zero_if_none(mo.group('latitude_arcseconds' )))/3600.0)
            lon = (float(zero_if_none(mo.group('longitude_degrees'))) 
                 + float(zero_if_none(mo.group('longitude_arcminutes')))/60.0 
                 + float(zero_if_none(mo.group('longitude_arcseconds')))/3600.0)
            # TODO: altitude
            print "geopy.point.Point() unable to read gps string, but tg.tagim got ..."
            print '('+str(lat)+','+str(lon)+') '+' from the string '+'"'+location_string+'" ?'
            print mo.groupdict()
        else:
            return (None,None,None)
    return (lat,lon,alt)

def latlon2exif(lat,lon,alt=0.0):
    # Need to rationalize them and get rid of sign (recording the sign separately)
    (latrat, latneg) = exif_gps_rationalize(lat)
    (lonrat, lonneg) = exif_gps_rationalize(lon)
    (altrat, altneg) = exif_gps_rationalize(0.0) # TODO: process altitude
    # Now need to incorporate the sign information into the direction reference strings (N/S and E/W)
    latref = 'N'
    if latneg:
        latref = 'S'
    lonref = 'E'
    if lonneg:
        lonref = 'W'
    altref = 1 # above sealevel
    if altneg:
        altref = 0 # below sealevel (negative)
    # Return a dictionary or hash with the appropriate EXIF tag keys and values (integer fractions of deg, min, s) for GPS positions 
    return	{
                EXIF_GPS_LAT_LABEL: latrat, 
                EXIF_GPS_LON_LABEL: lonrat, 
                EXIF_GPS_ALT_LABEL: altrat,
                EXIF_GPS_LAT_LABEL+EXIF_GPS_REF_SUFFIX: latref,
                EXIF_GPS_LON_LABEL+EXIF_GPS_REF_SUFFIX: lonref,
                EXIF_GPS_ALT_LABEL+EXIF_GPS_REF_SUFFIX: altref,
            }

def deg2dm(decimal_degrees):
    """
    Convert decimal degrees to degrees, minutes, sign
    """
    sgn = copysign(1.,decimal_degrees)
    degrees = int(abs(decimal_degrees))
    decmial_minutes = abs(decimal_degrees)-degrees
    return (degrees, minutes, sgn)

def latlon2pyexiv2(lat_deg,lon_deg):
    (d1,m1,sgn1) = deg2dm(lat_deg)
    if sgn1:
        sgn1 = 0
    else:
        sgn1 = -1
    (d2,m2,sgn2) = deg2dm(lon_deg)
    if sgn2:
        sgn2 = 0
    else:
        sgn2 = -1
    # 'DDD,MM.mmk' (k is N/S or E/W
    lat = pyexiv2.GPSCoordinate.from_string('{0:2d},{1:2.4d}{2:1s}'.format(d1,m1,chr(sgn1*(ord('N')-ord('S'))+ord('N'))))
    lon = pyexiv2.GPSCoordinate.from_string('{0:2d},{1:2.4d}{2:1s}'.format(d2,m2,chr(sgn2*(ord('E')-ord('W'))+ord('E'))))
    return (lat,lon)

def set_gps_location(exiv_image, lat, lng):
    """Adds GPS position as EXIF metadata

    Keyword arguments:
    exiv_image -- pyexiv2.Image(filename)
                  the metadata should have already been read
                  this function will not write the new information
                  but rather modify the EXIF tags in memory
                  Do an exif_image.write() to save the changed tags
    lat -- latitude (as float)
    lng -- longitude (as float)

    based on code by Maksym Kozlenko at:
      http://stackoverflow.com/questions/453395/what-is-the-best-way-to-geotag-jpeg-images-with-python
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    # convert decimal coordinates into degrees, munutes and seconds
    exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
    exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))

    exiv_image = pyexiv2.Image(file_name)
    exif_keys = exiv_image.exifKeys() 

    exiv_image["Exif.GPSInfo.GPSLatitude"] = exiv_lat
    exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
    exiv_image["Exif.GPSInfo.GPSLongitude"] = exiv_lng
    exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]
    exiv_image["Exif.Image.GPSTag"] = 654
    exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    exiv_image["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'


# create a dictionary of the EXIF labels and strings (fractions of integers in d/d m/m s/s format)
def exif_gps_strings(location_string):
    loctuple=location2latlon(location_string)
    if not loctuple or ( not loctuple[0] and not loctuple[1] and not loctuple[2] ):
        return {}
    return latlon2exif(loctuple[0],loctuple[1],loctuple[2])

def exif_unrationalize_gps(gps_exif_dict):
    # turn an exif representation of a gps position into a pair of floats for lat lon 
    #   gps_exif_dict = {lat_label: latrat, lon_label: lonrat, lat_label+ref_suffix: latref, lon_label+ref_suffix: lonref}, with floats expressed as fractions in deg, min, sec
    # result = (lat,lon)
    if not gps_exif_dict:
        return {}
    values = {}
    for i,label in enumerate(EXIF_GPS_POS_LABELS):
        values[label] = 0.0
        # WARN: str.split() with multiple delimiters NEVER works!!!!
        # v_array = gps_exif_dict[label].split(SPACE+'/')
        if not label in gps_exif_dict:
            continue
        v_array = re.findall(r'[-+0-9]+',gps_exif_dict[label])
        print str(v_array)
        assert 6==len(v_array), "6=={lenv}==len({v_array})".format(lenv=len(v_array),v_array=v_array)
        odd = 1.0
        multiplier = 1.0
        f = 1.0
        for v in v_array:
#			print '---------------------'
#			print 'v,numerator,multiplier,toggle,adder,value',v,f,multiplier,odd,f,'/',float(v),'/',multiplier,values[label]
            if odd>0:
                f = float(v)
            else:
                assert float(v)>0, "v={v}>0".format(v=v)
                # TODO: does this just duplicate the assert statement with more verbosity?
                if float(v) <= 0:
                    raise ValueError("An EXIF Rational type string should never have a negative or zero denominator. Erroneous rational string was '"
                                     +gps_exif_dict[label]+"', which parsed into these values of alternating numerator and denomenator'"+' '.join(v_array)
                                     +"', which gives the bad denomenator value of '"+v+"'.")
                values[label] += (f/float(v))/multiplier
                multiplier *= 60.0
            odd *= -1
            print 'v,numerator,multiplier,toggle,adder,value',v,f,multiplier,odd,f,'/',float(v),'/',multiplier,values[label]
#			print '---------------------'
    return(values)

def parse_date(s):
    from datetime import datetime
    from math import floor

    mo=DATETIME_PATTERN.match(s)
    if mo:
        y = zero_if_none(mo.group('y'))
        if len(y) == 2:
            if y[0] == '0':
                y = int(y) + 2000
#			else:
#				y = int(y)
#				if y > 20 and y < 100:
#					y = y + 1900
        y = int(y)
        mon = int(zero_if_none(mo.group('mon')))
        d = int(zero_if_none(mo.group('d')))
        h = int(zero_if_none(mo.group('h')))
        m = int(zero_if_none(mo.group('m')))
        s_f = float(zero_if_none(mo.group('s')))
        s = int(floor(s_f))
        us = int((s_f-s)*1000000.0)
        return datetime(y,mon,d,h,m,s,us)
    else:
        raise ValueError("Date time string not recognizeable or not within a valid date range (2199 BC to 2199 AD): %s" % s)
#	return date.datetime.strptime(s,"%y %m %d %H:%M:%S")

def set_image_path(filename):
    print filename
    if filename:
        output = subprocess.Popen(
            ["gconftool-2",'--type','str','--set','/desktop/gnome/background/picture_filename',str(filename)])
    else:
        output = subprocess.Popen(
            ["gconftool-2"               ,'--get','/desktop/gnome/background/picture_filename'], stdout=subprocess.PIPE).communicate()[0]
    return output

def exif2latlon(exif_dict):
    if not exif_dict:
        return (None,None,None)
    values = exif_unrationalize_gps(exif_dict)
    if not values:
        return (None,None,None)
    for i in range(3):
        if not EXIF_GPS_POS_LABELS[0] in values:
            return (None,None,None)
    return (values[EXIF_GPS_POS_LABELS[0]],values[EXIF_GPS_POS_LABELS[1]],values[EXIF_GPS_POS_LABELS[2]])

def test_gps():
    test_gps_s = [
        '6.96131666667N, 117.043733333 E',
        '6.96131666667 S, 117.043733333W',
        '6.96131666667  S, 117.043733333  W',
        '6.96131666667, 117.043733333',
        "06 57.679 117 02.624'",
        "06 57.679'S 117 02.624'W",
        '06 deg 57.679 min n 117 deg 02.624min w',
        '08 deg 54.776 S 140 deg 06.285 W',
        "8 deg 56.725' S 140 deg 10.063' W", # Danial's bay? Nuku Hiva island near the mouth of the creek from the "cascades".
    ]
    for t in test_gps_s:
        print "gps string: '{0}' ==".format(t)
        (lat,lon,alt)=location2latlon(t)
        r = latlon2exif(lat,lon,alt)
        if not r:
            raise RuntimeError("Unable to process the GPS location string: "+t)
            break
        for k,v in r.items():
            print "    {k} => '{v}'".format(k=k,v=v)
        # {lat_label: latrat, lon_label: lonrat, lat_label+ref_suffix: latref, lon_label+ref_suffix: lonref}
        #print '----------- what labels are missing -----------'
        #print r
        v_dict = exif_unrationalize_gps(r) # 3 floats in a dictionary to replace the 3 fractions that were there before
        # take the float values and construct a string and reconvert to fractions and see that it's still the same set of strings
        #print r 
        #print ' ?== ' 
        # WARN: this doesn't work, need to put together a full-circle assert/test
        (lat1,lon1,alt1)=exif2latlon(r) # WARN sign is corrupted by this point
        assert lat1<=  90.0
        assert lat1>= -90.0
        assert lon1<= 180.0
        assert lon1>=-180.0
        assert abs(lat-lat1)<1e-6, "lat: abs({lat}-{lat1})<1e-6".format(lat=lat,lat1=lat1)
        assert abs(lon-lon1)<1e-6, "lon: abs(lon-lon1)<1e-6".format(lon=lon,lon1=lon1)
        assert alt==alt1

        s = exif_gps_strings(str(lat) + ' deg ' + str(lon) + ' deg ' + str(alt) + ' m ')
        # WARN: this doesn't really verify the original conversion from string into floats
        (lat2,lon2,alt2)=exif2latlon(s)
        assert lat2<=  90.0
        assert lat2>= -90.0
        assert lon2<= 180.0
        assert lon2>=-180.0
        assert abs(lat-lat2)<1e-6, "lat: abs({lat}-{lat2})<1e-6".format(lat=lat,lat2=lat2)
        assert abs(lon-lon2)<1e-6, "lon: abs(lon-lon2)<1e-6".format(lon=lon,lon2=lon2)
        assert alt1==alt2 
        #print sassert
    test_date_s = [
        '2011/02/14 12:06:38',
        '08/02/14 12:06:38',
        '2011-02-14-12-06-38',
        '2011_02_14_12:06:38'
    ]
    for t in test_date_s:
        print "date string: '{0}' ---------------------------".format(t)
        r = parse_date(t)
        print "  dateime: "+str(r)

# TODO: gnome gconf settings don't match the path to DBG_PATH, but this works anyway, why?
def shuffle_background_photo(image=''): 
    #(user,home) = tg.user_home();
    dbg_log_file = open(DBG_LOG_PATH,mode='a')
    db_log_file = open(DB_LOG_PATH,mode='a')
    import random, commands, shutil
    if image and os.path.isfile(image):
        shutil.copy(os.path.realpath(image),DBG_PATH) # overwrite the existing background image
        msg = "{0}:{1}:\n  Copied-designated image file, '{2}', to desktop background image location.".format(
                  __file__,__name__,image)
        print >> dbg_log_file, msg
        print >> dbg_log_file, image
        db_log_file.write(str(image)+'\n')
        dbg_log_file.close()
        db_log_file.close()
        return image
    msg = "{0}:{1}:\n  Starting desktop background random selection.".format(__file__,__name__)
    print >> dbg_log_file, msg
    # TODO use tg.utils.find_in_files or shutil or similar instead of cat and grep:
    status, PHOTOCOUNT = commands.getstatusoutput('cat {0} | grep / -c'.format(DBG_CATALOG_PATH))  # status=0 if success

    RANDPHOTOPATH = ''
    status = True # status = 0 when successful shell command is run
    while status or not RANDPHOTOPATH or not os.path.isfile(RANDPHOTOPATH):
        # TODO use tg.utils.replace_in_file instead of sed:
        status, RANDPHOTOPATH = commands.getstatusoutput(
            'sed -n {0}p "{1}"'.format(str(random.randint(1,int(PHOTOCOUNT))),DBG_CATALOG_PATH))
    shutil.copy(RANDPHOTOPATH,DBG_PATH)
    print >> dbg_log_file, "  Finished copying over the desktop background image file with the image at:"
    #+os.linesep
    print >> dbg_log_file, RANDPHOTOPATH
    dbg_log_file.close()
    db_log_file.write(str(RANDPHOTOPATH)+'\n')
    db_log_file.close()
    return RANDPHOTOPATH

    #mv ${SAFEHOME}/Desktop/DESKTOP_BACKGROUND_PHOTO_INFO.txt" ${SAFEHOME}/Desktop/DESKTOP_BACKGROUND_PHOTO_INFO.txt.prepend.tmp"
    #identify -verbose "${RANDPHOTOPATH}" >> "${SAFEHOME}/Desktop/DESKTOP_BACKGROUND_PHOTO_INFO.txt"
    #cat ${SAFEHOME}/Desktop/DESKTOP_BACKGROUND_PHOTO_INFO.txt.prepend.tmp" >> ${SAFEHOME}/Desktop/DESKTOP_BACKGROUND_PHOTO_INFO.txt.prepend.tmp"

def update_image_catalog():
    # TODO: use shutils python module instead of linux bash shell command
    import commands
    command = "find '{0}' \( -type f -and -size +200k \) -and \( -iname '*.jpg' -or -iname '*.png' -or -iname '*.bmp' -or -iname '*.raw' \) -print > '{1}'".format(DBG_PHOTOS_PATH, DBG_CATALOG_PATH)
    print command
    status,output = commands.getstatusoutput(command)
    return status

# path to file used to set things like the unity boot up screen background
UBUNTU_SPLASH_CONFIG_PATH = '/etc/lightdm/unity-greeter.conf'

# Set the ubuntu startup screen background to an image file
def set_splash_background(image='',ubuntu_splash_conf=UBUNTU_SPLASH_CONFIG_PATH):
    print 'file='+__file__
    import tg.regex_patterns
    import tg.utils
    dbg_log_file = open(DBG_LOG_PATH,mode='a')
    if image and os.path.isfile(image):
        # read file into string?
        EOL = tg.regex_patterns.UTIL_PATTERNS['EOL']
        patt = r'(?m)(?P<pretext>'+EOL+r'[[]greeter[]](?:.*'+EOL+r')+\s*background\s*=\s*)' \
               + tg.regex_patterns.PATH_PATTERNS['LIN']
        # substitute patten with image path
        tg.utils.multiline_replace_in_file(patt,r"""(?P=pretext)'"""+image+"'",ubuntu_splash_conf)
        # re.sub = sub(patt, repl, string, count=0, flags=0)
        msg = "{0}:{1}:\n  Set Ubuntu splash screen (bootup background) to '{2}'.".format(__file__,__name__,image)
        print >> dbg_log_file, msg

def update_image_catalog():
    import commands
    command = "find '{0}' \( -type f -and -size +200k \) -and \( -iname '*.jpg' -or -iname '*.png' -or -iname '*.bmp' -or -iname '*.raw' \) -print > '{1}'".format(DBG_PHOTOS_PATH, DBG_CATALOG_PATH)
    print command
    status,output = commands.getstatusoutput(command)
    return status

def image_path_from_log(sequence_num=None):
    # Is subprocess.Popen better than os.system(...)? commands module might be better
    # It allows retrieval of output is the main thing.
    # TODO: use python functions in utils.replace_in_file or shutil instead of sed/tail
    if sequence_num:
        status,output = commands.getstatusoutput( 'tail -n {0} {1} | head -n 1'.format( abs(sequence_num)*1+1, DB_LOG_PATH ))
    else: 
        status,output = commands.getstatusoutput('sed -n \$p {0}'.format(DB_LOG_PATH))
    if output[-1]=='\n': # this has only ever happened with the subprocess.Popen command, but you never know
        output=output[:-1]
    return  os.path.normpath(os.path.abspath(output.strip()))

# TODO: this no longer seems to work, in the latest Ubuntu
def image_path_from_gnome():
    # Is subprocess.Popen better than os.system(...)? commands module might be better
    # It allows retrieval of output is the main thing.
    output = subprocess.Popen(["gconftool-2",'--get','/desktop/gnome/background/picture_filename'], stdout=subprocess.PIPE).communicate()[0]
    if output[-1]=='\n':
        output=output[:-1]
    return  os.path.normpath(os.path.abspath(output.strip()))

def image_path():
    path_log=image_path_from_log()
    path_gnome=image_path_from_gnome()
    print 'image_path_from_log():   ' + path_log + "\n"
    print 'image_path_from_gnome(): ' + path_gnome + "\n"

    if identical_images(path_log,path_gnome):
        return path_log
    else:
        raise RuntimeError("Unable to locate the source file for the image currently displayed as the desktop background.")
    return False

def identical_images(path1,path2):
    from PIL import Image
    im1=Image.open(path1)
    im2=Image.open(path2)
    return bool(im1==im2)

def compare_images(path1,path2):
    return identical_images(path1,path2)

# this all needs to be in a db class

#import sqlalchemy
#engine = sqlalchemy.create_engine('sqlite://'+DBG_PHOTOS_DB, echo=True)
#from sqlalchemy.orm import sessionmaker
#Session = sessionmaker(bind=engine)
#session = Session()

#from sqlalchemy.ext.declarative.declarative_base
#class Photo(Base):
#    __tablename__ = 'users'
#    path = Column(String(256), primary_key=True)
#    sig  = Column(String(256))  # md5 or hash string signature of image file (pixel+metadata)
#    def __init__(self, path, sig):
#        self.path = path
#        self.sig  = sig
#    def __repr__(self):
#        return "<Photo('%s','%s')>" % (self.path, self.sig)
#class Tag(Base):
#    __tablename__ = 'users'
#    path = Column(String(256), primary_key=True)
#    sig  = Column(String(256))  # md5 or hash string signature of image file (pixel+metadata)
#    def __init__(self, path, sig):
#        self.path = path
#        self.sig  = sig
#    def __repr__(self):
#        return "<Photo('%s','%s')>" % (self.path, self.sig)

#def db_initialize(db_path=DBG_DB_PATH):
#	import sqlite3
#	conn = sqlite3.connect(db_path)
#	c = conn.cursor()
#	c.execute('create table tag(name text, count integer)')
#	c.execute('create table photo(name text, tag)')
#	c.execute('create table photo_tag(name text, tag)')

#def db_add_tag(tag,db_path=DBG_DB_PATH):
#	import sqlite3
#	conn = sqlite3.connect(db_path)
#	c = conn.cursor()
#	c.execute("select * from tag where name='?'",tag)
#	t = c.fetchall()
#	if (len(t)==1)
#		c.execute("update * from tag where name='?'",tag)
#		
#	# Create table
#	#c.execute("create table tags (name text, frequency integer)")

#	# Insert a row of data
#	c.execute("insert tags values ('2006-01-05','BUY','RHAT',100,35.14)")

## Save (commit) the changes
#conn.commit()

## We can also close the cursor if we are done with it
#c.close()

## Create table
#c.execute('''create table stocks
#(date text, trans text, symbol text,
# qty real, price real)''')

## Insert a row of data
#c.execute("""insert into stocks
#          values ('2006-01-05','BUY','RHAT',100,35.14)""")

## Save (commit) the changes
#conn.commit()


## patterns=['*.JPG','*.jpg','*.JPEG','*.jpeg']):
#def clean_tags(dir_or_file=DBG_PHOTOS_PATH, patterns=['*.[Jj][Pp][Gg]','*.[Jj][Pp][Ee][Gg]'] ):
#	if os.path.isfile(dir_or_file):
#		return
##	if not path:
##		dir_or_file = DBG_PHOTOS_PATH
#	os.path.isfile
#	import fnmatch
#	for base_dir, dirs, files in os.walk(dir_or_file):
#		for pat in patterns
#			for filename in fnmatch.filter(files, pat ):
#				clean_tags( os.path.join(base_dir, filename) )

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

