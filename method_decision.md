# Method decision (ML1)

Written 2026-10-12, **before fitting PCA or SVD to the data**. It is based only on the
matrix report and the definitions in Section 3. The results that test it are in
[reports/pca_vs_svd.md](reports/pca_vs_svd.md). This note is not edited after the results.

## Decision

**Truncated SVD is the main model.** PCA is run on the same matrix with the same k for the
comparison (ML5).

## Why

1. **The zeros mean something, and SVD keeps them.** The training matrix is 97.95% zeros
   ([matrix_report.md](reports/matrix_report.md)). A zero means "this shop has not bought this
   product". SVD decomposes the matrix as it is, so the fit runs on the 5.0 MB sparse matrix.
   PCA first subtracts each product's average, which turns every zero into a small negative
   number. Stored, that centred matrix is 5,456 x 3,680 = 20.1 million non-zero cells,
   160.6 MB. scikit-learn can centre implicitly without storing it, but the model still
   describes each customer as a deviation from the average customer.
2. **One fit gives everything the recommender needs.** SVD returns product factors (V), for
   the "also bought" box, and customer factors (U S), for scoring customers, together.
3. **Component 1 keeps useful signal.** The matrix has no negative cells, so SVD's first
   component should give every product a weight of the same sign. In plain words, it measures
   overall buying: how much a customer buys and how popular a product is. Popularity helps
   predict what someone buys next. PCA removes the average first, so its first component will
   instead be the biggest contrast between kinds of customers.
4. **Its headline number answers Sarah's question.** "k components rebuild the purchase table
   with X% error" is a direct answer to "what do we lose by compressing".
5. **It is the standard tool for this job.** Latent-factor recommenders and latent semantic
   analysis use SVD on sparse count data.

## Where PCA may still win

The share of variance explained is easier to read. Removing the "big shop vs small shop"
axis may also give marketing a cleaner customer map (ML6). We will check both and use PCA for
the map if it is clearly better there.

## What would change the decision

We switch to PCA if, at the same k, it has a hit rate at 10 on the held-out purchases at least
1 percentage point higher than SVD, with similar fit time and memory.

## Predictions to check in ML5

- SVD fits at least as fast as PCA and needs less memory. Centring the matrix explicitly would
  need at least 160 MB.
- SVD component 1 gives every product a weight of the same sign and follows product popularity
  closely. PCA component 1 has mixed signs and contrasts two groups of products.
- The stored factors are about the same size for both: about 3.7 MB at k = 50, plus 3,680
  product averages for PCA.
- SVD's hit rate at 10 is at least as high as PCA's, and both beat the best-seller baseline.

## k for the comparison

The comparison uses k = 50, the brief's example value. The final k is chosen in ML2. k is a
single parameter at the top of the notebook, so the comparison can be re-run at the chosen k.
