#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines the setup for this package.

Increment the version number prior to making a release and
do not forget to document your changes in CHANGES.md

:file: setup.py
:authors: Blue Yonder GmbH
:date: 2014/02/11
"""
import os
from setuptools import setup
# version string handling: http://dcreager.net/2010/02/10/setuptools-git-version-numbers/
from version import get_git_version

## Get long_description from README.md:
here = os.path.dirname(os.path.abspath(__file__))
long_description = ''
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read().strip()

setup(
    name='sqlalchemy_exasol',
    version=get_git_version(),
    license='License :: OSI Approved :: BSD License',
    url='https://github.com/BY-jk/sqlalchemy_exasol',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database'
    ],
    description='EXASOL dialect for SQLAlchemy',
    long_description=long_description,
    author='Blue Yonder GmbH',
    packages=['sqlalchemy_exasol'],
    install_requires=["SQLAlchemy>=0.8.2, <0.9", "pyodbc>=3.0.6"],
    tests_require=['nose>=0.11', 'coverage>=3.7.1', 'mock>=1.0.1'],
    test_suite='run_tests.run',
    entry_points={
          'sqlalchemy.dialects': ['exa.pyodbc = exa:pyodbc.dialect']
    },
)
