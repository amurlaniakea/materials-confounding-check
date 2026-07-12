# Tasks — materials-confounding-check v1 (FEAT-001..007)

**Licencia**: AGPL-3.0-or-later · **Año**: 2026 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com

## Checklist de implementación (orden de ejecución)

### 0. Preparación
- [x] **T001** — Leer `spec.md` y `plan.md` completos.
- [x] **T002** — Crear rama `feature/001-mvp` en el repo propio del proyecto.
- [x] **T003** — Verificar entorno (venv, pyproject, pytest).
- [x] **T0** — ✅ CERRADO a nivel de política (2026-07-12): endpoint de datasets confirmado en 3/4 fuentes (figshare 202, web 200); MOFSimplify referencia confirmada. ⚠️ Contenido real (Content-Type/primeros KB) NO verificado — eso es T008 (Fase 2). HTTP 202 ≠ fichero descargado. Ver mission.md sección T0 + nota de rigor.
- [x] **T060** — ✅ Giskard verificado por auditor (4.8k★, v2 legacy, NO cubre test bibliográfico) → diferencial confirmado. Ver mission.md.

### 1. Modelos / Datos (FEAT-001)
- [x] **T010** — `models.py`: `Dataset`, `Metadata`, `ConfoundingVerdict`.
- [x] **T011** — `io_data.py`: `read_dataset` CSV/JSON/parquet + validación estructural.
- [x] **T012** — Tests de ingestión (AC-1, AC-6).

### 2. Metadata + Tests (FEAT-002..006)
- [x] **T020** — `metadata.py`: enriquecimiento Crossref (hook offline + cache).
- [x] **T021** — `tests_/metadata_clf.py` (Test 1) + baseline de permutación.
- [x] **T022** — `tests_/fingerprint.py` (Test 2) + baseline de permutación.
- [x] **T023** — `tests_/split_eval.py` (Test 3, bucketizado de year).
- [x] **T024** — `tests_/verdict.py` (Test 4).

### 3. Orquestación + CLI (FEAT-006 + CLI)
- [x] **T030** — `check.py`: `run` → `ConfoundingVerdict` (AC-2, AC-3).
- [x] **T031** — `cli.py`: typer `check --in --out --seed --no-metadata-enrich` (AC-1, AC-5).

### 4. Fixture + Determinismo (FEAT-007)
- [x] **T040** — `tests/data/fixture.py`: fixture con confounding inyectado, seed fijo.
- [x] **T041** — `test_ac4_detection.py`: AC-4 NO-CIRCULAR (detecta inyectado, no limpio).
- [x] **T042** — `test_ac2_metadata.py`, `test_ac3_split.py`, `test_ac5_flags.py`, `test_ac6_invalid.py` (unificados en test_ac2_ac3_ac5.py + test_ac1_pipeline.py).

### 5. Calidad y cierre (hasta ~90%)
- [x] **T050** — `ruff check .` → All checks passed.
- [x] **T051** — `pytest` rápida (7 passed) + coverage medido: **77% TOTAL** (core 85-100%; cli.py/metadata.py 0% sin test). Sin afirmar cifra sin medir (corrección deuda técnica #3).
- [x] **T052** — Contrato único de dataclass verificado (`check.Dataset is models.Dataset`).
- [x] **T053** — Snapshot crudo en `sdd/verify_mvp.md` para el auditor externo.
- [x] **T054** — Null distribution: N=100 permutaciones deterministas + decisión por percentil-95 (corrección deuda técnica #1; sustituye margen fijo).
- [x] **T055** — AC-4 con sweep de 4 seeds (`@pytest.mark.slow`); veredicto estable (corrección deuda técnica #2).
- [x] **T056** — `pytest --cov` ejecutado; 77% real documentado (cierra T051).

### 6. Fase 2 — datasets reales (T008)
- [x] **T008** — `dataset_verify.py`: verifica contenido REAL (Content-Type + primeros KB, no solo
  status). Tests locales (http.server) csv→ok / html→rejected / 202→flagged; test real TADF
  (figshare zip, HTTP 200, application/zip, magic PK) pasa. Batería: URL figshare 12641035 que se
  INFIRIÓ era FALSA (artículo de econometría) → corregida en mission.md; URL real de batería NO
  verificada por Hermes, no inventada. Perovskite/MOFSimplify: referencia confirmada, URL de
  descarga no verificada (pendiente, no bloquea).

### 7. Fase 2 — cierre de cobertura (cli.py / metadata.py)
- [x] **T057** — Tests de pytest para `cli.py` (4 tests, CliRunner): spurious→high, clean→reporte
  bien formado, `--n-perm` se propaga, entrada rota→exit 2. Cobertura cli.py: **92%** (líneas
  60/64 = `main()`, no ejercidas por CliRunner — aceptable).
- [x] **T058** — Tests de pytest para `metadata.py` (3 tests): offline devuelve rows igual,
  online NO fabrica metadata (integridad), preserva campos existentes. Cobertura metadata.py:
  **56%** (ramas de cache-file no ejercidas; hook offline core cubierto).
- Cobertura TOTAL del proyecto subió de 77% → **~88%**.

### Nota de concurrencia (resuelta)
- #1 Permutación de 1 muestra + margen fijo → null de 100 permutaciones + percentil-95.
- #2 Un solo seed → sweep de 4 seeds (spurious→high, clean→low estables).
- #3 Claim de cobertura sin medir → medido real (77%).

### Nota de concurrencia (resuelta)
- Durante Fase 2, un **subagente hermano** (`20260712_021035_e392fc`) escribió `verify_mvp.md` en
  paralelo. No hubo colisión destructiva (el patch de Hermes se aplicó íntegro). Sil confirmó que
  era un subagente legítimo, no un artefacto del entorno. Riesgo acotado: evitar escritura
  concurrente sin coordinación en el repo con `.git` propio cuando haya datos reales de por medio.

## Definición de "Done"
- Compila (`py_compile`) + tests locales verdes + ruff OK + sin warnings nuevos.
- AC-4 no circular (fixture con confounding inyectado independiente).

## Notas / Blockers
- ✅ T0: CERRADO (2026-07-12) — accesibilidad de datasets confirmada en 3/4 fuentes (figshare 202, web 200); MOFSimplify referencia confirmada, URL pendiente de localizar (no bloquea). Ver mission.md sección T0.
- ✅ T060: Giskard verificado por auditor externo (4.8k★, v2 legacy, NO cubre el test bibliográfico) → diferencial confirmado. Gap reforzado.
- Repo del proyecto con `.git` propio; `.gitignore` excluye secretos. Nunca `git add` en /home/sil.

---

*Actualizar checkboxes al completar cada tarea. Marcar blockers inmediatamente.*
