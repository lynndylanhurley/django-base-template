from fabric.api import *
import re


def clean_known_hosts():
	"""Known hosts become problematic after having shelled into multiple vagrant instances.
	Remove any localhost entries (127.0.0.1)."""

	local("sed 's/^[^1]*127\.0\.0\.1[^$]*$//' ~/.ssh/known_hosts | sed '/^$/d' >~/.ssh/known_hosts")


def get_ssh_param(params, key):
	return filter(lambda s: re.search(r'^%s' % key, s), params)[0].split()[1]


def get_vagrant_params():
	"""Parse vagrant's ssh-config for given key's value
	This is helpful when dealing with multiple vagrant instances."""

	clean_known_hosts()
	result = local('vagrant ssh-config', capture=True)
	lines = result.split('\n')
	lines = [l.strip() for l in lines]

	ret = {
		'user': get_ssh_param(lines, 'User'),
		'host': get_ssh_param(lines, 'HostName'),
		'port': get_ssh_param(lines, 'Port'),
		'identity_file': get_ssh_param(lines, 'IdentityFile')
	}

	return ret
