from inspect import cleandoc

pytest_plugins = "pytester"


def test_connection_with_block_cleans_up_properly(pytester, exasol_config):
    config = exasol_config
    # Because the error only occurs on process shutdown we need to run a test within a test
    # (We require the result (stderr) of a terminated process triggering the failure.
    pytester.makepyfile(
        # fmt: off
        cleandoc(
            f"""
        from sqlalchemy import create_engine, sql

        def test():
            url = "exa+websocket://{{user}}:{{pw}}@{{host}}:{{port}}?SSLCertificate=SSL_VERIFY_NONE"
            url = url.format(
                user="{config.username}",
                pw="{config.password}",
                host="{config.host}",
                port={config.port}
            )
            engine = create_engine(url)
            query = "SELECT 42;"
            with engine.connect() as con:
                result = con.execute(sql.text(query)).fetchall()
        """
        ),
        # fmt: on
    )
    r = pytester.runpytest_subprocess()
    actual = str(r.stderr)

    # We can't assert here actual != "", because runpytest_subprocess prints warnings
    # that can't be caught for Python 3.13 since we moved from pytest-itde plugin to
    # the pytest-backend plugin.
    # The warnings look like the following:
    #   <frozen importlib._bootstrap_external>:784: ResourceWarning: unclosed database in
    #   <sqlite3.Connection object at 0x7faa81955b70>
    #   ResourceWarning: Enable tracemalloc to get the object allocation traceback
    #
    # One possible reason could be that pytest-backend starts the integration-test-docker-environment
    # asynchronous in a subprocess.
    assert "Exception" not in actual
