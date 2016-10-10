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
import versioneer
versioneer.versionfile_source = 'sqlalchemy_exasol/_version.py'
versioneer.versionfile_build = 'sqlalchemy_exasol/_version.py'
versioneer.tag_prefix = '' # tags are like 1.2.0
versioneer.parentdir_prefix = 'myproject-' # dirname like 'myproject-1.2.0'
import os
from setuptools import setup

## Get long_description from README.md:
here = os.path.dirname(os.path.abspath(__file__))
long_description = ''
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read().strip()

setup(
    name='sqlalchemy_exasol',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='License :: OSI Approved :: BSD License',
    url='https://github.com/blue-yonder/sqlalchemy_exasol',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Database'
    ],
    description='EXASOL dialect for SQLAlchemy',
    long_description=long_description,
    author='Blue Yonder GmbH',
    packages=['sqlalchemy_exasol'],
    install_requires=["SQLAlchemy>=1.0.4, <2", "pyodbc>=3.0.6", "six>=1.5"],
    extras_require={'turbodbc': ['turbodbc>=0.2.4']},
    tests_require=['pytest', 'pytest-cov', 'mock>=1.0.1'],
    test_suite='pytest.main',
    entry_points={
          'sqlalchemy.dialects': ['exa.pyodbc = sqlalchemy_exasol.pyodbc:EXADialect_pyodbc',
                                  'exa.turbodbc = sqlalchemy_exasol.turbodbc:EXADialect_turbodbc']
    },
)
