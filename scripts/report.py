import csv
import json
import sys
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    FileType,
)
from collections import namedtuple
from collections.abc import (
    Generator,
    Iterable,
)
from typing import (
    Any,
    TextIO,
)

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


def skipped_test_from(obj: dict[str, Any]) -> Test:
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
        except KeyError:
            pass
    # Assumption: Every skipped test should have at least one 'longrepr' in a stage
    assert False


def _create_parser() -> ArgumentParser:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("connector", choices=["pyodbc"])
    parser.add_argument("test_results")
    parser.add_argument("-o", "--output", type=FileType("w"), default="-")
    parser.add_argument("-f", "--format", choices=["human", "csv"], default="csv")
    parser.add_argument("--debug", action="store_true", default=False)
    return parser


def all_skipped_tests(path: str) -> Generator[Test, None, None]:
    with open(path) as f:
        data = json.load(f)
        for test in data["tests"]:
            if test["outcome"] == "skipped":
                yield skipped_test_from(test)


def _human(tests: Iterable[Test], output: TextIO) -> None:
    for t in tests:
        print(
            f"ID: {t.nodeid}, Details: {t.details}, Filename: {t.filename}, Line: {t.lineno}",
            file=output,
        )


def _csv(tests: Iterable[Test], output: TextIO) -> None:
    fields = ("test-case", "status", "details")

    def test_to_entry(t: Test) -> dict[str, Any]:
        return {
            "test-case": t.nodeid,
            "status": t.outcome,
            "details": t.details,
        }

    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for test in tests:
        writer.writerow(test_to_entry(test))


def main(
    test_results: str, output: TextIO, format: str, **kwargs: dict[str, Any]
) -> int:
    skipped_tests = all_skipped_tests(test_results)
    dispatcher = {"human": _human, "csv": _csv}
    dispatcher[format](skipped_tests, output)
    return 0


def cli_main() -> None:
    parser = _create_parser()
    cli_args = parser.parse_args()
    kwargs = vars(cli_args)

    def default() -> None:
        try:
            sys.exit(main(**kwargs))
        except Exception as ex:
            print(
                f"Aborting execution, details: {ex}. Rerun with --debug for more details.",
                file=sys.stderr,
            )
            sys.exit(-1)

    def debug() -> None:
        sys.exit(main(**kwargs))

    _main = default if not cli_args.debug else debug
    _main()


if __name__ == "__main__":
    cli_main()
