from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from tools.release_qualification import (
    EXPECTED_CONSOLE_SCRIPTS,
    EXPECTED_PACKAGE_FILES,
    DistributionQualificationError,
    qualify_distributions,
    qualify_sdist,
    qualify_wheel,
)


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
    wheel = tmp_path / "chess_mentor_engine-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "chess_mentor_engine-1.0.0.tar.gz"
    _write_wheel(wheel)
    _write_sdist(sdist)

    qualify_distributions(wheel, sdist, expected_version="1.0.0")


def test_wheel_rejects_wrong_release_version(tmp_path: Path) -> None:
    wheel = tmp_path / "chess_mentor_engine-0.1.0-py3-none-any.whl"
    _write_wheel(wheel, version="0.1.0")

    with pytest.raises(DistributionQualificationError, match="wheel version"):
        qualify_wheel(wheel, expected_version="1.0.0")


@pytest.mark.parametrize(
    "script_name",
    ["cme", "cme-local-tutor", "cme-participant-review"],
)
def test_wheel_rejects_missing_promised_console_script(
    tmp_path: Path,
    script_name: str,
) -> None:
    wheel = tmp_path / "chess_mentor_engine-1.0.0-py3-none-any.whl"
    _write_wheel(wheel, omitted_script=script_name)

    with pytest.raises(DistributionQualificationError, match=script_name):
        qualify_wheel(wheel, expected_version="1.0.0")


@pytest.mark.parametrize(
    "package_file",
    [
        "chess_mentor_engine/py.typed",
        "chess_mentor_engine/chess_knowledge/data/ontology.v1.json",
        "chess_mentor_engine/chess_knowledge/data/strategy.v1.json",
    ],
)
def test_wheel_rejects_missing_required_package_data(
    tmp_path: Path,
    package_file: str,
) -> None:
    wheel = tmp_path / "chess_mentor_engine-1.0.0-py3-none-any.whl"
    _write_wheel(wheel, omitted_package_file=package_file)

    with pytest.raises(DistributionQualificationError, match=Path(package_file).name):
        qualify_wheel(wheel, expected_version="1.0.0")


def test_sdist_rejects_missing_required_package_data(tmp_path: Path) -> None:
    package_file = "chess_mentor_engine/chess_knowledge/data/ontology.v1.json"
    sdist = tmp_path / "chess_mentor_engine-1.0.0.tar.gz"
    _write_sdist(sdist, omitted_package_file=package_file)

    with pytest.raises(DistributionQualificationError, match="ontology.v1.json"):
        qualify_sdist(sdist, expected_version="1.0.0")
