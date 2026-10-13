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
