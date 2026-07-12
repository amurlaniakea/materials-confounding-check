# Roadmap — materials-confounding-check

**Licencia**: AGPL-3.0-or-later · **Año**: 2026 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com

## Visión general
Pivot de `crystal-stability-screen` (gap invalidado por PhononScore). MVP de 1–2 semanas que
implementa el test de falsificación de confounding bibliográfico como CLI reusable sobre un
dataset arbitrario. Fase 2 valida contra los 5 datasets del paper (si T0 los confirma
accesibles). Fase 3 empaqueta y sube a GitHub con aislamiento git.

## Fases / Releases

### Fase 1 — MVP CLI + 4 tests (2026-07 → 2026-08, ~2 semanas)
| Feature ID | Feature | Prioridad | Estimación | Estado |
|------------|---------|-----------|------------|--------|
| 001 | Modelo `Dataset`/`Metadata` + ingestión CSV/JSON/parquet | P0 | 2 días | pendiente |
| 002 | Enriquecimiento bibliográfico (Crossref: autor/journal/año) | P0 | 2 días | pendiente |
| 003 | Test 1: clasificador metadata-desde-descriptores | P0 | 2 días | pendiente |
| 004 | Test 2: modelo con bibliographic fingerprint como único input | P0 | 2 días | pendiente |
| 005 | Test 3: group/time-split vs random, caída de rendimiento | P0 | 2 días | pendiente |
| 006 | Test 4: veredicto de riesgo + reporte | P0 | 1 día | pendiente |
| 007 | Fixture sintético + tests AC-1..AC-6 | P0 | 2 días | pendiente |

### Fase 2 — Validación con datasets reales (post-MVP, condicionada a T0)
| Feature ID | Feature | Prioridad | Estimación | Estado |
|------------|---------|-----------|------------|--------|
| 008 | Pipeline sobre MOF/perovskite/batería/TADF del paper (T0 ya cerrado a nivel política). **Incluye check estricto: `curl -sI` Content-Type/Content-Length + descarga de primeros KB para confirmar CSV/JSON real, NO solo status code.** | P1 | 3 días | pendiente |
| 009 | Diferencial frente a Giskard ya confirmado por auditor (4.8k★, v2 legacy) | P1 | 1 día | done |

### Fase 3 — Empaquetado + GitHub + Calidad (al ~90%)
| Feature ID | Feature | Prioridad | Estimación | Estado |
|------------|---------|-----------|------------|--------|
| 010 | pyproject (package-mode=false), README, LICENSE, RESEARCH.md | P0 | 1 día | pendiente |
| 011 | GitHub Actions (ruff→pytest→SonarCloud) | P0 | 1 día | pendiente |
| 012 | `gh repo create --source . --push` (aislamiento git) | P0 | 0.5 día | pendiente |

## Dependencias entre features
- `003`–`006` dependen de `001`, `002`.
- `007` depende de `001`–`006`.
- `008` depende de `007` y de T0 (datasets accesibles).
- `009` (Giskard) es independiente; debe cerrarse antes de publicar.

## Riesgos y mitigaciones
| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Los 5 datasets no son accesibles (403/credenciales) | Media | Medio | T0 documenta blocker; MVP usa fixture sintético con confounding conocido. |
| Giskard cubre este test (gap cae) | Baja | Alto | `009` verifica API antes de publicar; si cae, reacotar o pivotar. |
| Crossref rate-limit en enriquecimiento | Media | Bajo | cache local de metadata; modo offline con metadata ya presente. |
| Fugado de secretos al crear repo en /home/sil | Baja | Alto | `.gitignore` excluye secretos; `git init` propio dentro del dir. |

---

*Documento vivo — actualizar al replanificar.*
