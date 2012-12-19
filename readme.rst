opbeat
************

opbeat is a command line client for `Opbeat <https://opbeat.com/>`_. It provides
access to the Opbeat API through the command line.


.. image:: https://secure.travis-ci.org/opbeat/opbeatcli.png?branch=master
   :target: http://travis-ci.org/opbeat/opbeatcli


Commands
===============

opbeat allows you to run different commands. For most commands you need to be authenticated
with Opbeat. The following arguments are valid for all commands:

	::
	
	-s SERVER, --server SERVER

Override server. Can be set with environment variable OPBEAT_SERVER

	::
	
	-t ACCESS_TOKEN, --access-token ACCESS_TOKEN

Set access token. Can be set with environment variable OPBEAT_ACCESS_TOKEN.

	::

	 --verbose

Increase output verbosity

Login
-----------

	::
	
		opbeat [-s SERVER] login

Logs into the Opbeat platform and saves credentials on the machine.

Deployment
-------------

	::
		
		opbeat [-t ACCESS_TOKEN] [-s SERVER] deployment -p PROJECT_ID [-d DIRECTORY] [-m MODULE_NAME]

Notifies Opbeat about version of installed software. By default, it will collect all available python modules.

It will also check if the current working directory (override with ``-d``) is a
Subversion, Git or Mercurial repository. If this is the case, the most recent
revision/commit hash is sent, as module ``MODULE_NAME``. Default module name is 
``_repository``.
