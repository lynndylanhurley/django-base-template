from settings import *

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

GRAPPELLI_ADMIN_TITLE = '%(project_title)'
