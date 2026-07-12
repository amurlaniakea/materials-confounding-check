# Research notes & sources

This tool implements the *Clever Materials* falsification test for materials-science ML datasets:
does the model rely on a **bibliographic fingerprint** (year / author / journal leaking the target)
rather than chemistry? These are the primary sources consulted while building it.

## Core motivation
- **Jablonka, A. M., et al. — "Clever Materials" (2026).** Demonstrates widespread confounding /
  shortcut learning across 5 materials-science tasks (MOF thermal stability, MOF solvent removal,
  perovskite solar cells, battery materials, TADF emitters) and argues for routine falsification
  tests. The repo `lamalab-org/clever-materials-hans` (MIT) is the reference implementation but is
  not a reusable CLI — this tool fills that gap.
  - Preprint: arXiv:2602.17730

## Datasets (from the *Clever Materials* Methods section)
| Task | Source | Reference | DOI / link |
|------|--------|-----------|------------|
| Battery materials | Huang & Cole, *Scientific Data* 2020 | dataset of battery materials | https://doi.org/10.1038/s41597-020-00602-2 |
| Perovskite solar cells | Shabih et al. / Jacobsson, *Nature Energy* 2021 | perovskitedatabase.com | https://www.perovskitedatabase.com |
| MOF (MOFSimplify) | Nandy et al., *Scientific Data* 2022 | MOF stability simplification | https://doi.org/10.1038/s41597-022-01181-0 |
| TADF emitters | Huang & Cole, *Scientific Data* 2024 | thermally activated delayed fluorescence molecules | https://doi.org/10.1038/s41597-023-02897-3 |

> Note (honesty): the figshare article id `12641035` was at one point inferred for the battery
> dataset but turned out to be an unrelated econometrics article. The battery dataset's real
> download URL was not verified here; the DOI above is the confirmed bibliographic reference.
> TADF (figshare `24004182`) was confirmed reachable; MOFSimplify/perovskite references are
> confirmed but their direct download URLs were not verified by this project.

## Gap vs existing tooling
- **Giskard** (`Giskard-AI/giskard`, ~4.8k★) covers generic tabular data-leakage scanning, but its
  v2 tabular scanner is legacy / unmaintained and does **not** run the bibliographic-fingerprint
  test specific to materials science. That gap is what this tool targets.

## Related
- `crystal-stability-screen` (archived): a prior niche candidate invalidated because
  `PhononScore` (MIT, functional) already fills that gap.
