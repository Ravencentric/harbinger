from __future__ import annotations

from hashlib import sha256
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


def globber(path: Path, patterns: str | Iterable[str], recursive: bool = False) -> Generator[Path, None, None]:
    """
    Similar to pathlib.glob/rglob but accepts multiple patterns and only returns files.
    """
    if isinstance(patterns, str):
        patterns = (patterns,)

    glob = path.rglob if recursive else path.glob

    for pattern in patterns:
        for file in glob(pattern):
            if file.is_file():
                yield file.resolve()


def filehash(file: Path, /) -> str:
    """
    Return the sha256 checksum of the given file.
    """
    checksum = sha256()

    buf = bytearray(2**18)
    view = memoryview(buf)

    with file.open("rb") as f:
        while True:
            size = f.readinto(buf)
            if size == 0:
                break  # EOF
            checksum.update(view[:size])

    return checksum.hexdigest().casefold()
