import subprocess
import sys
from pathlib import Path
from uuid import uuid4

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

    cmd = (sys.executable, "-m", "harbinger", "flac", basedir, tmp_path, "--glob", "*.ac3")
    subprocess.run(cmd, check=True)

    assert (tmp_path / "Big Buck Bunny - S01E01.flac").stat().st_size == control
    assert (tmp_path / "Big Buck Bunny - S01E02.flac").stat().st_size == control
    assert (tmp_path / "Big Buck Bunny - S01E03.flac").stat().st_size == control
