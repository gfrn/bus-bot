import subprocess
import sys

from bus_bot import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "bus_bot", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
