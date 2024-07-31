from __future__ import annotations

from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING

from harbinger.exceptions import ExecutableNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable


def exe(name: str) -> Path:
    """
    A wrapper for shutil.which that raises an error
    instead of returning None.
    """

    if executable := which(name):
        return Path(executable).resolve()
    else:
        raise ExecutableNotFoundError(name)


def globs(path: Path, patterns: str | Iterable[str], recursive: bool = False) -> Generator[Path, None, None]:
    if isinstance(patterns, str):
        patterns = (patterns,)

    globber = path.rglob if recursive else path.glob

    for pattern in patterns:
        for file in globber(pattern):
            yield file.resolve()
