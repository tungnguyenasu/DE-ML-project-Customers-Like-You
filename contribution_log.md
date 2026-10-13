# Contribution log (C2)

Individual project: Tung Nguyen holds both the Data Engineer and the ML Engineer role, so every task
below is owned by the same person. Evidence points to the commit and the file that show the work
(`git show <commit>`).

| Date | Task | Owner | Evidence (commit, file or figure) | Status |
| --- | --- | --- | --- | --- |
| 2026-10-12 | Step 0: data downloaded, row count noted | Tung Nguyen | `2ffad03`, [README.md](README.md#data) (1,067,371 lines) | Done |
| 2026-10-12 | J1: success targets | Tung Nguyen | `e1c29e1`, [README.md](README.md#success-targets-j1) | Done |
| 2026-10-12 | DE1: data profile | Tung Nguyen | `2ffad03`, [data_profile.md](reports/data_profile.md) | Done |
| 2026-10-12 | DE2: cleaning and cleaning log | Tung Nguyen | `2ffad03`, [cleaning_log.md](reports/cleaning_log.md) | Done |
| 2026-10-12 | DE3: time split and held-out purchases | Tung Nguyen | `2ffad03`, validation split `337bbbd`, [split_report.md](reports/split_report.md) | Done |
| 2026-10-12 | DE4: sparse matrix and index maps | Tung Nguyen | `2ffad03`, [build_matrix.py](build_matrix.py) | Done |
| 2026-10-12 | DE5: matrix report | Tung Nguyen | `2ffad03`, [matrix_report.md](reports/matrix_report.md) | Done |
| 2026-10-12 | DE6 (stretch): one-command rebuild | Tung Nguyen | `2ffad03`, `python build_matrix.py` | Done |
| 2026-10-12 | ML1: method decision before fitting | Tung Nguyen | `3268578`, [method_decision.md](method_decision.md) | Done |
| 2026-10-12 | ML2: k chosen with evidence | Tung Nguyen | `f6e8fcd`, [analysis.ipynb](analysis.ipynb) section 2, [choose_k.png](figures/choose_k.png), [compression_loss.png](figures/compression_loss.png) | Done |
| 2026-10-12 | ML3: recommendation function | Tung Nguyen | `a1098ee` and `f6e8fcd`, [recommender.py](recommender.py), [nightly_job.py](nightly_job.py) | Done |
| 2026-10-12 | ML4: test evaluation and nightly-job timing | Tung Nguyen | `f6e8fcd`, [results.md](reports/results.md) | Done |
| 2026-10-12 | ML5: PCA vs SVD comparison table | Tung Nguyen | `a1098ee`, re-run `f6e8fcd`, [pca_vs_svd.md](reports/pca_vs_svd.md) | Done |
| 2026-10-12 | ML6: customer map and named segments | Tung Nguyen | `f6e8fcd`, [customer_map.png](figures/customer_map.png) | Done |
| 2026-10-12 | ML7 (stretch): purchase-value sensitivity | Tung Nguyen | `f6e8fcd`, [analysis.ipynb](analysis.ipynb) section 7 | Done |
| 2026-10-12 | J2: one-page memo | Tung Nguyen | `a54ed29`, [memo.pdf](memo.pdf) | Done |
| 2026-10-12 | J3: slides | Tung Nguyen | `a54ed29`, [slides.pptx](slides.pptx) | Done |
| 2026-10-12 | README: how to run and submission checklist | Tung Nguyen | `3a0d31b`, [README.md](README.md) | Done |
| 2026-10-12 | C2: contribution log | Tung Nguyen | this file | Done |
| n/a | C3: peer evaluation | n/a | Individual project, so peer factor 1.00 | Not applicable |

Tools: the work was developed with Claude Code, an AI coding assistant.

Signed: Tung Nguyen    Date: 10/12/2026
