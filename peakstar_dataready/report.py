"""Render the Report to self-contained HTML, JSON, and a terminal summary.

報告為單一 HTML 檔（內嵌 CSS，可離線開、可列印成 PDF），套 Peakstar 品牌色。
文案不使用 em-dash。
"""

from __future__ import annotations

import dataclasses
import html
import json
from pathlib import Path

from . import i18n
from .analyze import Report

TOOL = "dataready"

LIGHT_COLOR = {"green": "#2E7D32", "yellow": "#E07B39", "red": "#C62828"}
SEV_COLOR = {"high": "#C62828", "medium": "#E07B39", "low": "#3B5EA6"}

# 品牌色：深藍 #0D1F3C / #1E3A5F，鈷藍 #3B5EA6，琥珀 #E07B39
_CSS = """
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, "Segoe UI", "Microsoft JhengHei", sans-serif;
       color: #0D1F3C; background: #f4f6fa; line-height: 1.6; }
.wrap { max-width: 860px; margin: 0 auto; padding: 32px 24px 64px; }
header { background: linear-gradient(135deg, #0D1F3C, #1E3A5F); color: #fff;
         border-radius: 16px; padding: 28px 32px; }
header h1 { margin: 0 0 4px; font-size: 26px; }
header .sub { color: #b9c6dd; font-size: 14px; }
header .meta { margin-top: 14px; font-size: 13px; color: #cdd8ea; }
.gauge { text-align: center; margin: 28px 0; }
.gauge .score { font-size: 72px; font-weight: 800; line-height: 1; }
.gauge .max { font-size: 22px; color: #5b6b85; }
.badge { display: inline-block; padding: 6px 16px; border-radius: 999px; color: #fff;
         font-weight: 700; font-size: 15px; margin-top: 10px; }
.lead { text-align: center; max-width: 620px; margin: 10px auto 0; color: #1E3A5F; }
.cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin: 24px 0; }
.card { background: #fff; border-radius: 12px; padding: 16px 18px;
        border-left: 6px solid #ccc; box-shadow: 0 1px 3px rgba(13,31,60,.06); }
.card h3 { margin: 0 0 4px; font-size: 16px; display: flex; justify-content: space-between; }
.card .dimscore { font-weight: 800; }
.card p { margin: 0; font-size: 13px; color: #5b6b85; }
.card .bar { height: 7px; border-radius: 4px; background: #e6eaf2; margin-top: 10px; overflow: hidden; }
.card .bar > i { display: block; height: 100%; }
section h2 { font-size: 18px; border-bottom: 2px solid #3B5EA6; padding-bottom: 6px;
             margin-top: 32px; }
.finding { background: #fff; border-radius: 10px; padding: 12px 16px; margin: 10px 0;
           border-left: 5px solid #999; }
.finding .sev { font-size: 11px; font-weight: 700; color: #fff; padding: 2px 8px;
                border-radius: 6px; margin-right: 8px; }
.means { background: #fff7f0; border: 1px solid #f0d6bf; border-radius: 12px; padding: 18px 22px; }
.means .big { font-size: 30px; font-weight: 800; color: #C0531B; }
.cta { margin-top: 32px; background: #fff; border: 1px solid #d9e0ec;
       border-left: 6px solid #3B5EA6; border-radius: 12px; padding: 22px 26px; }
.cta h2 { color: #1E3A5F; border: 0; margin: 0 0 8px; font-size: 17px; }
.cta p { color: #5b6b85; max-width: 640px; margin: 0 0 12px; }
.cta a { color: #3B5EA6; text-decoration: none; font-weight: 700; }
.cta .link { display: block; margin-top: 8px; font-size: 12px; color: #9aa6bd; word-break: break-all; }
footer { margin-top: 28px; font-size: 12px; color: #7c8aa3; text-align: center; }
@media (max-width: 600px) { .cards { grid-template-columns: 1fr; } }
"""


def _esc(s: object) -> str:
    return html.escape(str(s))


def render_findings_text(report: Report, lang: str) -> list[str]:
    tmpls = i18n.FINDINGS[lang]
    out = []
    for f in report.findings:
        tmpl = tmpls.get(f["code"], f["code"])
        try:
            out.append(tmpl.format(**f))
        except Exception:
            out.append(tmpl)
    return out


def to_html(report: Report, lang: str = "zh") -> str:
    ui = i18n.UI[lang]
    names = i18n.DIM_NAMES[lang]
    descs = i18n.DIM_DESC[lang]
    light = report.light
    color = LIGHT_COLOR[light]

    cards = []
    for d in report.dimensions:
        dcolor = LIGHT_COLOR[_light(d.score)]
        cards.append(
            f'<div class="card" style="border-left-color:{dcolor}">'
            f'<h3><span>{_esc(names[d.key])}</span>'
            f'<span class="dimscore" style="color:{dcolor}">{d.score:.0f}</span></h3>'
            f'<p>{_esc(descs[d.key])}</p>'
            f'<div class="bar"><i style="width:{max(2, d.score):.0f}%;background:{dcolor}"></i></div>'
            f'</div>'
        )

    finding_lines = render_findings_text(report, lang)
    if finding_lines:
        fblocks = []
        for f, text in zip(report.findings, finding_lines):
            sc = SEV_COLOR[f["severity"]]
            fblocks.append(
                f'<div class="finding" style="border-left-color:{sc}">'
                f'<span class="sev" style="background:{sc}">{f["severity"].upper()}</span>'
                f'{_esc(text)}</div>'
            )
        findings_html = "".join(fblocks)
    else:
        findings_html = f'<p>{_esc(ui["no_findings"])}</p>'

    wl_word = ui["workload_word"][report.workload]
    url = i18n.consult_url(TOOL, light)
    cta_body = i18n.CTA_BODY[lang][light]

    parts = [
        "<!doctype html><html lang=\"", lang, "\"><head><meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"<title>{_esc(ui['title'])} - Peakstar</title>",
        "<style>", _CSS, "</style></head><body><div class=\"wrap\">",
        "<header><h1>", _esc(ui["title"]), "</h1>",
        "<div class=\"sub\">", _esc(ui["subtitle"]), "</div>",
        "<div class=\"meta\">",
        _esc(ui["scanned_target"]), ": ", _esc(report.root), " &nbsp;|&nbsp; ",
        _esc(ui["generated"]), ": ", _esc(report.generated_at), " &nbsp;|&nbsp; ",
        _esc(ui["files"]), ": ", str(report.file_count), " (",
        _esc(ui["supported"]), " ", str(report.supported_count), " / ",
        _esc(ui["unsupported"]), " ", str(report.unsupported_count), ")",
        "</div></header>",
        "<div class=\"gauge\"><div class=\"score\" style=\"color:", color, "\">",
        f"{report.total_score:.0f}", "</div><div class=\"max\">/ 100 &nbsp;",
        _esc(ui["total"]), "</div>",
        "<div class=\"badge\" style=\"background:", color, "\">",
        _esc(i18n.LIGHT_WORD[lang][light]), "</div></div>",
        "<section><h2>", _esc(ui["dimensions"]), "</h2>",
        "<div class=\"cards\">", "".join(cards), "</div></section>",
        "<section><h2>", _esc(ui["findings"]), "</h2>", findings_html, "</section>",
        "<section><h2>", _esc(ui["means"]), "</h2><div class=\"means\">",
        "<div class=\"big\">", str(report.expected_failure_rate), "%</div>",
        "<div>", _esc(ui["failure_rate"]), "</div>",
        "<div style=\"margin-top:10px\">", _esc(ui["workload"]), ": <b>", _esc(wl_word),
        "</b></div></div></section>",
        "<div class=\"cta\"><h2>", _esc(ui["cta_title"]), "</h2><p>", _esc(cta_body),
        "</p><a href=\"", url, "\">", _esc(i18n.CTA_BUTTON[lang]), "</a>",
        "<span class=\"link\">", url, "</span></div>",
        "<footer>", _esc(ui["disclaimer"]), "<br>", _esc(ui["about"]),
        " &nbsp;|&nbsp; DataReady v", _version(), "</footer>",
        "</div></body></html>",
    ]
    return "".join(parts)


def to_json(report: Report, lang: str = "zh") -> str:
    data = dataclasses.asdict(report)
    data["tool"] = TOOL
    data["version"] = _version()
    data["findings_text"] = render_findings_text(report, lang)
    data["consult_url"] = i18n.consult_url(TOOL, report.light)
    return json.dumps(data, ensure_ascii=False, indent=2)


def terminal_summary(report: Report, lang: str = "zh") -> str:
    ui = i18n.UI[lang]
    names = i18n.DIM_NAMES[lang]
    lines = [
        "",
        f"  {ui['title']}  ({i18n.LIGHT_WORD[lang][report.light]})",
        f"  {ui['total']}: {report.total_score:.0f}/100",
        f"  {ui['failure_rate']}: {report.expected_failure_rate}%",
        "  " + "-" * 44,
    ]
    for d in report.dimensions:
        lines.append(f"  {names[d.key]:<8} {d.score:5.0f}/100   (w={d.weight:.0%})")
    lines.append("  " + "-" * 44)
    for text in render_findings_text(report, lang):
        lines.append(f"  ! {text}")
    return "\n".join(lines)


def write_reports(report: Report, out_dir: Path, formats: list[str], lang: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    if "html" in formats:
        p = out_dir / "report.html"
        p.write_text(to_html(report, lang), encoding="utf-8")
        written.append(p)
    if "json" in formats:
        p = out_dir / "report.json"
        p.write_text(to_json(report, lang), encoding="utf-8")
        written.append(p)
    return written


def _light(score: float) -> str:
    from . import rules
    return rules.light_for(score)


def _version() -> str:
    from . import __version__
    return __version__
