# Resultados del diseño antiguo (2026-10-06 a 2026-11-02)

Salidas del código del diseño antiguo (PLAN del 2026-10-06), conservadas como registro de lo que dio ese diseño [me, 2026-11-21]. No son resultados del planteamiento actual. El texto que las interpretaba (`RESULTS.md`, `EXPLICACION*.md`, `PREGUNTAS.md`, `CODE-REVIEW.md`) se eliminó en el barrido del 2026-11-21; se puede recuperar en el commit `4106db3`.

`run.log` registra cada ejecución con fecha, duración y recuentos.

## Qué script produjo cada archivo
Comprobado el 2026-11-21 buscando el nombre de cada archivo en el código.

| Prefijo | Script | Archivos |
|---|---|---|
| 01 | `code/dataset-prep/01_reply_edges.py` | `01_reply_funnel.csv` |
| 04 | `code/_obsoleto/01-…/04_h1_comment_level.py` | `04_h1_comment_level.csv`, `04_h1_by_year.png` |
| 05 | `code/_obsoleto/01-…/05_h2_h3_dyad_faction.py` | `05_h2_dyad.csv`, `05_h2_dyad.png`, `05_h2_by_depth_year.csv`, `05_h3_factions.csv`, `05_h3_projected_factions.csv`, `05_h3_stance_by_faction_relation.csv`, `05_projection_validation.csv`, `05_reply_back.csv` |
| 06 | `code/_obsoleto/01-…/06_lifetime.py` (+ `h4.py`) | `06_h4_*.csv`, `06_h4_cox.png`, `06_km_by_cohort.csv`, `06_lifetime_*`, `06_opposition_by_tenure.csv` |
| 07 | `code/_obsoleto/01-…/07_multiverse.py` | `07_multiverse.png`, `07_multiverse_h2.csv`, `07_multiverse_h4.csv` |
| 08 | `code/_obsoleto/01-…/08_positive_votes.py` | `08_*` |
| 09 | `code/_obsoleto/01-…/09_top_decile_lifetime.py` | `09_*` |

## Cifras principales, leídas de los CSV (2026-11-21)
Solo describen lo que calculó el diseño antiguo. Sus problemas están en `notes/method/BASE-VERIFICADA.md`, §4.

| Qué | Valor | Archivo, fila |
|---|---|---|
| H1: P(voto − \| responde) vs P(voto − \| no responde), mismo comentario | 0,533 vs 0,301; OR_MH = 4,43 [4,42; 4,44]; 8.117.960 estratos (comentarios) | `04_h1_comment_level.csv`, `all` |
| H1 positivo | OR_MH = 0,226 | `08_h1_positive.csv`, `all` |
| H2 (variante `excl`): proporción de aristas negativas (≥ 5 votos) | 0,314 vs 0,181 del nulo; diferencia 0,133 [0,126; 0,140] | `05_h2_dyad.csv`, `excl,p_negedge5` |
| H3: proporción de respuestas entre facciones | 0,260 observado; 0,232 nulo; 0,468 mezcla aleatoria por tamaño | `05_h3_factions.csv` |
| Proyección de facciones | AUC 0,629; accuracy 0,676; 14.787 etiquetados | `05_projection_validation.csv` |
| Reply-back: P(B responde a la respuesta de A) | 0,318 si A votó − al padre; 0,166 si votó +; 0,298 si no votó | `05_reply_back.csv` |
| H4 (Cox), HR por DE | votos − recibidos 1,114 [1,104; 1,123]; respuestas hostiles recibidas 1,059 [1,050; 1,068]; respuestas hostiles enviadas 1,040; recibió alguna respuesta 0,946; log comentarios 1,229 | `06_h4_cox.csv` |
| H4: población | 98.670 usuarios en el landmark de 30 días; 59,1 % eventos | `run.log` |
