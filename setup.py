#!/usr/bin/env python
"""
opbeatcli is a command line client for `Opbeat <https://opbeat.com/>`_.
It provides access to the Opbeat API through the command line. It is also
useful for use in your own applications. "opbeat" is installed as a binary.

"""
from setuptools import setup

from opbeatcli import __version__


tests_require = [
    'nose',
    'mock',
    'unittest2',
]

install_requires = [
    'requests',
    'pip==1.2.1'
]


try:
    # noinspection PyUnresolvedReferences
    import argparse
except ImportError:
    install_requires.append('argparse')


setup(
    name='opbeatcli',
    version=__version__,
    author='Ron Cohen',
    author_email='ron@opbeat.com',
    url='http://github.com/opbeat/opbeatcli',
    description=__doc__.strip(),
    long_description=open('README.rst').read().strip(),
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
