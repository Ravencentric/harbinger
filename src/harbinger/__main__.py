from __future__ import annotations

import sys
from collections.abc import Iterable
from os import cpu_count

from cyclopts import App, Group
from cyclopts.types import ResolvedExistingPath, ResolvedPath
from loguru import logger

logger.remove()
logger.add(
    sys.stderr, format="<green>{time:HH:mm:ss}</> | <lvl>{level:<8}</> | <cyan>{function}</> - <lvl>{message}</>"
)

app = App(name="harbinger")
encoders = Group(name="Encoders")

app["--help"].group = ""
app["--version"].group = ""

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
    glob: Iterable[str] | None = None,
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
    glob : Iterable[str], optional
        Patterns to match files in the source directory.
    recursive : bool, optional
        Whether to search for files recursively in subdirectories of src.
    threads : int, optional
        Number of threads to use for concurrent encoding.
    """
    from concurrent.futures import ThreadPoolExecutor

    from harbinger.utils import globs
    from harbinger.wrappers.opusenc import OPSUENC_CODECS, opusenc

    default_glob = {f"*{codec}" for codec in OPSUENC_CODECS}

    if threads is None:
        if cpu := cpu_count():
            threads = cpu + 2 # Default is cpu count + 4

    if src.is_file():
        opusenc(src, bitrate, dst)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            files = globs(src, glob or default_glob, recursive)
            for file in files:
                executor.submit(opusenc, file, bitrate, dst)

            executor.shutdown()


@app.command(
    help="Reference FLAC wrapper with concurrent encoding and support for more codecs via FFmpeg.",
    group=encoders,
)
def flac(
    src: ResolvedExistingPath,
    dst: ResolvedPath | None = None,
    /,
    *,
    compression: int = 8,
    wipe_metadata: bool = True,
    glob: Iterable[str] | None = None,
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
    glob : Iterable[str], optional
        Patterns to match files in the source directory.
    recursive : bool, optional
        Whether to search for files recursively in subdirectories of src.
    threads : int, optional
        Number of threads to use for concurrent encoding.
    """
    from concurrent.futures import ThreadPoolExecutor

    from harbinger.utils import globs
    from harbinger.wrappers.flac import FLAC_CODECS, flac

    default_glob = {f"*{codec}" for codec in FLAC_CODECS}

    if threads is None:
        if cpu := cpu_count():
            threads = cpu + 2  # Default is cpu count + 4

    if src.is_file():
        flac(src, compression, dst, wipe_metadata)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            files = globs(src, glob or default_glob, recursive)
            for file in files:
                executor.submit(flac, file, compression, dst, wipe_metadata)

            executor.shutdown()

if __name__ == "__main__":
    app()
