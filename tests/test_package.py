import tomllib
from pathlib import Path

from chess_mentor_engine import __version__


def test_package_declares_synchronized_v1_release_identity() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert __version__ == "1.0.0"
    assert pyproject["project"]["version"] == __version__
