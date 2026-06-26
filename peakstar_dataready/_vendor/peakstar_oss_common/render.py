"""把 ReportDoc 渲染成自包含 HTML、JSON、終端摘要。

報告為單一 HTML 檔（內嵌 CSS，可離線開、可列印成 PDF），套 Peakstar 品牌色。
文案不使用 em-dash。此模組為三個開源工具共用，確保品牌與行為一致。
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .brand import LIGHT_COLOR, SEV_COLOR, light_for
from .model import ReportDoc

# 品牌色：深藍 #0D1F3C / #1E3A5F、青綠(teal) #43B2A1、琥珀 #E07B39
_CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, "Segoe UI", "Microsoft JhengHei", sans-serif;
       color: #1B2B33; background: #F4F8F7; line-height: 1.6; }
.wrap { max-width: 860px; margin: 0 auto; padding: 32px 24px 64px; }
header { background: linear-gradient(135deg, #22577A, #2E8C8C); color: #fff;
         border-radius: 16px; padding: 28px 32px; }
header h1 { margin: 0 0 4px; font-size: 26px; }
header .sub { color: #b9c6dd; font-size: 14px; }
header .meta { margin-top: 14px; font-size: 13px; color: #cdd8ea; }
.gauge { text-align: center; margin: 28px 0; }
.gauge .score { font-size: 72px; font-weight: 800; line-height: 1; }
.gauge .max { font-size: 22px; color: #5b6b85; }
.badge { display: inline-block; padding: 6px 16px; border-radius: 999px; color: #fff;
         font-weight: 700; font-size: 15px; margin-top: 10px; }
.cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin: 24px 0; }
.card { background: #fff; border-radius: 12px; padding: 16px 18px;
        border-left: 6px solid #ccc; box-shadow: 0 1px 3px rgba(13,31,60,.06); }
.card h3 { margin: 0 0 4px; font-size: 16px; color: #22577A; display: flex; justify-content: space-between; }
.card .dimscore { font-weight: 800; }
.card p { margin: 0; font-size: 13px; color: #5b6b85; }
.card .bar { height: 7px; border-radius: 4px; background: #e6eaf2; margin-top: 10px; overflow: hidden; }
.card .bar > i { display: block; height: 100%; }
section h2 { font-size: 18px; color: #22577A; border-bottom: 2px solid #43B2A1; padding-bottom: 6px;
             margin-top: 32px; }
.finding { background: #fff; border-radius: 10px; padding: 12px 16px; margin: 10px 0;
           border-left: 5px solid #999; }
.finding .sev { font-size: 11px; font-weight: 700; color: #fff; padding: 2px 8px;
                border-radius: 6px; margin-right: 8px; }
.means { background: #fff7f0; border: 1px solid #f0d6bf; border-radius: 12px; padding: 18px 22px; }
.means .big { font-size: 30px; font-weight: 800; color: #B0791E; }
.cta { margin-top: 32px; background: #fff; border: 1px solid #d9e0ec;
       border-left: 6px solid #43B2A1; border-radius: 12px; padding: 22px 26px; }
.cta h2 { color: #22577A; border: 0; margin: 0 0 8px; font-size: 17px; }
.cta p { color: #5b6b85; max-width: 640px; margin: 0 0 12px; }
.cta a { color: #43B2A1; text-decoration: none; font-weight: 700; }
.cta .link { display: block; margin-top: 8px; font-size: 12px; color: #9aa6bd; word-break: break-all; }
footer { margin-top: 28px; font-size: 12px; color: #7c8aa3; text-align: center; }
@media (max-width: 600px) { .cards { grid-template-columns: 1fr; } }
"""


def _esc(s: object) -> str:
    return html.escape(str(s))


def _light(doc: ReportDoc, score: float) -> str:
    return light_for(score, doc.green_min, doc.yellow_min)


def to_html(doc: ReportDoc) -> str:
    light = _light(doc, doc.total_score)
    color = LIGHT_COLOR[light]

    cards = []
    for d in doc.dimensions:
        dcolor = LIGHT_COLOR[_light(doc, d.score)]
        cards.append(
            f'<div class="card" style="border-left-color:{dcolor}">'
            f'<h3><span>{_esc(d.name)}</span>'
            f'<span class="dimscore" style="color:{dcolor}">{d.score:.0f}</span></h3>'
            f'<p>{_esc(d.desc)}</p>'
            f'<div class="bar"><i style="width:{max(2, d.score):.0f}%;background:{dcolor}"></i></div>'
            f'</div>'
        )

    if doc.findings:
        fblocks = []
        for f in doc.findings:
            sc = SEV_COLOR.get(f.severity, "#999")
            fblocks.append(
                f'<div class="finding" style="border-left-color:{sc}">'
                f'<span class="sev" style="background:{sc}">{_esc(f.severity.upper())}</span>'
                f'{_esc(f.text)}</div>'
            )
        findings_html = "".join(fblocks)
    else:
        findings_html = f'<p>{_esc(doc.no_findings_text)}</p>'

    meta_html = " &nbsp;|&nbsp; ".join(
        f"{_esc(label)}: {_esc(value)}" for label, value in doc.meta
    )

    means_inner = []
    if doc.means_stat is not None:
        means_inner.append(f'<div class="big">{_esc(doc.means_stat.value)}</div>')
        means_inner.append(f'<div>{_esc(doc.means_stat.label)}</div>')
    for label, value in doc.means_rows:
        means_inner.append(
            f'<div style="margin-top:10px">{_esc(label)}: <b>{_esc(value)}</b></div>'
        )

    parts = [
        '<!doctype html><html lang="', _esc(doc.lang), '"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_esc(doc.title)} - Peakstar</title>",
        "<style>", _CSS, "</style></head><body><div class=\"wrap\">",
        "<header><h1>", _esc(doc.title), "</h1>",
        '<div class="sub">', _esc(doc.subtitle), "</div>",
        '<div class="meta">', meta_html, "</div></header>",
        '<div class="gauge"><div class="score" style="color:', color, '">',
        f"{doc.total_score:.0f}", '</div><div class="max">/ 100 &nbsp;',
        _esc(doc.score_caption), "</div>",
        '<div class="badge" style="background:', color, '">',
        _esc(doc.light_word), "</div></div>",
        "<section><h2>", _esc(doc.dimensions_heading), "</h2>",
        '<div class="cards">', "".join(cards), "</div></section>",
        "<section><h2>", _esc(doc.findings_heading), "</h2>", findings_html, "</section>",
    ]
    if means_inner:
        parts += [
            "<section><h2>", _esc(doc.means_heading), '</h2><div class="means">',
            "".join(means_inner), "</div></section>",
        ]
    parts += [
        '<div class="cta"><h2>', _esc(doc.cta.title), "</h2><p>", _esc(doc.cta.body),
        '</p><a href="', _esc(doc.cta.url), '">', _esc(doc.cta.button), "</a>",
        '<span class="link">', _esc(doc.cta.url), "</span></div>",
        "<footer>", _esc(doc.disclaimer), "<br>", _esc(doc.about),
        " &nbsp;|&nbsp; ", _esc(doc.tool), " v", _esc(doc.version), "</footer>",
        "</div></body></html>",
    ]
    return "".join(parts)


def to_json(doc: ReportDoc) -> str:
    light = _light(doc, doc.total_score)
    data = {
        "tool": doc.tool,
        "version": doc.version,
        "lang": doc.lang,
        "title": doc.title,
        "total_score": doc.total_score,
        "light": light,
        "dimensions": [
            {"key": d.key, "name": d.name, "desc": d.desc, "score": d.score}
            for d in doc.dimensions
        ],
        "findings": [{"severity": f.severity, "text": f.text} for f in doc.findings],
        "means": {
            "stat": (None if doc.means_stat is None
                     else {"value": doc.means_stat.value, "label": doc.means_stat.label}),
            "rows": [{"label": l, "value": v} for l, v in doc.means_rows],
        },
        "meta": [{"label": l, "value": v} for l, v in doc.meta],
        "cta": {"title": doc.cta.title, "body": doc.cta.body,
                "button": doc.cta.button, "url": doc.cta.url},
        "consult_url": doc.cta.url,
    }
    if doc.extra:
        data["extra"] = doc.extra
    return json.dumps(data, ensure_ascii=False, indent=2)


def terminal_summary(doc: ReportDoc) -> str:
    lines = [
        "",
        f"  {doc.title}  ({doc.light_word})",
        f"  {doc.score_caption}: {doc.total_score:.0f}/100",
    ]
    if doc.means_stat is not None:
        lines.append(f"  {doc.means_stat.label}: {doc.means_stat.value}")
    lines.append("  " + "-" * 44)
    for d in doc.dimensions:
        lines.append(f"  {d.name:<8} {d.score:5.0f}/100")
    lines.append("  " + "-" * 44)
    for f in doc.findings:
        lines.append(f"  ! {f.text}")
    return "\n".join(lines)


def write_reports(doc: ReportDoc, out_dir: Path, formats: list[str]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    if "html" in formats:
        p = out_dir / "report.html"
        p.write_text(to_html(doc), encoding="utf-8")
        written.append(p)
    if "json" in formats:
        p = out_dir / "report.json"
        p.write_text(to_json(doc), encoding="utf-8")
        written.append(p)
    return written
