#!/usr/bin/env python3
"""把 peakstar-oss-common 的程式碼重新 vendor 進本工具。

單一真相來源是 peakstar-oss-common repo。改完那邊後，跑這支把最新版複製進
peakstar_dataready/_vendor/peakstar_oss_common/。

用法：
    py scripts/sync_common.py [COMMON_REPO_PATH]

COMMON_REPO_PATH 預設為 ../peakstar-oss-common（與本 repo 並列）。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
DEST = HERE / "peakstar_dataready" / "_vendor" / "peakstar_oss_common"


def main() -> int:
    src_root = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "peakstar-oss-common"
    src = src_root / "peakstar_oss_common"
    if not src.is_dir():
        print(f"找不到 common 套件：{src}", file=sys.stderr)
        return 2
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(src, DEST, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"已同步 {src} -> {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
