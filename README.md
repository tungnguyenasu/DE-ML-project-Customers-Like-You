# Customers Like You: GiftLane recommendations and customer map

PCA / SVD mini-project (DS 5020) on the UCI Online Retail II transaction log.

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
