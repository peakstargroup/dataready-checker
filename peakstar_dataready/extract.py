"""Per-file extraction and signal detection. Standard library only.

每個 parser 都包在 try/except 內，無法解析的檔標記為 corrupt 而非中斷。
所有解析皆於本機進行，不外送任何內容。
"""

from __future__ import annotations

import hashlib
import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from . import rules


@dataclass
class FileInfo:
    path: Path
    ext: str
    size: int
    mtime: float
    supported: bool = True
    extractable: bool = False
    corrupt: bool = False
    encrypted: bool = False
    is_scanned_pdf: bool = False
    text: str = ""
    char_count: int = 0
    pages: int = 0
    heading_count: int = 0
    csv_consistent: bool | None = None
    merged_cells: int = 0
    content_hash: str = ""
    note: str = ""

    @property
    def name(self) -> str:
        return self.path.name


# 報告/分析只需取樣前段文字，限制記憶體用量
_TEXT_SAMPLE_LIMIT = 200_000


def _norm_hash(text: str) -> str:
    """正規化後雜湊：可抓到『換檔名的整份複製』近似重複。"""
    norm = re.sub(r"\s+", " ", text.lower()).strip()
    return hashlib.sha256(norm.encode("utf-8", "ignore")).hexdigest() if norm else ""


def _strip_xml(xml: str) -> str:
    text = re.sub(r"<[^>]+>", " ", xml)
    return re.sub(r"[ \t]+", " ", text)


# ---------- format parsers ----------

def _parse_text(data: bytes) -> dict:
    text = data.decode("utf-8", "ignore")
    headings = len(re.findall(r"(?m)^\s{0,3}#{1,6}\s+\S", text))
    return {"text": text, "heading_count": headings, "extractable": bool(text.strip())}


def _parse_csv(data: bytes) -> dict:
    import csv as _csv

    text = data.decode("utf-8", "ignore")
    rows = list(_csv.reader(io.StringIO(text)))
    consistent = None
    if rows:
        widths = {len(r) for r in rows if r}
        consistent = len(widths) <= 1 and (max(widths) if widths else 0) > 1
    return {"text": text, "csv_consistent": consistent, "extractable": bool(text.strip())}


def _parse_html(data: bytes) -> dict:
    raw = data.decode("utf-8", "ignore")
    headings = len(re.findall(r"<h[1-6][\s>]", raw, re.IGNORECASE))
    text = _strip_xml(raw)
    return {"text": text, "heading_count": headings, "extractable": bool(text.strip())}


def _parse_docx(data: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    headings = len(re.findall(r'w:val="Heading', xml))
    # 以段落結尾還原換行，保留切塊用的段落邊界
    xml = xml.replace("</w:p>", "\n")
    text = _strip_xml(xml).strip()
    return {"text": text, "heading_count": headings, "extractable": bool(text)}


def _parse_xlsx(data: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        shared = ""
        if "xl/sharedStrings.xml" in names:
            shared_xml = z.read("xl/sharedStrings.xml").decode("utf-8", "ignore")
            shared = " ".join(re.findall(r"<t[^>]*>(.*?)</t>", shared_xml, re.DOTALL))
        merged = 0
        for n in names:
            if n.startswith("xl/worksheets/") and n.endswith(".xml"):
                ws = z.read(n).decode("utf-8", "ignore")
                merged += len(re.findall(r"<mergeCell ", ws))
    return {"text": shared, "merged_cells": merged, "extractable": bool(shared.strip())}


def _parse_pptx(data: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        slides = [n for n in z.namelist()
                  if re.match(r"ppt/slides/slide\d+\.xml$", n)]
        chunks = []
        for n in slides:
            xml = z.read(n).decode("utf-8", "ignore")
            chunks.append(" ".join(re.findall(r"<a:t>(.*?)</a:t>", xml, re.DOTALL)))
    text = "\n\n".join(c for c in chunks if c.strip())
    return {"text": text, "pages": len(slides), "extractable": bool(text.strip())}


def _parse_pdf(data: bytes) -> dict:
    encrypted = b"/Encrypt" in data
    pages = len(re.findall(rb"/Type\s*/Page[^s]", data))
    if pages == 0:
        counts = [int(x) for x in re.findall(rb"/Count\s+(\d+)", data)]
        pages = max(counts) if counts else 1
    text_chars = 0
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL):
        raw = m.group(1)
        try:
            import zlib
            content = zlib.decompress(raw)
        except Exception:
            content = raw
        for tm in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)\s*(?:Tj|'|\")", content):
            text_chars += len(tm.group(1))
        for tm in re.finditer(rb"\[(.*?)\]\s*TJ", content, re.DOTALL):
            for sm in re.finditer(rb"\(((?:[^()\\]|\\.)*)\)", tm.group(1)):
                text_chars += len(sm.group(1))
    extractable = (not encrypted) and text_chars > 0
    is_scanned = (not encrypted) and text_chars == 0
    return {
        "text": "x" * min(text_chars, _TEXT_SAMPLE_LIMIT),  # 佔位，PDF 內容不外存
        "char_count": text_chars,
        "pages": pages,
        "encrypted": encrypted,
        "is_scanned_pdf": is_scanned,
        "extractable": extractable,
    }


_PARSERS = {
    ".txt": _parse_text,
    ".md": _parse_text,
    ".markdown": _parse_text,
    ".csv": _parse_csv,
    ".html": _parse_html,
    ".htm": _parse_html,
    ".docx": _parse_docx,
    ".xlsx": _parse_xlsx,
    ".pptx": _parse_pptx,
    ".pdf": _parse_pdf,
}


def analyze_file(path: Path) -> FileInfo:
    ext = path.suffix.lower()
    try:
        stat = path.stat()
        size, mtime = stat.st_size, stat.st_mtime
    except OSError:
        size, mtime = 0, 0.0

    info = FileInfo(path=path, ext=ext, size=size, mtime=mtime)

    if ext not in rules.SUPPORTED_EXTS:
        info.supported = False
        info.note = "unsupported format"
        return info

    parser = _PARSERS[ext]
    try:
        data = path.read_bytes()
        result = parser(data)
    except Exception as exc:  # noqa: BLE001 - 任何解析錯誤都記為 corrupt
        info.corrupt = True
        info.extractable = False
        info.note = f"parse error: {type(exc).__name__}"
        return info

    for key, value in result.items():
        setattr(info, key, value)

    text = info.text or ""
    if info.char_count == 0:
        info.char_count = len(text)
    info.text = text[:_TEXT_SAMPLE_LIMIT]
    if info.extractable and ext != ".pdf":
        info.content_hash = _norm_hash(text)
    return info
