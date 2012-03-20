import os, sys
from settings import *

DEBUG = True
TEMPLATE_DEBUG = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, "uploads")

MIDDLEWARE_CLASSES += (
  'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'project-name',
		'USER': 'vagrant',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
  'INTERCEPT_REDIRECTS' : False
}

INSTALLED_APPS += (
	'debug_toolbar',
)


# fast db for testing
if 'test' in sys.argv:
	DATABASES['default'] = {'ENGINE': 'sqlite3'}


# easy email testing
EMAIL_PORT    = 1025
EMAIL_HOST    = 'localhost'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

COMPRESS_ENABLED = False
