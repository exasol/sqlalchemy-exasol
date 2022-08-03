from subprocess import run
from typing import Sequence


def tags() -> Sequence[str]:
    """
    Returns a list of all tags, sorted from [0] oldest to [-1] newest.
    PreConditions:
    - the git cli tool needs to be installed
    - the git cli tool can be found via $PATH
    - the code is executed where the working directory is within a git repository
    """
    command = ["git", "tag", "--sort=committerdate"]
    result = run(command, capture_output=True, check=True)
    tags_generator = (tag.strip() for tag in result.stdout.decode("utf-8").splitlines())
    return list(tags_generator)
