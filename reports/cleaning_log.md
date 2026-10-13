# Cleaning log (DE2)

The rules run in this order. *Rows removed* counts the lines a rule removes after the rules
above it have run. *Flagged on raw file* counts every raw line the rule matches on its own,
so you can see where rules overlap.

Starting point: 1,067,371 raw lines.

| rule | rows removed | rows left | flagged on raw file |
| --- | --- | --- | --- |
| Line repeated in the next year's sheet (1-9 Dec 2010) | 22,523 | 1,044,848 | 22,523 |
| Cancellation (invoice starts with C), set aside for netting | 19,165 | 1,025,683 | 19,494 |
| Quantity <= 0 (returns and stock adjustments) | 3,393 | 1,022,290 | 22,950 |
| Price <= 0 (free, test and bad-debt lines) | 2,636 | 1,019,654 | 6,207 |
| Not a product (POST, M, D, BANK CHARGES, gift vouchers, ...) | 4,709 | 1,014,945 | 6,093 |
| Missing Customer ID | 226,758 | 788,187 | 243,007 |
| Exact duplicate of another line | 11,610 | 776,577 | 34,335 |

Clean purchase lines: **776,577** (72.8% of raw).
Cancellation lines set aside for netting (with customer ID and product code): 17,586.
