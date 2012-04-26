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


def sync_psql_db(from_env_str, to_env_str):
	"""Sync local postgres db to remote server"""

	from_env = getattr(environments, from_env_str)
	to_env = getattr(environments, to_env_str)

	# work on origin server
	from_env()

	env.host_string = env.get('hosts')[0]
	fname = "%s_%s.sql" % ( env.get('project_name'), strftime('%Y%m%d%H%M%S', gmtime() ))
	run( "uname -r")
	run( "pg_dump --file=/var/tmp/%s --format=p %s" % ( fname, env.get('project_name') ))
	local( "scp %s@%s:/var/tmp/%s /var/tmp/%s" % ( env.get('user'), env.get('hosts')[0], fname, fname) )

	if env.get('key_filename'):
		local('rsync -avh -e "ssh -i %s -p %s" %s@%s:%s/uploads/* /tmp/%s-uploads' % (env.get('key_filename'), env.get('hosts')[0].split(":")[1], env.get('user'), env.get('hosts')[0].split(":")[0], env.get('project_root'), env.get('project_name')) )
	else:
		local('rsync -avh %s@%s:%s/uploads/* /tmp/%s-uploads' % (env.get('user'), env.get('hosts')[0], env.get('project_root'), env.get('project_name')) )

	# work on destination server
	to_env()

	env.host_string = env.get('hosts')[0]
	put("/var/tmp/%s" % fname, "/var/tmp/%s" % fname )
	try:
		run( "dropdb %s" % env.get('project_name'))
	except:
		pass

	sudo("sudo -u postgres createdb -O %s %s" % (env.get('user'), env.get('db_name')))
	run( "psql -d %s -f /var/tmp/%s" % ( env.get('project_name'), fname ))

	if env.get('key_filename'):
		local('rsync -avh -e "ssh -i %s -p %s" /tmp/%s-uploads/* %s@%s:%s/uploads' % (env.get('key_filename'), env.get('hosts')[0].split(':')[1], env.get('project_name'), env.get('user'), env.get('hosts')[0].split(':')[0], env.get('project_root')) )
	else:
		local("rsync -avh /tmp/%s-uploads/* %s@%s:%s/uploads" % (env.get('project_name'), env.get('user'), env.get('hosts')[0], env.get('project_root')) )

