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
