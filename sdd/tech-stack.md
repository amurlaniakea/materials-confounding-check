# Tech Stack — materials-confounding-check

**Licencia**: AGPL-3.0-or-later · **Año**: 2026 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com

## Stack principal
| Capa | Tecnología | Versión | Justificación |
|------|------------|---------|---------------|
| Lenguaje | Python | 3.12 | Ecosistema materials-ML + sklearn nativo. |
| CLI | typer | ≥0.12 | CLI tipada y ligera. |
| Validación | pydantic | ≥2.7 | Validación del contrato `Dataset`/`Metadata`. |
| ML | scikit-learn | ≥1.5 | Clasificadores/regresores para metadata-clf y fingerprint; determinista con seed. |
| Metadata | crossref (crossref_commons) / requests | - | Enriquecimiento bibliográfico vía Crossref API. |
| Testing | pytest | ≥8.0 | Runner estándar, fixtures deterministas. |
| Lint/Format | ruff | ≥0.5 | Lint+format en un binario. |
| CI/CD | GitHub Actions | - | ruff → pytest → SonarCloud. |

**Decisión de peso (hardware):** sin GPU/RAM modesta, se usa scikit-learn (CPU, determinista),
no torch. El test de Jablonka es de biblioteca estándar; no requiere deep learning.

## Convenciones de código
- **Estilo**: PEP 8. **Naming**: snake_case / PascalCase / UPPER.
- **Commits**: Conventional Commits. **Branching**: feature branches → PR → main tras CI + review.

## Arquitectura
- **Patrón**: Modular con pipeline de 4 etapas (Strategy por test).
- **Estructura**:
  ```
  src/materials_confounding_check/
  ├── __init__.py
  ├── models.py          # Dataset, Metadata, ConfoundingVerdict (dataclasses canónicas)
  ├── io_data.py         # lectura CSV/JSON/parquet -> Dataset
  ├── metadata.py        # enriquecimiento Crossref (autor/journal/año)
  ├── tests_/
  │   ├── metadata_clf.py     # test 1
  │   ├── fingerprint.py      # test 2
  │   ├── split_eval.py       # test 3 (group/time vs random)
  │   └── verdict.py          # test 4 (score + qué dispara)
  ├── check.py           # orquesta los 4 tests -> Report
  └── cli.py             # typer entrypoint
  tests/
  data/fixture.py        # fixture sintético, seed fijo, confounding conocido
  ```

## Dependencias clave
| Paquete | Propósito | Licencia |
|---------|-----------|----------|
| typer | CLI | MIT |
| pydantic | validación | MIT |
| scikit-learn | clasificadores/regresores | BSD-3 |
| crossref_commons | metadata bibliográfica | MIT |
| numpy/pandas | estructuras | BSD |
| pytest / ruff | tests/lint | MIT |

## Infraestructura
- **Hosting**: N/A (CLI local). **Secrets**: solo si se usa API key de Crossref (opcional; la API pública funciona sin key).

---

*Documento vivo — actualizar al cambiar stack o convenciones.*
