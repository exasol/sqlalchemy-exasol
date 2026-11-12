"""PyExasol version flags and markers for tests whose behavior depends on the version.

Add a new flag here whenever a PyExasol release changes behavior that
SQLAlchemy-Exasol exposes, so that tests do not compare version strings inline.
"""

import pyexasol
import pytest
from packaging.version import Version

_INSTALLED = Version(pyexasol.__version__)

# PyExasol 3.0.0 changed the default WebSocket DBAPI conversion so that fetched
# values are converted to Python types as early as possible (PEP 249). It also
# introduced the ``fetch_mapper`` option, mapped HASHTYPE in the cursor metadata and
# returns TIMESTAMP WITH LOCAL TIME ZONE as ``datetime`` and INTERVAL DAY TO SECOND
# as ``ExaTimeDelta``.
# https://github.com/exasol/pyexasol/releases/tag/3.0.0
PYEXASOL_3 = _INSTALLED >= Version("3.0.0")

# PyExasol 4.0.0 introduced the ``insert_mapper`` option and stricter validation of
# the Python values sent to the database: VARCHAR only accepts ``str``, timezone-aware
# datetime objects are rejected for DATE and TIMESTAMP types, and INTERVAL DAY TO
# SECOND accepts ``timedelta`` and ``ExaTimeDelta``.
# https://github.com/exasol/pyexasol/releases/tag/4.0.0
PYEXASOL_4 = _INSTALLED >= Version("4.0.0")

# The markers expect tests of newer behavior to fail with older PyExasol versions.
# They are strict, so a test passing despite the version also fails the run.
requires_pyexasol_3 = pytest.mark.xfail(
    not PYEXASOL_3, reason="Requires PyExasol >= 3.0.0", strict=True
)
requires_pyexasol_4 = pytest.mark.xfail(
    not PYEXASOL_4, reason="Requires PyExasol >= 4.0.0", strict=True
)
