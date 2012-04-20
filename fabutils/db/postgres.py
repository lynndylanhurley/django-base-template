from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists, append, upload_template, sed
from fabric.contrib.project import rsync_project
from fabric.api import *
from fabric.colors import *
from environments import *
from pprint import pprint


def init_db():
	try:
		sudo("sudo -u postgres createuser -D -A -P %s" % env.user)
	except:
		pass
	try:
		sudo("sudo -u postgres createdb -O %s %s" % (env.user, env.db_name))
	except:
		pass
	append("/etc/postgresql/*/main/pg_hba.conf", "local all all ident", use_sudo=True)
