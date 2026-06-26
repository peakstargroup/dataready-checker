"""Scoring engine: 6 維度 -> 總分 -> 燈號 / 預期失敗率 / findings.

分數越穩越好：整合測試以『clean > medium > dirty 的分數排序』驗證，
而非依賴脆弱的絕對值。
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from . import rules
from .extract import FileInfo


@dataclass
class Dimension:
    key: str
    score: float
    weight: float


@dataclass
class Report:
    root: str
    generated_at: str
    file_count: int
    supported_count: int
    unsupported_count: int
    text_file_count: int
    total_score: float
    light: str
    expected_failure_rate: int
    workload: str
    dimensions: list[Dimension]
    findings: list[dict]
    stats: dict = field(default_factory=dict)


def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def _segments(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n|\n#{1,6}\s", text)
    return [p for p in (s.strip() for s in parts) if p]


# ---------- per-file quality (0..100) ----------

def _structure_quality(f: FileInfo) -> float:
    ext = f.ext
    if ext in (".md", ".markdown", ".docx", ".html", ".htm"):
        base = 40.0
        if f.heading_count >= 1:
            base += 40
        if f.heading_count >= 3:
            base += 20
        if f.heading_count == 0 and len(f.text) > 4000:
            base = 30
        return _clamp(base)
    if ext == ".pptx":
        return 70.0
    if ext == ".csv":
        return 80.0 if f.csv_consistent else 35.0
    if ext == ".xlsx":
        return 45.0 if f.merged_cells > 0 else 70.0
    if ext == ".pdf":
        return 55.0  # 可抽取文字但結構未知，給中性偏上
    if ext == ".txt":
        return 50.0 if "\n\n" in f.text else 30.0
    return 50.0


def _chunkability_quality(f: FileInfo) -> float:
    tokens = f.char_count / rules.CHARS_PER_TOKEN
    if tokens < rules.TINY_DOC_TOKENS:
        return 30.0
    if f.ext == ".pdf":
        # 以頁數當切塊邊界 proxy
        return 85.0 if f.pages >= 1 else 50.0
    segs = _segments(f.text) or [f.text]
    max_seg_tokens = max(len(s) for s in segs) / rules.CHARS_PER_TOKEN
    if max_seg_tokens > rules.OVERSIZED_SEGMENT_TOKENS:
        # 過長無分段，越長扣越多
        over = max_seg_tokens / rules.OVERSIZED_SEGMENT_TOKENS
        return _clamp(70 - min(40, (over - 1) * 25))
    if len(segs) >= 3:
        return 90.0
    return 70.0


# ---------- folder-level dimensions ----------

def _dim_extractability(supported: list[FileInfo]) -> float | None:
    if not supported:
        return None
    ok = sum(1 for f in supported if f.extractable)
    return 100.0 * ok / len(supported)


def _dim_structure(textfiles: list[FileInfo]) -> float | None:
    if not textfiles:
        return None
    return sum(_structure_quality(f) for f in textfiles) / len(textfiles)


def _dim_chunkability(textfiles: list[FileInfo]) -> float | None:
    if not textfiles:
        return None
    return sum(_chunkability_quality(f) for f in textfiles) / len(textfiles)


def _dim_redundancy(textfiles: list[FileInfo], supported: list[FileInfo]) -> float | None:
    if not supported:
        return None
    hashes = [f.content_hash for f in textfiles if f.content_hash]
    dup_ratio = 0.0
    if hashes:
        dup_ratio = 1 - len(set(hashes)) / len(hashes)
    ver = sum(1 for f in supported if rules.VERSION_NAME_RE.search(f.name))
    ver_ratio = ver / len(supported)
    return _clamp(100 - dup_ratio * 70 - ver_ratio * 30)


def _dim_freshness(supported: list[FileInfo], now: float) -> float | None:
    dated = [f for f in supported if f.mtime > 0]
    if not dated:
        return None
    stale = sum(1 for f in dated if (now - f.mtime) / 86400 > rules.STALE_DAYS)
    very = sum(1 for f in dated if (now - f.mtime) / 86400 > rules.VERY_STALE_DAYS)
    stale_ratio = stale / len(dated)
    very_ratio = very / len(dated)
    return _clamp(100 - stale_ratio * 60 - very_ratio * 20)


def _dim_metadata(supported: list[FileInfo]) -> float | None:
    if not supported:
        return None
    bad = 0
    for f in supported:
        stem = f.path.stem
        if rules.GENERIC_NAME_RE.match(stem) or rules.VERSION_NAME_RE.search(f.name):
            bad += 1
    bad_ratio = bad / len(supported)
    parents = {str(f.path.parent) for f in supported}
    root_dump = 0.0
    if len(supported) > 10 and len(parents) == 1:
        root_dump = 20.0
    return _clamp(100 - bad_ratio * 70 - root_dump)


# ---------- findings ----------

def _build_findings(supported, textfiles, dims, now) -> list[dict]:
    out: list[dict] = []
    n = len(supported) or 1

    scanned = sum(1 for f in supported if f.is_scanned_pdf)
    noextract = sum(1 for f in supported if not f.extractable)
    if dims.get("extractability") is not None and dims["extractability"] < 90:
        out.append({
            "code": "LOW_EXTRACTABILITY", "severity": "high",
            "pct": round(100 * noextract / n), "scanned": scanned,
        })
    if scanned:
        out.append({"code": "SCANNED_PDF", "severity": "high", "count": scanned})

    if dims.get("structure") is not None and dims["structure"] < 60:
        out.append({"code": "LOW_STRUCTURE", "severity": "medium",
                    "score": round(dims["structure"])})

    oversized = sum(1 for f in textfiles
                    if _chunkability_quality(f) < 55 and f.ext != ".pdf"
                    and f.char_count / rules.CHARS_PER_TOKEN >= rules.TINY_DOC_TOKENS)
    tiny = sum(1 for f in textfiles
               if f.char_count / rules.CHARS_PER_TOKEN < rules.TINY_DOC_TOKENS)
    if oversized:
        out.append({"code": "OVERSIZED_CHUNK", "severity": "medium", "count": oversized})
    if tiny:
        out.append({"code": "TINY_FRAGMENTS", "severity": "low", "count": tiny})

    hashes = [f.content_hash for f in textfiles if f.content_hash]
    if hashes:
        dup_ratio = 1 - len(set(hashes)) / len(hashes)
        if dup_ratio > 0.1:
            out.append({"code": "HIGH_DUPLICATION", "severity": "medium",
                        "pct": round(dup_ratio * 100)})

    dated = [f for f in supported if f.mtime > 0]
    if dated:
        stale = sum(1 for f in dated if (now - f.mtime) / 86400 > rules.STALE_DAYS)
        if stale / len(dated) > 0.3:
            out.append({"code": "STALE_DATA", "severity": "low",
                        "pct": round(100 * stale / len(dated))})

    bad = sum(1 for f in supported
              if rules.GENERIC_NAME_RE.match(f.path.stem)
              or rules.VERSION_NAME_RE.search(f.name))
    if bad / n > 0.2:
        out.append({"code": "BAD_FILENAMES", "severity": "low",
                    "pct": round(100 * bad / n)})

    order = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda d: order[d["severity"]])
    return out[:5]


def build_report(files: list[FileInfo], root: str, now: float | None = None) -> Report:
    now = time.time() if now is None else now
    supported = [f for f in files if f.supported and not f.corrupt]
    textfiles = [f for f in supported if f.extractable and f.text]

    raw = {
        "extractability": _dim_extractability(supported),
        "structure": _dim_structure(textfiles),
        "chunkability": _dim_chunkability(textfiles),
        "redundancy": _dim_redundancy(textfiles, supported),
        "freshness": _dim_freshness(supported, now),
        "metadata": _dim_metadata(supported),
    }

    dims: list[Dimension] = []
    num = den = 0.0
    for key, weight in rules.WEIGHTS.items():
        score = raw[key]
        if score is None:
            score = 0.0  # 無可評資料視為 0（例如全是掃描檔/不支援檔）
        dims.append(Dimension(key=key, score=round(score, 1), weight=weight))
        num += score * weight
        den += weight
    total = round(num / den, 1) if den else 0.0

    findings = _build_findings(supported, textfiles, raw, now)

    stats = {
        "scanned_pdf": sum(1 for f in supported if f.is_scanned_pdf),
        "encrypted": sum(1 for f in supported if f.encrypted),
        "corrupt": sum(1 for f in files if f.corrupt),
        "duplicate_groups": _dup_groups(textfiles),
    }

    return Report(
        root=root,
        generated_at=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
        file_count=len(files),
        supported_count=len(supported),
        unsupported_count=sum(1 for f in files if not f.supported),
        text_file_count=len(textfiles),
        total_score=total,
        light=rules.light_for(total),
        expected_failure_rate=rules.expected_failure_rate(total),
        workload=rules.workload_for(total),
        dimensions=dims,
        findings=findings,
        stats=stats,
    )


def _dup_groups(textfiles: list[FileInfo]) -> int:
    seen: dict[str, int] = {}
    for f in textfiles:
        if f.content_hash:
            seen[f.content_hash] = seen.get(f.content_hash, 0) + 1
    return sum(1 for c in seen.values() if c > 1)
