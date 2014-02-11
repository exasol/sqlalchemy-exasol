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
VERSION = '0.7.0'

from setuptools import setup

setup(
    name='sqlaexasol',
    version=VERSION,
    description='EXASOL dialect for SQLAlchemy',
    author='Blue Yonder',
    packages=['exa'],
    install_requires=["SQLAlchemy>=0.8.2, <0.9", "pyodbc>=3.0.6"],
    tests_require=['nose>=0.11', 'coverage>=3.7.1', 'mock>=1.0.1'],
    test_suite='test.test_exa',
    entry_points={
          'sqlalchemy.dialects': ['exa.pyodbc = exa:pyodbc.dialect']
    },
)
