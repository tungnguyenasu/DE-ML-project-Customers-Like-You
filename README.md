# Customers Like You: GiftLane recommendations and customer map

PCA / SVD mini-project (DS 5020) on the UCI Online Retail II transaction log.

**Team:** Tung Nguyen, Data Engineer and ML Engineer (individual project).

**Result:** Truncated SVD on a 1/0 "bought it" matrix with k = 70. The "also bought" suggestions
reach a hit rate at 10 of 40.4% on purchases the model never saw, against 26.9% for best sellers. The
stored model is 31x smaller than the full table, the nightly job takes under a second, and four
customer groups come out of the same model.

## Success targets (J1)

Sarah Okafor's request, turned into numbers we can check. A target is met only if every rule
below the table also holds. The targets were written on 2026-10-12, after the first PCA vs SVD
comparison and before k, the purchase value and the scoring rule were chosen or the final test was run.

| # | Sarah asked for | Target | How it is measured | Status |
| --- | --- | --- | --- | --- |
| 1 | "Shrink the data" | The stored factors are **at least 10x smaller** than the full customer x product table (160.6 MB) | Size of customer + product factors in MB, 8-byte floats | **Met**: 5.1 MB at k = 70, 31x smaller |
| 2 | "The job runs nightly" | The nightly job runs in **under 1 minute** on a laptop: fit, "also bought" lists for every product, top 10 for every customer | Wall-clock time of the whole job | **Met**: 0.7 s, peak memory 327 MB |
| 3 | "Better than just showing our best sellers" | Hit rate at 10 **at least 3 percentage points above** the best-seller baseline | Held-out purchases (last 2 months, products new to the customer), measured once after k and the scoring rule are fixed on a validation split | **Met**: 40.4% against 26.9%, +13.5 points (95% interval +10.9 to +16.1) |
| 4 | "One simple picture of our main customer groups" | **3 to 6 groups** on a 2-component map, each with **at least 5% of customers** and a name taken from its products and countries; no two groups share more than 5 of their top-10 distinctive products | Group sizes, and overlap of each group's top-10 products by lift (among the 50 it buys most) | **Met**: 4 groups, the smallest 10%, no shared top-10 products |

Why these thresholds:

- **Target 1** is measured against the table the old prototype builds. The sparse purchase matrix
  is already only 5.0 MB, so it is not the size problem Sarah describes.
- **Target 3** needs more than a win. With 1,903 test customers, a hit rate moves by about
  1 point from chance alone, so 3 points is a real improvement.
- **Target 4** requires little overlap so that each group gets its own campaign: two groups that
  buy the same products are one audience, not two.

Rules for every target:

- No test purchase is used by any fitting or tuning step (R2).
- No customer IDs appear in the memo, slides, figures or reports (R4).
- `python build_matrix.py` rebuilds everything from the raw file with the same output every
  time, and all seeds are fixed (R6).

## Submission checklist

| Item | Where |
| --- | --- |
| Data downloaded and row count noted | [Data](#data) below |
| README with targets, how to run, team roles | this file |
| Script that rebuilds the matrix from the raw file | [build_matrix.py](build_matrix.py) |
| Analysis notebook, runs top to bottom | [analysis.ipynb](analysis.ipynb) |
| Cleaning log and matrix report (DE2, DE5) | [cleaning_log.md](reports/cleaning_log.md), [matrix_report.md](reports/matrix_report.md) |
| PCA vs SVD comparison table (ML5) | [pca_vs_svd.md](reports/pca_vs_svd.md) |
| Customer map with named segments (ML6) | [customer_map.png](figures/customer_map.png), [results.md](reports/results.md) |
| One-page memo for Sarah (J2) | [memo.pdf](memo.pdf) |
| Slides (J3) | [slides.pptx](slides.pptx), with speaker notes |
| Contribution log (C2) | [contribution_log.md](contribution_log.md) |
| Peer evaluation (C3) | Not applicable: individual project, peer factor 1.00 |
| Individual reflection | [reflection.md](reflection.md) |

## Data

Online Retail II, UCI Machine Learning Repository (Chen, 2012,
https://doi.org/10.24432/C5CG6D, CC BY 4.0), downloaded 2026-10-12 from
https://archive.ics.uci.edu/dataset/502/online+retail+ii.

Put `online_retail_II.xlsx` in `data/raw/`. The `data/` folder is not committed.

Row count on load: **1,067,371 lines** (sheet *Year 2009-2010*: 525,461; sheet *Year 2010-2011*: 541,910).
The two sheets share 1-9 Dec 2010 (22,523 identical lines), which the build removes once.

## How to run

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python build_matrix.py            # about 1 minute; rebuilds every matrix and report from the raw file
jupyter nbconvert --to notebook --execute --inplace analysis.ipynb   # about 2 minutes; or open it and Run All
python nightly_job.py             # the nightly job: writes data/output/also_bought.csv and customer_top10.csv
python make_memo.py               # rebuilds memo.pdf from reports/results.json
cd slides && npm install && npm run build   # rebuilds slides.pptx (needs Node.js)
```

`build_matrix.py` options: `--test-months 2`, `--min-customers 10`, `--raw`, `--out`, `--reports`.
Nothing in the build is random, so a rerun gives byte-identical files. The notebook and the
models use seed 42 throughout.

## What the build produces

| File | Contents |
| --- | --- |
| `reports/data_profile.md` | DE1: rows per sheet, types, missing values per column |
| `reports/cleaning_log.md` | DE2: lines removed by each cleaning rule |
| `reports/split_report.md` | DE3: train/test and validation sizes, and how the held-out sets were chosen |
| `reports/matrix_report.md` | DE5: shape, non-zeros, sparsity, dense vs sparse vs factor memory |
| `reports/build_summary.json` | all of the above as numbers |
| `data/processed/matrix_binary.npz` | **the matrix the model uses**: customers x products, 1 if the customer kept any units |
| `data/processed/matrix_log1p.npz`, `matrix_quantity.npz` | the same cells as log(1 + units) and raw units (ML7) |
| `data/processed/product_index.csv` | column index -> StockCode, description, number of buyers, units |
| `data/processed/customer_index.csv` | row index -> Customer ID, country, products, invoices, spend (private, R4) |
| `data/processed/test_holdout.csv` | held-out (customer_idx, product_idx) pairs for hit rate at 10 |
| `data/processed/train_lines.parquet`, `test_lines.parquet` | clean purchase lines either side of the cutoff |
| `data/processed/validation/` | the same files for the validation split inside the training period |

Current build: 5,456 customers x 3,680 products, 411,136 non-zeros (97.95% sparse),
160.6 MB dense against 5.0 MB sparse. The test period starts 2011-10-09, with 44,552
held-out purchases for 1,903 customers. The reasons for every rule are in
[decision_log.md](decision_log.md).

## Analysis

| File | Contents |
| --- | --- |
| `method_decision.md` | ML1: PCA or SVD, decided and justified before fitting |
| `analysis.ipynb` | ML2 to ML7: choosing k, the recommender, evaluation, PCA vs SVD, customer map, sensitivity |
| `recommender.py` | shared model code: fit, compression loss, recommend, hit rate, bootstrap, nightly job, k-means |
| `nightly_job.py` | the nightly job as a script, using the settings in `reports/model_choice.json` |
| `reports/results.md` | success targets checked, and the ML2, ML4, ML6 and ML7 results |
| `reports/pca_vs_svd.md` | the filled ML5 comparison table, findings, ML1 predictions checked |
| `reports/model_choice.json`, `results.json`, `validation_sweep.csv` | the chosen settings and every number used by the memo and slides |
| `figures/` | figures written by the notebook (no customer IDs) |
| `make_memo.py`, `slides/make_slides.js` | build `memo.pdf` and `slides.pptx` from the numbers above |

### Loading the matrix

```python
import pandas as pd, scipy.sparse as sp

A = sp.load_npz("data/processed/matrix_binary.npz")                 # csr, customers x products
products = pd.read_csv("data/processed/product_index.csv", dtype={"StockCode": str})
customers = pd.read_csv("data/processed/customer_index.csv")         # contains IDs: never export
holdout = pd.read_csv("data/processed/test_holdout.csv", dtype={"StockCode": str})
```
