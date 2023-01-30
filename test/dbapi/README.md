The test structure needs additional refactoring, due to the fact that the conftest.py within the integration path
registers the sqla testing plugin, which makes it very hard to test without an sqla setup. The sqla setup and
sqla based tests only should be used for the sqla compliance tests.

All exasol tests should be reworked to not depend on and/or require the sqla test setup.


-> Create ROADMAP issue or fix at the end of the feature