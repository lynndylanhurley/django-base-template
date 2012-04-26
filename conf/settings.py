from common_settings import *
from path import path

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': '%(project_name)s',
		'USER': '%(user)s',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/tmp/memcached.sock',
    }
}

DEBUG = %(debug)s
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

MEDIA_ROOT = path(__file__).abspath().dirname().dirname() / 'uploads'
