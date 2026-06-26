"""測試資料工廠：用標準函式庫生成各格式的最小有效檔案。

說明（呼應任務「想一下需要哪些測試資料」）：
我們需要四類測試資料：
  1. clean   結構良好、近期、無重複  -> 應綠燈
  2. medium  部分問題                -> 應黃燈
  3. dirty   掃描檔/超長/重複/舊/亂名 -> 應紅燈
  4. edge    空資料夾 / 不支援格式 / 損毀檔
所有 fixture 皆於暫存目錄即時生成，mtime 以 os.utime 控制，確保測試可重現。
"""

from __future__ import annotations

import io
import os
import time
import zipfile
from pathlib import Path

DAY = 86400


def set_age(path: Path, days_old: float) -> None:
    t = time.time() - days_old * DAY
    os.utime(path, (t, t))


def write_text(folder: Path, name: str, content: str, days_old: float = 1) -> Path:
    p = folder / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    set_age(p, days_old)
    return p


def write_bytes(folder: Path, name: str, data: bytes, days_old: float = 1) -> Path:
    p = folder / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    set_age(p, days_old)
    return p


def _zip(members: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in members.items():
            z.writestr(name, content)
    return buf.getvalue()


def docx_bytes(text: str = "Body paragraph with enough words to count.",
               headings: int = 1) -> bytes:
    paras = []
    for i in range(headings):
        paras.append(
            f'<w:p><w:pPr><w:pStyle w:val="Heading{i+1}"/></w:pPr>'
            f'<w:r><w:t>Section {i+1}</w:t></w:r></w:p>'
        )
    paras.append(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>")
    body = "".join(paras)
    xml = f'<?xml version="1.0"?><w:document><w:body>{body}</w:body></w:document>'
    return _zip({"word/document.xml": xml})


def xlsx_bytes(strings: list[str] | None = None, merged: int = 0) -> bytes:
    strings = strings or ["Name", "Value", "Alpha", "Beta"]
    si = "".join(f"<si><t>{s}</t></si>" for s in strings)
    sst = f'<?xml version="1.0"?><sst>{si}</sst>'
    merge = "".join('<mergeCell ref="A1:B1"/>' for _ in range(merged))
    ws = f'<?xml version="1.0"?><worksheet><sheetData><row><c><v>0</v></c></row>' \
         f'</sheetData><mergeCells>{merge}</mergeCells></worksheet>'
    return _zip({"xl/sharedStrings.xml": sst, "xl/worksheets/sheet1.xml": ws})


def pptx_bytes(slides: list[str] | None = None) -> bytes:
    slides = slides or ["First slide title", "Second slide content"]
    members = {}
    for i, txt in enumerate(slides, 1):
        members[f"ppt/slides/slide{i}.xml"] = (
            f'<?xml version="1.0"?><p:sld><p:cSld><p:spTree>'
            f"<a:t>{txt}</a:t></p:spTree></p:cSld></p:sld>"
        )
    return _zip(members)


def html_text(headings: int = 1, body: str = "Readable html body text.") -> str:
    hs = "".join(f"<h{min(i+1,6)}>Heading {i+1}</h{min(i+1,6)}>" for i in range(headings))
    return f"<html><body>{hs}<p>{body}</p></body></html>"


def pdf_text_bytes(text: str = "Hello readable world this is extractable text.") -> bytes:
    safe = text.replace("(", "").replace(")", "")
    body = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type /Catalog>>endobj\n"
        b"2 0 obj<</Type /Page>>endobj\n"
        b"3 0 obj<</Length 60>>\nstream\n"
        + b"BT /F1 12 Tf (" + safe.encode("latin-1", "ignore") + b") Tj ET\n"
        + b"endstream\nendobj\n%%EOF\n"
    )
    return body


def pdf_scanned_bytes() -> bytes:
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type /Catalog>>endobj\n"
        b"2 0 obj<</Type /Page>>endobj\n"
        b"3 0 obj<</Subtype/Image /Length 20>>\nstream\n"
        b"/Im0 Do\xff\xd8\xff\xe0 binary\n"
        b"endstream\nendobj\n%%EOF\n"
    )


def long_unstructured(tokens: int = 4000) -> str:
    word = "lorem "
    return word * tokens  # 單一無分段超長區塊


# ---------- 整組資料夾 ----------

def _para(prefix: str, n: int = 6) -> str:
    return "".join(f"{prefix}說明內容第{i}點，描述具體做法與注意事項，長度足夠形成語意完整的段落。" for i in range(n))


def make_clean(root: Path) -> Path:
    d = root / "clean"
    md = (
        "# 產品導論\n\n" + _para("導論") + "\n\n"
        "## 安裝步驟\n\n" + _para("安裝") + "\n\n"
        "## 進階設定\n\n" + _para("設定") + "\n\n"
        "## 常見問題\n\n" + _para("問答") + "\n"
    )
    write_text(d / "handbook", "guide.md", md, days_old=10)
    rows = "name,age,city,plan\n" + "\n".join(
        f"User{i},{20+i},City{i%5},Plan{i%3}" for i in range(40))
    write_text(d / "data", "customers.csv", rows, days_old=5)
    long_body = _para("規格", 12)
    write_bytes(d, "product_spec.docx", docx_bytes(text=long_body, headings=3), days_old=8)
    write_bytes(d, "kickoff_slides.pptx",
                pptx_bytes(["專案願景與目標說明", "里程碑時程規劃", "團隊分工與責任"]), days_old=12)
    write_text(d, "faq.html", html_text(headings=3, body=_para("常見問答", 10)), days_old=3)
    return d


def make_medium(root: Path) -> Path:
    d = root / "medium"
    body = "# 報告\n\n" + ("段落內容。\n\n" * 5)
    write_text(d, "report.md", body, days_old=20)
    write_text(d, "report_copy.md", body, days_old=20)        # 重複 + 版本字樣
    write_text(d, "notes.txt", "一行接一行沒有分段的雜記" * 20, days_old=400)  # 低結構
    write_bytes(d, "untitled.docx", docx_bytes(headings=0), days_old=900)  # 通用名 + 無標題 + 偏舊
    write_text(d, "memo_v2.txt", "簡短備忘。\n\n第二段。", days_old=50)
    return d


def make_dirty(root: Path) -> Path:
    # 模擬中小企業常見的「堆滿掃描公文的共用磁碟」：多數是掃描影像 PDF、
    # 加上超長無結構檔、大量重複、檔名無語意、且多年未更新，全部堆在同一層。
    d = root / "dirty"
    for i in range(1, 9):  # 8 份掃描影像 PDF（AI 讀不到）
        write_bytes(d, f"scan{i:03d}.pdf", pdf_scanned_bytes(), days_old=1200 + i * 20)
    write_bytes(d, "加密文件.pdf", b"%PDF-1.4\n/Encrypt\n/Type /Page\n%%EOF\n", days_old=1400)
    write_text(d, "未命名.txt", long_unstructured(4000), days_old=2000)  # 超長無結構 + 過期 + 通用名
    write_bytes(d, "文件 - 複製.docx", docx_bytes(headings=0, text="短"), days_old=1500)
    write_text(d, "document1.txt", "x", days_old=2200)  # 碎檔 + 通用名 + 過期
    # 多份一模一樣的超長無分段傾印檔，檔名全是版本字樣
    dump = "重複內容沒有分段一直接下去" * 1500
    write_text(d, "final_最終版.txt", dump, days_old=2000)
    write_text(d, "final_最終版 (1).txt", dump, days_old=2000)
    write_text(d, "final_最終版 copy.txt", dump, days_old=2000)
    return d


def make_edge_unsupported(root: Path) -> Path:
    d = root / "edge"
    write_bytes(d, "archive.zip", b"PK\x03\x04 not really", days_old=1)
    write_bytes(d, "broken.docx", b"not a real zip at all", days_old=1)  # corrupt
    return d
