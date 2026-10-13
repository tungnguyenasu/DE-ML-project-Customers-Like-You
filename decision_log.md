# Decision log (R1)

Every data decision behind `build_matrix.py`, with its reason. Numbers come from
[reports/](reports/) and change only if a rule changes.

## Loading

**D1. Use both yearly sheets, and keep 1-9 Dec 2010 once.**
The 2009-2010 sheet runs to 9 Dec 2010 and the 2010-2011 sheet starts on 1 Dec 2010.
The 22,523 lines (1,088 invoices) in that window are identical in both sheets, line for
line. Keeping both copies would double-count that week. An invoice found in two sheets
is kept from the later sheet only.

**D2. Read Invoice, StockCode and Description as text.**
Invoices start with "C" or "A" for cancellations and adjustments, and some descriptions
are stored as numbers in Excel. Reading these columns as text keeps codes like 85123A intact.

## Cleaning (DE2, see [cleaning_log.md](reports/cleaning_log.md))

**D3. Cancellations are not purchases, and they also undo the purchase they cancel.**
Deleting only the "C" line still counts the original order as a purchase, and a cancelled
order counted as a purchase is exactly the mistake the brief warns about. So cancelled
units are subtracted from the same customer's purchases of the same product in the same
period (train or test). A pair with no units left is not a purchase.
In training, 12,286 of 417,719 customer-product pairs had units cancelled, and 2,784 were
fully cancelled and dropped. The largest cell fell from 74,215 units (an order cancelled the
same day) to 25,164. A cancellation with no matching purchase in its period is ignored,
because its purchase came before December 2009 or was removed by another rule.

**D4. Remove lines with quantity <= 0 that are not cancellations.**
All 3,393 are stock write-offs ("damages", "missing", "check"), with no customer and a price
of zero. They are not customer behaviour.

**D5. Remove lines with price <= 0.**
A line given away for free is not a sale: free samples, test products, manual fixes and
bad-debt adjustments. Only 70 of these 2,636 lines belong to a customer.

**D6. A product is a StockCode of five digits plus optional letters, after trimming and upper-casing.**
Everything else is a charge or a book-keeping line: POST, DOT and C2 (postage), M (manual),
D (discount), S (samples), BANK CHARGES, AMAZONFEE, ADJUST, CRUK, PADS, TEST001, B (bad debt)
and the gift vouchers. The website-only DCGS codes and SP1002 also fall out. None of the DCGS
lines has a customer ID, and SP1002 has 2 buyers, below the product filter anyway.
The 173 lower-case codes (for example 15056bl) carry the same descriptions as their upper-case
codes, so they are merged. Letter variants (85123A and 85123B) stay separate, because they
are different colours or designs that a customer chooses between.
Known leftover: one delivery charge has a five-digit code, 23444 "Next Day Carriage", bought by
29 customers. It is 1 of 3,680 columns, and it appears in none of the "also bought" or customer
top-10 lists, so the frozen matrix keeps it. A future rebuild should add it to the rule.

**D7. Remove lines without a Customer ID.**
These lines cannot be placed in a customer row. They make up 22.8% of the raw lines and
most of what the cleaning removes.

**D8. Remove exact duplicate lines.**
11,610 lines are identical to another line in every column, down to the minute. The most
likely cause is double recording. Dropping them changes no 1/0 cell and moves a log cell by
at most log 2.

Result: 776,577 clean purchase lines (72.8% of raw), plus 17,586 cancellation lines kept aside
for netting.

## Split (DE3, see [split_report.md](reports/split_report.md))

**D9. The test period is the last 2 months, from 2011-10-09 12:50, with no gap.**
This follows the brief. The split is made before anything is fitted, and the product
filter, matrix and index maps all use training lines only (R2).

**D10. A held-out purchase is a product the customer bought in the test period that is a zero cell in their training row.**
This evaluates what the "also bought" box is for: suggesting products the customer does not
already buy. Three kinds of test pairs are left out, and the counts are in the split report:
- customers not in the training matrix (cold start): the model has nothing to base suggestions on;
- products outside the kept catalogue: the model cannot recommend them;
- repeat purchases: the box should not suggest what the customer already buys.

That leaves 44,552 held-out pairs for 1,903 test customers.
Risk: the test window is the pre-Christmas peak, so seasonal products are over-represented.
Both earlier Christmas seasons are in training, which helps.

## Matrix (DE4, DE5, see [matrix_report.md](reports/matrix_report.md))

**D11. Cell value = log(1 + units kept).**
Units are heavy-tailed: the median cell is 6 units, the 99th percentile is 228 and the
maximum is 25,164. With raw units, SVD's squared error would be dominated by a few wholesale
cells. A 1/0 flag throws away the difference between a shop that bought 2 and one that
bought 2,000. log1p keeps the order but compresses the tail: 6 units becomes 1.9, and
25,164 becomes 10.1. The 1/0 and raw-unit versions are saved with the same cells for the
ML7 sensitivity check.
Update: the validation split (M8) showed the 1/0 version predicts new purchases better, so the
recommender uses it (M9). log(1 + units) stays the default matrix the build reports on.

**D12. Keep products bought by at least 10 different customers in training.**
With fewer buyers there is too little co-purchase signal for a reliable similarity, and a
product page would show suggestions driven by a handful of shops. The filter removes 839 of
4,519 products (19%) but only 3,799 of 414,935 non-zero cells (0.9%). It also matches the
brief's example threshold. The threshold can be changed with `--min-customers`.

**D13. Keep every customer with at least one kept product.**
That is 5,456 customers. There is no minimum, because the box should work for small buyers
too. The ML Engineer can still filter customers for the customer map.

**D14. Customer IDs stay in `data/processed/`, which is not committed.**
The reports, figures and `test_holdout.csv` use row indices (`customer_idx`). Only
`customer_index.csv` maps an index back to an ID (R4).

## Modelling (ML1, ML5, see [pca_vs_svd.md](reports/pca_vs_svd.md))

**M1. Truncated SVD is the main model.**
The reasons are in [method_decision.md](method_decision.md), written before anything was
fitted. PCA's best hit-rate lead was 0.6 points in the first comparison (k = 50) and 0.3 points at the
final settings, both under the 1-point bar set in advance, so the decision stands.

**M2. Both methods use the ARPACK solver with seed 42.**
With the same solver, any difference comes from centring alone. ARPACK is also exact. On this
matrix it fitted faster than scikit-learn's default randomized solver and gave a slightly lower
error (0.7883 vs 0.7889 at k = 50).

**M3. PCA runs on the sparse matrix with implicit centring.**
Centring explicitly gives the same model but peaks at 490 MB, against 8 MB.

**M4. Best-seller baseline: the 10 products with the most distinct training buyers that the customer has not bought.**
Counting buyers rather than units stops a few bulk wholesale orders from deciding what
"best-selling" means. The box should reflect how many shops buy a product.

**M5. k = 50 for the first comparison only.**
This was the brief's example value, used before k was chosen. The final comparison in
[pca_vs_svd.md](reports/pca_vs_svd.md) is re-run at the chosen settings (M10) and reaches the same
conclusions.

**M6. The scoring rule is chosen on validation, not on the test.**
The first comparison reported two rules on the test purchases: ML3's cosine rule (21% hit rate, below
the baseline's 27%) and the rebuilt-row rule (37%). Choosing between them there would let the test
purchases shape a model decision (R2), so the choice is made on the validation split (M8).

**M7. The scikit-learn version of k-means is replaced by SciPy's.**
On this laptop, an application-control policy blocks one of scikit-learn's compiled files, so
`sklearn.cluster` will not import. `recommender.kmeans` runs SciPy's k-means++ with 10 seeded
restarts and keeps the run with the lowest within-group sum of squares, which is what
`KMeans(n_init=10)` does.

**M8. A validation split repeats the test split inside the training period.**
`build_matrix.py` cuts the training lines at 9 Aug 2011 and holds out new-product purchases from then
until the test cutoff (24,202 pairs, 1,397 customers). The main matrix and test files are unchanged,
byte for byte. Its risk: validation is late summer, the test is the pre-Christmas peak.

**M9. The model uses the 1/0 matrix, the rebuilt-row rule and k = 70, all chosen on validation.**
Validation hit rates for 3 purchase values x 8 values of k x 2 rules are in
[validation_sweep.csv](reports/validation_sweep.csv). The 1/0 matrix with the rebuilt-row rule was
best (42.4% at k = 70, against a 25.6% baseline). log(1 + units) peaked at 39.7% and raw units at 25.0%.
The cosine rule never beat best sellers. A plain "bought it" flag carries more signal for a shop's
next new product than how many units it bought.

**M10. k = 70: the smallest k within 1 point of the best validation hit rate.**
The rule was fixed before looking. One point is about one standard error of a validation hit rate.
The grid was the brief's five values plus 30, 70 and 150. The reconstruction error falls smoothly
with no elbow, so it cannot choose k on its own.

**M11. The test purchases are scored once, after M9 and M10.**
The final result: 40.4% against 26.9% for best sellers, +13.5 points with a 95% bootstrap interval of
+10.9 to +16.1 (2,000 resamples of the 1,903 test customers, seed 42).

**M12. The customer map uses component 1 (log scale) and component 2 divided by component 1.**
Component 1 is overall buying, so the raw components 1 and 2 mostly sort shops by size. Dividing
component 2 by component 1 gives taste regardless of size: home decoration against children's items.
k-means on the two standardised coordinates, for 3 to 6 groups, chose 4 groups: the highest
silhouette among the solutions that meet success target 4. Groups are described by their top-10
products by lift, among the 50 products each group buys most. Names follow rules written next to the
profiles in the notebook. They use SVD, the main model; PCA gives the same components (M1).
