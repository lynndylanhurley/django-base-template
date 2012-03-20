from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists, append
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


def bootstrap():
	# make sure we can even do this
	append("~/.bash_profile", "export WORKON_HOME=$HOME/.virtualenvs")
	append("~/.bash_profile", "export PYTHONPATH=settings.local")
	append("~/.bash_profile", "source /usr/local/bin/virtualenvwrapper.sh")

	# make directory skeleton
	run("mkdir -p ~/sites/%s/releases" % env.project_name)
	run("mkdir -p ~/logs/nginx")
	run("mkdir -p ~/logs/uwsgi")
	run("mkdir -p ~/bin")
	sudo("rm -rf ~/.virtualenvs")

	# install deps
	sudo("apt-get update")
	sudo("apt-get upgrade")
	sudo("apt-get install python-software-properties")
	#sudo("add-apt-repository ppa:uwsgi/release")
	sudo("apt-get update")
	sudo("apt-get install nginx")
	sudo("apt-get install postgresql")
	sudo("apt-get install python-pip python-dev build-essential libpq-dev python-virtualenv")

	# python deps
	run("pip install -U pip")
	run("pip install -U virtualenv virtualenvwrapper")

	set_permissions()
	run("mkvirtualenv --clear --no-site-packages --distribute %s" % env.project_name)

	init_db()
	deploy()


def set_permissions():
	"""Reset permissions on all related files."""
	with current_env():
		sudo("chown -R %s:%s /home/%s/.virtualenvs" % (env.user, env.user, env.user))
		sudo("chown -R %s:%s %s" % (env.user, env.user, env.project_root))


def deploy():
	archive_current()
	upload_current()
	configure()
	#rebuild_index()
	#collect_static()
	#compress_js_and_css()
	#prune_releases()
	#link_current()
	#restart_server()


def archive_current():
	"""Create an archive from the latest git commit. The branch is specified
	in the 'env' variable in from the environments module."""

	print(white("-->Using branch %s" % env.branch))
	local('mkdir -p /tmp/%s' % env.release)
	local('git archive %s deploy | tar -x -C /tmp/%s' % (env.branch, env.release))


def upload_current():
	"""Upload most recent changes into new release directory."""
	print(white("Creating new release on production"))

	with cd( "%s/releases" % env.project_root ):
		run("mkdir %s" % env.release)
		# copy previous env.release to new dir for rsync
		if exists("current"):
			run("cp -R current/* %s" % env.release)

		# rsync local tmp archive with previous release copy
		rsync_project(remote_dir='%s/releases/%s' % (env.project_root, env.release), local_dir='/tmp/%s/deploy/' % env.release, delete=True)


def configure():
	set_permissions()
	build_deps()
	migrate()
	#upload_settings()


def build_deps():
	with current_project():
		sudo('pip install -r requirements.txt')


def migrate():
	with current_project():
		run( './manage.py syncdb' )
		run( './manage.py migrate --all --delete-ghost-migrations' )


def init_db():
	try:
		sudo("sudo -u postgres createuser -D -A -P %s" % env.user)
	except:
		pass
	try:
		sudo("sudo -u postgres createdb -O %s %s" % (env.user, env.db_name))
	except:
		pass
	append("/etc/postgresql/8.4/main/pg_hba.conf", "local all postgres ident sameuser", use_sudo=True)


def upload_settings():
	upload_template(filename='deploy/conf/nginx.conf', destination='/etc/nginx/sites_available/%s' % env.project_name, context=env, backup=False, use_sudo=True)
	upload_template(filename='deploy/conf/upstart.conf', destination='/etc/init/%s.conf' % env.project_name, context=env, backup=False, use_sudo=True)
	upload_template(filename='deploy/conf/uwsgi.ini', destination='%s/uwsgi.ini' % env.project_root, context=env, backup=False, use_sudo=True)
	upload_template(filename='deploy/conf/local.py', destination='%s/current/local.py' % env.project_root, context=env, backup=False, use_sudo=False)

	sudo("ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s" % (env.project_name, env.project_name))


def collect_static(release):
	print(white("Collecting static files"))
	with current_project(release):
		sudo('rm -rf static/*')
		run('./manage.py collectstatic --noinput')


def fetch_requirements():
	with current_project():
		run("pip install -r requirements.txt")


def link_current(release):
	with current_project():
		if exists("current"):
			run ('unlink current')

		run("ln -sf %s/releases/%s %s/current" % (env.project_root, env.release, env.project_root))


def prune_releases():
	"""Remove all but the 5 most recent release directories."""
	files = get_releases()
	del files[-5:]

	print white("removing folders: %r" % files)

	for f in files:
		sudo("rm -rf %s" % f)


def start_site():
	"""Start all processes necessary to the site."""
	sudo("nginx")


def restart_site():
	"""Restart all processes necessary to the site."""
	sudo("nginx -s reload")


def stop_site():
	"""Stop all processes related to the site."""
	try:
		sudo("nginx -s stop")
	except:
		pass


def get_releases():
	"""Return array of release directories with names that start with a number."""
	files = run('ls -a %s/releases' % env.project_root)
	files = re.split("[\s]+", files)
	files = filter(lambda f: re.match("^[\d]+", f), files)
	files = map(lambda f: "%s/releases/%s" % (env.project_root, f), files)
	files.sort()
	return files
