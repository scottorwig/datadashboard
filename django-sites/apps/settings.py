# Django settings for django-sites project.
import ConfigParser
import sys

config_file = '/home/data_server.cfg'

sys.path.append('/var/www/django-sites/apps/boevacancy')

config = ConfigParser.ConfigParser()
config.read(config_file)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # (config.get('django','admin_name'), config.get('django','admin_email')),
)

MANAGERS = ADMINS

DATABASE_ENGINE = config.get('django','database_engine')
DATABASE_NAME = config.get('django','database_name')
DATABASE_USER = config.get('django','database_user')
DATABASE_PASSWORD = config.get('django','database_password')
DATABASE_HOST = config.get('django','database_host')                   # Set to empty string for localhost.
DATABASE_PORT = config.get('django','database_port')                    # Set to empty string for default.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = config.get('django','secret_key')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'apps.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
)

TEMPLATE_DIRS = (
    'templates',
    '/var/www/django-sites/apps/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'apps.disciplineform',
    'apps.datadashboard',
)

EMAIL_HOST = config.get('django','email_host')
EMAIL_HOST_USER = config.get('django','email_host_user')
EMAIL_HOST_PASSWORD = config.get('django','email_host_password')
EMAIL_PORT = config.get('django','email_port')
EMAIL_USE_TLS = config.getboolean('django','email_use_tls')