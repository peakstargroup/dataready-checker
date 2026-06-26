<div align="center">

# DataReady

### Before you spend a dollar on AI, spend 30 seconds checking whether your data is ready to feed it

**Data readiness check ｜ Zero dependencies ｜ Runs locally, sends nothing ｜ One board-ready report**

[繁體中文](README.md) ｜ [English](README.en.md)

`Python 3.11+` ｜ `MIT License` ｜ `0 dependencies` ｜ by [Peakstar](https://www.peakstargroup.com)

</div>

---

## An uncomfortable truth for CTOs and CIOs

Most enterprise AI projects fail not because of the model, but because of the data.

What you saw was a slick RAG demo on clean sample data. What you did not see is your real data: scanned-image PDFs, scattered spreadsheets, ten copies of "final_v3", a shared drive nobody has updated in five years. Feed that to AI and you do not get intelligence, you get confident nonsense.

The problem: **before you sign off the budget and set the KPIs, nobody can measure how bad your data actually is.**

DataReady does exactly that. It is a thermometer, not a cure. In 30 seconds it turns a vague "our data seems off" into an objective score you can put in a board deck.

```bash
pipx install peakstar-dataready
dataready scan ./company-docs --lang en
```

Open `report.html` and you get:

- **A 0 to 100 data readiness score** with a red / yellow / green light
- **A scorecard across six dimensions**: Extractability, Structure, Chunkability, Redundancy, Freshness, Metadata
- **An "expected RAG failure rate on current data"** (rough estimate)
- **A prioritized list of red flags**, each explaining what is wrong and why it matters

> Example report: see [`examples/report-en/report.html`](examples/report-en/report.html).

---

## Why this should be the first tool you run before adopting AI

| Your situation | DataReady helps |
|----------------|-----------------|
| A vendor says "just give us the data and we will build AI" | Quantify readiness first; avoid burning budget on garbage data |
| You must explain AI risk to the board | A one-page objective report turning tech risk into "expected failure rate" |
| You do not know what to clean first | The six-dimension scorecard points to the weakest link |
| Security blocks "yet another install" | Zero dependencies, local execution, nothing sent out |

This is not a toy for engineers. It is a quantifiable basis for the decision makers who must answer: should we invest, and what must we fix first.

---

## Three design choices that make it safe to run inside your company

**1. Zero dependencies (standard library only).** No PyTorch, no C extensions, no GPU. A clean Python tool that passes security review and runs on legacy environments.

**2. Local execution, nothing sent out.** DataReady never uploads any file or content anywhere. All analysis happens on your machine. Telemetry is off by default and, even if enabled, records only anonymous event counts, never content.

**3. Read-only.** It only reads, scores, and reports. It never touches your files.

---

## Install

```bash
pipx install peakstar-dataready          # recommended
uvx peakstar-dataready scan ./your-docs  # one-off, no install
# from source (zero deps): py -m peakstar_dataready scan ./your-docs
```

Requires Python 3.11+. No other dependencies.

---

## Usage

```bash
dataready scan <PATH> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--out <dir>` | Report output directory | `./dataready-report` |
| `--format html,json` | Output formats | `html,json` |
| `--lang zh\|en` | Report language | `zh` |
| `--max-files N` | Cap files scanned (sampling) | all |
| `--include <glob>` | Include only matching names | common formats |
| `--exclude <glob>` | Exclude matching names | none |
| `--open` | Open the report when done | off |

Supported: PDF, Word (docx), Excel (xlsx), PowerPoint (pptx), CSV, Markdown, HTML, plain text.

---

## What it does, and what it deliberately does not

We believe honesty beats promises, so here is the line.

**DataReady does:** quantify readiness, find the weakest link, detect scanned PDFs, encrypted / corrupt files, duplicates, stale files and meaningless filenames, and give you a report you can communicate internally.

**DataReady deliberately does not:** clean your data, run OCR, convert files, connect to your ERP, give you industry-specific chunking strategies, or benchmark you against peers.

That line is intentional. Diagnosis can be automated; **treatment cannot.** Turning messy real data into a usable AI asset depends heavily on your industry context. That is where consulting earns its keep.

---

## From check-up to delivery

Diagnosis is only the first step. A yellow or red report is not bad news; it is a chance to see the problem before you commit the budget. Turning messy, scattered data into a usable AI asset depends heavily on industry context, which is the work Peakstar does day to day with SMEs in Taiwan and Japan.

---

## Open-core

All scanning, scoring, reporting and the basic rule pack are fully open source under MIT. Advanced, industry-specific rule packs (for example finance, healthcare, public relations and government, with industry thresholds, peer benchmarks and compliance considerations) are tailored per engagement and provided by Peakstar as part of a project, not bundled in this open-source repo.

## Develop and test

```bash
py -m unittest discover -s tests -t .
```

## License

MIT. See [LICENSE](LICENSE).

## About Peakstar

Peakstar is an AI consulting and engineering delivery firm focused on SME digital transformation in Taiwan and Japan. Business value first, honesty over promises, from strategy through stable operation.
[www.peakstargroup.com](https://www.peakstargroup.com)
