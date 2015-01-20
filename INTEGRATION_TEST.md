# Integration Test Setup

The travis build is configured to test against an EXASolution database instance hosted by EXASOL. This text describes how to get such a test DB, as well as how to make the right entries in the .travis.yml file.

## 1 - Register with EXASOL

You need an account on the EXASOL user portal. Sign up here: https://www.exasol.com/portal/display/WEL/Home

## 2 - Request a Demo User

In the issue tracker (https://www.exasol.com/support/secure/Dashboard.jspa) create a ticket on Project "Public Demo" with Type "Registration". Fill in whatever fields are required. You will receive an e-mail with an automatically generated user account with test schemata in an EXASolution 4.x and 5.x database cluster (as of January 2015). 

The SQLAlchemy test suite requires the schema 'test_schema' for all tests to pass. So you will have to ask EXASOL to grant your user access to this schema.

## 3 - Install Travis Command Line Client

You need to install the Travis command line client. Find installation instructions on the travis-ci-org homepage or try this link https://github.com/travis-ci/travis.rb#installation (January 2015).

## 4 - Encrypt the Connection Strings

Change into a directory that belongs the to git repository of the sqlalchemy_exasol project. Travis CLI inspects the directory to check for a git repo. For each database version run the following command:

    travis encrypt TESTDB=exa+pyodbc://<USER>:<PASSWORD>@<IP-RANGE>:<PORT>/<USER> EXA_<MAJOR_VERSION>=nil

e.g.

    travis encrypt TESTDB=exa+pyodbc://USER10:SECURE@8.8.8.8..9:1234/USER10 EXA_4=nil

The EXA_<MAJOR_VERSION> environment variable is used to make identification of the DB backend easy from the travis build page. From the output copy the line starting with 'secure'

## 5 - Update the .travis.yml Config File

Add the generated secure strings to the 'env > matrix' section of the .travis.yml file (replacing previous entries if necessary).

Check the configuration file syntax with:

    travis lint

If everything is fine, commit and push your changes and watch the builds unfold.
