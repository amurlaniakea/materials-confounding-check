# Verify — MVP v1 (FEAT-001..007), revisado por deuda técnica

**Fecha**: 2026-07-12 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com
**Método**: SDD (Constitution → Specify → Plan → Tasks → Implement → Verify)
**Revisión**: corrige 3 deudas técnicas señaladas por el auditor externo (permutación de 1 muestra,
un solo seed, claim de cobertura sin medir).

## Correcciones aplicadas (deuda técnica)
1. **Null distribution, no fixed margin.** `metadata_clf` y `fingerprint` decidían antes contra un
   margen fijo (0.05 → 0.10) sobre UNA sola permutación. Eso es exactamente el anti-patrón Clever-Hans
   que el proyecto detecta: ajustar el umbral hasta que "pasa" con este seed. Ahora: **N=100
   permutaciones deterministas por seed**, decisión por **percentil-95** de la distribución nula
   (`real > np.percentile(perm_accs, 95)`). Mecánico, no reabre diseño.
2. **Sweep de seeds.** AC-4 corre ahora con **4 seeds** (20260712, 101, 777, 424242). Marcado
   `@pytest.mark.slow` (excluido de la suite rápida, ejecutado aparte). Si el veredicto volteara con
   el seed, el null seguiría siendo frágil; con N=100 permutaciones + percentil-95 se mantiene estable.
3. **Cobertura medida, no afirmada.** T051 ya no dice "≥85% cobertura" sin medir: se corrió
   `pytest --cov` y el número real es 77% TOTAL (ver abajo). cli.py y metadata.py bajan el total
   (sin tests de pytest); el core lógico está 85-100%.

## Resultado de verificación (evidencia cruda)
### py_compile
```
COMPILE OK
```
### ruff
```
All checks passed!
```
### pytest rápida (sin slow) + cobertura real
```
7 passed, 2 deselected, 774 warnings in 141.00s
TOTAL 308 stmts, 72 miss, 77% cover
  check.py ............ 100%
  models.py ........... 96%
  metadata_clf.py ..... 98%
  fingerprint.py ...... 87%  (faltan ramas regression en el fixture actual, que es classification)
  split_eval.py ....... 85%
  verdict.py .......... 85%
  io_data.py .......... 79%  (ramas JSON/parquet no ejercidas en fixture CSV)
  cli.py .............. 0%   (no test de pytest; validado manualmente con `mcc`, ver abajo)
  metadata.py ......... 0%   (hook offline; Fase 2 conecta Crossref)
```
### pytest slow (sweep de seeds, n_perm=100)
```
2 passed (test_ac4_spurious_detected_across_seeds, test_ac4_clean_not_flagged_across_seeds)
en 145.74s — veredicto estable en los 4 seeds.
```
### CLI end-to-end (AC-1, AC-5, AC-6) — manual
- Spurious fixture → `risk=high triggered=['metadata_clf','bibliographic_fingerprint']`
- Clean fixture   → `risk=low triggered=[]`
- Broken input    → `error: missing required target column 'target' (AC-6)` · `exit=2`

## AC cubiertos
| AC | Estado | Evidencia |
|----|--------|-----------|
| AC-1 | ✅ | CLI corre 4 tests + reporte JSON |
| AC-2 | ✅ | metadata_clf reporta above_chance + baseline + permuted_p95 (n_perm) |
| AC-3 | ✅ | split_eval reporta delta_random_vs_group |
| AC-4 | ✅ NO-CIRCULAR + ROBUSTO | fixture inyectado; clean→low, spurious→high en 4 seeds; null de 100 perm |
| AC-5 | ✅ | --seed determinista, --no-metadata-enrich aceptado |
| AC-6 | ✅ | entrada rota → exit 2 + mensaje claro |

## Confirmación de n_perm de PRODUCCIÓN (condición de aprobación de Fase 2)
El auditor pidió confirmar con evidencia qué `n_perm` usa la CLI de producción (no los tests).
Verificado en crudo:
- `check.py:12` → `def run(..., n_perm: int = 100)` (default de producción = **100**).
- `cli.py:29` → `n_perm: typer.Option(100, "--n-perm", ...)`; `cli.py:41` → `run(..., n_perm=n_perm)`.
- Ejecución real: `mcc check --in ds.csv --out rep.json` (SIN `--n-perm`) → reporte JSON
  `"bibliographic_fingerprint": { "n_perm": 100, ... }`.

Conclusión: el rigor estadístico (null de 100 permutaciones + percentil-95) está ACTIVO en uso
real. Los tests bajaron a `n_perm=20` SOLO en sus llamadas locales (`run(ds, ..., n_perm=20)`)
para velocidad de la suite rápida; el código de producción nunca se tocó. Se añadió `--n-perm`
como opción explícita en la CLI para blindar el default ante ediciones futuras.

## T008 — verificación de contenido real de datasets (Fase 2)
El módulo `dataset_verify.py` verifica contenido REAL (Content-Type + primeros KB), no solo
status code. HTTP 202 ≠ fichero descargado; una landing HTML no es el dataset.

Tests (locales, http.server determinista — la red del sandbox reinicia conexiones externas):
- CSV real → `ok=True`, `kind=csv`, `http_code=200` ✅
- HTML landing → `ok=False`, `kind=html` ✅
- Endpoint 202 async → `ok=False`, `note` menciona 202 ✅

Test real (marcado `@pytest.mark.slow`, red externa):
- TADF figshare ndownloader 43183206 → `ok=True`, `http_code=200`, `Content-Type=application/zip`,
  cuerpo = zip con CSVs (magic `PK`) ✅

Hallazgo honesto durante T008: la URL figshare `12641035` que se INFIRIÓ para el dataset de
**batería** era FALSA — ese article es "Direct effect and spatial spillover effect of different
spatial weight matrices in strategic innovation" (econometría), no el dataset de batería de
Huang & Cole. Corregido en `mission.md`: la URL real de batería NO se verificó ni se inventó;
queda como referencia bibliográfica confirmada (DOI 10.1038/s41597-020-00602-2) pendiente de
localizar en "Data availability". TADF (24004182) sí es correcto y verificado.

## Nota de concurrencia (resuelta)
Durante Fase 2 un subagente hermano (`20260712_021035_e392fc`) escribió `verify_mvp.md` en
paralelo. Sin colisión destructiva. Sil confirmó que era un subagente legítimo, no un artefacto.
- GroupKFold con años únicos → bucketizado de `year` en grupos de 5 años.
- Typer con un solo comando colapsaba → `@app.callback()` añadido para enrutar `mcc check`.
- Coste: N=100 permutaciones × CV es caro → suite rápida usa n_perm=20; el claim estadístico
  (n_perm=100 + sweep de seeds) queda en el marker `slow`, ejecutable aparte.

## Pendiente (Fase 2, no bloquea)
- T008: verificar contenido REAL de los 4 datasets (HTTP 202 ≠ fichero; `curl -sI` Content-Type +
  primeros KB) antes de darlos por buenos.
- T009: diferencial frente a Giskard ya confirmado por auditor (4.8k★, v2 legacy).
- Fase 2: conectar Crossref real en metadata.py (hoy hook offline) + añadir tests de pytest a cli.py.

---

*Verificación en crudo entregada al auditor externo (Sil/Claude) antes de aprobar Fase 2.*
