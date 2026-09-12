from __future__ import annotations

import argparse
import configparser
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path

EXPECTED_PROJECT_NAME = "chess-mentor-engine"
EXPECTED_CONSOLE_SCRIPTS = {
    "cme": "chess_mentor_engine.cli:main",
    "cme-candidate-tutor": "chess_mentor_engine.candidate_tutor_cli:main",
    "cme-coach-review": "chess_mentor_engine.coach_review_cli:main",
    "cme-reviewed-coaching": "chess_mentor_engine.reviewed_coaching_cli:main",
    "cme-reviewed-coaching-ledger": (
        "chess_mentor_engine.reviewed_coaching_ledger_cli:main"
    ),
    "cme-coach-review-reference": "chess_mentor_engine.coach_review_reference_cli:main",
    "cme-persisted-coach-review-reference": (
        "chess_mentor_engine.persisted_review_reference_cli:main"
    ),
    "cme-participant-review": "chess_mentor_engine.participant_review_package_cli:main",
    "cme-local-tutor": "chess_mentor_engine.local_tutor_entry:main",
}
EXPECTED_PACKAGE_FILES = (
    "chess_mentor_engine/py.typed",
    "chess_mentor_engine/chess_knowledge/data/ontology.v1.json",
    "chess_mentor_engine/chess_knowledge/data/strategy.v1.json",
)


class DistributionQualificationError(ValueError):
    """A built distribution does not satisfy the Version 1.0 contract."""


def _single_member(names: set[str], suffix: str, label: str) -> str:
    matches = sorted(name for name in names if name.endswith(suffix))
    if len(matches) != 1:
        raise DistributionQualificationError(
            f"wheel must contain exactly one {label}; found {len(matches)}"
        )
    return matches[0]


def qualify_wheel(path: Path, *, expected_version: str) -> None:
    """Validate release identity, console scripts, and package data in one wheel."""
    if not path.is_file():
        raise DistributionQualificationError(f"wheel does not exist: {path}")

    expected_prefix = f"chess_mentor_engine-{expected_version}-"
    if not path.name.startswith(expected_prefix) or path.suffix != ".whl":
        raise DistributionQualificationError(
            "wheel version is not identified by the expected filename: "
            f"expected {expected_version!r}, got {path.name!r}"
        )

    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        metadata_name = _single_member(names, ".dist-info/METADATA", "METADATA")
        entry_points_name = _single_member(
            names,
            ".dist-info/entry_points.txt",
            "entry_points.txt",
        )

        metadata = Parser().parsestr(archive.read(metadata_name).decode("utf-8"))
        if metadata.get("Name") != EXPECTED_PROJECT_NAME:
            raise DistributionQualificationError(
                f"wheel project name is {metadata.get('Name')!r}; "
                f"expected {EXPECTED_PROJECT_NAME!r}"
            )
        if metadata.get("Version") != expected_version:
            raise DistributionQualificationError(
                f"wheel version is {metadata.get('Version')!r}; "
                f"expected {expected_version!r}"
            )

        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read_string(archive.read(entry_points_name).decode("utf-8"))
        if not parser.has_section("console_scripts"):
            raise DistributionQualificationError(
                "wheel entry_points.txt is missing [console_scripts]"
            )
        actual_scripts = dict(parser.items("console_scripts"))
        for name, expected_target in EXPECTED_CONSOLE_SCRIPTS.items():
            actual_target = actual_scripts.get(name)
            if actual_target != expected_target:
                raise DistributionQualificationError(
                    f"console script {name!r} maps to {actual_target!r}; "
                    f"expected {expected_target!r}"
                )

        for package_file in EXPECTED_PACKAGE_FILES:
            if package_file not in names:
                raise DistributionQualificationError(
                    f"wheel is missing required package data: {package_file}"
                )


def qualify_sdist(path: Path, *, expected_version: str) -> None:
    """Validate source distribution identity and required source/package files."""
    if not path.is_file():
        raise DistributionQualificationError(f"sdist does not exist: {path}")

    expected_name = f"chess_mentor_engine-{expected_version}.tar.gz"
    if path.name != expected_name:
        raise DistributionQualificationError(
            f"sdist filename is {path.name!r}; expected {expected_name!r}"
        )

    root = f"chess_mentor_engine-{expected_version}"
    required = {
        f"{root}/pyproject.toml",
        f"{root}/README.md",
        f"{root}/LICENSE",
        f"{root}/src/chess_mentor_engine/__init__.py",
        *(f"{root}/src/{package_file}" for package_file in EXPECTED_PACKAGE_FILES),
    }
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())

    missing = sorted(required - names)
    if missing:
        raise DistributionQualificationError(
            "sdist is missing required files: " + ", ".join(missing)
        )


def qualify_distributions(
    wheel_path: Path,
    sdist_path: Path,
    *,
    expected_version: str,
) -> None:
    """Validate both binary and source Version 1.0 distribution artifacts."""
    qualify_wheel(wheel_path, expected_version=expected_version)
    qualify_sdist(sdist_path, expected_version=expected_version)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Chess Mentor Engine Version 1.0 distribution artifacts."
    )
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--sdist", required=True, type=Path)
    parser.add_argument("--expected-version", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    qualify_distributions(
        args.wheel,
        args.sdist,
        expected_version=args.expected_version,
    )
    print(
        "Version 1.0 distribution artifacts qualified: "
        f"{args.wheel.name}, {args.sdist.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
