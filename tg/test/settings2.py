"""Zinnia Blog Settings"""
import os
gettext = lambda s: s

DEBUG = True

DATABASES = { 'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'apps/zinnia_blog/demo.db',
        } }

USE_I18N = True
USE_L10N = True

LANGUAGES = (('en', gettext('English')),
             ('fr', gettext('French')),
             ('de', gettext('German')),
             ('es', gettext('Spanish')),
             ('it', gettext('Italian')),
             ('nl', gettext('Dutch')),
             ('hu', gettext('Hungarian')),
             ('cs', gettext('Czech')),
             ('sk', gettext('Slovak')),
             ('ru', gettext('Russian')),
             ('pl', gettext('Polish')),
             ('eu', gettext('Basque')),
             ('hr_HR', gettext('Croatian')),
             ('pt_BR', gettext('Brazilian Portuguese')),
             ('zh_CN', gettext('Simplified Chinese')),)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

#ROOT_URLCONF = 'zinnia_blog.urls'


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'zinnia.context_processors.version',
    "zinnia_blog.context_processors.get_site_name",
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sitemaps',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'mptt',
    'zinnia',
    'tagging',
    'django_xmlrpc',
    )


#from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
#XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS