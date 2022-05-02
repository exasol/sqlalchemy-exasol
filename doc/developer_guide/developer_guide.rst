Development
============
This chapter contains information helpful when you want to engage in development of this project.

Prerequisites
-------------
If you want to engage in development of this project you should have the following libraries and tools available.

Tools
+++++
* python_ >= 3.7
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

Tests
-----

#. Install all python dependencies needed for development

    .. code-block::

        pip install -r requirements_dev.txt


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
.. _git: https://git-scm.com/
.. _Docker: https://www.docker.com/
.. _integration-test-docker-environment: https://github.com/exasol/integration-test-docker-environment
.. _Prerequisites: https://github.com/exasol/integration-test-docker-environment#prerequisites>
