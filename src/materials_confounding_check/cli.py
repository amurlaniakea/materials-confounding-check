"""CLI entrypoint: `mcc check --in <dataset> --out <report.json>`."""

from __future__ import annotations

import json
import sys

import typer

from materials_confounding_check.check import run
from materials_confounding_check.io_data import read_dataset

app = typer.Typer(help="Bibliographic-confounding falsification test for materials ML datasets.")


@app.callback()
def main_callback() -> None:
    """Bibliographic-confounding falsification test for materials ML datasets."""
    pass


@app.command()
def check(
    in_file: str = typer.Option(..., "--in", help="Dataset CSV/JSON/parquet"),
    out_file: str = typer.Option(..., "--out", help="Output JSON report path"),
    seed: int = typer.Option(20260712, "--seed", help="Determinism seed"),
    no_metadata_enrich: bool = typer.Option(False, "--no-metadata-enrich", help="Skip Crossref enrichment (offline)"),
    group_by: str = typer.Option("year", "--group-by", help="Group/time split key: year|author"),
    n_perm: int = typer.Option(100, "--n-perm", help="Null-distribution permutations (statistical rigor). Default 100."),
) -> None:
    """Run the four falsification tests and write a JSON verdict."""
    try:
        dataset = read_dataset(in_file)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"error: {e}", err=True)
        raise typer.Exit(code=2)
    except Exception as e:  # pragma: no cover - defensive
        typer.echo(f"error: unexpected failure reading dataset: {e}", err=True)
        raise typer.Exit(code=2)

    verdict = run(dataset, seed=seed, group_by=group_by, n_perm=n_perm)
    with open(out_file, "w") as fh:
        json.dump(
            {
                "risk": verdict.risk,
                "score": verdict.score,
                "triggered_tests": verdict.triggered_tests,
                "report": verdict.report,
            },
            fh,
            indent=2,
        )
    typer.echo(
        f"risk={verdict.risk} score={verdict.score} triggered={verdict.triggered_tests}",
        err=True,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(main())
