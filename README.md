# Customers Like You: GiftLane recommendations and customer map

PCA / SVD mini-project (DS 5020) on the UCI Online Retail II transaction log.

**Team:** Tung Nguyen, Data Engineer and ML Engineer (individual project).

## Success targets (J1)

Sarah Okafor's request, turned into numbers we can check. A target is met only if every rule
below the table also holds.

| # | Sarah asked for | Target | How it is measured | Status |
| --- | --- | --- | --- | --- |
| 1 | "Shrink the data" | The stored factors are **at least 10x smaller** than the full customer x product table (160.6 MB) | Size of customer + product factors in MB, 8-byte floats | Met for every k tried: 0.7 MB (k = 10) to 14.6 MB (k = 200) |
| 2 | "The job runs nightly" | The nightly job runs in **under 1 minute** on a laptop: fit, "also bought" lists for every product, top 10 for every customer | Wall-clock time of the whole job | On track: fit 0.2 s and scoring 0.3 s at k = 50. The full job is timed in ML4 |
| 3 | "Better than just showing our best sellers" | Hit rate at 10 **at least 3 percentage points above** the best-seller baseline | Held-out purchases (last 2 months, products new to the customer), measured once after k and the scoring rule are fixed on a validation split | Open (ML2 to ML4). The Section 3 comparison found the brief's cosine rule 5.7 points *below* the baseline and the rebuilt-row rule 10.2 points above |
| 4 | "One simple picture of our main customer groups" | **3 to 6 groups** on a 2-component map, each with **at least 5% of customers** and a name taken from its top products and countries; no two groups share more than half of their top-10 products | Group sizes and top-10 product overlap from the clustering | Open (ML6). Component 1 is overall buying, so the map may split big shops from small ones first |

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
python build_matrix.py            # about 1 minute; rebuilds everything from the raw file
```

Options: `--test-months 2`, `--min-customers 10`, `--raw`, `--out`, `--reports`.
Nothing in the build is random, so a rerun gives byte-identical files.

## What the build produces

| File | Contents |
| --- | --- |
| `reports/data_profile.md` | DE1: rows per sheet, types, missing values per column |
| `reports/cleaning_log.md` | DE2: lines removed by each cleaning rule |
| `reports/split_report.md` | DE3: train/test sizes and how the held-out set was chosen |
| `reports/matrix_report.md` | DE5: shape, non-zeros, sparsity, dense vs sparse vs factor memory |
| `reports/build_summary.json` | all of the above as numbers |
| `data/processed/matrix_log1p.npz` | **main matrix**: customers x products, log(1 + units kept) |
| `data/processed/matrix_binary.npz`, `matrix_quantity.npz` | same cells as 1/0 and raw units (ML7) |
| `data/processed/product_index.csv` | column index -> StockCode, description, number of buyers, units |
| `data/processed/customer_index.csv` | row index -> Customer ID, country, products, invoices, spend (private, R4) |
| `data/processed/test_holdout.csv` | held-out (customer_idx, product_idx) pairs for hit rate at 10 |
| `data/processed/train_lines.parquet`, `test_lines.parquet` | clean purchase lines either side of the cutoff |

The reasons for every rule are in [decision_log.md](decision_log.md).

Current build: 5,456 customers x 3,680 products, 411,136 non-zeros (97.95% sparse),
160.6 MB dense against 5.0 MB sparse. The test period starts 2011-10-09, with 44,552
held-out purchases for 1,903 customers.

## Analysis

```bash
jupyter nbconvert --to notebook --execute --inplace analysis.ipynb   # or open it and Run All
```

| File | Contents |
| --- | --- |
| `method_decision.md` | ML1: PCA or SVD, decided and justified before fitting |
| `analysis.ipynb` | Section 3: PCA vs SVD on the same matrix and k (ML5) |
| `recommender.py` | shared model code: fit, compression loss, recommend, hit rate, timing |
| `reports/pca_vs_svd.md` | the filled ML5 comparison table, findings, ML1 predictions checked |
| `figures/` | figures written by the notebook (no customer IDs) |

### Loading the matrix

```python
import pandas as pd, scipy.sparse as sp

A = sp.load_npz("data/processed/matrix_log1p.npz")                  # csr, customers x products
products = pd.read_csv("data/processed/product_index.csv", dtype={"StockCode": str})
customers = pd.read_csv("data/processed/customer_index.csv")         # contains IDs: never export
holdout = pd.read_csv("data/processed/test_holdout.csv", dtype={"StockCode": str})
```
