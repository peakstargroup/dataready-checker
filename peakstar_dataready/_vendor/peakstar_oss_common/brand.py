"""Peakstar 共用品牌常數與燈號邏輯。

品牌規則（嚴格）：文案不使用 em-dash。品牌色：深藍 #0D1F3C / #1E3A5F、
鈷藍 #3B5EA6、琥珀 #E07B39。三個開源工具共用同一套報告外觀以維持品牌一致。
"""

from __future__ import annotations

# 燈號顏色與嚴重度顏色
LIGHT_COLOR = {"green": "#2E7D32", "yellow": "#E07B39", "red": "#C62828"}
SEV_COLOR = {"high": "#C62828", "medium": "#E07B39", "low": "#3B5EA6"}

# 共用預設燈號門檻（各工具可於建立 ReportDoc 時覆寫，例如安全工具採較嚴門檻）
DEFAULT_GREEN_MIN = 80
DEFAULT_YELLOW_MIN = 50


def light_for(score: float, green_min: int = DEFAULT_GREEN_MIN,
              yellow_min: int = DEFAULT_YELLOW_MIN) -> str:
    """score (0..100) -> 'green' | 'yellow' | 'red'."""
    if score >= green_min:
        return "green"
    if score >= yellow_min:
        return "yellow"
    return "red"
