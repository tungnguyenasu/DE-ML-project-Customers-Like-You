# Time split (DE3)

Test period: the last 2 months, from **2011-10-09 12:50:00** (inclusive) to the last invoice
on 2011-12-09 12:50:00. The training matrix, the product filter and
every count in the matrix report use training lines only (R2).

|  | train | test |
| --- | --- | --- |
| Purchase lines | 660,194 | 116,383 |
| Customers | 5,474 | 2,420 |
| Products | 4,529 | 2,902 |
| First invoice | 2009-12-01 07:45:00 | 2011-10-09 12:59:00 |
| Last invoice | 2011-10-09 12:49:00 | 2011-12-09 12:50:00 |

## Held-out purchases (`test_holdout.csv`)

A held-out pair is a product a customer bought in the test period (units net of test-period
cancellations) that is a zero cell in their row of the training matrix.

| step | pairs |
| --- | --- |
| Customer-product pairs bought in the test period | 94,562 |
| Customer not in the training matrix (cold start) | -13,735 |
| Product not in the kept catalogue | -4,698 |
| Customer already bought it in training (repeat) | -31,577 |
| Held-out pairs | 44,552 |

Test customers with at least one held-out product: **1,903**
(median 15 held-out products each, max 451).

## Validation split (`validation/`)

The same split, repeated inside the training period: a matrix from training lines before
**2011-08-09 12:50:00**, and held-out pairs from then until the test cutoff. It is used to choose k and the
scoring rule, so the test purchases are used once, for the final result (R2).

|  | value |
| --- | --- |
| Matrix | 5,134 customers x 3,486 products, 371,275 non-zeros |
| Customer-product pairs bought in the test period | 62,739 |
| Customer not in the training matrix (cold start) | -10,250 |
| Product not in the kept catalogue | -5,402 |
| Customer already bought it in training (repeat) | -22,885 |
| Held-out pairs | 24,202 |
| Validation customers with a held-out product | 1,397 |
