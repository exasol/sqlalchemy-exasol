Development
============
This guide contains information helpful when you want to engage in development of this project.
``sqlalchemy-exasol`` provides an Exasol dialect for ``sqlalchemy``. For further information
on the creation of a dialect, see `SQLAlchemy's README.dialects.rst <https://github.com/sqlalchemy/sqlalchemy/blob/main/README.dialects.rst>`__.

.. note::
    This project uses the `features of the Exasol-Toolbox <https://exasol.github.io/python-toolbox/main/user_guide/features/index.html>`__.
    These features include: common Git hooks, CI/CD templates, common
    task sessions via ``nox``, a standardized release preparation & triggering, etc.

Prerequisites
-------------
If you want to engage in development of this project, you should have the following libraries and tools available.

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
    provided on the Exasol-Toolbox's page for
    `Git hooks <https://exasol.github.io/python-toolbox/main/user_guide/features/git_hooks/index.html>`__.


Task Runner (Nox)
-----------------
Most repeating and complex tasks within this project are automated using the session runner `nox`.
To get an overview about the available ``sessions`` just run:

.. code-block::

    poetry run -- nox -l

To run a specific task, execute the following command:

.. code-block::

    poetry run -- nox -s <task-name>

You can modify or add a new task by editing the ``noxfile.py`` file.

Tests
-----

.. attention::

    If something is not working or unclear, you may want to look into the CI/CD action_ files.

.. _action: https://github.com/exasol/sqlalchemy-exasol/actions
.. _python: https://www.python.org/
.. _poetry: https://python-poetry.org/
.. _git: https://git-scm.com/
.. _Docker: https://www.docker.com/
