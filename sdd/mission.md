# Mission — materials-confounding-check

**Estado**: Constitución (Fase 1 de SDD) · nicho propuesto tras PIVOTE de `crystal-stability-screen` (gap invalidado por PhononScore, 2026-07-12)
**Licencia**: AGPL-3.0-or-later · **Año**: 2026 · **Autor**: Pedro Sordo Martínez — amurlaniakea@gmail.com

## Qué construimos
Una CLI (`materials-confounding-check`) que aplica el **test de falsificación de confounding
bibliográfico** de Jablonka et al., "Clever Materials" (arXiv:2602.17730, feb 2026) a un dataset
arbitrario de materials science aportado por el usuario. Dado un dataset con features químicas
+ metadata bibliográfica (autor/journal/año, enriquecida vía Crossref), la herramienta:

1. Entrena un clasificador que predice metadata bibliográfica desde los descriptores químicos.
   Si predice por encima del azar → hay señal de confounding.
2. Entrena un modelo usando SOLO esa metadata predicha ("bibliographic fingerprint") como input.
   Si su rendimiento se acerca al del modelo con features químicas reales → el dataset no descarta
   que el modelo "haga trampa" aprendiendo atajos bibliográficos en vez de química.
3. Aplica splits group/time (separar train/test por autor o por año) y compara la caída de
   rendimiento vs. split aleatorio.
4. Emite un **veredicto de riesgo de confounding** (score + qué test lo dispara).

## Para quién
- **Usuario principal**: autores de benchmarks de ML en materials science (MOFs, perovskitas,
  baterías, TADF) que quieren blindar su dataset antes de publicar; revisores que sospechan
  confounding.
- **Stakeholders**: grupos de materials informatics; laboratorios que entrenan modelos de
  propiedad (capacidad, PCE, estabilidad) y necesitan separar "utilidad predictiva" de
  "evidencia de entendimiento químico".

## Problema que resuelve
Los benchmarks de ML en materials science no descartan que los modelos aprendan atajos
bibliográficos (autor/journal/año) en vez de química real. "Clever Materials" (Jablonka 2026)
lo demuestra en 5 tareas: en MOFs/perovskitas/baterías/TADF, la metadata bibliográfica se predice
por encima del azar desde descriptores estándar, y usada como único input a veces se acerca al
modelo descriptor-based. Eso significa que muchos datasets no descartan explicaciones no-químicas
del éxito. El paper motiva "routine falsification tests" — pero **solo publica el código de
reproducir su paper concreto**, no una herramienta reusable.

## Valor diferencial (gap ACOTADO — lectura obligatoria)
El repo `lamalab-org/clever-materials-hans` (MIT, 0★, creado 2026-02-02) es código de
reproducibilidad del paper (showyourwork + Snakefile, datos NO incluidos en el repo — ver T0).
**NO es una CLI reusable** que el usuario pueda apuntar a su propio dataset. Ese es el gap.

**Matiz de honestidad (para no repetir el error de crystal-stability-screen):**
Existe tooling genérico adyacente de detección de leakage/spurious-correlation en ML tabular
— el auditor citó **Giskard** (~1000★, scan() con detectores de "Data Leakage" y "Spurious
correlation"). Giskard NO hace el test específico de Jablonka: predecir metadata bibliográfica
desde descriptores químicos y usarla como "bibliographic fingerprint". Es dominio y metodología
distintos. **VERIFICADO POR AUDITOR EXTERNO (2026-07-12, Sil, con acceso a búsqueda)**: Giskard
(`Giskard-AI/giskard`) es REAL — 4.8k★, 345 forks, activo. Matiz que REFUERZA el gap: el
proyecto está en reescritura a v3 (mid-2026) centrada en testing de agentes LLM; **el scanner
tabular con detectores de "Data Leakage"/"Spurious correlation" (v2) sigue disponible pero en
modo legacy sin mantenimiento activo**, y de todas formas NO cubre el test de bibliographic
fingerprint. O sea: el tooling adyacente no solo no cubre el test específico — encima está
deprecado. Gap confirmado y reforzado, no debilitado. (Yo, Hermes, no pude confirmar Giskard por
API esta sesión por rate-limit del token; lo registro aquí por verificación del auditor.)

## Métricas de éxito (KPIs)
| Métrica | Target | Cómo se mide |
|---------|--------|--------------|
| Detección de confounding conocido | 100% sobre fixture sintético con ground truth (confounding inyectado) | AC-4 |
| Determinismo | misma entrada → mismo veredicto | AC-4 (seed fijo) |
| Cobertura de tests del paper | los 4 pasos (metadata-clf, fingerprint, group/time split, veredicto) implementados | AC-1..AC-3 |
| Falsos silenciosos | 0 crashes; fallo = error explícito | AC-6 |
| Cobertura tests | ≥ 85% en módulos core | CI pytest + SonarCloud |

## Fuera de alcance (Out of scope)
- Reemplazar a Giskard como framework genérico de leakage detection en ML tabular. Este proyecto
  es un **test de dominio específico** (materials science + bibliographic fingerprint), no un
  scanner genérico.
- Reentrenar modelos de propiedad del usuario; solo evalúa riesgo de confounding de su dataset.
- Servidor/API web — es CLI local.

## T0 — Verificación de datasets (CERRADO 2026-07-12, evidencia real)
El repo `clever-materials-hans` **NO incluye los 5 datasets** (`src/data/.gitignore` = `*`;
confirmado en crudo). Pero el paper "Clever Materials" cita las **fuentes originales** (no el repo
de reproducibilidad), y todas son papers de *Scientific Data* (Nature) cuya política editorial
exige depósito público de datos. Verificación real por Hermes (curl HTTPS, sin inventar URLs):

| Dataset | Fuente original (confirmada) | URL de datos | Accesibilidad |
|---------|------------------------------|--------------|---------------|
| Batería | Huang & Cole, *Scientific Data* 2020 (DOI 10.1038/s41597-020-00602-2) | **URL de descarga NO verificada por Hermes** — la URL figshare `12641035` que se infirió era FALSA (ese article es de econometría, no el dataset); no se inventa una nueva. | 🔴 referencia bibliográfica confirmada vía DOI; URL de datos pendiente de localizar en "Data availability" del paper |
| TADF | Huang & Cole, *Scientific Data* 2023 (DOI 10.1038/s41597-023-02897-3) | figshare ndownloader 43183206 (zip 5MB, confirmado vía API del article 24004182) | ✅ VERIFICADO T008: HTTP 200, Content-Type application/zip, cuerpo = zip con CSVs (magic PK) — contenido real confirmado |
| Perovskita | Shabih et al. 2026 (basado en Jacobsson2021, *Nature Energy*) | perovskitedatabase.com (200) — descarga vía interfaz web | 🟡 HTTP 200 en landing; contenido del fichero NO verificado por descarga directa (requiere navegación de la web) |
| MOF (térmica/solvente) | Nandy et al., *Scientific Data* 2022 (MOFSimplify, DOI 10.1038/s41597-022-01181-0) | Zenodo (403 a curl = rate-limit de scripts, NO bloqueo de política) — URL exacta pendiente de localizar en landing del paper | 🟡 referencia confirmada, URL/contenido no verificados por Hermes |
| (tests internos) | — | — | — |

> ⚠️ **NOTA DE RIGOR (2026-07-12)**: los códigos 202/200 arriba confirman que el **endpoint
> existe y acepta la petición**, NO que el fichero del dataset se haya descargado ni que su
> `Content-Type` sea CSV/JSON real. `202 Accepted` es un código de aceptación asíncrona (típico de
> la API de figshare), no de entrega de binario. El check estricto (`curl -sI` → Content-Type/
> Content-Length, o descargar los primeros KB y confirmar CSV/JSON real) queda como tarea
> obligatoria de Fase 2 (T008), no como "confirmado". No se repite el patrón de sobreclaim de
> crystal-stability-screen.

**Veredicto T0**: accesibilidad **PROBABLE** (no confirmada a nivel de contenido) en 3/4 fuentes
(endpoint existe: figshare 202, web 200). Ninguna mostró bloqueo de política tipo
PhononScore/Zenodo-con-credenciales. La verificación de **contenido real** (Content-Type CSV/JSON,
primeros KB del fichero) es tarea de Fase 2 (T008), no de Constitución. MOFSimplify: referencia
bibliográfica confirmada, URL de descarga no verificada por mí (Zenodo rate-lima curl). El MVP
puede usar fixture sintético para AC de determinismo y añadir los datasets reales en Fase 2 sin
blocker. **T0 = CERRADO a nivel de "sin bloqueo de política"; verificación de contenido pendiente
en T008".**

---

*Documento vivo — actualizar cuando cambie la visión del proyecto.*
