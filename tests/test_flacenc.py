import subprocess
from pathlib import Path
from uuid import uuid4

from harbinger.tools.flac import concurrent_flacenc

basedir = Path("tests/__test_data__/").resolve()


def test_flacenc(tmp_path: Path) -> None:
    ffmpeg_flac = tmp_path / f"{uuid4()}.flac"

    subprocess.run(
        (
            "ffmpeg",
            "-i",
            basedir / "Big Buck Bunny - S01E01.ac3",
            "-c:a",
            "flac",
            "-compression_level",
            "0",
            ffmpeg_flac,
        )
    )

    ref_flac = tmp_path / f"{uuid4()}.flac"

    subprocess.run(("flac", "-f", "-8", "-V", ffmpeg_flac, "-o", ref_flac))

    control = ref_flac.stat().st_size

    for encoded in concurrent_flacenc(basedir, tmp_path, glob=("*.ac3")):
        assert encoded.stat().st_size == control
