#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines the setup for this package.

Do not forget to document your changes in CHANGES.md

:file: setup.py
:authors: Blue Yonder GmbH
:date: 2014/02/11
"""
from setuptools import setup

import os


## Get long_description from README.md:
here = os.path.dirname(os.path.abspath(__file__))
long_description = ''
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read().strip()

setup(
    name='sqlalchemy_exasol',
    setup_requires=["setuptools_scm"],
    license='License :: OSI Approved :: BSD License',
    url='https://github.com/blue-yonder/sqlalchemy_exasol',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database'
    ],
    description='EXASOL dialect for SQLAlchemy',
    long_description=long_description,
    author='Blue Yonder GmbH',
    packages=['sqlalchemy_exasol'],
    install_requires=["SQLAlchemy>=1.0.4, <2", "pyodbc>=3.0.6", "six>=1.5"],
    extras_require={'turbodbc': ['turbodbc>=1.1.0']},
    tests_require=['pytest', 'mock>=1.0.1'],
    test_suite='pytest.main',
    use_scm_version={"write_to": "sqlalchemy_exasol/_version.py"},
    entry_points={
          'sqlalchemy.dialects': ['exa.pyodbc = sqlalchemy_exasol.pyodbc:EXADialect_pyodbc',
                                  'exa.turbodbc = sqlalchemy_exasol.turbodbc:EXADialect_turbodbc']
    },
)
