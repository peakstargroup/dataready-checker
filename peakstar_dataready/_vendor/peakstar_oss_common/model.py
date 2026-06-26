"""共用報告資料模型。

設計原則：common 對任何工具的領域邏輯一無所知。各工具自行算分、決定維度與
findings、把所有「已在地化」的字串塞進這個 ReportDoc，再交給 render 產報告。
這樣同一個報告外觀就能服務 DataReady / TrustLens / MCPGuard 三個工具。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Dimension:
    """一個評分維度。name / desc 為已在地化字串。"""
    key: str
    name: str
    desc: str
    score: float


@dataclass
class Finding:
    """一條重點發現。severity 為 high|medium|low；text 為已在地化整句。"""
    severity: str
    text: str


@dataclass
class Stat:
    """『這代表什麼』區塊的主數字（例如預期失敗率）。"""
    value: str
    label: str


@dataclass
class Cta:
    title: str
    body: str
    button: str
    url: str


@dataclass
class ReportDoc:
    """一份報告的完整、已在地化、可直接渲染的模型。

    各工具負責把領域結果翻成這個結構；render 只管畫，不做判斷。
    """
    tool: str
    version: str
    lang: str
    title: str
    subtitle: str
    total_score: float
    light_word: str                       # 總分燈號的在地化詞（綠燈 / Green ...）
    score_caption: str                    # 儀表下方說明（資料準備度總分 ...）
    dimensions: list[Dimension]
    dimensions_heading: str
    findings: list[Finding]
    findings_heading: str
    no_findings_text: str
    means_heading: str
    cta: Cta
    disclaimer: str
    about: str
    meta: list[tuple[str, str]] = field(default_factory=list)   # 頁首 label:value
    means_stat: Stat | None = None        # 主數字（可無）
    means_rows: list[tuple[str, str]] = field(default_factory=list)  # 額外 label:value
    green_min: int = 80
    yellow_min: int = 50
    extra: dict = field(default_factory=dict)  # 工具專屬、給機器整合的結構化資料（不影響 HTML）
