"""Walk a folder and analyze each file. Local only."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from .extract import FileInfo, analyze_file


def walk(
    root: Path,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_files: int | None = None,
) -> list[FileInfo]:
    files: list[FileInfo] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        name = path.name
        if include and not any(fnmatch.fnmatch(name, g) for g in include):
            continue
        if exclude and any(fnmatch.fnmatch(name, g) for g in exclude):
            continue
        files.append(analyze_file(path))
        if max_files and len(files) >= max_files:
            break
    return files
