from __future__ import annotations

import fnmatch
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

ALLOWED_SUFFIXES = {
    "",
    ".cmd",
    ".docx",
    ".example",
    ".json",
    ".md",
    ".py",
    ".sqlite3",
    ".txt",
    ".yaml",
    ".yml",
}

ALLOWED_NO_SUFFIX_NAMES = {
    "Dockerfile",
    "manage.py",
}

ALLOWED_HIDDEN_FILES = {
    ".env",
    ".env.example",
    ".env.native.example",
    ".env.docker.example",
    ".gitignore",
    ".gitkeep",
}

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
}

RUNTIME_ARTIFACT_PATTERNS = {
    "*.pyc",
    "*.pyo",
}

RUNTIME_WARNING_PATTERNS = {
    "*.log",
}


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def is_runtime_artifact(path: Path) -> bool:
    if "__pycache__" in path.parts:
        return True
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in RUNTIME_ARTIFACT_PATTERNS)


def is_runtime_warning(path: Path) -> bool:
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in RUNTIME_WARNING_PATTERNS)


def has_allowed_extension(path: Path) -> bool:
    name = path.name
    suffix = path.suffix.lower()

    if name in ALLOWED_HIDDEN_FILES:
        return True
    if suffix == "":
        return name in ALLOWED_NO_SUFFIX_NAMES
    return suffix in ALLOWED_SUFFIXES


def main() -> int:
    runtime_artifacts_blocking: list[Path] = []
    runtime_artifacts_warning: list[Path] = []
    unexpected_extensions: list[Path] = []
    scanned = 0

    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        current_dir = Path(dirpath)
        if is_ignored(current_dir):
            dirnames[:] = []
            continue

        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        for filename in filenames:
            file_path = current_dir / filename
            rel_path = file_path.relative_to(ROOT_DIR)
            scanned += 1

            if is_runtime_artifact(rel_path):
                runtime_artifacts_blocking.append(rel_path)
                continue

            if is_runtime_warning(rel_path):
                runtime_artifacts_warning.append(rel_path)
                continue

            if not has_allowed_extension(rel_path):
                unexpected_extensions.append(rel_path)

    print(f"Scanned files: {scanned}")

    if runtime_artifacts_warning:
        print("\nRuntime artifacts (warnings):")
        for path in sorted(runtime_artifacts_warning):
            print(f"- {path}")

    if runtime_artifacts_blocking:
        print("\nRuntime artifacts (blocking):")
        for path in sorted(runtime_artifacts_blocking):
            print(f"- {path}")

    if unexpected_extensions:
        print("\nUnexpected file extensions found:")
        for path in sorted(unexpected_extensions):
            print(f"- {path}")

    if runtime_artifacts_blocking or unexpected_extensions:
        print("\nAudit failed. Run scripts\\clean_runtime.cmd and remove/rename unexpected files.")
        return 1

    if runtime_artifacts_warning:
        print("\nAudit passed with warnings.")
        return 0

    print("File/extension audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
