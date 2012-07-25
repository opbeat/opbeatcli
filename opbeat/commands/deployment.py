from opbeat.command import CommandBase
from opbeat.runner import build_client
from opbeat.conf import defaults
# import pkg_resources
from pip.vcs import vcs
from pip.util import get_installed_distributions
from pip.vcs import git, mercurial
import sys

import os
import socket

VCS_NAME_MAP = {
	'git':'git',
	'hg':'mercurial',
	'svn':'subversion'
}

SERVER_NAME = socket.gethostname()


_VERSION_CACHE ={}
def get_versions_from_installed(module_list=None):
	if not module_list:
		return {}

	ext_module_list = set()
	for m in module_list:
		parts = m.split('.')
		ext_module_list.update('.'.join(parts[:idx]) for idx in xrange(1, len(parts) + 1))

	versions = {}
	for module_name in ext_module_list:
		if module_name not in _VERSION_CACHE:
			try:
				__import__(module_name)
			except ImportError:
				continue
			app = sys.modules[module_name]
			if hasattr(app, 'get_version'):
				get_version = app.get_version
				if callable(get_version):
					version = get_version()
				else:
					version = get_version
			elif hasattr(app, 'VERSION'):
				version = app.VERSION
			elif hasattr(app, '__version__'):
				version = app.__version__
			elif pkg_resources:
				# pull version from pkg_resources if distro exists
				try:
					version = pkg_resources.get_distribution(module_name).version
				except pkg_resources.DistributionNotFound:
					version = None
			else:
				version = None

			if isinstance(version, (list, tuple)):
				version = '.'.join(str(o) for o in version)
			_VERSION_CACHE[module_name] = version
		else:
			version = _VERSION_CACHE[module_name]
		if version is None:
			continue
		versions[module_name] = version

	return versions

def get_version_from_distributions(distributions):
	result = {}
	for d in distributions:
		
		result[d.key] = {'module':d.key}

		if d.has_version():
			result[d.key]['version'] = d.version

		vcs_version = get_version_from_location(d.location)
		if vcs_version:
			result[d.key]['vcs'] = vcs_version

	return result

# Recursively try to find vcs.
def get_version_from_location(location):
	backend_cls = vcs.get_backend_from_location(location)
	if backend_cls:
		backend = backend_cls()
		url, rev = backend.get_info(location)

		vcs_type = VCS_NAME_MAP[backend_cls.name]

		return {'type': vcs_type,'revision':rev, 'repository':url}
	else:
		head, tail = os.path.split(location)
		if head and head != '/': ## TODO: Support windows
			return get_version_from_location(head)
		else:
			return None

def get_repository_info(directory=None):
	if not directory:
		directory = os.getcwd()
	cwd_rev_info = get_version_from_location(directory)
	return cwd_rev_info

def split_netloc(netloc, path):
	if '@' in netloc:
		_, netloc = netloc.split('@')

	if ':' in netloc:
		host, netlocpath = netloc.split(':')
		path = "/" + netlocpath + path
	else:
		host = netloc

	return host, path

def annotate_url_with_ssh_config_info(url):
	from os.path import expanduser
	from urlparse import urlsplit, urlunsplit
	from ssh.config import SSHConfig

	def hostinfo(host, config, username=None):
		hive = config.lookup(host)
		if 'hostname' in hive:
			host = hive['hostname']
		if 'user' in hive:
			host = '%s@%s' % (hive['user'], host)
		elif username:
			host = '%s@%s' % (username, host)

		if 'port' in hive:
			host = '%s:%s' % (host, hive['port'])
		return host

	try:
		config_file = file(expanduser('~/.ssh/config'))
	except IOError, ex:
		logger.debug(ex)
	else:
		config = SSHConfig()
		config.parse(config_file)
		
		parsed_url = urlsplit(url)
		if not parsed_url.hostname:
			# schema missing
			parsed_url = urlsplit("ssh://" + url)

			if parsed_url.path:
				path = parsed_url.path
		
				# if '@' in host:
				# 	user, host = host.split('@')

				# if ':' in host:
				# 	host, path = host.split(':')

				# lookup = config.lookup(host)
				parsed_asdict = parsed_url._asdict()
				
				host, path = split_netloc(parsed_url.netloc, path)

				netloc = hostinfo(host, config, parsed_url.username, parsed_url.password)

				# parsed_asdict['netloc'] = 
				parsed_asdict['path'] = path or parsed_url.path
				# parsed_asdict['username'] = user or parsed_url.username

			return urlunsplit(parsed_asdict.values())
	return url


def send_deployment_info(client, include_paths = None, directory=None):
	if include_paths:
		versions = get_versions_from_installed(include_paths)
		versions = dict([(module, {'module':module, 'version':version}) for module, version in versions.items()])
	else:
		versions = {}

	dist_versions = get_version_from_distributions(get_installed_distributions())
	versions.update(dist_versions)

	rep_info = get_repository_info(directory)

	if rep_info:
		versions['_repository'] = {'module':'_repository', 'vcs':rep_info}

	# Versions are returned as a dict of "module":"version"
	# We convert it here. Just ditch the keys.
	list_versions = [v for k,v in versions.items()]

	server_name = SERVER_NAME

	data = {'server_name':server_name, 'releases':list_versions}

	url = client.server+(defaults.DEPLOYMENT_API_PATH.format(client.project_id))
	
	# client.build_msg(data=data)

	return client.send(url=url,data=data)


class SendDeploymentCommand(CommandBase):
	name = "deployment"
	description = "Sends deployment info ASAP."

	def add_args(self):
		self.parser.add_argument('-p','--project-id', help='Use this project id.', dest="project_id", required=True)
		self.parser.add_argument('-i','--include-path', help='Search this directory.', dest="include_paths")
		self.parser.add_argument('-d','--directory', help='Take repository information from this directory.', dest="directory", default=os.getcwd())
		self.parser.add_argument('-m','--module-name', help='Use this as the module name.', default="_repository")

	def run(self, args):
		self.logger.info('Sending deployment info...')
		self.logger.info("Using directory: %s", args.directory)
		client = build_client(project_id = args.project_id, server = args.server, access_token = args.access_token)

		send_deployment_info(client, args.include_paths, args.directory)
		# if len(args) > 0:
		# 	directory = os.path.abspath(args[0])
		# 	self.logger.debug("Using directory: %s", directory)
		# else:
		# 	directory = None

		# client.send_deployment_info(directory=args.directory)
		# self.logger.info('success!')

command = SendDeploymentCommand

