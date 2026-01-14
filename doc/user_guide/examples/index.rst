.. _examples:

Examples
========

.. toctree::
    :maxdepth: 1
    :hidden:

    connection_configuration
    testing_connection

Here we group and present the code for our examples. While there are docstrings and
comments in the code to provide context, please look to our :ref:`getting_started`
guide, sub-pages in :ref:`features`, and the
`general documentation of SQLAlchemy <https://docs.sqlalchemy.org/en/20/>`_
for a more detailed walkthrough.

Pre-requisites
--------------

- `Poetry <https://python-poetry.org/docs/#installing-with-the-official-installer>`__ >= 2.1.0

Preparation
-----------

Some basic preparation steps are required to see the examples in action:

#. Download the `SQLAlchemy-Exasol source code <https://github.com/exasol/sqlalchemy-exasol/>`__.\
#. Inside the folder where you have SQLAlchemy-Exasol's source code, install the dependencies using:

    .. code-block:: bash

        poetry install

#. Make sure you have installed or have access to an Exasol database. For **testing** purposes, you may use:
    - `exasol/docker-db <https://hub.docker.com/r/exasol/docker-db/tags>`__, which can be easily accessed by using ``poetry run -- nox -s db:start``
    - the free `Exasol Community Edition <https://www.exasol.com/free-signup-community-edition/>`__

#. Open the ``/examples/`` directory and edit the file configuration file, as described in :ref:`example_configuration`.
#. To verify that your connection configuration is correct, run the code, as described in :ref:`example_connection`:
#. Now, you may run whatever examples you would like:

    .. code-block:: bash

        poetry run -- python examples/<path_to_desired_module>.py
