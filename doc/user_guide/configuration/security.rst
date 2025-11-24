.. _security:

Security
========

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, which utilizes
`PyExasol <https://github.com/exasol/pyexasol/>`__ in the backend.
It works with different Exasol database variants: on-premise and, for
testing purposes, Docker-based. Each of these have shared and unique
authentication methods and require a TLS/SSL certificate setup. Throughout this
guide on security, an overview of the security features of SQLAlchemy-Exasol is
provided, as well as examples and links to the relevant PyExasol documentation.

.. _authentication:

Authentication
**************

For the various Exasol DBs, there are different ways to set up and use the access
credentials for a connection made with the :ref:`instance_url` or :ref:`url_string`
provided to the engine.

+------------------+------------------------------+----------------------------------------+
| Exasol DB        | Setting Credentials          | SQLAlchemy-Exasol parameters           |
+==================+==============================+========================================+
| on-premise       | `on-premise authentication`_ | * ``username``                         |
|                  |                              | * ``password``                         |
+------------------+------------------------------+----------------------------------------+
| Docker (testing) | `Docker authentication`_     | * ``username``                         |
|                  |                              | * ``password``                         |
+------------------+------------------------------+----------------------------------------+

.. _on-premise authentication: https://docs.exasol.com/db/latest/sql/create_user.htm
.. _Docker authentication: https://github.com/exasol/docker-db?tab=readme-ov-file#connecting-to-the-database


#. Connect to Exasol on-premise or Docker

   .. code-block:: python

      from sqlalchemy import create_engine, URL

        url_object = URL.create(
            drivername="exa+websocket",
            username="sys",
            password="exasol",
            host="127.0.0.1",
            port="8563",
        )

        create_engine(url_object)
