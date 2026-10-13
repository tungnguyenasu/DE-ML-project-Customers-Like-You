# Contribution log (C2)

Individual project: Tung Nguyen holds both the Data Engineer and the ML Engineer role, so every task
below is owned by the same person. Evidence points to the commit and the file that show the work
(`git show <commit>`).

| Date | Task | Owner | Evidence (commit, file or figure) | Status |
| --- | --- | --- | --- | --- |
| 2026-10-12 | Step 0: data downloaded, row count noted | Tung Nguyen | `f2b324a`, [README.md](README.md#data) (1,067,371 lines) | Done |
| 2026-10-12 | J1: success targets | Tung Nguyen | `965ced7`, [README.md](README.md#success-targets-j1) | Done |
| 2026-10-12 | DE1: data profile | Tung Nguyen | `f2b324a`, [data_profile.md](reports/data_profile.md) | Done |
| 2026-10-12 | DE2: cleaning and cleaning log | Tung Nguyen | `f2b324a`, [cleaning_log.md](reports/cleaning_log.md) | Done |
| 2026-10-12 | DE3: time split and held-out purchases | Tung Nguyen | `f2b324a`, validation split `14fd643`, [split_report.md](reports/split_report.md) | Done |
| 2026-10-12 | DE4: sparse matrix and index maps | Tung Nguyen | `f2b324a`, [build_matrix.py](build_matrix.py) | Done |
| 2026-10-12 | DE5: matrix report | Tung Nguyen | `f2b324a`, [matrix_report.md](reports/matrix_report.md) | Done |
| 2026-10-12 | DE6 (stretch): one-command rebuild | Tung Nguyen | `f2b324a`, `python build_matrix.py` | Done |
| 2026-10-12 | ML1: method decision before fitting | Tung Nguyen | `3e071d9`, [method_decision.md](method_decision.md) | Done |
| 2026-10-12 | ML2: k chosen with evidence | Tung Nguyen | `8ab1b13`, [analysis.ipynb](analysis.ipynb) section 2, [choose_k.png](figures/choose_k.png), [compression_loss.png](figures/compression_loss.png) | Done |
| 2026-10-12 | ML3: recommendation function | Tung Nguyen | `ce1f433` and `8ab1b13`, [recommender.py](recommender.py), [nightly_job.py](nightly_job.py) | Done |
| 2026-10-12 | ML4: test evaluation and nightly-job timing | Tung Nguyen | `8ab1b13`, [results.md](reports/results.md) | Done |
| 2026-10-12 | ML5: PCA vs SVD comparison table | Tung Nguyen | `ce1f433`, re-run `8ab1b13`, [pca_vs_svd.md](reports/pca_vs_svd.md) | Done |
| 2026-10-12 | ML6: customer map and named segments | Tung Nguyen | `8ab1b13`, [customer_map.png](figures/customer_map.png) | Done |
| 2026-10-12 | ML7 (stretch): purchase-value sensitivity | Tung Nguyen | `8ab1b13`, [analysis.ipynb](analysis.ipynb) section 7 | Done |
| 2026-10-12 | J2: one-page memo | Tung Nguyen | `d62246c`, [memo.pdf](memo.pdf) | Done |
| 2026-10-12 | J3: slides | Tung Nguyen | `d62246c`, [slides.pptx](slides.pptx) | Done |
| 2026-10-12 | README: how to run and submission checklist | Tung Nguyen | `6250380`, [README.md](README.md) | Done |
| 2026-10-12 | C2: contribution log | Tung Nguyen | this file | Done |
| n/a | C3: peer evaluation | n/a | Individual project, so peer factor 1.00 | Not applicable |

Tools: the work was developed with Claude Code, an AI coding assistant. Each commit carries a
`Co-Authored-By` line to show it.

Signed: ______________________ (Tung Nguyen)    Date: ______________
