"""The nightly job: refit the model, write the "also bought" lists and customer suggestions.

    python nightly_job.py

Uses the purchase value, k and scoring rule chosen on the validation split in
analysis.ipynb (reports/model_choice.json). Outputs go to data/output/, which is
not committed: the customer file is keyed by row index, and only
data/processed/customer_index.csv maps an index back to a customer ID (R4).
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

import recommender as rec


def main():
    choice = json.loads((Path(__file__).parent / "reports" / "model_choice.json").read_text(encoding="utf-8"))
    A, products, _ = rec.load(choice["value"])
    start = time.perf_counter()
    _, also_bought, top = rec.nightly_job(A, choice["k"], cosine=choice["rule"] == "cosine")
    seconds = time.perf_counter() - start

    out = rec.DATA.parent / "output"
    out.mkdir(exist_ok=True)
    codes, names = products["StockCode"].to_numpy(), products["Description"].to_numpy()
    n = also_bought.shape[1]
    pd.DataFrame({
        "StockCode": codes.repeat(n), "Description": names.repeat(n), "rank": np.tile(np.arange(1, n + 1), len(codes)),
        "also_bought": codes[also_bought.ravel()], "also_bought_description": names[also_bought.ravel()],
    }).to_csv(out / "also_bought.csv", index=False)
    pd.DataFrame({
        "customer_idx": np.arange(A.shape[0]).repeat(n), "rank": np.tile(np.arange(1, n + 1), A.shape[0]),
        "StockCode": codes[top.ravel()],
    }).to_csv(out / "customer_top10.csv", index=False)
    print(f"{choice['value']} matrix, k = {choice['k']}, {choice['rule']} rule: "
          f"{len(codes):,} product lists and {A.shape[0]:,} customer lists in {seconds:.1f} s -> {out}")


if __name__ == "__main__":
    main()
