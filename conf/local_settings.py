from settings import *
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

DEBUG = %(debug)s
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

GRAPPELLI_ADMIN_TITLE = '%(project_title)s'
MEDIA_ROOT = path(__file__).abspath().dirname() / 'uploads'
