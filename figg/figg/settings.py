import sys, os
import manage

# Django settings for figg project.

SITE_ROOT = os.path.dirname(os.path.realpath(manage.__file__))
print "site root %s" % SITE_ROOT
DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEST = "test" in sys.argv
TWITTER_CONSUMER_TOKEN = "6s2rtDUZPjVaLrId06uHw"
TWITTER_CONSUMER_SECRET = "dBKgcsu4INJDYtFTPN8k0bBTQBuGrAKQZHeW8XXk"
ROOT_DIR = os.path.join(os.path.dirname(__file__))
USER_TZ = True


ADMINS = (
    ('00fredkingham', 'fredkingham@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',#'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        #'ENGINE': 'django.db.backends.', 'sqlite3' # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'figg_db',
        'TEST_NAME': 'figg_test_db',
        'USER': 'power_user',                      # Not used with sqlite3.
        'PASSWORD': 'IAmNotAT1000',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

if DEBUG:
    HOME = "http://127.0.0.1:8000"
else:    
    HOME = "http://fi.gg"

if TEST:
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
else:
    EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'fred@fi.gg'
    EMAIL_HOST_PASSWORD = 'IAmNotAT1000'
    EMAIL_PORT = 587

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Dublin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '%s/../umedia/' % SITE_ROOT

if DEBUG:
    HOME = "http://127.0.0.1:8000"
else:    
    HOME = "http://fi.gg"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/umedia/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/../media/' % SITE_ROOT

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    "%s/main/static" % SITE_ROOT,
    "%s/mainPage/static" % SITE_ROOT,
    "%s/twitter/static" % SITE_ROOT,
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'f95p1uf3^n*+y7l1c^wt4z)rgh!2opheno((7u9y9+8i27sx04'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'figg.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'figg.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, "main/templates"),
    os.path.join(SITE_ROOT, 'mainPage/templates'),
    os.path.join(SITE_ROOT, 'notifications/templates'),
    os.path.join(SITE_ROOT, 'twitter/templates'),
    os.path.join(SITE_ROOT, 'figg_calendar/templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'main',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'mainPage',
    'figg_calendar',
    'common',
    'django.contrib.comments', 
    'social_auth',
    'twitter',
    'standalone',
    'notifications',
    'utils',
    'tweepy',
    'imagekit',
    'web_crawler',
    'kombu.transport.django',  
    'djcelery', 
)

BROKER_URL = "redis://localhost"

import djcelery  
djcelery.setup_loader()

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },

        'console':{
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(SITE_ROOT), 'logs/figg_main.log'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
        'debug_logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(SITE_ROOT), 'logs/figg_main.log'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
        'notificationLog': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(SITE_ROOT), 'logs/figg_notifications.log'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
        'tweetImporter': {
            'level':'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(SITE_ROOT), 'logs/tweet_importer.log'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'mainPage': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True
        },
        'figg_calendar': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True
        },
        'social_auth': {
            'handlers': ['console', 'debug_logfile'],
            'level': 'DEBUG',
            'propagate': True
        },

        'notifications':{
            'handlers': ['console', 'notificationLog'],
            'level': 'INFO',
            'propagate': True
        },
        'notifications':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'twitter':{
            'handlers': ['console', 'tweetImporter'],
            'level': 'INFO',
            'propagate': True
        },
        'twitter':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'web_crawler':{
            'handlers': ['console', 'tweetImporter'],
            'level': 'INFO',
            'propagate': True
        },
        'web_crawler':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}


AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.contrib.flickr.FlickrBackend',
    'social_auth.backends.OpenIDBackend',
    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    'django.contrib.auth.backends.ModelBackend',
)

DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False
}

LOGIN_URL          = '/login/twitter/'
LOGIN_REDIRECT_URL = '/login/twitter/'
LOGIN_ERROR_URL    = '/login/twitter/'
# SOCIAL_AUTH_ENABLED_BACKENDS = ('twitter')
LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = True

if TEST:
    QUEUE_NAME = "test"
else:
    QUEUE_NAME = "processes"

try:
    from local_settings import *
except:
    pass
