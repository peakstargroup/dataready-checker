<div align="center">

# DataReady

### 在你花一塊錢做 AI 之前，先花 30 秒看你的資料夠不夠格餵 AI

**資料準備度健檢 ｜ 零相依 ｜ 本機執行、零外送 ｜ 一頁 board-ready 報告**

[繁體中文](README.md) ｜ [English](README.en.md)

`Python 3.11+` ｜ `MIT License` ｜ `0 dependencies` ｜ by [Peakstar 品得網絡數位](https://www.peakstargroup.com)

</div>

---

## 給 CTO / CIO 的一個不舒服的事實

大多數企業 AI 專案失敗，不是輸在模型，是輸在資料。

你看到的是一場很厲害的 RAG / 知識庫 demo。你看不到的是：demo 用的是乾淨樣本，而你公司真正的資料是掃描影像 PDF、東一份西一份的 Excel、十個版本的「最終版」、五年沒人更新的共用磁碟。把這種資料接上 AI，得到的不是智慧，是「一本正經地胡說」。

問題是：**在你簽下預算、立下 KPI 之前，沒有人能先量出你的資料到底有多糟。**

DataReady 就是來做這件事的。它是一支體溫計，不是藥。30 秒內，把抽象的「我的資料好像不太行」變成一份可以放進董事會簡報的客觀分數。

```bash
pipx install peakstar-dataready
dataready scan ./公司文件
```

打開 `report.html`，你會拿到：

- **一個 0 到 100 的資料準備度總分**，配紅 / 黃 / 綠燈
- **六大維度的計分卡**：可讀取性、結構化程度、切塊友善度、重複與一致性、新鮮度、元資料
- **「以目前資料直接做 RAG 的預期失敗率」**（概略估計）
- **最該注意的紅旗清單**，每一項都告訴你病在哪、為什麼是問題

> 範例報告：見 [`examples/report/report.html`](examples/report/report.html)（中文）與 [`examples/report-en/report.html`](examples/report-en/report.html)（English）。

---

## 為什麼這應該是你導入 AI 前跑的第一個工具

| 你的處境 | DataReady 幫你 |
|----------|----------------|
| 廠商說「給我們資料就能做 AI」 | 先量化資料準備度，避免用垃圾資料燒掉預算 |
| 要向董事會 / 老闆說明 AI 風險 | 一頁客觀報告，把技術風險翻成「預期失敗率」 |
| 不知道該先整理哪些資料 | 六維計分卡直接指出最弱的環節 |
| 資安部門擋下「又要裝一堆東西」 | 零相依、本機執行、零外送，好過審查 |

這不是給工程師玩的玩具，是給決策者在「要不要投、投之前要先補什麼」這個問題上，一個可量化的依據。

---

## 三個讓你敢在公司內部跑的設計

**1. 零相依（只用 Python 標準函式庫）。**
不裝 PyTorch、不裝一堆 C 擴充、不需要 GPU。一支乾淨的 Python 工具，資安審查容易過，老舊環境也跑得動。

**2. 本機執行，零外送。**
DataReady 不會上傳你的任何一個檔案、任何一段內容到任何地方。所有分析都在你的機器上完成。遙測預設關閉，即使開啟也只記匿名事件計數，永不含內容。資料健檢工具自己不應該變成資料外洩風險。

**3. 唯讀。**
它只讀、只算、只產報告，不會動到你的任何一個檔案。

---

## 安裝

```bash
# 建議用 pipx 安裝為獨立工具
pipx install peakstar-dataready

# 或一次性執行（不安裝）
uvx peakstar-dataready scan ./your-docs

# 或從原始碼（零相依，clone 後直接跑）
git clone https://github.com/peakstargroup/dataready-checker
cd dataready-checker
py -m peakstar_dataready scan ./your-docs
```

需求：Python 3.11 以上。沒有其他相依套件。

---

## 用法

```bash
dataready scan <資料夾路徑> [選項]
```

| 選項 | 說明 | 預設 |
|------|------|------|
| `--out <dir>` | 報告輸出目錄 | `./dataready-report` |
| `--format html,json` | 輸出格式 | `html,json` |
| `--lang zh\|en` | 報告語言 | `zh` |
| `--max-files N` | 最多掃描檔數（大型磁碟取樣用） | 全部 |
| `--include <glob>` | 只納入符合的檔名，逗號分隔 | 常見格式 |
| `--exclude <glob>` | 排除符合的檔名，逗號分隔 | 無 |
| `--open` | 完成後自動開啟報告 | 關 |

支援格式：PDF、Word（docx）、Excel（xlsx）、PowerPoint（pptx）、CSV、Markdown、HTML、純文字。

範例：

```bash
# 掃描整個共用磁碟，產出中文報告並自動開啟
dataready scan "D:\公司共用" --open

# 只看 PDF 的可讀取狀況
dataready scan ./contracts --include "*.pdf"
```

---

## 它做什麼，以及它刻意不做什麼

我們相信「誠實重於承諾」，所以把話說清楚。

**DataReady 會做：**
- 量化你的資料準備度，找出最弱的環節
- 偵測掃描影像 PDF、加密 / 損毀檔、重複檔、過期檔、無語意檔名
- 給你一份可以對內溝通的客觀報告

**DataReady 刻意不做（因為這些需要脈絡與判斷）：**
- 不幫你清洗資料、不做 OCR、不轉檔、不接 ERP
- 不給你產業專屬的切塊與 metadata 策略
- 不告訴你「你的分數對比同業落在哪」

這條線是故意畫的。診斷可以自動化，**治療不行**。把又髒又散的真實資料變成可用的 AI 資產，高度依賴你所在產業的脈絡，這正是顧問的價值所在。

---

## 從健檢到落地

診斷只是第一步。如果報告是黃燈或紅燈，那不是壞消息，而是在投入預算前先看見問題的機會。把又髒又散的資料變成可用的 AI 資產，高度依賴產業脈絡，這也是 Peakstar 在台灣與日本中小企業每天在做的事。

---

## 開源說明（open-core）

本倉庫的所有掃描、評分、報告邏輯與基礎規則包，皆以 MIT 授權完全開源，歡迎使用與貢獻。

針對特定產業的進階客製規則（如金融、醫療、公共關係、政府等，含產業專屬閾值、同業基準與合規考量）需依場景客製，由 Peakstar 於合作專案中提供，不在本開源倉庫內。

---

## 開發與測試

零相依，測試只用標準函式庫的 `unittest`：

```bash
py -m unittest discover -s tests -t .
```

測試涵蓋各格式解析、六維評分邏輯、以及「乾淨 / 中等 / 髒」三組樣本的分數排序與紅旗偵測。

---

## 授權

MIT License。見 [LICENSE](LICENSE)。

## 關於 Peakstar

Peakstar（品得網絡數位）是一家專注台灣與日本中小企業的 AI 顧問與工程交付公司。我們相信商業價值優先、誠實重於承諾，從策略一路陪伴到上線穩定運行。
[www.peakstargroup.com](https://www.peakstargroup.com)
