# Spec — materials-confounding-check v1 (FEAT-001..007)

**Licencia**: AGPL-3.0-or-later · **Año**: 2026 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com

## Qué hace
Toma un dataset de materials science (features químicas + metadata bibliográfica) y aplica 4 tests
de falsificación de confounding bibliográfico, emitiendo un veredicto de riesgo.

## Contexto / Motivación
Ver `mission.md`: "Clever Materials" (Jablonka 2026, arXiv:2602.17730) demuestra confounding
bibliográfico en 5 tareas; motiva falsification tests rutinarios, pero no hay herramienta reusable.

## Criterios de aceptación (AC)
| ID | Criterio | Cómo se verifica |
|----|----------|------------------|
| AC-1 | Dado un dataset con features+metadata, la CLI corre los 4 tests y emite un reporte con veredicto | `mcc check --in dataset.csv --out rep.json` → exit 0; reporte tiene los 4 bloques |
| AC-2 | Test 1 reporta accuracy/F1 de predecir metadata desde descriptores, con baseline de azar | aserto sobre `report.metadata_clf.above_chance == bool` |
| AC-3 | Test 3 compara rendimiento group/time-split vs random y reporta caída (Δ) | aserto sobre `report.split_eval.delta_random_vs_group` |
| AC-4 | Sobre fixture sintético (seed fijo, confounding INYECTADO conocido) el veredicto detecta el confounding en 100% | `pytest tests/test_ac4_detection.py` → detecta en los casos con confounding, no en los limpios |
| AC-5 | CLI acepta `--no-metadata-enrich` (usar metadata ya presente, offline) y `--seed` | ambos flags cambian comportamiento y se reflejan en reporte |
| AC-6 | Entrada sin features o metadata requerida da error claro y exit != 0, sin traceback crudo | `check --in broken.csv` → mensaje + exit 2 |

> ⚠️ **NOTA DE AUDITORÍA (2026-07-12)**: AC-4 usa fixture con confounding *conocido e inyectado*
> (no generado por las mismas reglas del tester), así que NO es circular como el AC-4 de
> crystal-stability-screen. El fixture define independientemente qué filas tienen atajo
> bibliográfico; el tester debe recuperarlo. Si falla, es fallo real del tester, no del fixture.

## Casos de uso / User Stories
- **Como** autor de benchmark de materials ML **quiero** testear mi dataset por confounding
  **para** no publicar un éxito espurio.
- **Como** revisor **quiero** un test reproducible **para** evaluar si un paper descarta atajos.

## Reglas de negocio / Edge cases
| Escenario | Comportamiento esperado |
|-----------|-------------------------|
| Dataset sin columna de autor/año | Error de validación (AC-6) salvo `--no-metadata-enrich` con metadata presente. |
| `--seed` fijo | Mismos resultados (determinismo, AC-4). |
| Fixture limpio (sin confounding) | Veredicto = "low risk", ningún test dispara. |
| Fixture con atajo | Veredicto = "high risk", al menos 1 test dispara y nombra cuál. |

## API / Interfaces

### Contratos de datos
```python
@dataclass
class Dataset:
    dataset_id: str
    features: dict[str, list[float]]     # descriptor -> valores por fila
    metadata: list[Metadata]             # por fila
    target: list[float]                  # propiedad a predecir

@dataclass
class Metadata:
    row_id: str
    author: str
    journal: str
    year: int

@dataclass
class ConfoundingVerdict:
    risk: str                            # "low" | "medium" | "high"
    score: float                         # [0,1]
    triggered_tests: list[str]
    report: dict                         # 4 bloques
```

### CLI
| Comando | Args | Salida | Códigos |
|---------|------|--------|---------|
| `check` | `--in <csv/json/parquet>`, `--out <json>`, `--seed <int>`, `--no-metadata-enrich` | reporte JSON + resumen stderr | 0 ok, 2 inválido |

## No funcionales
- **Performance**: datasets del paper (<10k filas) en segundos en CPU.
- **Seguridad**: validación estricta (pydantic); sin ejecución de código; Crossref es solo lectura.
- **Determinismo**: scikit-learn con `random_state=seed`.

## Dependencias
- Requiere: FEAT-001 (modelo), FEAT-002 (metadata), FEAT-003..006 (tests), FEAT-007 (fixture).
- Bloquea: FEAT-008 (validación real, condicionada a T0).

---

*Documento vivo — actualizar antes de cualquier cambio importante en la feature.*
