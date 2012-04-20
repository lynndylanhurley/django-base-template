from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists, append, upload_template, sed
from fabric.contrib.project import rsync_project
from fabric.api import *
from fabric.colors import *
from environments import *
from pprint import pprint

@_contextmanager
def current_env():
	with cd("%s" % env.project_root):
		with prefix('workon %s' % env.project_name):
			yield

@_contextmanager
def current_project():
	with current_env():
		with cd("releases/%s" % env.release):
			yield

def prepare_server():
	# for my sanity
	append("~/.bash_profile", "alias l=ls")
	append("~/.bash_profile", "alias ll='ls -al'")
	append("~/.bash_profile", "export PROJECT_NAME=%s" % env.project_name)
	append("~/.bash_profile", "export VAGRANT_ROOT=/vagrant/deploy")

	# make directory skeleton
	run("mkdir -p ~/sites/%s/releases" % env.project_name)
	run("mkdir -p ~/sites/%s/uploads" % env.project_name)
	run("mkdir -p ~/logs/nginx")
	run("mkdir -p ~/logs/uwsgi")
	run("mkdir -p ~/bin")


def install_python():
	# install python + deps
	run("curl -kL http://xrl.us/pythonbrewinstall | bash")
	append("~/.bash_profile", "[[ -s $HOME/.pythonbrew/etc/bashrc ]] && source $HOME/.pythonbrew/etc/bashrc")
	run("pythonbrew install 2.7.2")
	run("pythonbrew switch 2.7.2")

	run("pip install -U pip")
	run("pip install -U virtualenv virtualenvwrapper")
	append("~/.bash_profile",
	"""
if [ $USER == %s ]; then
	export WORKON_HOME=$HOME/.virtualenvs
	source $PATH_PYTHONBREW_CURRENT/virtualenvwrapper.sh
fi
	""" % env.user)

	run("mkvirtualenv --clear --no-site-packages --distribute %s" % env.project_name)


def archive_current():
	"""Create an archive from the latest git commit. The branch is specified
	in the 'env' variable in from the environments module."""

	print(white("-->Using branch %s" % env.branch))
	local('mkdir -p /tmp/%s' % env.release)
	local('git archive %s deploy | tar -x -C /tmp/%s' % (env.branch, env.release))


def upload_current():
	"""Upload most recent changes into new release directory."""
	print(white("Creating new release on production"))

	with cd( env.project_root ):
		run("mkdir -p releases/%s" % env.release)

		if exists("current"):
			run("cp -R current/* releases/%s" % env.release)

	rsync_project(remote_dir='%s/releases/%s' % (env.project_root, env.release), local_dir='/tmp/%s/deploy/' % env.release, delete=True)


def migrate():
	with current_project():
		run( './manage.py syncdb' )
		run( './manage.py migrate --all --delete-ghost-migrations' )


def collect_static():
	print(white("Collecting static files"))
	with current_project():
		run('rm -rf static/*')
		run('./manage.py collectstatic --noinput')


def build_python_deps():
	with current_project():
		run("pip install -r requirements.txt")


def upload_settings():
	#upload templates
	upload_template(filename='conf/nginx.conf', destination='/etc/nginx/sites-available/%s' % env.project_name, context=env, backup=False, use_sudo=True)
	upload_template(filename='conf/upstart.conf', destination='/etc/init/%s.conf' % env.project_name, context=env, backup=False, use_sudo=True)
	upload_template(filename='conf/uwsgi.ini', destination='%s' % env.project_root, context=env, backup=False, use_sudo=True)
	upload_template(filename='conf/settings.py', destination='%s/releases/%s' % (env.project_root, env.release), context=env, backup=False, use_sudo=False)

	#re-link nginx conf
	if exists("/etc/nginx/sites-enabled/%s" % env.project_name):
		sudo("unlink /etc/nginx/sites-enabled/%s" % env.project_name)
	if exists("/etc/nginx/sites-enabled/default"):
		sudo("unlink /etc/nginx/sites-enabled/default")
	sudo("ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s" % (env.project_name, env.project_name))



def link_current():
	with cd(env.project_root):
		if exists("current"):
			run ('unlink current')

		run("ln -s %s/releases/%s %s/current" % (env.project_root, env.release, env.project_root))


def prune_releases():
	"""Remove all but the 5 most recent release directories."""
	files = get_releases()
	del files[-5:]

	print white("removing folders: %r" % files)

	for f in files:
		run("rm -rf %s" % f)


def get_releases():
	"""Return array of release directories with names that start with a number."""
	files = run('ls -a %s/releases' % env.project_root)
	files = re.split("[\s]+", files)
	files = filter(lambda f: re.match("^[\d]+", f), files)
	files = map(lambda f: "%s/releases/%s" % (env.project_root, f), files)
	files.sort()
	return files


def cleanup():
	"""Just to be sure."""
	with current_project():
		run('rm -rf *.pyc')
