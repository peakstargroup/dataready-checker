"""peakstar-oss-common: Peakstar 開源工具組的共用報告與遙測底座。

零相依（純標準庫）。三個工具（DataReady / TrustLens / MCPGuard）共用同一套
報告外觀與隱私行為。各工具自行算分並建立 ReportDoc，交給此處渲染。

採 vendoring 散佈：各工具把本套件複製進自己的 package（見各工具 _vendor/），
維持「工具本身零相依」的品牌主張。本倉庫為單一真相來源。
"""

from __future__ import annotations

from . import brand, render, telemetry
from .model import Cta, Dimension, Finding, ReportDoc, Stat

__version__ = "0.1.0"

__all__ = [
    "brand",
    "render",
    "telemetry",
    "Cta",
    "Dimension",
    "Finding",
    "ReportDoc",
    "Stat",
    "__version__",
]
