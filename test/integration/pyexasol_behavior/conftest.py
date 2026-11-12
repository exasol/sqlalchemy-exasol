"""Fixtures for tests that use PyExasol directly (no SQLAlchemy)."""

import json
from contextlib import suppress
from typing import Any

import pytest

# (test id, SQL, parameter metadata of the WebSocket response), in the order prepared.
PREPARE_RESPONSES: list[tuple[str, str, dict[str, Any]]] = []


@pytest.fixture
def prepare(pyexasol_connection, request):
    """Prepare a statement, check and record the parameter metadata of the response.

    ``prepare(sql, expected)`` returns the prepared statement and the data type of
    its first placeholder. It fails if the parameter metadata that the database sends
    in its WebSocket response differs from ``expected``, which every test writes out
    in full. The response is recorded before the check, so it is also listed for a
    failing test. All prepared statements are closed after the test.
    """
    statements = []

    def _prepare(sql, expected):
        statement = pyexasol_connection.cls_statement(
            pyexasol_connection, sql, prepare=True
        )
        statements.append(statement)
        response = statement.parameter_data
        PREPARE_RESPONSES.append((request.node.nodeid, sql, response))
        assert response == expected
        return statement, response["columns"][0]["dataType"]

    yield _prepare
    for statement in statements:
        with suppress(Exception):
            statement.close()


def pytest_terminal_summary(terminalreporter):
    """List the WebSocket prepare responses seen by the tests of this directory."""
    if not PREPARE_RESPONSES:
        return
    terminalreporter.section("WebSocket prepare responses (parameter metadata)")
    for node_id, sql, response in PREPARE_RESPONSES:
        terminalreporter.write_line(node_id.split("::", 1)[-1])
        terminalreporter.write_line(f"  {sql}")
        terminalreporter.write_line(f"  {json.dumps(response)}")
