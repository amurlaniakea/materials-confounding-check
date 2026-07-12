# Plan — materials-confounding-check v1 (FEAT-001..007)

**Licencia**: AGPL-3.0-or-later · **Año**: 2026 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com

## Enfoque técnico
CLI typer. Entrada: dataset (CSV/JSON/parquet) con features químicas + metadata bibliográfica.
`metadata.py` enriquece vía Crossref (autor/journal/año) con cache local y modo offline.
Cuatro módulos en `tests_/` implementan los tests de Jablonka como funciones puras
(`dataset, seed -> resultado`). `check.py` orquesta y emite `ConfoundingVerdict`. El fixture
sintético (`data/fixture.py`) inyecta confounding de forma INDEPENDIENTE (filas con autor/año
correlacionado con target por diseño) para que AC-4 no sea circular.

## Archivos a crear / modificar
| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/materials_confounding_check/__init__.py` | crear | exports + `__version__`. |
| `src/materials_confounding_check/models.py` | crear | `Dataset`, `Metadata`, `ConfoundingVerdict` (canónicas, UNA vez). |
| `src/materials_confounding_check/io_data.py` | crear | `read_dataset` CSV/JSON/parquet con validación pydantic. |
| `src/materials_confounding_check/metadata.py` | crear | enriquecimiento Crossref + cache + modo offline. |
| `src/materials_confounding_check/tests_/metadata_clf.py` | crear | Test 1. |
| `src/materials_confounding_check/tests_/fingerprint.py` | crear | Test 2. |
| `src/materials_confounding_check/tests_/split_eval.py` | crear | Test 3. |
| `src/materials_confounding_check/tests_/verdict.py` | crear | Test 4. |
| `src/materials_confounding_check/check.py` | crear | `run(dataset, seed) -> ConfoundingVerdict`. |
| `src/materials_confounding_check/cli.py` | crear | typer `check`. |
| `tests/data/fixture.py` | crear | fixture con confounding inyectado, seed fijo. |
| `tests/test_ac1_pipeline.py`, `test_ac2_metadata.py`, `test_ac3_split.py`, `test_ac4_detection.py`, `test_ac5_flags.py`, `test_ac6_invalid.py` | crear | AC-1..AC-6. |

## Estructuras de datos / Modelos
```python
@dataclass
class Dataset:
    dataset_id: str
    features: dict[str, list[float]]
    metadata: list[Metadata]
    target: list[float]

@dataclass
class ConfoundingVerdict:
    risk: str
    score: float
    triggered_tests: list[str]
    report: dict
```

## Algoritmos / Lógica clave
- **Test 1 (metadata_clf)**: clasificador (sklearn) predice author/journal/año desde features;
  mide accuracy/F1 vs baseline de azar (1/n_clases). `above_chance = acc > baseline + margen`.
- **Test 2 (fingerprint)**: modelo de la propiedad target usando SOLO metadata predicha como
  input; compara su R²/accuracy contra el modelo con features químicas reales.
  `ratio = perf_fingerprint / perf_chemo`; si `ratio` alto → confounding sospechoso.
- **Test 3 (split_eval)**: entrena con split aleatorio y con group/time split (por autor/año);
  `delta = perf_random - perf_group`; caída grande → el modelo depende de atajos de grupo.
- **Test 4 (verdict)**: `score = f(above_chance, ratio, delta)`; `risk` por umbrales;
  `triggered_tests` lista los tests que superaron su umbral.

El fixture inyecta confounding así: en las filas "spurious", `year` se correlaciona con `target`
(rango de años distinto por clase de target), de modo que un tester correcto lo recupere vía
Test 1 y Test 3. Las filas "clean" tienen metadata independiente del target.

## Configuración / Environment variables
| Variable | Requerida | Default | Descripción |
|----------|-----------|---------|-------------|
| `MCC_SEED` | No | `20260712` | Semilla por defecto. |
| `CROSSREF_MAILTO` | No | - | Email para Crossref polite pool (opcional). |

## Seguridad
- **Validación**: pydantic en `Dataset`. **Sin red en modo offline**. **Sin privilegios**.

## Testing strategy
| Tipo | Qué | Herramienta | Cobertura |
|------|-----|-------------|-----------|
| Unit | cada test sobre fixture | pytest | 100% tests_ |
| Integration | `run` → `ConfoundingVerdict` + CLI | pytest + CliRunner | ≥85% |
| Determinismo | AC-4 fixture con seed | pytest | 100% detección |

## Riesgos técnicos
| Riesgo | Mitigación |
|--------|------------|
| Dataclass duplicada | `Dataset`/`Metadata`/`ConfoundingVerdict` definidas UNA vez en `models.py`. Test: `check.Dataset is models.Dataset`. |
| AC-4 circular | Fixture con confounding inyectado independientemente (no por las reglas del tester). |
| Crossref rate-limit | cache + `--no-metadata-enrich`. |

---

*Documento vivo — actualizar si el enfoque técnico cambia durante la implementación.*
