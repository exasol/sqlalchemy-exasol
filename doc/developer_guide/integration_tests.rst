Integration Test
================

The integration tests are located within `test/integration`. They are split in
two groups.

#. The SQLAlchemy conformance test suite

    The sqlalchemy conformance test suite is provided and maintained by the sqlalchemy project and intended to support third party dialect developers.
    For further details see also `README.dialects.rst <https://docs.exasol.com/db/latest/sql_reference.htm>`_.

#. Our custom Exasol test suite

    The Exasol test suite consists of test written and maintained by exasol.

.. note::

    In order to reduce the likelihood of test side effects, the `sqlalchemy` and the `exasol` test suites
    are executed in separate pytest test runs.

.. attention::

    The exasol database does do implicit schema/context changes (open & close schema)
    in certain scenarios. Keep this in mind when setting up (writing) tests.

    #. CREATE SCHEMA implicitly changes the CURRENT_SCHEMA context

        When you create a new schema, you implicitly open this new schema.

    #. DROP SCHEMA sometimes switches the context to <null>

        If the CURRENT_SCHEMA is dropped an implicit context switch to <null> is done

    For further details have a look at the `Exasol-Documentation <https://docs.exasol.com/db/latest/sql_reference.htm>`_.

    .. note::

        Creating/Using a new un-pooled connection can be used for protecting against
        this side effect.


Setup
=====

Integration testing automatically is done by GitHub Actions contained in this repository, which provide a CI/CD pipeline to test, build, and deploy sqlalchemy_exasol to PyPI.
All important tasks within the actions are using **nox**, which also can be used locally.

Two main workflows are used for this purpose:

CI
---

This is meant to be used as the test workflow. It's located under:

.. code-block::

    sqlalchemy_exasol/.github/workflows/CI.yml

This workflow will be executed anytime there's a commit pushed to any branch that is **not master**, or whenever there's a pull request created where the base branch is **not master**. It runs a Docker Container with an Exasol database for every version specified in *matrix.exasol_version*, and uses those DBs to executes all tests in the repository. If everything went fine, it will create a package distribution using both sdist and wheel.

To run it just commit and push to any non-master branch and watch the workflow run in:

`<https://github.com/exasol/sqlalchemy_exasol/actions>`_

CI-CD
-----

This is meant to be used as the Production workflow. It's located under:

.. code-block::

    sqlalchemy_exasol/.github/workflows/CI-CD.yml

This workflow will be executed anytime there's a commit pushed to **master**, or whenever a **tag** (release) is pushed. It does all the same steps than the CI workflow with one additional step at the end: Upload the package to Pypi. This upload step only happens when a tag is pushed, it will not be executed when commits are done in master.

To run it just commit and push to master (*Optional:* push a tag in case you want PyPI upload) and watch the workflow run in:

`<https://github.com/exasol/sqlalchemy_exasol/actions>`_

The status of the CI-CD workflow will always be reflected in the badge called "build" in the README.rst and Home Page of this repository
