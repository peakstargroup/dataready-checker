"""Telemetry: 預設關閉，且絕不外送任何內容（三工具共用）。

隱私鐵則（共用設計系統第 3 節）：所有工具一律本機執行、零外送。即使使用者以
環境變數 PEAKSTAR_TELEMETRY=1 啟用，此實作也僅在本機記一筆『匿名事件計數』，
永不包含檔名、路徑、API 回應或任何使用者內容，也不連線。要接後端需另行整合，
且必須 opt-in。
"""

from __future__ import annotations

import os


def enabled() -> bool:
    return os.environ.get("PEAKSTAR_TELEMETRY", "0") == "1"


def record(event: str) -> None:
    """No-op by default. 只接受事件名稱字串，不接受任何使用者資料。"""
    if not enabled():
        return
    # 刻意不連線、不寫入內容。保留為未來 opt-in 後端整合的掛載點。
    return
