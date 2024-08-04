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


def multi_filehash(
    files: tuple[Path, ...],
    /,
    *,
    check: bool = True,
    table: bool = True,
    fullpath: bool = False,
) -> None:
    """
    Compute and print the sha256 hash values for the given files.

    Parameters
    ----------
    files : tuple[Path, ...]
        Files to hash.
    check : bool, optional
        Checks if all hashes are the same and prints a corresponding message.
    table : bool, optional
        Prints the file names and their hashes in a markdown table format.
    fullpath : bool, optional
        Print the fullpath alongside the hash.
    """
    if len(files) == 1:
        print(filehash(files[0]))
    else:
        from rich import print as richprint
        from rich.box import MARKDOWN
        from rich.table import Table

        checksums = []
        if table:
            hashtable = Table("file", "sha256", box=MARKDOWN)
            for file in files:
                checksum = filehash(file)
                checksums.append(checksum)
                hashtable.add_row(file.as_posix() if fullpath else file.name, checksum)
            richprint(hashtable)
        else:
            for file in files:
                checksum = filehash(file)
                checksums.append(checksum)
                print(f"{file.as_posix() if fullpath else file.name}: {checksum}")

        if check:
            if len(set(checksums)) == 1:
                richprint(":white_heavy_check_mark: All hashes match!")
            else:
                richprint(":warning:  Hash mismatch detected!")  # the double space is artistic intent
