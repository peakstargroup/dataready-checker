"""繁中 / English strings for report rendering. 預設繁中。"""

DIM_NAMES = {
    "zh": {
        "extractability": "可讀取性",
        "structure": "結構化程度",
        "chunkability": "切塊友善度",
        "redundancy": "重複與一致性",
        "freshness": "新鮮度",
        "metadata": "元資料與可追溯",
    },
    "en": {
        "extractability": "Extractability",
        "structure": "Structure",
        "chunkability": "Chunkability",
        "redundancy": "Redundancy",
        "freshness": "Freshness",
        "metadata": "Metadata",
    },
}

DIM_DESC = {
    "zh": {
        "extractability": "文字能否被機器抽出（vs 掃描影像 / 加密 / 損毀）",
        "structure": "有無標題層級、表格是否規整、版面是否一致",
        "chunkability": "文件長度與語意邊界是否利於切塊",
        "redundancy": "重複 / 近似重複檔比例、版本是否混亂",
        "freshness": "內容是否夠新、過期比例",
        "metadata": "檔名是否有語意、目錄是否有組織",
    },
    "en": {
        "extractability": "Can machines extract the text (vs scanned image / encrypted / corrupt)",
        "structure": "Headings, table regularity, layout consistency",
        "chunkability": "Document length and semantic boundaries suit chunking",
        "redundancy": "Exact / near duplicate ratio, version sprawl",
        "freshness": "Recency of content, share of stale files",
        "metadata": "Filename semantics and directory organization",
    },
}

LIGHT_WORD = {
    "zh": {"green": "綠燈", "yellow": "黃燈", "red": "紅燈"},
    "en": {"green": "Green", "yellow": "Yellow", "red": "Red"},
}

# findings: code -> 模板（以 .format(**finding) 帶入數值）
FINDINGS = {
    "zh": {
        "LOW_EXTRACTABILITY": "{pct}% 的檔案無法被機器抽取文字（掃描影像 / 加密 / 損毀）。模型讀不到的內容，等於不存在。",
        "SCANNED_PDF": "偵測到 {count} 份疑似掃描影像 PDF。沒有 OCR 前，這些文件對 AI 是黑的。",
        "LOW_STRUCTURE": "文件結構化程度偏低（{score}/100）。缺少標題層級會讓檢索切出語意破碎的片段。",
        "OVERSIZED_CHUNK": "{count} 份文件過長且缺乏分段。一次塞太多會稀釋重點，反而升高幻覺。",
        "TINY_FRAGMENTS": "{count} 份檔案過於碎小，單獨切塊缺乏脈絡。",
        "HIGH_DUPLICATION": "約 {pct}% 內容為重複 / 近似重複。重複資料會讓檢索回傳互相打架的版本。",
        "STALE_DATA": "約 {pct}% 檔案超過兩年未更新。過期內容是『統計上相關但事實已錯』的主要來源。",
        "BAD_FILENAMES": "約 {pct}% 檔名缺乏語意（如『最終版_v3』『未命名』）。難以標註來源與建立可追溯性。",
    },
    "en": {
        "LOW_EXTRACTABILITY": "{pct}% of files yield no machine-extractable text (scanned image / encrypted / corrupt). What the model cannot read does not exist.",
        "SCANNED_PDF": "{count} likely scanned-image PDFs detected. Without OCR, these are invisible to the AI.",
        "LOW_STRUCTURE": "Low structural quality ({score}/100). Missing headings make retrieval cut semantically broken fragments.",
        "OVERSIZED_CHUNK": "{count} documents are long and unsegmented. Dumping too much dilutes signal and raises hallucination.",
        "TINY_FRAGMENTS": "{count} files are too small to carry context on their own.",
        "HIGH_DUPLICATION": "About {pct}% of content is duplicate / near-duplicate. Duplicates make retrieval return conflicting versions.",
        "STALE_DATA": "About {pct}% of files are over two years old. Stale content is the main source of 'statistically relevant but factually wrong'.",
        "BAD_FILENAMES": "About {pct}% of filenames lack meaning (e.g. 'final_v3', 'untitled'). Hard to attribute sources and build traceability.",
    },
}

UI = {
    "zh": {
        "title": "資料準備度健檢報告",
        "subtitle": "在你花錢做 AI 之前，先看你的資料夠不夠格餵 AI",
        "scanned_target": "掃描標的",
        "generated": "產生時間",
        "total": "資料準備度總分",
        "dimensions": "六大維度",
        "findings": "重點發現",
        "no_findings": "未發現重大紅旗。資料基礎良好，建議直接進入場景設計。",
        "means": "這代表什麼",
        "failure_rate": "以目前資料直接做 RAG 的預期失敗率（概略估計）",
        "workload": "預估資料整備工作量級（概略，非報價）",
        "files": "檔案總數",
        "supported": "可分析檔",
        "unsupported": "不支援格式",
        "score": "分數",
        "weight": "權重",
        "cta_title": "下一步：從健檢到落地",
        "disclaimer": "本報告為自動化診斷，採保守估計，僅供參考，不構成保證。所有分析皆於本機執行，未上傳任何檔案內容。",
        "about": "Peakstar（品得網絡數位）：AI 顧問與工程交付，專注台灣與日本中小企業數位轉型。",
        "workload_word": {"S": "小", "M": "中", "L": "大"},
    },
    "en": {
        "title": "Data Readiness Report",
        "subtitle": "Before you spend on AI, see if your data is ready to feed it",
        "scanned_target": "Scanned target",
        "generated": "Generated",
        "total": "Data Readiness Score",
        "dimensions": "Six Dimensions",
        "findings": "Top Findings",
        "no_findings": "No major red flags found. Your data foundation looks solid; proceed to scenario design.",
        "means": "What this means",
        "failure_rate": "Expected RAG failure rate on current data (rough estimate)",
        "workload": "Estimated data-prep workload (rough, not a quote)",
        "files": "Total files",
        "supported": "Analyzable",
        "unsupported": "Unsupported",
        "score": "Score",
        "weight": "Weight",
        "cta_title": "Next step: from check-up to delivery",
        "disclaimer": "This report is an automated, conservative diagnostic for reference only and is not a guarantee. All analysis runs locally; no file content is uploaded.",
        "about": "Peakstar: AI consulting and engineering delivery, focused on SME digital transformation in Taiwan and Japan.",
        "workload_word": {"S": "Small", "M": "Medium", "L": "Large"},
    },
}

CTA_BODY = {
    "zh": {
        "red": "你的資料準備度為紅燈。資料整備高度依賴產業脈絡，也是 AI 專案成敗的關鍵。這份報告先讓你看見問題在哪；把又髒又散的資料變成可用資產，正是 Peakstar 在台日中小企業每天在做的事。",
        "yellow": "你的資料準備度為黃燈：已有基礎，但仍有明顯缺口。在投入 AI 前補強資料，能大幅降低失敗率。需要時，歡迎參考 Peakstar 的做法。",
        "green": "你的資料準備度為綠燈，基礎良好。下一步是把資料優勢轉成可驗收的 AI 場景。",
    },
    "en": {
        "red": "Your data readiness is Red. Data prep depends heavily on industry context and is where AI projects are won or lost. This report shows you where the gaps are; turning messy, scattered data into a usable asset is the work Peakstar does with SMEs in Taiwan and Japan.",
        "yellow": "Your data readiness is Yellow: a base exists but with clear gaps. Fixing data before investing in AI sharply lowers failure rates.",
        "green": "Your data readiness is Green, a solid base. The next step is turning that data advantage into verifiable AI use cases.",
    },
}

CTA_BUTTON = {"zh": "了解 Peakstar 的做法", "en": "How Peakstar approaches this"}


def consult_url(tool: str, light: str) -> str:
    # 單一、低調的來源標記。開源預設版不埋 campaign / 燈號層級追蹤，
    # 這只是讓官網看得到 DataReady 帶來的流量。
    return "https://www.peakstargroup.com/?ref=dataready"
