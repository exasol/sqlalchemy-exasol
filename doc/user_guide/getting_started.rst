.. _getting_started:

Getting Started
===============

This guide is designed to get a new user started with ``sqlalchemy-exasol``.

Prerequisites
-------------

- Exasol >= 7.1
- Python >= 3.10

Installing
----------

`sqlalchemy-exasol is distributed through PyPI <https://pypi.org/project/sqlalchemy_exasol/>`__.
It can be installed via pip, poetry, or any other compatible dependency management tool:

.. code-block:: bash

   pip install sqlalchemy-exasol

.. note::

    SQLAlchemy will be installed as well, as it is a required dependency for SQLAlchemy-Exasol.

First Step
----------

For your first step, we recommend, running this on a safe-to-test database:

.. literalinclude:: ../../examples/getting_started/0_test_first_connection.py
       :language: python3
       :caption: examples/getting_started/0_test_first_connection.py

..  note::

    The connection may be of data type :ref:`url_string` or a
    :ref:`instance_url`. The code examples throughout the User Guide use data
    type ``URL``, as it is less complicated.

Next Steps
----------

The SQLAlchemy-Exasol documentation covers many topics at different levels of experience:

* For best securing your connection, see :ref:`security`.
* For other connection parameters, see :ref:`connection_parameters`.
* Check out the available :ref:`features` & related :ref:`examples`, demonstrating the most
  important features.
