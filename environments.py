from fabric.api import env, settings, run
from contextlib import contextmanager as _contextmanager
from time import gmtime, strftime
from fabric.api import *


@_contextmanager
def common():
	yield
	env.project_name = 'project-name'
	env.db_name = env.project_name
	env.project_root = '/home/%s/sites/%s' % (env.user, env.project_name)
	env.python_path = "/home/%s/.virtualenvs/%s" % (env.user, env.project_name)
	env.uwsgi_port = 8000
	env.use_ssh_config = True
	env.branch = "master"
	env.debug = False
	env.release = strftime('%Y%m%d%H%M%S', gmtime())


def dev():
	with common():
		env.user = 'vagrant'
		env.hosts = ['127.0.0.1:2200']
		env.domain = 'localhost'
		env.settings_class = 'production'
		# use vagrant ssh key
		result = local('vagrant ssh-config | grep IdentityFile', capture=True)
		env.key_filename = result.split()[1]
		env.debug = True
