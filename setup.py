#!/usr/bin/env python
"""
opbeat
=========

opbeat is a command line client for `Opbeat <https://opbeat.com/>`_. It provides
access to the Opbeat API through the command line. It is also useful for use in
your own applications.

"""

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
	import multiprocessing
except ImportError:
	pass

from setuptools import setup, find_packages

tests_require = [
	# 'Django>=1.,<=1.4',
	'nose',
	'mock',
	'unittest2',
]

install_requires = [
	'ssh',
	'requests',
	'pip'
]

setup(
	name='opbeat',
	version='1.0.1',
	author='Ron Cohen',
	author_email='ron@opbeat.com',
	url='http://github.com/opbeat/opbeat',
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
			'opbeat = opbeat.runner:main',
		],
	},
	classifiers=[
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'Operating System :: OS Independent',
		'Topic :: Software Development'
	],
)
