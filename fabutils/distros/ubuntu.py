from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists, append, upload_template, sed
from fabric.contrib.project import rsync_project
from fabric.api import *
from fabric.colors import *
from environments import *
from pprint import pprint

def install_distro_deps():
	# install deps
	sudo("apt-get update")
	#sudo("apt-get upgrade")
	sudo("apt-get install python-software-properties")
	sudo("add-apt-repository ppa:nginx/stable")
	sudo("apt-get update")
	sudo("apt-get install nginx libpq-dev postgresql vim curl")

def init_nginx():
	sed("/etc/nginx/nginx.conf", "user www-data;", "user %s;" % env.user, use_sudo=True)
	append("/etc/nginx/nginx.conf", "user vagrant;", use_sudo=True)
