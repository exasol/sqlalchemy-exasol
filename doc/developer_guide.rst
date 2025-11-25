.. _developer_guide:

:octicon:`tools` Developer Guide
================================
This guide contains information helpful when you want to engage in development of this project.
``sqlalchemy-exasol`` provides an Exasol dialect for ``sqlalchemy``. For further information
on the creation of a dialect, see `SQLAlchemy's README.dialects.rst <https://github.com/sqlalchemy/sqlalchemy/blob/main/README.dialects.rst>`__.

.. note::
    This project uses the `features of the Exasol-Python-Toolbox <https://exasol.github.io/python-toolbox/main/user_guide/features/index.html>`__.
    These features include: common Git hooks, CI/CD templates, common
    task sessions via ``nox``, a standardized release preparation & triggering, etc.

Prerequisites
-------------
Tools
+++++
* python_
* poetry_
* git_
* Docker_

Locale
+++++++
Make sure the locale is set up appropriately.

Example: Set up an English locale

.. code-block::

    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
    export LANG=en_US.UTF-8

Set up Your Workspace
+++++++++++++++++++++

#. Get the Source Code
    .. code-block::

        git clone https://github.com/exasol/sqlalchemy-exasol.git

#. Set up the Tooling & Virtual Environment
    .. code-block::

        poetry env use python3.10
        poetry install


#. Install the Git Hooks
    A `.pre-commit-config.yaml` is included in the source code. Follow the instructions
    provided on the Exasol-Python-Toolbox's page for
    `Git hooks <https://exasol.github.io/python-toolbox/main/user_guide/features/git_hooks/index.html>`__.


Task Runner (Nox)
-----------------
Most repeating and complex tasks within this project are automated using the session runner ``nox``.
To get an overview about the available ``sessions`` just run:

.. code-block::

    poetry run -- nox -l

To run a specific task, execute the following command:

.. code-block::

    poetry run -- nox -s <task-name>

You can modify or add a new task by editing the ``noxfile.py`` file. For details,
please see the `User Guide <https://exasol.github.io/python-toolbox/main/user_guide/user_guide.html#user-guide>`__
of the Exasol-Python-Toolbox.

Running tests
-------------

.. note::
    If you manually run some integration tests or want to try a database-related operation
    out:

    .. code-block:: shell

        # to start a test database
        poetry run -- nox -s db:start -- --db-version <db_version>
        # to stop a test database
        poetry run -- nox -s db:stop

Unit Tests
++++++++++

The unit tests are located in the directory ``test/unit``.

.. code-block:: shell

    poetry run -- nox -s test:unit


Integration Tests
+++++++++++++++++

The integration tests are located in the directory ``test/integration``.

.. attention::

   A Docker container with a test database needs to be started for the integration tests.
   If a test group is not working or unclear, you may want to look into the CI/CD workflows_ files.

The integration tests are split into three groups to reduce the likelihood of test side effects:

#. The SQLAlchemy Conformance Test Suite

    The SQLAlchemy conformance test suite is provided and maintained by the sqlalchemy project and intended to support third party dialect developers.
    For further details, see also `README.dialects.rst <https://docs.exasol.com/db/latest/sql_reference.htm>`_.
    In general, if Exasol does not support a feature for a test, it is preferred to use a
    ``pytest.mark.xfail`` marker (rather than to skip the test or modify the
    ``sqlalchemy_exasol.requirements.py``). An ``xfail`` provides continuous feedback
    that an expected error is being raised, and is preferred as both SQLAlchemy and
    Exasol Databases are being updated, and it is possible that a future version
    may include this feature or require minor modifications for this to work.

    .. code-block:: shell

        poetry run -- nox -s test:sqla -- --connector websocket

#. Our Custom Exasol Test Suite

    The Exasol test suite consists of tests written and maintained by Exasol. These
    have a slight reliance upon the generic test classes provided by the SQLAlchemy
    Conformance Test Suite. This can sometimes prove problematic when the SQLAlchemy
    version is increased, as all of these tests may initially fail until the issue
    has been resolved.

    .. code-block:: shell

        poetry run -- nox -s test:exasol -- --connector websocket

#. Regression Test Suite

    This is an extension to the custom Exasol test suite that ensures that previously
    reported bugs are not experienced by customers as there are upgrades to the
    SQLAlchemy API and Exasol databases.

    .. code-block:: shell

        poetry run -- nox -s test:regression -- --connector websocket


.. attention::

    The Exasol database does do implicit schema/context changes (open & close schema)
    in certain scenarios. Keep this in mind when setting up (writing) tests.

    #. CREATE SCHEMA implicitly changes the CURRENT_SCHEMA context

        When you create a new schema, you implicitly open this new schema.

    #. DROP SCHEMA sometimes switches the context to <null>

        If the CURRENT_SCHEMA is dropped, an implicit context switch to <null> is done

    For further details, have a look at the `Exasol-Documentation <https://docs.exasol.com/db/latest/sql_reference.htm>`_.

    .. note::

        Creating/Using a new un-pooled connection can be used for protecting against
        this side effect.


Preparing & Triggering a Release
--------------------------------

The ``Exasol-Python-Toolbox`` provides nox sessions to semi-automate the release process:

.. code-block:: python

    # prepare a release
    nox -s release:prepare -- --type {major,minor,patch}

    # trigger a release
    nox -s release:trigger

For further information, please refer to the ``Exasol-Python-Toolbox``'s page `Creating a Release
<https://exasol.github.io/python-toolbox/main/user_guide/features/creating_a_release.html>`_.


.. _workflows: https://github.com/exasol/sqlalchemy-exasol/tree/master/.github/workflows
.. _python: https://www.python.org/
.. _poetry: https://python-poetry.org/
.. _git: https://git-scm.com/
.. _Docker: https://www.docker.com/
