"""把 DataReady 的分析結果轉成共用報告並渲染。

報告外觀與 JSON / 終端格式由共用底座 peakstar_oss_common 提供（見 _vendor/），
三個 Peakstar 開源工具共用同一套品牌一致的報告。本檔只負責把 DataReady 領域
結果（analyze.Report + i18n 在地化字串）翻成共用的 ReportDoc。文案不使用 em-dash。
"""

from __future__ import annotations

from pathlib import Path

from . import i18n, rules
from ._vendor.peakstar_oss_common import render as common_render
from ._vendor.peakstar_oss_common.model import Cta, Dimension, Finding, ReportDoc, Stat
from .analyze import Report

TOOL = "dataready"


def _version() -> str:
    from . import __version__
    return __version__


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


def _build_doc(report: Report, lang: str) -> ReportDoc:
    ui = i18n.UI[lang]
    names = i18n.DIM_NAMES[lang]
    descs = i18n.DIM_DESC[lang]

    dimensions = [
        Dimension(key=d.key, name=names[d.key], desc=descs[d.key], score=d.score)
        for d in report.dimensions
    ]
    findings = [
        Finding(severity=f["severity"], text=text)
        for f, text in zip(report.findings, render_findings_text(report, lang))
    ]
    meta = [
        (ui["scanned_target"], report.root),
        (ui["generated"], report.generated_at),
        (ui["files"],
         f'{report.file_count} ({ui["supported"]} {report.supported_count}'
         f' / {ui["unsupported"]} {report.unsupported_count})'),
    ]
    cta = Cta(
        title=ui["cta_title"],
        body=i18n.CTA_BODY[lang][report.light],
        button=i18n.CTA_BUTTON[lang],
        url=i18n.consult_url(TOOL, report.light),
    )
    extra = {
        "expected_failure_rate": report.expected_failure_rate,
        "workload": report.workload,
        "dimension_weights": {d.key: d.weight for d in report.dimensions},
        "stats": report.stats,
        "file_count": report.file_count,
        "supported_count": report.supported_count,
        "unsupported_count": report.unsupported_count,
        "text_file_count": report.text_file_count,
        "root": report.root,
        "generated_at": report.generated_at,
    }

    return ReportDoc(
        tool=TOOL,
        version=_version(),
        lang=lang,
        title=ui["title"],
        subtitle=ui["subtitle"],
        total_score=report.total_score,
        light_word=i18n.LIGHT_WORD[lang][report.light],
        score_caption=ui["total"],
        dimensions=dimensions,
        dimensions_heading=ui["dimensions"],
        findings=findings,
        findings_heading=ui["findings"],
        no_findings_text=ui["no_findings"],
        means_heading=ui["means"],
        means_stat=Stat(value=f"{report.expected_failure_rate}%", label=ui["failure_rate"]),
        means_rows=[(ui["workload"], ui["workload_word"][report.workload])],
        cta=cta,
        disclaimer=ui["disclaimer"],
        about=ui["about"],
        meta=meta,
        green_min=rules.GREEN_MIN,
        yellow_min=rules.YELLOW_MIN,
        extra=extra,
    )


def to_html(report: Report, lang: str = "zh") -> str:
    return common_render.to_html(_build_doc(report, lang))


def to_json(report: Report, lang: str = "zh") -> str:
    return common_render.to_json(_build_doc(report, lang))


def terminal_summary(report: Report, lang: str = "zh") -> str:
    return common_render.terminal_summary(_build_doc(report, lang))


def write_reports(report: Report, out_dir: Path, formats: list[str], lang: str) -> list[Path]:
    return common_render.write_reports(_build_doc(report, lang), out_dir, formats)
