from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists, append, upload_template, sed
from fabric.contrib.project import rsync_project
from fabric.api import *
from fabric.colors import *
from environments import *
from pprint import pprint

import fabutils
from fabutils.db import postgres
from fabutils.distros import ubuntu


def bootstrap():
	fabutils.prepare_server()
	ubuntu.install_distro_deps()
	ubuntu.init_nginx()
	fabutils.install_python()
	postgres.init_db()
	deploy()


def deploy():
	fabutils.archive_current()
	fabutils.upload_current()
	configure()
	fabutils.set_permissions()
	fabutils.migrate()
	#rebuild_index()
	fabutils.collect_static()
	#compress_js_and_css()
	#prune_releases()
	fabutils.link_current()
	restart_server()
	fabutils.cleanup()


def configure():
	fabutils.build_python_deps()
	fabutils.upload_settings()


def start_server():
	"""Start all processes necessary to the site."""
	sudo("nginx")
	sudo("start %s" % env.project_name)


def stop_server():
	"""Stop all processes related to the site."""
	try:
		sudo("nginx -s stop")
	except:
		pass

	try:
		sudo("stop %s" % env.project_name)
	except:
		pass


def restart_server():
	"""Restart all processes necessary to the site."""
	stop_server()
	start_server()


def run_dev_server():
	"""Run local dev server at localhost:8000"""
	with cd('$VAGRANT_ROOT'):
		run('chmod +x manage.py')
		run('workon %s && ./manage.py runserver_plus 0.0.0.0:8000' % env.project_name)


def sync_db(from_env, to_env):
	"""Sync DB + uploads folder from one env to another env"""
	postgres.sync_psql_db(from_env, to_env)


def migrate_app(app_name, initial=""):
	fabutils.migrate_app(app_name, bool(initial))
