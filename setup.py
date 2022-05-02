#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines the setup for this package.

Do not forget to document your changes in CHANGES.md

:file: setup.py
:authors: Blue Yonder GmbH, Exasol AG
:date: 2014/02/11
"""
import os

from setuptools import setup

# Get long_description from README.md:
here = os.path.dirname(os.path.abspath(__file__))
long_description = ""
with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read().strip()

setup(
    name="sqlalchemy_exasol",
    setup_requires=["setuptools_scm"],
    license="License :: OSI Approved :: BSD License",
    url="https://github.com/exasol/sqlalchemy-exasol",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Database",
    ],
    description="EXASOL dialect for SQLAlchemy",
    long_description=long_description,
    author="Blue Yonder GmbH, Exasol AG",
    author_email="opensource@exasol.com",
    packages=["sqlalchemy_exasol"],
    install_requires=["SQLAlchemy>=1.3.24, <1.4", "pyodbc>=4.0.32", "six>=1.5"],
    extras_require={"turbodbc": ["turbodbc>=3.3.0, <4"]},
    tests_require=["pytest", "mock>=1.0.1"],
    test_suite="pytest.main",
    use_scm_version={"write_to": "sqlalchemy_exasol/_version.py"},
    entry_points={
        "sqlalchemy.dialects": [
            "exa.pyodbc = sqlalchemy_exasol.pyodbc:EXADialect_pyodbc",
            "exa.turbodbc = sqlalchemy_exasol.turbodbc:EXADialect_turbodbc",
        ]
    },
)
