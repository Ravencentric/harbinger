from hashlib import sha256
from pathlib import Path


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
