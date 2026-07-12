# materials-confounding-check

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

CLI that applies the *Clever Materials* falsification test to materials-science ML datasets:
does your model cheat via a **bibliographic fingerprint** (year / author / journal leaking the
target) rather than from chemistry?

## What it does

Takes a dataset of materials with descriptors + bibliographic metadata (author, journal, year)
and a target property, and runs four falsification sub-tests:

1. **Metadata classifier** — can the bibliography be predicted from the chemical descriptors
   alone? (above-chance ⇒ a bibliographic signal is present)
2. **Bibliographic fingerprint** — does a model using ONLY the predicted metadata approach the
   descriptor model? (the dataset may not rule out "cheating" via bibliography)
3. **Group/time split** — does performance collapse under an author/year split vs a random split?
4. **Verdict** — assembles a `low` / `medium` / `high` confounding-risk score.

The statistical core uses a **null distribution of N=100 metadata permutations** (percentile-95
threshold), not a hand-tuned fixed margin — the same rigor the tool demands of the models it
audits.

## Install

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
```

## Usage

```bash
mcc check --in dataset.csv --out report.json
```

Options: `--seed` (determinism), `--n-perm` (null-distribution permutations, default 100),
`--group-by` (year|author), `--no-metadata-enrich` (offline).

The report JSON contains the four sub-test blocks and the final `risk` verdict.

## Why this exists

The *Clever Materials* paper (Jablonka et al.) showed leakage/confounding is widespread in
materials ML. Existing tools (e.g. Giskard) cover generic tabular leakage but do **not** run the
bibliographic-fingerprint test specific to materials science. This tool fills that gap.

## License

[AGPL-3.0-or-later](LICENSE) · Copyright © 2026 Pedro Sordo Martínez — amurlaniakea@gmail.com
