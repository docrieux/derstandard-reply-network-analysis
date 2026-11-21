# Código obsoleto

Código que ya no corresponde al planteamiento actual. Se guarda como registro de cómo avanzó el proyecto; no se usa para resultados nuevos.

| Carpeta | Movido | Motivo |
|---|---|---|
| `01-reply-opposition-lifetime/` | 2026-11-21 | Implementa el diseño antiguo (PLAN del 2026-10-06, H1–H4, escrito y ejecutado por la IA). Sustituido por el planteamiento del 2026-11-19 (ver `notes/method/WORKLOG.md`). |

Los scripts siguen funcionando desde aquí: `common.py` calcula las rutas con `HERE.parents[2]` y el nombre de la carpeta, que no cambian. Si se vuelven a ejecutar, escriben en `notes/experiments/01-reply-opposition-lifetime/results/`.

`check_duplicate_comments.py` y `check_self_votes.py` salieron de aquí el 2026-11-21: son comprobaciones del dataset, se repitieron con el mismo resultado y están en `code/dataset-checks/`.

`00_to_parquet.py` y `01_reply_edges.py` salieron de aquí el 2026-11-21: son preparación de datos genérica y están en `code/dataset-prep/`, con sus rutas en `prep_common.py`. Los scripts 02–09 de esta carpeta leen las tablas que generan.
