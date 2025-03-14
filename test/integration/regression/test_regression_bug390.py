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
        import warnings

        warnings.filterwarnings("ignore", category=ResourceWarning,
                                module="importlib._bootstrap_external")
                                
        from sqlalchemy import create_engine
        
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
                result = con.execute(query).fetchall()
        """
        ),
        # fmt: on
    )
    r = pytester.runpytest_subprocess()
    expected = ""
    actual = str(r.stderr)

    assert actual == expected
