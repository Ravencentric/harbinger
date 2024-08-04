import subprocess
import sys
from pathlib import Path

from harbinger.tools.filehash import filehash


def test_hash(snapshot):
    assert filehash(Path("tests/__test_data__/Big Buck Bunny - S01E01.ac3")) == snapshot


def test_multiple_hash(snapshot):
    multiple = subprocess.run(
        (
            sys.executable,
            "-m",
            "harbinger",
            "hash",
            "tests/__test_data__/Big Buck Bunny - S01E01.ac3",
            "tests/__test_data__/Big Buck Bunny - S01E01.ac3",
            "--no-table",
            "--no-check",
        ),
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert multiple == snapshot
