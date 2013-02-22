#!/usr/bin/env python
"""
opbeatcli
=========

opbeatcli is a command line client for `Opbeat <https://opbeat.com/>`_. It provides
access to the Opbeat API through the command line. It is also useful for use in
your own applications. "opbeat" is installed as a binary.

"""

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
	import multiprocessing
except ImportError:
	pass

import sys
from setuptools import setup, find_packages

tests_require = [
	'nose',
	'mock',
	'unittest2',
]

install_requires = [
	'requests',
	'pip==1.2.1'
]

if sys.version_info[:2] < (2, 7):
	install_requires.append('argparse')

setup(
	name='opbeatcli',
	version='1.1',
	author='Ron Cohen',
	author_email='ron@opbeat.com',
	url='http://github.com/opbeat/opbeatcli',
	description='opbeat is a client for Opbeat (https://opbeat.com)',
	long_description=__doc__,
	packages=find_packages(exclude=("tests",)),
	zip_safe=False,
	install_requires=install_requires,
	tests_require=tests_require,
	extras_require={'test': tests_require},
	test_suite = "nose.collector",
	include_package_data=True,
	entry_points={
		'console_scripts': [
			'opbeat = opbeatcli.runner:main',
		],
	},
	classifiers=[
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'Operating System :: OS Independent',
		'Topic :: Software Development'
	],
)
