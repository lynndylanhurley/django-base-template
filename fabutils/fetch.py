from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists, append, upload_template, sed
from fabric.contrib.project import rsync_project
from fabric.api import *
from fabric.colors import *
from environments import *
#from pprint import pprint
#import urllib2

@_contextmanager
def vagrant_env():
	with cd("$VAGRANT_ROOT"):
		with prefix('workon %s' % env.project_name):
			yield


MEDIA_ROOT = 'assets/'

HTML5BP_URL = "http://github.com/h5bp/html5-boilerplate/zipball/v3.0.2stripped"
BOOTSTRAP_BIN_URL = "http://twitter.github.com/bootstrap/assets/bootstrap.zip"
BOOTSTRAP_SRC_URL = "https://github.com/twitter/bootstrap/zipball/master"

def fetch_file(item):
	url, fname = item
	with vagrant_env():
		run("curl -o %s%s %s" % (MEDIA_ROOT, fname, url))


def fetch_files():
	map(lambda f: fetch_file(f), FILES)


def fetch_boilerplate():
	with vagrant_env():
		fname = '/tmp/html5bp.zip'
		run("wget %s -O %s" % (HTML5BP_URL, fname))
		with cd(MEDIA_ROOT):
			run('rm -rf h5bp*')
			run('unzip %s' % fname)
			run('rsync -a h5bp*/* . --remove-sent-files --ignore-existing --whole-file')
			run('rm -rf h5bp*')

		run("rm -rf %s" % fname)

def fetch_bootstrap():
	with vagrant_env():
		run('mkdir -p assets/less')
		bin_fname = '/tmp/bin-bootstrap.zip'
		src_fname = '/tmp/src-bootstrap.zip'

		run("wget %s -O %s" % (BOOTSTRAP_SRC_URL, src_fname))
		run("wget %s -O %s" % (BOOTSTRAP_BIN_URL, bin_fname))

		with cd(MEDIA_ROOT):
			run('rm -rf twitter-bootstrap*')
			run('rm -rf bootstrap*')

			run('unzip -u %s' % src_fname)
			run('unzip -u %s' % bin_fname)

			run('rsync -a twitter-bootstrap*/less/* less')
			run('rsync -a bootstrap*/js/* js/libs')

			run('rm -rf bootstrap*')
			run('rm -rf twitter-bootstrap*')

		run("rm -rf %s" % src_fname)
		run("rm -rf %s" % bin_fname)

