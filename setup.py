#!/usr/bin/env python
"""
opbeatcli is a command line client for `Opbeat <https://opbeat.com/>`_.
It provides access to the Opbeat API through the command line. It is also
useful for use in your own applications. "opbeat" is installed as a binary.

"""
from setuptools import setup

from opbeatcli import __version__

try:
    # Python 2.6 workaround to prevent:
    #     "TypeError: 'NoneType' object is not callable"
    #      in multiprocessing/util.py _exit_function
    # when running `python setup.py test`
    # <http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html>
    # noinspection PyUnresolvedReferences
    import multiprocessing
except ImportError:
    pass


with open('README.rst') as f:
    long_description = f.read().strip()


with open('requirements.txt') as f:
    install_requires = f.read().strip().splitlines()
try:
    # noinspection PyUnresolvedReferences
    import argparse
except ImportError:
    install_requires.append('argparse')


with open('requirements-tests.txt') as f:
    tests_require = f.read().strip().splitlines()

try:
    # noinspection PyUnresolvedReferences
    import unittest
    # noinspection PyStatementEffect
    unittest.TestCase.assertDictContainsSubset
except (ImportError, AttributeError):
    tests_require.append('unittest2')

setup(
    name='opbeatcli',
    version=__version__,
    author='Ron Cohen',
    author_email='ron@opbeat.com',
    url='http://github.com/opbeat/opbeatcli',
    description=__doc__.strip(),
    long_description=long_description,
    packages=['opbeatcli'],
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require
    },
    test_suite ='nose.collector',
    entry_points={
        'console_scripts': [
            'opbeat = opbeatcli.__main__:main',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
