from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from loguru import logger

from ..utils import exe, globber


def get_audio_channels(audio: Path) -> int:
    """
    Utility function to get the channel count from an audio file.
    """
    cmd = [
        exe("ffprobe"),
        audio,
        "-show_entries",
        "stream=channels",
        "-select_streams",
        "a",
        "-of",
        "compact=p=0:nk=1",
        "-v",
        "0",
    ]
    process = subprocess.run(
        cmd,  # type: ignore
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return int(process.stdout) if process.stdout.strip().isdigit() else 0


def opusenc(file: Path, bitrate: int | None = None, destination: Path | None = None) -> Path:
    """
    Thin opusenc wrapper that adds automatic bitrate selection and support for more codecs via an FFmpeg intermediate.
    """
    match destination:
        case None:
            destination = file.with_suffix(".opus")
        case _ if destination.suffix in (".opus", ".ogg"):
            destination.parent.mkdir(exist_ok=True, parents=False)
        case _:
            destination.mkdir(exist_ok=True, parents=False)
            destination = destination / f"{file.stem}.opus"

    if bitrate is None:
        match channels := get_audio_channels(file):
            case 1:
                bitrate = 96
            case 2:
                bitrate = 192
            case 7 | 8:
                bitrate = 480
            case _:
                bitrate = 320

    logger.info(f"Encoding {file.name} ({channels} ch) to Opus at {bitrate} kb/s...")

    try:  # try and see if opusenc handles given audio natively
        cmd = [exe("opusenc"), file, "--bitrate", f"{bitrate}", destination]
        subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True)  # type: ignore

    except (
        subprocess.CalledProcessError
    ):  # opusenc doesn't support the given file so we will use FFmpeg to create an intermediate flac
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
            "-f",
            "flac",
            "-",
        )

        pipe = subprocess.Popen(ffmpeg, stdout=subprocess.PIPE)
        cmd = [exe("opusenc"), "-", "--bitrate", f"{bitrate}", destination]
        subprocess.run(cmd, capture_output=True, check=True, stdin=pipe.stdout)  # type: ignore

    logger.success(f"Successfully encoded {file.name} to Opus")

    return destination


def concurrent_opusenc(
    src: Path,
    dst: Path | None = None,
    /,
    *,
    bitrate: int | None = None,
    glob: tuple[str, ...] = ("*.flac", "*.wav", "*.w64"),
    recursive: bool = False,
    threads: int | None = None,
) -> tuple[Path, ...]:
    """
    Opusenc wrapper with concurrent encoding, bitrate selection,
    and support for more codecs via FFmpeg.

    Parameters
    ----------
    src : Path
        Path to the source directory or file.
    dst : Path, optional
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

    if src.is_file():
        return (opusenc(src, bitrate, dst).resolve(),)
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            files = globber(src, glob, recursive)
            futures = [executor.submit(opusenc, file, bitrate, dst) for file in files]
            results = tuple([future.result().resolve() for future in as_completed(futures)])
            executor.shutdown()

        return results
