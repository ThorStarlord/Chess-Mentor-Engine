from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

EXPECTED_CONSOLE_SCRIPTS = {
    "cme": "chess_mentor_engine.cli:main",
    "cme-candidate-tutor": "chess_mentor_engine.candidate_tutor_cli:main",
    "cme-coach-review": "chess_mentor_engine.coach_review_cli:main",
    "cme-reviewed-coaching": "chess_mentor_engine.reviewed_coaching_cli:main",
    "cme-reviewed-coaching-ledger": "chess_mentor_engine.reviewed_coaching_ledger_cli:main",
    "cme-coach-review-reference": "chess_mentor_engine.coach_review_reference_cli:main",
    "cme-persisted-coach-review-reference": "chess_mentor_engine.persisted_review_reference_cli:main",
    "cme-participant-review": "chess_mentor_engine.participant_review_package_cli:main",
    "cme-local-tutor": "chess_mentor_engine.local_tutor_entry:main",
}
EXPECTED_PACKAGE_FILES = (
    "chess_mentor_engine/py.typed",
    "chess_mentor_engine/chess_knowledge/data/ontology.v1.json",
    "chess_mentor_engine/chess_knowledge/data/strategy.v1.json",
)


def _release_qualification() -> ModuleType:
    try:
        from tools import release_qualification
    except (ImportError, ModuleNotFoundError):
        pytest.fail("tools.release_qualification is missing")
    return release_qualification


def _write_wheel(
    path: Path,
    *,
    version: str = "1.0.0",
    omitted_script: str | None = None,
    omitted_package_file: str | None = None,
) -> None:
    dist_info = f"chess_mentor_engine-{version}.dist-info"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            f"{dist_info}/METADATA",
            "\n".join(
                [
                    "Metadata-Version: 2.1",
                    "Name: chess-mentor-engine",
                    f"Version: {version}",
                    "",
                ]
            ),
        )
        scripts = ["[console_scripts]"]
        scripts.extend(
            f"{name} = {target}"
            for name, target in EXPECTED_CONSOLE_SCRIPTS.items()
            if name != omitted_script
        )
        archive.writestr(f"{dist_info}/entry_points.txt", "\n".join(scripts) + "\n")
        for package_file in EXPECTED_PACKAGE_FILES:
            if package_file != omitted_package_file:
                archive.writestr(package_file, "{}\n")


def _add_tar_text(archive: tarfile.TarFile, path: str, content: str = "x\n") -> None:
    payload = content.encode("utf-8")
    info = tarfile.TarInfo(path)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def _write_sdist(
    path: Path,
    *,
    version: str = "1.0.0",
    omitted_package_file: str | None = None,
) -> None:
    root = f"chess_mentor_engine-{version}"
    with tarfile.open(path, "w:gz") as archive:
        for required in (
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "src/chess_mentor_engine/__init__.py",
        ):
            _add_tar_text(archive, f"{root}/{required}")
        for package_file in EXPECTED_PACKAGE_FILES:
            source_path = f"src/{package_file}"
            if package_file != omitted_package_file:
                _add_tar_text(archive, f"{root}/{source_path}")


def test_release_distributions_accept_exact_v1_contract(tmp_path: Path) -> None:
    qualifier = _release_qualification()
    assert qualifier.EXPECTED_CONSOLE_SCRIPTS == EXPECTED_CONSOLE_SCRIPTS
    assert qualifier.EXPECTED_PACKAGE_FILES == EXPECTED_PACKAGE_FILES

    wheel = tmp_path / "chess_mentor_engine-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "chess_mentor_engine-1.0.0.tar.gz"
    _write_wheel(wheel)
    _write_sdist(sdist)

    qualifier.qualify_distributions(wheel, sdist, expected_version="1.0.0")


def test_wheel_rejects_wrong_release_version(tmp_path: Path) -> None:
    qualifier = _release_qualification()
    wheel = tmp_path / "chess_mentor_engine-0.1.0-py3-none-any.whl"
    _write_wheel(wheel, version="0.1.0")

    with pytest.raises(qualifier.DistributionQualificationError, match="wheel version"):
        qualifier.qualify_wheel(wheel, expected_version="1.0.0")


@pytest.mark.parametrize(
    "script_name",
    ["cme", "cme-local-tutor", "cme-participant-review"],
)
def test_wheel_rejects_missing_promised_console_script(
    tmp_path: Path,
    script_name: str,
) -> None:
    qualifier = _release_qualification()
    wheel = tmp_path / "chess_mentor_engine-1.0.0-py3-none-any.whl"
    _write_wheel(wheel, omitted_script=script_name)

    with pytest.raises(qualifier.DistributionQualificationError, match=script_name):
        qualifier.qualify_wheel(wheel, expected_version="1.0.0")


@pytest.mark.parametrize(
    "package_file",
    list(EXPECTED_PACKAGE_FILES),
)
def test_wheel_rejects_missing_required_package_data(
    tmp_path: Path,
    package_file: str,
) -> None:
    qualifier = _release_qualification()
    wheel = tmp_path / "chess_mentor_engine-1.0.0-py3-none-any.whl"
    _write_wheel(wheel, omitted_package_file=package_file)

    with pytest.raises(
        qualifier.DistributionQualificationError,
        match=Path(package_file).name,
    ):
        qualifier.qualify_wheel(wheel, expected_version="1.0.0")


def test_sdist_rejects_missing_required_package_data(tmp_path: Path) -> None:
    qualifier = _release_qualification()
    package_file = "chess_mentor_engine/chess_knowledge/data/ontology.v1.json"
    sdist = tmp_path / "chess_mentor_engine-1.0.0.tar.gz"
    _write_sdist(sdist, omitted_package_file=package_file)

    with pytest.raises(
        qualifier.DistributionQualificationError,
        match="ontology.v1.json",
    ):
        qualifier.qualify_sdist(sdist, expected_version="1.0.0")
