# Current Status

```
# Status Update

## Test(s) Status

### sqlalchemy
* pyodbc 3 :no_entry_sign: failed, 190 :heavy_check_mark: passed , 359 :yellow_circle:  skipped, 0 :boom: errors
    * 1 test is caused by a potentially by an escaping issue
    * 2 failing tests are caused by incorrectly returned rowcounts
* turbodbc 6 :no_entry_sign: failed, 185 :heavy_check_mark: passed , 361 :yellow_circle:  skipped, 0 :boom: errors
    * 1 test is caused by a potentially by an escaping issue
    * 5 failing tests are caused by incorrectly returned rowcounts

### exasol
* pyodbc 9 :no_entry_sign: failed, 202 :heavy_check_mark: passed , 10 :yellow_circle:  skipped, 0 :boom: errors
    * All the failing 9 tests, are caused by the custom merge statement.
* turbodbc 9 :no_entry_sign: failed, 189 :heavy_check_mark: passed , 23 :yellow_circle:  skipped, 0 :boom: errors
    * All the failing 9 tests, are caused by the custom merge statement.

## Next Steps
* Investigate the escaping issue (DifficultParametersTest_*::test_round_trip[q?marks])
* Investigate the invalid returned row counts
* Refactor/Implement Merge statement in respect to new sqla syntax/api
```

# TODO's:

* TODO: Investigate/Fix the escaping issue (DifficultParametersTest_*::test_round_trip[q?marks])
* TODO: Investigate/Fix the invalid returned row counts
* TODO: Refactor/Implement custom merge statement based on new sqla api
* TODO: Move DB setup/preperation from noxfile to conftest.py

# Post Migration TODO's (tickets)

* TODO: Create ticket to Update to ITDE to 1.1.0
* TODO: Create ticket for migrating exasol tests to non sqla based fixture setup (e.g. pyexasol)
* TODO: Create ticket to additional details to developer guide
    # Architecture
        * https://www.aosabook.org/en/sqlalchemy.html
    # Custom SQL Constructs
        * https://docs.sqlalchemy.org/en/14/core/compiler.html
    # Other dialects with custom commands
        * https://github.com/SAP/sqlalchemy-hana/blob/master/sqlalchemy_hana/dialect.py
        * https://github.com/snowflakedb/snowflake-sqlalchemy
        * https://github.com/clach04/ingres_sa_dialect
        * https://github.com/sqlalchemy-redshift/sqlalchemy-redshift/blob/main/sqlalchemy_redshift/ddl.py
        * https://github.com/IBM/nzalchemy/blob/master/sqlalchemy-netezza/nzalchemy/base.py
