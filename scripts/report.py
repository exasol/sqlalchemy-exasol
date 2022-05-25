import argparse
import csv
import json
import sys
from collections import namedtuple

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
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("connector", choices=["pyodbc", "turbodbc"])
    parser.add_argument("test_results")
    parser.add_argument("-o", "--output", type=argparse.FileType("w"), default="-")
    parser.add_argument("-f", "--format", choices=["human", "csv"], default="csv")
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


def _human(tests, output):
    for t in tests:
        print(
            f"ID: {t.nodeid}, Details: {t.details}, Filename: {t.filename}, Line: {t.lineno}",
            file=output,
        )


def _csv(tests, output):
    fields = ("test-case", "status", "details")

    def test_to_entry(t):
        return {
            "test-case": t.nodeid,
            "status": t.outcome,
            "details": t.details,
        }

    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for test in tests:
        writer.writerow(test_to_entry(test))


def main(test_results, output, format, **kwargs):
    skipped_tests = all_skipped_tests(test_results)
    dispatcher = {"human": _human, "csv": _csv}
    dispatcher[format](skipped_tests, output)
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
