import subprocess
import sys
from pathlib import Path

basedir = Path("tests/__test_data__/").resolve()


def test_opusenc(tmp_path):
    cmd = (sys.executable, "-m", "harbinger", "opus", basedir, tmp_path)

    subprocess.run(cmd, check=True)
