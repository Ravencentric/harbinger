from __future__ import annotations

import subprocess
from pathlib import Path

from loguru import logger

from ..utils import exe

OPSUENC_CODECS = (".wav", ".wave", ".aif", ".aiff", ".flac", ".ogg")

def is_supported(file: Path) -> bool:
    return file.suffix.casefold() in OPSUENC_CODECS


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
        cmd, # type: ignore
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
        case _ :
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

    if is_supported(file): # opusenc already supports these codecs
        
        cmd = [exe("opusenc"), file, "--bitrate", f"{bitrate}", destination]
        subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True) # type: ignore

    else:  # opusenc doesn't support these codecs so we will use FFmpeg to create an intermediate flac

        ffmpeg = (
            exe("ffmpeg"),
            "-loglevel", "fatal",
            "-i", file,
            "-c:a", "flac",
            "-compression_level", "0",
            "-f", "flac",
            "-",
        )
        
        pipe = subprocess.Popen(ffmpeg, stdout=subprocess.PIPE)  # type: ignore
        cmd = [exe("opusenc"), "-", "--bitrate", f"{bitrate}", destination]
        subprocess.run(cmd, capture_output=True, check=True, stdin=pipe.stdout)  # type: ignore
    
    logger.success(f"Successfully encoded {file.name} to Opus")

    return destination