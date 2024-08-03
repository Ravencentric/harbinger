import subprocess
import sys
from os import getenv
from pathlib import Path
from uuid import uuid4

#import pytest

basedir = Path("tests/__test_data__/").resolve()

#CI = getenv("CI") == "true" 
 
#@pytest.mark.skipif(CI)
def test_opusenc(tmp_path: Path) -> None:
    cmd = (sys.executable, "-m", "harbinger", "opus", str(basedir), str(tmp_path), "--glob", "*.ac3")

    subprocess.run(cmd, check=True)

    flac_file = tmp_path / f"{uuid4()}.flac"

    subprocess.run(
        ("ffmpeg", "-i", basedir / "Big Buck Bunny - S01E01.ac3", "-c:a", "flac", "-compression_level", "0", flac_file)
    )

    opus_file = tmp_path / f"{uuid4()}.opus"

    subprocess.run(("opusenc", flac_file, "--bitrate", "192", opus_file))

    control = opus_file.stat().st_size

    assert (tmp_path / "Big Buck Bunny - S01E01.opus").stat().st_size == control
    assert (tmp_path / "Big Buck Bunny - S01E02.opus").stat().st_size == control
    assert (tmp_path / "Big Buck Bunny - S01E03.opus").stat().st_size == control
