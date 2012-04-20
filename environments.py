from fabric.api import env, settings, run
from contextlib import contextmanager as _contextmanager
from time import gmtime, strftime
from fabric.api import *
from fabutils.vagrant import get_vagrant_params


@_contextmanager
def common():
	env.debug = False
	yield
	env.project_name = '{{ app_name|slugify }}'
	env.project_title = '{{ app_name }}'
	env.db_name = env.project_name
	env.project_root = '/home/%s/sites/%s' % (env.user, env.project_name)
	env.python_path = "/home/%s/.virtualenvs/%s" % (env.user, env.project_name)
	env.uwsgi_port = 9000
	env.use_ssh_config = True
	env.branch = "master"
	env.release = strftime('%Y%m%d%H%M%S', gmtime())


def dev():
	vp = get_vagrant_params()

	with common():
		env.user                = vp.get('user')
		env.domain              = 'localhost'
		env.hosts               = ['%s:%s' % (vp.get('host'), vp.get('port'))]
		env.key_filename        = vp.get('identity_file')
		env.debug               = True
		env.disable_knows_hosts = True


# TODO: You edit this
def production():
	with common():
		env.user = ''
		env.hosts = []
		env.domain = ''
