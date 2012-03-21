from fabric.api import env, settings, run
from contextlib import contextmanager as _contextmanager
from time import gmtime, strftime
from fabric.api import *


@_contextmanager
def common():
	env.debug = False
	yield
	env.project_name = 'project-name'
	env.project_title = 'Project Title'
	env.db_name = env.project_name
	env.project_root = '/home/%s/sites/%s' % (env.user, env.project_name)
	env.python_path = "/home/%s/.virtualenvs/%s" % (env.user, env.project_name)
	env.uwsgi_port = 9000
	env.use_ssh_config = True
	env.branch = "master"
	env.release = strftime('%Y%m%d%H%M%S', gmtime())


def get_vagrant_param(key):
	"""Parse vagrant's ssh-config for given key's value"""
	result = local('vagrant ssh-config | grep %s' % key, capture=True)
	return result.split()[1]


def dev():
	with common():
		env.user         = get_vagrant_param('User')
		env.domain       = 'localhost'
		env.hosts        = ['%s:%s' % (get_vagrant_param('HostName'), get_vagrant_param('Port'))]
		env.key_filename = get_vagrant_param('IdentityFile')
		env.debug        = True


# TODO: You edit this
def production():
	with common():
		env.user = ''
		env.hosts = []
		env.domain = ''
