from __future__ import annotations

import subprocess
from pathlib import Path

from loguru import logger

from ..utils import exe


def flac(file: Path, compression: int = 8, destination: Path | None = None, wipe_metadata: bool = True) -> Path:
    """
    Thin flac wrapper that adds support for more codecs via an FFmpeg intermediate.
    """
    if not 0 <= compression <= 8:
        compression = 8

    match destination:
        case None:
            destination = file.with_suffix(".flac")
        case _ if destination.suffix == ".flac":
            destination.parent.mkdir(exist_ok=True, parents=False)
        case _:
            destination.mkdir(exist_ok=True, parents=False)
            destination = destination / f"{file.stem}.flac"

    logger.info(f"Encoding {file.name} to FLAC...")

    try:  # try running natively first
        cmd = [exe("flac"), "-f", f"-{compression}", "-V", file, "-o", destination]
        subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True)  # type: ignore

    except subprocess.CalledProcessError:
        # flac doesn't support the given audio file so we will use FFmpeg to create an intermediate flac
        from tempfile import TemporaryDirectory

        with TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            tempfile = Path(tmpdir) / f"{file.stem}.flac"

            ffmpeg = (
                exe("ffmpeg"),
                "-loglevel",
                "fatal",
                "-i",
                file,
                "-c:a",
                "flac",
                "-compression_level",
                "0",
                tempfile,
            )

            subprocess.run(ffmpeg, capture_output=True, check=True)
            cmd = [exe("flac"), "-f", f"-{compression}", "-V", tempfile, "-o", destination]
            subprocess.run(cmd, capture_output=True, check=True)  # type: ignore

            if wipe_metadata:
                subprocess.run((exe("metaflac"), "--remove-all", destination), capture_output=True, check=True)

    logger.success(f"Successfully encoded {file.name} to FLAC")

    return destination
