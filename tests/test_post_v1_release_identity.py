from pathlib import Path
import tomllib


def _project_version() -> str:
    with Path("pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)["project"]["version"]


def test_post_v1_main_uses_a_development_identity() -> None:
    assert _project_version() == "1.1.0.dev0"


def test_release_ci_does_not_hardcode_the_historical_v1_artifact() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "dist/chess_mentor_engine-1.0.0-py3-none-any.whl" not in workflow
    assert "dist/chess_mentor_engine-1.0.0.tar.gz" not in workflow
    assert '== "1.0.0"' not in workflow
