# Matrix report (DE4, DE5)

Rows are customers, columns are products, both from training lines only.
Cell value: **log(1 + units kept)**, where units kept = units bought minus units cancelled
for that customer and product (`matrix_log1p.npz`). The same cells are also saved as a
1/0 flag (`matrix_binary.npz`) and as raw units (`matrix_quantity.npz`) for ML7.

## Netting and filters

| step | count |
| --- | --- |
| Customer-product pairs bought in training | 417,719 |
| ... of which had units cancelled later in training | 12,286 |
| ... of which were fully cancelled (dropped) | 2,784 |
| Products with at least one buyer | 4,519 |
| Products kept (bought by >= 10 customers) | 3,680 |
| Customers with at least one purchase | 5,457 |
| Customers kept (bought at least one kept product) | 5,456 |

## Size

| measure | value |
| --- | --- |
| Shape | 5,456 customers x 3,680 products |
| Non-zero cells | 411,136 |
| Sparsity (share of zero cells) | 97.95% |
| Dense, 8-byte floats | 160.6 MB |
| Sparse CSR (values + column indices + row pointers) | 5.0 MB |

## Stored factors after compression to k components

Customer factors (5,456 x k) plus product factors (3,680 x k), 8-byte floats.

| k | factors | share of dense |
| --- | --- | --- |
| 10 | 0.7 MB | 0.5% |
| 20 | 1.5 MB | 0.9% |
| 50 | 3.7 MB | 2.3% |
| 100 | 7.3 MB | 4.6% |
| 200 | 14.6 MB | 9.1% |

## Distribution

|  | median | 90th pct | 99th pct | max |
| --- | --- | --- | --- | --- |
| Products per customer | 41 | 179 | 467.15 | 2244 |
| Customers per product | 66 | 272.1 | 587.05 | 1416 |
| Units per non-zero cell | 6 | 36 | 228 | 25164 |

MB = 10^6 bytes. Build time for the whole pipeline: 55 seconds.
