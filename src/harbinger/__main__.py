from __future__ import annotations

import sys

from cyclopts import App, Group
from cyclopts.types import ResolvedExistingFile, ResolvedExistingPath, ResolvedPath
from loguru import logger

logger.remove()
logger.add(
    sys.stderr, format="<green>{time:HH:mm:ss}</> | <lvl>{level:<8}</> | <cyan>{function}</> - <lvl>{message}</>"
)

app = App(name="harbinger", help="The Decepticon ship that carries weapons of mass destruction.")

app["--help"].group = ""
app["--version"].group = ""

encoders = Group.create_ordered("Encoders")  # type: ignore
utilities = Group.create_ordered("Utilities")  # type: ignore


@app.command(
    help="Opusenc wrapper with concurrent encoding, automatic bitrate selection, and support for more codecs via FFmpeg.",
    group=encoders,
)
def opus(
    src: ResolvedExistingPath,
    dst: ResolvedPath | None = None,
    /,
    *,
    bitrate: int | None = None,
    glob: tuple[str, ...] = ("*.flac", "*.wav", "*.w64"),
    recursive: bool = False,
    threads: int | None = None,
) -> None:
    """
    Opusenc wrapper with concurrent encoding, bitrate selection,
    and support for more codecs via FFmpeg.

    Parameters
    ----------
    src : ResolvedExistingPath
        Path to the source directory or file.
    dst : ResolvedPath, optional
        Destination file or directory where transcoded files will be saved.
    bitrate : int, optional
        Target bitrate in kbps.
    glob : tuple[str, ...], optional
        Patterns to match files in the source directory.
    recursive : bool, optional
        Whether to search for files recursively in subdirectories of src.
    threads : int, optional
        Number of threads to use for concurrent encoding.
    """
    from concurrent.futures import ThreadPoolExecutor

    from harbinger.utils import globber
    from harbinger.wrappers.opusenc import opusenc

    if src.is_file():
        opusenc(src, bitrate, dst)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            files = globber(src, glob, recursive)
            for file in files:
                executor.submit(opusenc, file, bitrate, dst)

            executor.shutdown()


@app.command(
    help="Reference FLAC wrapper with concurrent encoding and support for more codecs via FFmpeg.", group=encoders
)
def flac(
    src: ResolvedExistingPath,
    dst: ResolvedPath | None = None,
    /,
    *,
    compression: int = 8,
    wipe_metadata: bool = True,
    glob: tuple[str, ...] = ("*.wav", "*.w64"),
    recursive: bool = False,
    threads: int | None = None,
) -> None:
    """
    Reference FLAC wrapper with concurrent encoding and support for more codecs via FFmpeg.

    Parameters
    ----------
    src : ResolvedExistingPath
        Path to the source directory or file.
    dst : ResolvedPath, optional
        Destination file or directory where transcoded files will be saved.
    compression : int, optional
        Compression level.
    wipe_metadata : bool, optional
        Wipe non-essential metadata.
    glob : tuple[str, ...], optional
        Patterns to match files in the source directory.
    recursive : bool, optional
        Whether to search for files recursively in subdirectories of src.
    threads : int, optional
        Number of threads to use for concurrent encoding.
    """
    from concurrent.futures import ThreadPoolExecutor

    from harbinger.utils import globber
    from harbinger.wrappers.flac import flac

    if src.is_file():
        flac(src, compression, dst, wipe_metadata)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            files = globber(src, glob, recursive)
            for file in files:
                executor.submit(flac, file, compression, dst, wipe_metadata)

            executor.shutdown()


@app.command(name="hash", help="Compute and print the sha256 hash values for the given files.", group=utilities)
def hash_(
    files: tuple[ResolvedExistingFile, ...],
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
    from .utils import filehash

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


if __name__ == "__main__":
    app()
