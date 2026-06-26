"""Basic ruleset: thresholds, weights, patterns.

Open-core 邊界：此檔為公開的基礎規則包。針對特定產業的進階客製規則（金融/醫療/
公共關係/政府等的專屬閾值、同業基準與合規考量）需依場景客製，由 Peakstar 於合作
專案中提供，不在本開源倉庫內。
"""

import re

# 維度權重（總和 = 1.0），對應規格 01-spec-DataReady.md
WEIGHTS = {
    "extractability": 0.25,
    "structure": 0.20,
    "chunkability": 0.20,
    "redundancy": 0.15,
    "freshness": 0.10,
    "metadata": 0.10,
}

# 燈號門檻（共用設計系統 4.3）
GREEN_MIN = 80
YELLOW_MIN = 50  # 50..79 = 黃；< 50 = 紅

# 支援解析的副檔名
SUPPORTED_EXTS = {
    ".txt", ".md", ".markdown", ".csv",
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".html", ".htm",
}

# 切塊友善度的 token 估計（以 字元數 / 4 近似一個 token）
CHARS_PER_TOKEN = 4
OVERSIZED_SEGMENT_TOKENS = 2000   # 單一無分段區塊超過此值視為過長
TINY_DOC_TOKENS = 30              # 整份文件低於此值視為碎檔

# 新鮮度（天）
STALE_DAYS = 730        # 超過 2 年視為偏舊
VERY_STALE_DAYS = 1825  # 超過 5 年視為過期

# 檔名版本/重複字樣（中英）
VERSION_NAME_RE = re.compile(
    r"(?:[_\-\s]v\d+|final|最終|最终|定稿|完稿|copy|副本|複製|复制|\(\d+\)|[_\-\s]\d{8})",
    re.IGNORECASE,
)

# 低語意/通用檔名（會降低元資料分數）
GENERIC_NAME_RE = re.compile(
    r"^(?:document\d*|untitled|new\s*\w*|新增\w*|未命名\w*|新文件\w*|image\d*|img[_\-]?\d+|"
    r"scan\d*|dsc[_\-]?\d+|螢幕擷取|擷取畫面|\d+)$",
    re.IGNORECASE,
)


def light_for(score: float) -> str:
    """score (0..100) -> 'green' | 'yellow' | 'red'"""
    if score >= GREEN_MIN:
        return "green"
    if score >= YELLOW_MIN:
        return "yellow"
    return "red"


def workload_for(score: float) -> str:
    """概略估計資料整備工作量級 S/M/L（不構成報價）。"""
    if score >= GREEN_MIN:
        return "S"
    if score >= 60:
        return "M"
    return "L"


def expected_failure_rate(score: float) -> int:
    """把總分翻成『以目前資料直接做 RAG 的預期失敗率』(示意性推估，非統計預測)。

    係數刻意取保守值 0.35：寧可低估，避免被解讀為危言聳聽。
    """
    rate = round((100 - score) * 0.35)
    return max(5, min(95, rate))
