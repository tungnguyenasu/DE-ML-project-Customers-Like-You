"""Rebuild GiftLane's customer x product matrix from the raw Online Retail II file.

    python build_matrix.py

One command runs DE1 to DE5 (R6): profile the raw workbook, clean it, split it
by time, build the sparse training matrix and report on it. Reports go to
reports/ and contain no customer IDs (R4). Files keyed by customer ID stay in
data/processed/, which is not committed. decision_log.md gives the reason for
every rule. Nothing here is random, so every run gives the same output.
"""
import argparse
import json
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

# Column names differ between UCI releases; map them to one spelling.
RENAME = {"InvoiceNo": "Invoice", "UnitPrice": "Price", "CustomerID": "Customer ID"}
TEXT_COLUMNS = ["Invoice", "InvoiceNo", "StockCode", "Description"]
COLUMNS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]
PRODUCT_CODE = r"^\d{5}[A-Z]*$"  # five digits, then optional variant letters (85123A)
KEY = ["Customer ID", "StockCode"]
K_VALUES = [10, 20, 50, 100, 200]
MB = 1e6  # decimal megabytes, as in the brief's size check


def md_table(rows):
    rows = pd.DataFrame(rows)
    lines = [list(rows.columns), ["---"] * rows.shape[1], *rows.values.tolist()]
    return "\n".join("| " + " | ".join(map(str, line)) + " |" for line in lines)


def n(x):
    return f"{x:,}"


def load_sheets(path):
    sheets = pd.read_excel(path, sheet_name=None, dtype={c: str for c in TEXT_COLUMNS})
    sheets = {name: s.rename(columns=RENAME) for name, s in sheets.items()}
    for name, s in sheets.items():
        missing = set(COLUMNS) - set(s.columns)
        if missing:
            raise ValueError(f"sheet {name!r} is missing columns {sorted(missing)}")
    return sheets


def profile(sheets):
    """DE1: rows and dates per sheet; type, missing and distinct values per column."""
    per_sheet = [{"sheet": name, "rows": n(len(s)),
                  "first invoice": s["InvoiceDate"].min(), "last invoice": s["InvoiceDate"].max()}
                 for name, s in sheets.items()]
    df = pd.concat(sheets.values(), ignore_index=True)[COLUMNS]
    per_column = [{"column": c, "dtype": str(df[c].dtype), "missing": n(int(df[c].isna().sum())),
                   "missing %": f"{df[c].isna().mean():.2%}", "distinct": n(int(df[c].nunique()))}
                  for c in COLUMNS]
    return len(df), per_sheet, per_column


def clean(sheets):
    """DE2: apply the cleaning rules in order and log how many lines each removes.

    Cancellation lines are not purchases, but they are set aside so the matrix
    step can subtract them from the purchase they cancel.
    """
    df = pd.concat([s.assign(sheet=i) for i, s in enumerate(sheets.values())], ignore_index=True)
    df["StockCode"] = df["StockCode"].str.strip().str.upper()
    # 1-9 Dec 2010 is in both yearly sheets; keep an invoice from the last sheet it is in.
    repeated = df["sheet"] < df.groupby("Invoice")["sheet"].transform("max")
    cancelled = df["Invoice"].str.startswith("C")
    not_product = ~df["StockCode"].str.match(PRODUCT_CODE)
    no_customer = df["Customer ID"].isna()
    rules = [
        ("Line repeated in the next year's sheet (1-9 Dec 2010)", repeated),
        ("Cancellation (invoice starts with C), set aside for netting", cancelled),
        ("Quantity <= 0 (returns and stock adjustments)", df["Quantity"] <= 0),
        ("Price <= 0 (free, test and bad-debt lines)", df["Price"] <= 0),
        ("Not a product (POST, M, D, BANK CHARGES, gift vouchers, ...)", not_product),
        ("Missing Customer ID", no_customer),
    ]
    keep = pd.Series(True, index=df.index)
    log = []
    for rule, hit in rules:
        removed = keep & hit
        keep &= ~hit
        log.append({"rule": rule, "rows removed": int(removed.sum()), "rows left": int(keep.sum()),
                    "flagged on raw file": int(hit.sum())})
    purchases = df.loc[keep, COLUMNS]
    duplicate = purchases.duplicated()
    purchases = purchases[~duplicate]
    log.append({"rule": "Exact duplicate of another line", "rows removed": int(duplicate.sum()),
                "rows left": len(purchases), "flagged on raw file": int(df[COLUMNS].duplicated().sum())})

    usable = ~repeated & ~not_product & ~no_customer & (df["Quantity"] < 0)
    cancels = df.loc[cancelled & usable, COLUMNS].drop_duplicates()
    cancels = cancels.assign(Quantity=-cancels["Quantity"])  # units cancelled, as a positive number
    return purchases.astype({"Customer ID": "int64"}), cancels.astype({"Customer ID": "int64"}), log


def net_units(buys, cancels):
    """Units bought minus units cancelled, for each (customer, product) that was bought."""
    bought = buys.groupby(KEY)["Quantity"].sum()
    cancelled = cancels.groupby(KEY)["Quantity"].sum().reindex(bought.index, fill_value=0)
    return bought - cancelled, int((cancelled > 0).sum())


def most_common(lines, key, column):
    counts = lines.groupby([key, column]).size().sort_values(ascending=False, kind="stable")
    return counts.reset_index().drop_duplicates(key).set_index(key)[column]


def build(train, train_cancels, min_customers):
    """DE4: sparse customer x product matrices from training lines only."""
    net, with_cancel = net_units(train, train_cancels)
    bought = net[net > 0]
    customers_per_product = bought.groupby(level="StockCode").size()
    products = customers_per_product.index[customers_per_product >= min_customers]
    kept = bought[bought.index.get_level_values("StockCode").isin(products)]
    customers = pd.Index(kept.index.get_level_values("Customer ID").unique(), name="Customer ID")
    rows = customers.get_indexer(kept.index.get_level_values("Customer ID"))
    cols = products.get_indexer(kept.index.get_level_values("StockCode"))
    units = kept.to_numpy(dtype=float)
    values = {"log1p": np.log1p(units), "binary": np.ones_like(units), "quantity": units}
    matrices = {name: sp.csr_matrix((v, (rows, cols)), shape=(len(customers), len(products)))
                for name, v in values.items()}

    product_map = pd.DataFrame({
        "product_idx": np.arange(len(products)),
        "StockCode": products,
        "Description": most_common(train, "StockCode", "Description").reindex(products).str.strip().to_numpy(),
        "n_customers": customers_per_product.reindex(products).to_numpy(),
        "units": kept.groupby(level="StockCode").sum().reindex(products).to_numpy(),
    })
    lines = train[train["Customer ID"].isin(customers)]
    by_customer = lines.groupby("Customer ID")
    customer_map = pd.DataFrame({
        "customer_idx": np.arange(len(customers)),
        "Customer ID": customers,
        "Country": most_common(lines, "Customer ID", "Country").reindex(customers).to_numpy(),
        "n_products": np.diff(matrices["binary"].indptr),
        "n_invoices": by_customer["Invoice"].nunique().reindex(customers).to_numpy(),
        "spend_gbp": (lines["Quantity"] * lines["Price"]).groupby(lines["Customer ID"]).sum()
                     .reindex(customers).round(2).to_numpy(),
    })
    steps = [
        ("Customer-product pairs bought in training", len(net)),
        ("... of which had units cancelled later in training", with_cancel),
        ("... of which were fully cancelled (dropped)", int((net <= 0).sum())),
        ("Products with at least one buyer", len(customers_per_product)),
        (f"Products kept (bought by >= {min_customers} customers)", len(products)),
        ("Customers with at least one purchase", bought.index.get_level_values("Customer ID").nunique()),
        ("Customers kept (bought at least one kept product)", len(customers)),
    ]
    return matrices, customer_map, product_map, kept.index, steps


def hold_out(test, test_cancels, customers, products, train_pairs):
    """DE3: test-period purchases of products the customer never bought in training (R2)."""
    net, _ = net_units(test, test_cancels)
    pairs = net[net > 0].reset_index()
    drops = [
        ("Customer not in the training matrix (cold start)", ~pairs["Customer ID"].isin(customers)),
        ("Product not in the kept catalogue", ~pairs["StockCode"].isin(products)),
        ("Customer already bought it in training (repeat)", pd.MultiIndex.from_frame(pairs[KEY]).isin(train_pairs)),
    ]
    funnel = [("Customer-product pairs bought in the test period", len(pairs))]
    keep = pd.Series(True, index=pairs.index)
    for label, drop in drops:
        funnel.append((label, -int((keep & drop).sum())))
        keep &= ~drop
    held = pairs[keep]
    funnel.append(("Held-out pairs", len(held)))
    return pd.DataFrame({
        "customer_idx": customers.get_indexer(held["Customer ID"]),
        "product_idx": products.get_indexer(held["StockCode"]),
        "StockCode": held["StockCode"].to_numpy(),
        "units": held["Quantity"].to_numpy(),
    }), funnel


def matrix_size(A):
    """DE5: shape, sparsity and memory of the full matrix against stored factors."""
    n_c, n_p = A.shape
    dense = n_c * n_p * 8 / MB
    return {
        "customers": n_c, "products": n_p, "nonzeros": int(A.nnz),
        "sparsity": 1 - A.nnz / (n_c * n_p),
        "dense_mb": dense,
        "sparse_csr_mb": (A.data.nbytes + A.indices.nbytes + A.indptr.nbytes) / MB,
        "factors_mb": {k: (n_c + n_p) * k * 8 / MB for k in K_VALUES},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", default="data/raw/online_retail_II.xlsx")
    parser.add_argument("--out", default="data/processed", help="matrices, index maps, train and test files")
    parser.add_argument("--reports", default="reports", help="profile, cleaning log, split and matrix reports")
    parser.add_argument("--test-months", type=int, default=2, help="length of the test period at the end")
    parser.add_argument("--min-customers", type=int, default=10, help="keep products with at least this many buyers")
    args = parser.parse_args()
    out, reports = Path(args.out), Path(args.reports)
    out.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    start = time.time()

    print(f"DE1 loading {args.raw} (about a minute)")
    sheets = load_sheets(args.raw)
    raw_rows, per_sheet, per_column = profile(sheets)

    print("DE2 cleaning")
    purchases, cancels, log = clean(sheets)

    print("DE3 splitting by time")
    cutoff = purchases["InvoiceDate"].max() - pd.DateOffset(months=args.test_months)
    is_test, cancel_is_test = purchases["InvoiceDate"] >= cutoff, cancels["InvoiceDate"] >= cutoff
    train, test = purchases[~is_test], purchases[is_test]

    print("DE4 building the matrix")
    matrices, customer_map, product_map, train_pairs, steps = build(train, cancels[~cancel_is_test], args.min_customers)
    customers, products = pd.Index(customer_map["Customer ID"]), pd.Index(product_map["StockCode"])
    held_out, funnel = hold_out(test, cancels[cancel_is_test], customers, products, train_pairs)

    for name, A in matrices.items():
        sp.save_npz(out / f"matrix_{name}.npz", A)
    customer_map.to_csv(out / "customer_index.csv", index=False)
    product_map.to_csv(out / "product_index.csv", index=False)
    train.to_parquet(out / "train_lines.parquet", index=False)
    test.to_parquet(out / "test_lines.parquet", index=False)
    held_out.to_csv(out / "test_holdout.csv", index=False)

    print("DE5 writing reports")
    size = matrix_size(matrices["log1p"])
    seconds = time.time() - start
    per_customer = held_out.groupby("customer_idx").size()
    A = matrices["quantity"]
    spread = {
        "Products per customer": np.diff(A.indptr),
        "Customers per product": np.diff(A.tocsc().indptr),
        "Units per non-zero cell": A.data,
    }

    (reports / "data_profile.md").write_text(f"""# Data profile (DE1)

Source: `{args.raw}`, built {date.today()}. Total raw lines: **{n(raw_rows)}**.

## Sheets

{md_table(per_sheet)}

## Columns (both sheets stacked)

{md_table(per_column)}

The sheets overlap: invoices dated 1-9 Dec 2010 appear in both, line for line.
The cleaning log removes the {n(log[0]["rows removed"])} repeated lines first.
""", encoding="utf-8")

    (reports / "cleaning_log.md").write_text(f"""# Cleaning log (DE2)

The rules run in this order. *Rows removed* counts the lines a rule removes after the rules
above it have run. *Flagged on raw file* counts every raw line the rule matches on its own,
so you can see where rules overlap.

Starting point: {n(raw_rows)} raw lines.

{md_table([{**r, **{k: n(r[k]) for k in ("rows removed", "rows left", "flagged on raw file")}} for r in log])}

Clean purchase lines: **{n(len(purchases))}** ({len(purchases) / raw_rows:.1%} of raw).
Cancellation lines set aside for netting (with customer ID and product code): {n(len(cancels))}.
""", encoding="utf-8")

    (reports / "split_report.md").write_text(f"""# Time split (DE3)

Test period: the last {args.test_months} months, from **{cutoff}** (inclusive) to the last invoice
on {purchases["InvoiceDate"].max()}. The training matrix, the product filter and
every count in the matrix report use training lines only (R2).

{md_table([
        {"": "Purchase lines", "train": n(len(train)), "test": n(len(test))},
        {"": "Customers", "train": n(train["Customer ID"].nunique()), "test": n(test["Customer ID"].nunique())},
        {"": "Products", "train": n(train["StockCode"].nunique()), "test": n(test["StockCode"].nunique())},
        {"": "First invoice", "train": train["InvoiceDate"].min(), "test": test["InvoiceDate"].min()},
        {"": "Last invoice", "train": train["InvoiceDate"].max(), "test": test["InvoiceDate"].max()},
    ])}

## Held-out purchases (`test_holdout.csv`)

A held-out pair is a product a customer bought in the test period (units net of test-period
cancellations) that is a zero cell in their row of the training matrix.

{md_table([{"step": s, "pairs": n(c)} for s, c in funnel])}

Test customers with at least one held-out product: **{n(len(per_customer))}**
(median {per_customer.median():.0f} held-out products each, max {n(int(per_customer.max()))}).
""", encoding="utf-8")

    (reports / "matrix_report.md").write_text(f"""# Matrix report (DE4, DE5)

Rows are customers, columns are products, both from training lines only.
Cell value: **log(1 + units kept)**, where units kept = units bought minus units cancelled
for that customer and product (`matrix_log1p.npz`). The same cells are also saved as a
1/0 flag (`matrix_binary.npz`) and as raw units (`matrix_quantity.npz`) for ML7.

## Netting and filters

{md_table([{"step": s, "count": n(c)} for s, c in steps])}

## Size

{md_table([
        {"measure": "Shape", "value": f"{n(size['customers'])} customers x {n(size['products'])} products"},
        {"measure": "Non-zero cells", "value": n(size["nonzeros"])},
        {"measure": "Sparsity (share of zero cells)", "value": f"{size['sparsity']:.2%}"},
        {"measure": "Dense, 8-byte floats", "value": f"{size['dense_mb']:.1f} MB"},
        {"measure": "Sparse CSR (values + column indices + row pointers)", "value": f"{size['sparse_csr_mb']:.1f} MB"},
    ])}

## Stored factors after compression to k components

Customer factors ({n(size['customers'])} x k) plus product factors ({n(size['products'])} x k), 8-byte floats.

{md_table([{"k": k, "factors": f"{mb:.1f} MB", "share of dense": f"{mb / size['dense_mb']:.1%}"}
           for k, mb in size["factors_mb"].items()])}

## Distribution

{md_table([{"": label, "median": f"{np.median(v):g}", "90th pct": f"{np.percentile(v, 90):g}",
            "99th pct": f"{np.percentile(v, 99):g}", "max": f"{v.max():g}"} for label, v in spread.items()])}

MB = 10^6 bytes. Build time for the whole pipeline: {seconds:.0f} seconds.
""", encoding="utf-8")

    (reports / "build_summary.json").write_text(json.dumps({
        "built": str(date.today()), "raw_rows": raw_rows, "cleaning": log,
        "clean_purchase_lines": len(purchases), "cancellation_lines": len(cancels),
        "cutoff": str(cutoff), "train_lines": len(train), "test_lines": len(test),
        "matrix_steps": dict(steps), "holdout_funnel": dict(funnel),
        "holdout_customers": len(per_customer), "matrix": size, "seconds": round(seconds, 1),
        "settings": {"test_months": args.test_months, "min_customers": args.min_customers},
    }, indent=2), encoding="utf-8")

    print(f"done in {seconds:.0f}s: {n(size['customers'])} x {n(size['products'])} matrix, "
          f"{n(size['nonzeros'])} non-zeros, {n(len(held_out))} held-out pairs for {n(len(per_customer))} customers")


if __name__ == "__main__":
    main()
