import subprocess
import sys


def test_single_hash(snapshot):
    single = subprocess.run(
        (sys.executable, "-m", "harbinger", "hash", "UNLICENSE"), capture_output=True, check=True
    ).stdout.strip()
    assert single == snapshot


def test_multiple_hash(snapshot):
    multiple = subprocess.run(
        (sys.executable, "-m", "harbinger", "hash", "UNLICENSE", "UNLICENSE", "--no-table", "--no-check"),
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert multiple == snapshot
