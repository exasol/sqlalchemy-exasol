import urllib.error
import subprocess
from itertools import repeat
from pathlib import Path
from typing import Iterable, Tuple
from urllib import request


def documentation(root: Path) -> Iterable[Path]:
    """Returns an iterator over all documentation files of the project"""
    docs = Path(root).glob("**/*.rst")

    def _deny_filter(path):
        return not ("venv" in path.parts)

    return filter(lambda path: _deny_filter(path), docs)


def urls(files: Iterable[Path]) -> Iterable[Tuple[Path, str]]:
    """Returns an iterable over all urls contained in the provided files"""

    def should_filter(url):
        _filtered = []
        return url.startswith("mailto") or url in _filtered

    for file in files:
        cmd = ['python', '-m', 'urlscan', '-n', f'{file}']
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if result.returncode != 0:
            stderr = result.stderr.decode('utf8')
            msg = f"Could not retrieve url's from file: {file}, details: {stderr}"
            raise Exception(msg)
        stdout = result.stdout.decode('utf8').strip()
        _urls = (url.strip() for url in stdout.split('\n'))
        yield from zip(
            repeat(file), filter(lambda url: not should_filter(url), _urls)
        )


def check(url: str) -> Tuple[int, str]:
    """Checks if an url is still working (can be accessed)"""
    try:
        # User-Agent needs to be faked otherwise some webpages will deny access with a 403
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        result = request.urlopen(req)
        return result.code, f"{result.msg}"
    except urllib.error.HTTPError as ex:
        return ex.status, f"{ex}"
