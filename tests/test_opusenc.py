import subprocess
from pathlib import Path
from uuid import uuid4

from harbinger.tools.opusenc import concurrent_opusenc

basedir = Path("tests/__test_data__/").resolve()


def test_opusenc(tmp_path: Path) -> None:
    flac_file = tmp_path / f"{uuid4()}.flac"

    subprocess.run(
        ("ffmpeg", "-i", basedir / "Big Buck Bunny - S01E01.ac3", "-c:a", "flac", "-compression_level", "0", flac_file)
    )

    opus_file = tmp_path / f"{uuid4()}.opus"

    subprocess.run(("opusenc", flac_file, "--bitrate", "192", opus_file), check=False)

    control = opus_file.stat().st_size

    for encoded in concurrent_opusenc(basedir, tmp_path, glob=("*.ac3")):
        assert encoded.stat().st_size == control
