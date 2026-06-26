"""DataReady CLI (argparse, stdlib only).

用法：
    py -m peakstar_dataready scan <PATH> [選項]
    dataready scan <PATH> [選項]            # 安裝後
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from . import __version__, collect, report as report_mod, telemetry
from .analyze import build_report


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dataready",
        description="DataReady: 資料準備度健檢 (Data Readiness check) by Peakstar. "
                    "在你花錢做 AI 之前，先看你的資料夠不夠格餵 AI。本機執行，零外送。",
    )
    p.add_argument("--version", action="version", version=f"DataReady {__version__}")
    sub = p.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="掃描資料夾並產出資料準備度報告")
    scan.add_argument("path", help="要健檢的資料夾路徑")
    scan.add_argument("--out", default="./dataready-report", help="報告輸出目錄")
    scan.add_argument("--format", default="html,json", help="輸出格式，逗號分隔：html,json")
    scan.add_argument("--lang", default="zh", choices=["zh", "en"], help="報告語言")
    scan.add_argument("--max-files", type=int, default=None, help="最多掃描檔數（取樣）")
    scan.add_argument("--include", default=None, help="只納入符合的檔名 glob，逗號分隔")
    scan.add_argument("--exclude", default=None, help="排除符合的檔名 glob，逗號分隔")
    scan.add_argument("--open", action="store_true", help="完成後自動開啟 HTML 報告")
    scan.add_argument("--no-telemetry", action="store_true", help="強制關閉遙測（預設本就關閉）")
    return p


def _split(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def run_scan(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser()
    if not root.exists() or not root.is_dir():
        print(f"錯誤：找不到資料夾 {root}", file=sys.stderr)
        return 2

    if not args.no_telemetry:
        telemetry.record("scan_started")

    include = _split(args.include)
    exclude = _split(args.exclude)
    formats = _split(args.format) or ["html", "json"]

    print(f"掃描中：{root} ...")
    files = collect.walk(root, include=include, exclude=exclude, max_files=args.max_files)
    if not files:
        print("資料夾內沒有可掃描的檔案。", file=sys.stderr)
        return 1

    report = build_report(files, root=str(root))
    out_dir = Path(args.out).expanduser()
    written = report_mod.write_reports(report, out_dir, formats, args.lang)

    print(report_mod.terminal_summary(report, args.lang))
    print()
    for p in written:
        print(f"  報告已產生：{p}")
    print(f"\n  關於 DataReady 與 Peakstar：{report_mod.i18n.consult_url('dataready', report.light)}")

    if not args.no_telemetry:
        telemetry.record("scan_completed")

    if args.open:
        html_path = out_dir / "report.html"
        if html_path.exists():
            webbrowser.open(html_path.resolve().as_uri())

    return 0


def _ensure_utf8_output() -> None:
    """在非 UTF-8 主控台（Windows cp1252 / cp950 等）上，繁中輸出會觸發
    UnicodeEncodeError 讓整支 CLI 當掉。盡力把 stdout/stderr 切到 UTF-8；
    reconfigure 於 Python 3.7+ 可用，環境不支援則安靜略過。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_output()
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
