#!/usr/bin/env python
# Filename: gtkutil.py
"""Utilities for manipulating GUI objects using GTK3 (GObject) -- needs Quartz on Mac OSX, Gnome/X11 on Linux

Examples:

>>> os.path.isfile(get_background_image_path())
True
"""

# tg
import get_paths

get_paths.stripit = True

# gnome
from gi.repository import Gio  # , Gtk
gsettings = Gio.Settings.new('org.gnome.desktop.background')


def set_background_image_path(path):
    """Set the desktop background image to the path specified"""
    gsettings.set_string('picture-uri', "file://" + get_paths.make_uri(path))


def get_background_image_path():
    """Retrieve the path of the desktop background image currently displayed

    >>> os.path.isfile(get_background_image_path())
    True"""
    print gsettings.get_string('picture-uri')
    return get_paths.normalize_path(gsettings.get_string('picture-uri'))
get_background_path = get_background_image_path
get_desktop_background_path = get_background_image_path


def copy_over_background_image(path):
    """Copy an image file to the path used for the desktop background image"""
    dest = get_background_image_path()
    shutil.copy(path, dest)


def image_path_from_gnome(uri=False):
    """Set the desktop background image to the path specified"""
    uri = gsettings.get_string('picture-uri')
    if uri:
        return uri
    from tagim.tg.get_paths import get_path
    return get_paths.get_path(uri, stripit=True, quote_char='')


# def set_image_path(filename):
#     print filename
#     if filename:
#         output = subprocess.Popen(
#             ["gconftool-2",'--type','str','--set','/desktop/gnome/background/picture_filename',str(filename)])
#     else:
#         output = subprocess.Popen(
#             ["gconftool-2"               ,'--get','/desktop/gnome/background/picture_filename'], stdout=subprocess.PIPE).communicate()[0]
#     return output


