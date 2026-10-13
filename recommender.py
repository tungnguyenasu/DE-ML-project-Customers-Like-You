"""Shared model code: fit SVD or PCA, recommend products, evaluate (ML2 to ML5).

The analysis notebook and the nightly job both import from here, so every
number in the PCA vs SVD comparison and the evaluation comes from the same
functions. Inputs are the files written by build_matrix.py.
"""
import time
import tracemalloc
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.preprocessing import normalize

SEED = 42
MB = 1e6  # decimal megabytes, as in the matrix report
DATA = Path(__file__).parent / "data" / "processed"


def load(value="log1p", data=DATA):
    """Training matrix, product index and held-out pairs. Customer IDs are not loaded (R4)."""
    A = sp.load_npz(data / f"matrix_{value}.npz")
    products = pd.read_csv(data / "product_index.csv", dtype={"StockCode": str})
    holdout = pd.read_csv(data / "test_holdout.csv", dtype={"StockCode": str})
    return A, products, holdout


def fit(method, A, k):
    """Truncated SVD or PCA with the same ARPACK solver, so differences come from centring."""
    if method == "svd":
        return TruncatedSVD(n_components=k, algorithm="arpack", random_state=SEED).fit(A)
    if method == "pca":
        return PCA(n_components=k, svd_solver="arpack", random_state=SEED).fit(A)
    raise ValueError(f"unknown method {method!r}")


def compression_loss(model, A):
    """What is lost by compressing, for SVD or PCA.

    Returns the relative reconstruction error ||A - A_k|| / ||A|| (Frobenius norm,
    A_k includes PCA's column means) and the share of the total that the k
    components keep, measured the way each method measures it: around zero for
    SVD, around the average customer for PCA (its explained variance ratio).
    """
    V = model.components_.T
    mean = getattr(model, "mean_", np.zeros(A.shape[1]))
    total = sp.linalg.norm(A) ** 2
    centred_total = total - A.shape[0] * mean @ mean  # ||A - mean||^2 without densifying
    kept = np.sum((A @ V - mean @ V) ** 2)
    return {"relative_error": np.sqrt((centred_total - kept) / total), "share_kept": kept / centred_total}


def factor_size_mb(model, A):
    """Size of what the nightly job stores: customer factors, product factors, and PCA's means."""
    stored = A.shape[0] * model.n_components + model.components_.size + getattr(model, "mean_", np.empty(0)).size
    return stored * 8 / MB


def _top(scores, n):
    best = np.argpartition(-scores, n, axis=1)[:, :n]
    order = np.argsort(-np.take_along_axis(scores, best, axis=1), axis=1, kind="stable")
    return np.take_along_axis(best, order, axis=1)


def similar_products(product_factors, n=10):
    """ML3: for every product, the n most similar products by cosine of their factor vectors."""
    P = normalize(product_factors)
    S = P @ P.T
    np.fill_diagonal(S, -np.inf)
    return _top(S, n)


def similarity_scorer(product_factors):
    """ML3: score each product by its cosine similarity to what the customer bought, weighted by how much."""
    P = normalize(product_factors)
    return lambda rows: (rows @ P) @ P.T


def reconstruction_scorer(model):
    """Score each product by the customer's rebuilt row A_k (plus PCA's means).

    The same as similarity_scorer with dot products instead of cosines: a
    product's vector length, which grows with how much it sells, is kept.
    """
    V = model.components_.T
    mean = getattr(model, "mean_", np.zeros(V.shape[0]))
    return lambda rows: (rows @ V - mean @ V) @ V.T + mean


def popularity_scorer(A):
    """R3 baseline: score each product by how many training customers bought it."""
    buyers = np.diff(A.tocsc().indptr).astype(float)
    return lambda rows: np.tile(buyers, (rows.shape[0], 1))


def recommend(A, score, customers=None, n=10, batch=1000):
    """Top-n products for each customer, never one already in their training row."""
    customers = np.arange(A.shape[0]) if customers is None else np.asarray(customers)
    top = np.empty((len(customers), n), dtype=np.int64)
    for start in range(0, len(customers), batch):
        rows = A[customers[start:start + batch]]
        scores = np.array(score(rows), dtype=float)
        scores[rows.nonzero()] = -np.inf
        top[start:start + batch] = _top(scores, n)
    return top


def hit_rate(top, customers, holdout):
    """Share of test customers with at least one held-out product in their top-n.

    top[i] holds the recommendations for customer customers[i].
    """
    position = pd.Series(np.arange(len(customers)), index=customers)
    recs = top[position[holdout["customer_idx"]].to_numpy()]
    hit = (recs == holdout["product_idx"].to_numpy()[:, None]).any(axis=1)
    return pd.Series(hit).groupby(holdout["customer_idx"].to_numpy()).any().mean()


def measure(fn, repeats=3):
    """Run fn: best-of-`repeats` wall time in seconds, and peak memory allocated in one run in MB."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        times.append(time.perf_counter() - start)
    tracemalloc.start()
    fn()
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return result, min(times), peak / MB
