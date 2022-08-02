import argparse
import subprocess
import sys
from collections import namedtuple
from inspect import cleandoc
from pathlib import Path
from shutil import which

Version = namedtuple("Version", ["major", "minor", "patch"])

_SUCCESS = 0
_FAILURE = 1

# fmt: off
_VERSION_MODULE_TEMPLATE = cleandoc('''
# ATTENTION:
# This file is generated, do not edit it manually!
# If you need to change the version, do so in the project.toml, e.g. by using `poetry version X.Y.Z`.

MAJOR = {major}
MINOR = {minor}
PATCH = {patch}

VERSION = f"{{MAJOR}}.{{MINOR}}.{{PATCH}}"
''') + "\n"


# fmt: on


def version_from_string(s):
    """Converts a version string of the following format major.minor.patch to a version object"""
    major, minor, patch = (int(number, base=0) for number in s.split("."))
    return Version(major, minor, patch)


class CommitHookError(Exception):
    """Indicates that this commit hook encountered an error"""


def version_from_python_module(path):
    """Retrieve version information from the `version` module"""
    with open(path) as file:
        _locals, _globals = {}, {}
        exec(file.read(), _locals, _globals)

        try:
            version = _globals["VERSION"]
        except KeyError as ex:
            raise CommitHookError("Couldn't find version within module") from ex

        return version_from_string(version)


def version_from_poetry():
    poetry = which("poetry")
    if not poetry:
        raise CommitHookError("Couldn't find poetry executable")

    result = subprocess.run([poetry, "version"], capture_output=True)
    version = result.stdout.decode().split()[1]
    return version_from_string(version)


def write_version_module(version, path, exists_ok=True):
    version_file = Path(path)
    if version_file.exists() and not exists_ok:
        raise CommitHookError(f"Version file [{version_file}] already exists.")
    version_file.unlink(missing_ok=True)
    with open(version_file, "w") as f:
        f.write(
            _VERSION_MODULE_TEMPLATE.format(
                major=version.major, minor=version.minor, patch=version.patch
            )
        )


def _create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("version_module", help="Path to version module")
    parser.add_argument("files", nargs="*")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="enabled debug mode for execution.",
    )
    parser.add_argument(
        "-f",
        "--fix",
        action="store_true",
        default=False,
        help="fix instead of check.",
    )
    return parser


def _main_debug(args):
    module_version = version_from_python_module(args.version_module)
    poetry_version = version_from_poetry()

    if args.fix:
        write_version_module(poetry_version, args.version_module)

    if not module_version == poetry_version:
        print(
            f"Version in pyproject.toml {poetry_version} and {args.version_module} {module_version} do not match!"
        )
        if args.fix:
            print(
                f"Updating version in file ({args.version_module}) from {module_version} to {poetry_version}"
            )
        return _FAILURE

    return _SUCCESS


def _main(args):
    try:
        return _main_debug(args)
    except Exception as ex:
        print(f"Error while executing program, details: {ex}", file=sys.stderr)
        return _FAILURE


def main(argv=None):
    parser = _create_parser()
    args = parser.parse_args()
    entry_point = _main if not args.debug else _main_debug
    return entry_point(args)


if __name__ == "__main__":
    sys.exit(main())
