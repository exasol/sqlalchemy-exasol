import sys
import json
import argparse
from collections import namedtuple

LEGIT_TESTS_TO_SKIP = {
    "pyodbc": [
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_dsn",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_dsn_without_user",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_overrides_default",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_trusted",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_with_custom_parameter",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_with_driver",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_with_parameter_set_to_none",
        "test/test_exadialect_turbodbc.py::EXADialectTurbodbcTest::test_create_connect_args_with_turbodbc_args",
    ],
    "turbodbc": [
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_autotranslate",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_dsn",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_trusted",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_with_driver",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_with_param",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_with_param_multiple",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_create_connect_args_with_unknown_params",
        "test/test_exadialect_pyodbc.py::EXADialect_pyodbcTest::test_is_disconnect",
    ],
}

Test = namedtuple(
    "Test",
    [
        "nodeid",
        "outcome",
        "details",
        "filename",
        "lineno",
    ],
)


def skipped_test_from(obj):
    for stage in ("setup", "call", "teardown"):
        try:
            filename, _, details = eval(obj[stage]["longrepr"])
            # we just take the first description + reason we find
            return Test(
                nodeid=obj["nodeid"],
                outcome=obj["outcome"],
                details=details,
                filename=filename,
                lineno=obj["lineno"],
            )
        except KeyError as ex:
            pass
    # Assumption: Every skipped test should have at least one 'longrepr' in a stage
    assert False


def _create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "connector", choices=["pyodbc", "turbodbc"]
    )
    parser.add_argument("test_results")
    parser.add_argument("--action", choices=["list-skipped"], default="list-skipped")
    parser.add_argument(
        "--debug", type=bool, action=argparse.BooleanOptionalAction, default=False
    )
    return parser


def all_skipped_tests(path):
    with open(path, "r") as f:
        data = json.load(f)
        for test in data["tests"]:
            if test["outcome"] == "skipped":
                yield skipped_test_from(test)


def main(test_results, connector, action, debug=False):
    skipped_tests = all_skipped_tests(test_results)
    skipped_tests = filter(
        lambda test: test.nodeid not in LEGIT_TESTS_TO_SKIP[connector], skipped_tests
    )
    for t in skipped_tests:
        print(f"{t.nodeid}: {t.details}")
    return 0


def cli_main():
    parser = _create_parser()
    cli_args = parser.parse_args()
    kwargs = vars(cli_args)

    def default():
        try:
            sys.exit(main(**kwargs))
        except Exception as ex:
            print(
                f"Aborting execution, details: {ex}. Rerun with --debug for more details.",
                file=sys.stderr,
            )
            sys.exit(-1)

    def debug():
        sys.exit(main(**kwargs))

    _main = default if not cli_args.debug else debug
    _main()


if __name__ == "__main__":
    cli_main()
