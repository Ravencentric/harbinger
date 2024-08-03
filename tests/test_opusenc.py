import subprocess
import sys
from pathlib import Path

basedir = Path("tests/__test_data__/").resolve()


def test_opusenc(tmp_path: Path) -> None:
    cmd = (sys.executable, "-m", "harbinger", "opus", str(basedir), str(tmp_path), "--glob", "*.ac3")

    subprocess.run(cmd, check=True)

    control = (basedir / "control.opus").stat().st_size

    print(len(list(tmp_path.glob("*"))))

    assert (tmp_path / "Big Buck Bunny - S01E01.opus").stat().st_size == control
    assert (tmp_path / "Big Buck Bunny - S01E02.opus").stat().st_size == control
    assert (tmp_path / "Big Buck Bunny - S01E03.opus").stat().st_size == control
