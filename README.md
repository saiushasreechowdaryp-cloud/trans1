# Inbound & SKU Intelligence — POC dashboard (synthetic data)

SP Jain MGB capstone, WMS Team A. Illustrative scenario for Transworld Group.
**Every record is synthetic. Nothing in this dashboard is Transworld data.**

## Run
```bash
cd poc_dashboard
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                     # opens http://localhost:8501
```
Tests: `pip install pytest && python -m pytest tests -q` (18 tests).

## Files
| Path | Purpose |
|---|---|
| `app.py` | Entry point: sidebar navigation, workbook loading, error handling |
| `src/loader.py` | Reads the Excel workbook, finds each table's header row, validates required sheets/columns, keeps codes as text |
| `src/logic.py` | Derived fields, routing rules, review queue, new-SKU drafts, all KPIs and validation metrics |
| `src/ui.py` | Theme, synthetic-data banner, KPI tiles, process track, chart helpers |
| `views/p1_3.py` | Pages 1–3: overview, inbound processing, document intelligence |
| `views/p4_6.py` | Pages 4–6: SKU intelligence, new SKU onboarding, exceptions & human review |
| `views/p7_9.py` | Pages 7–9: POC validation, end-to-end demo, future implementation |
| `data/Transworld_POC_Inbound_SKU_Intelligence_SYNTHETIC.xlsx` | The dataset (unchanged) |
| `tests/test_app.py` | Automated tests (every page, every shipment, every demo step, filters, buttons, bad workbooks, KPIs move with data) |
| `.streamlit/config.toml` | Theme |

## How the numbers are produced
The app reads only the raw columns (data as received, ground truth, simulated AI output) and recomputes
everything else itself: routes, correctness flags, shipment outcomes, exception test results and every KPI.
Formula/result columns in the workbook are not used, so a stale Excel cache can never leak into the dashboard.
Thresholds (80 % document, 90 % SKU) are read from the `Decision_Rules` sheet.

## Assumptions
- Confidence bands: High = at/above the workbook's auto threshold (90 %); Medium = 75–90 % ("validate");
  Low = below 75 %. The 75 % floor is a presentation setting (`MEDIUM_FLOOR` in `src/logic.py`).
- Match type is derived: extracted code = matched code → Exact; Existing with a different code → Fuzzy (code corrected);
  Ambiguous → Fuzzy (multiple/weak candidates); New → No match.
- New-SKU draft category is inferred from the SKU prefix's category in the Item Master; weight per unit = line weight ÷ quantity.
- The "nearest Item Master records" table on the SKU page is a live text-similarity calculation (Python `difflib`)
  used to explain matches; decisions shown are the simulated AI output in the workbook.
- Approve / Edit / Reject decisions live only in the browser session; nothing is written to the workbook or any WMS.
- "Human review cases" on the overview = line items not auto-processed (review + new-SKU approval).

## Known data limitations
- No per-field extraction confidence exists, so "low-confidence extraction" cannot be listed directly; extraction
  errors surface through validation (e.g. SYN-SH-007 mis-read quantity → conflict).
- `Extraction_Correct` is a single line-level test flag, not field-by-field.
- HS codes are stored as text; pandas would otherwise drop leading zeros (0901.21 → 901.21). The loader forces text.
- Ambiguous lines carry two candidate SKUs in `GT_Matched_SKU` (e.g. "EL-4001 or EL-4011") by design.
- SYN-SH-016 has no invoice quantities because the invoice is the missing document (by design).
