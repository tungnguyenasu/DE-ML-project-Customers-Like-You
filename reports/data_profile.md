# Data profile (DE1)

Source: `data/raw/online_retail_II.xlsx`, built 2026-10-12. Total raw lines: **1,067,371**.

## Sheets

| sheet | rows | first invoice | last invoice |
| --- | --- | --- | --- |
| Year 2009-2010 | 525,461 | 2009-12-01 07:45:00 | 2010-12-09 20:01:00 |
| Year 2010-2011 | 541,910 | 2010-12-01 08:26:00 | 2011-12-09 12:50:00 |

## Columns (both sheets stacked)

| column | dtype | missing | missing % | distinct |
| --- | --- | --- | --- | --- |
| Invoice | str | 0 | 0.00% | 53,628 |
| StockCode | str | 0 | 0.00% | 5,305 |
| Description | str | 4,382 | 0.41% | 5,698 |
| Quantity | int64 | 0 | 0.00% | 1,057 |
| InvoiceDate | datetime64[us] | 0 | 0.00% | 47,635 |
| Price | float64 | 0 | 0.00% | 2,807 |
| Customer ID | float64 | 243,007 | 22.77% | 5,942 |
| Country | str | 0 | 0.00% | 43 |

The sheets overlap: invoices dated 1-9 Dec 2010 appear in both, line for line.
The cleaning log removes the 22,523 repeated lines first.
