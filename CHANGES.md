# 0.8.5
* default schema is set to 'SYS' to create reasonable reflections

# 0.8.4
* reduce dependency version to python package six from >=1.7 to >=1.5

# 0.8.3
* fix versioneer build parameter in setup.py to enable pip install

# 0.8.2
* added missing README.rst

# 0.8.1

* updated repository url
* p3k support - contribution by iadrich

# 0.8.0

* added support for SQL MERGE
* upgraded to SQLA 0.9.x (build requires >= 0.9.6)
* bug fixes
    * incorrect quoting of identifiers with leading _
    * incorrect implementation for retrieving last generated PK (for auto inc columns)

# 0.7.5

* switched to versioneer

# 0.7.4

* changed README from md to rst to display reasonable content on pypi

# 0.7.0

* First version of the SQLAlchemy EXASOL dialect released under BSD license
* a lot of minor bug fixes to pass the SQLAlchemy test suite
