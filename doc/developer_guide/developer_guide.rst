Development
============
This chapter contains information helpful when you want to engage in development of this project.

Prerequisites
-------------
If you want to engage in development of this project you should have the following libraries and tools available.

Tools
+++++
* python_ >= 3.8
* poetry_ >= 1.1.0
* git_
* Docker_
* integration-test-docker-environment_
    * Prerequisites_

Libraries
+++++++++
* unixodbc
* unixodbc-dev
* libboost-date-time-dev
* libboost-locale-dev
* libboost-system-dev


Example: Install of required system libraries on Ubuntu

.. code-block::

    sudo apt-get install unixodbc unixodbc-dev libboost-date-time-dev libboost-locale-dev libboost-system-dev


Locale
+++++++
Make sure the local is setup appropriately.

Example: Setting up an english locale

.. code-block::

    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
    export LANG=en_US.UTF-8


Project Layout
++++++++++++++

.. attention::

    Currently it is required that the integration-test-docker-environment_  project is checked out in parallel to this
    project. For more details on this have a look at the `Settings` in `noxfile.py`

    Expected Layout:

    .. code-block::

        |-sqlalchemy-exasol/
        ├─ ...
        |-integration-test-docker-environment
        ├─ ...
        |
        ...

Setup Your Workspace
--------------------

Get The Source
++++++++++++++

.. code-block::

    git clone https://github.com/exasol/sqlalchemy-exasol.git

Setup the Tooling & Virtual Environment
+++++++++++++++++++++++++++++++++++++++

.. code-block::

    poetry shell
    poetry install

.. warning::

    make sure you have the poetry shell active whenever you want to work in the workspace

Install the Git Commit Hooks
++++++++++++++++++++++++++++

.. code-block::

    pre-commit install

.. note::

    This may need to be rerun if you want or do add non standard hook types, for further details
    see `pre-commit install -h`.


Task Runner (Nox)
-----------------
Most repeating and complex tasks within this project are automated using the task runner `nox`.
To get an overview about the available `tasks` just run:

.. code-block::

    nox -l

All task(s) which will be run by default will have a leading `*`.
In order to run a specific task execute the following command:

.. code-block::

    nox -s <task-name>

You can modify or add new task by editing the file `noxfile.py`.

Tests
-----

#. Install all python dependencies needed for development

    .. code-block::

        # make sure you are using the virtual environment poetry has setup for this project
        poetry shell


#. Run all tests with `pyodbc` connector

    .. code-block::

        nox

    or

    .. code-block::

        nox -s "verify(connector='pyodbc')"

#. Run all tests with `turbodbc` connector

    .. code-block::

        nox -s "verify(connector='turbodbc')"

.. attention::

    If something still is not working or unclear, you may want to look into the CI/CD action_ files.


.. _action: https://github.com/exasol/sqlalchemy_exasol/actions
.. _python: https://www.python.org/
.. _poetry: https://python-poetry.org/
.. _git: https://git-scm.com/
.. _Docker: https://www.docker.com/
.. _integration-test-docker-environment: https://github.com/exasol/integration-test-docker-environment
.. _Prerequisites: https://github.com/exasol/integration-test-docker-environment#prerequisites>
