# Experimento 01: registro de decisiones del diseño antiguo

> Diseño antiguo (PLAN del 2026-10-06). Barrido del 2026-11-21: se conserva solo lo que tiene fuente (`results/run.log`, CSV de `results/`, código). Los resultados principales están en `results/README.md`. Las interpretaciones, advertencias y próximos pasos sin fuente se eliminaron (recuperables en el commit `4106db3`).

Tarea de [[2026-09-30]]: *Analyze who replies to whom and whether their positions are opposed, complemented with an analysis of users' lifetime*.
Código: `code/dataset-prep/` (pasos 00 y 01) y `code/_obsoleto/01-reply-opposition-lifetime/` (pasos 02–09). Datos derivados: `data/derstandard/derived/`.

## Decisiones sobre los datos
Las de limpieza, con sus cifras, están en `notes/dataset/data-treatment.md`. Fuente: `results/run.log`.
1. **Comentarios duplicados:** `DISTINCT`, de 75.644.850 a 75.385.329 filas (verificado: `code/dataset-checks/check_duplicate_comments.py`).
2. **Votos:** se descartan 27.122.483 votos con votante NULL; un voto por (comentario, votante); 0 pares con signos contradictorios; 383.858.436 votos limpios.
3. **Respuestas** (53.427.803 → 44.350.672): 326.643 inconsistentes, 11 sin padre, 7.976.578 con autor borrado, 773.899 autorrespuestas. 26 respuestas tienen el padre posterior y se mantienen.
4. **Modelo nulo (diseño antiguo):** para cada respuesta, el destino nulo es el autor de un comentario anterior del mismo artículo elegido al azar, excluyendo a A (semilla 20261006). Cobertura: 44.349.679 de 44.350.672. 0 comentarios nulos posteriores a la respuesta, 0 de otro artículo, 0 iguales a A. El nulo coincide con el destino real en 1.760.319 casos (4,0 %).
5. **Los votos no tienen fecha** (solo el mes del archivo): ver `BASE-VERIFICADA.md`, H1 de §3.
6. **Inicio de actividad:** `06_lifetime.py` recorta la primera actividad a 2013-01-01 (`greatest(T_START, …)`).
7. **Proporción agregada de votos negativos en las parejas:** 0,071 en las respuestas frente a 0,045 en el nulo (`05_h2_dyad.csv`, `all,neg_share`). Los titulares usaron medidas por arista.
8. **Corrección en H4:** la primera versión de `h4.py` encogía las proporciones hacia Beta(1,1); se cambió a encogerlas hacia la tasa de la población con pseudo-recuento M = 2 (`h4.py`, `h4_frame(…, M=2)` y comentario de la línea 51).
9. **Proyección de facciones a usuarios sin etiqueta:** AUC 0,629 y accuracy 0,676 (`05_projection_validation.csv`); no se usó en conclusiones. Con ella, la proporción entre facciones es 0,297 frente a 0,245 del nulo (`run.log`, `[h3-proj]`).
10. **Votos positivos y top 10 % (2026-11-02, [AI, not yet reviewed]):** scripts 08 y 09. El OR de H1 positivo es el inverso del negativo porque sale de la misma tabla 2×2 (`08_h1_positive.csv`: 0,226 ≈ 1/4,43).

## Limitaciones de los datos para el planteamiento del 2026-11-19
Apuntadas en el repaso del 2026-11-21 [AI, a petición mía]. Son hechos de los datos, no decisiones.
- **Los votos no tienen fecha** (decisión 5). No se puede saber si un voto es anterior o posterior a la respuesta del mismo usuario. Afecta a cómo se formula la pregunta de los votos negativos al responder.
- **Usuarios borrados.** Se excluyen 7.976.578 respuestas (14,9 %) y 27,1M de votos. No se ha comprobado si se comportan distinto del resto; si eran más conflictivos, el foro parecerá más tranquilo de lo que fue.
- **26 respuestas con el padre posterior a la respuesta** (decisión 3). El filtro de `inconsistent_comment_metadata` («Inconsistent timestamp», 1.208 comentarios) no las detecta. Se mantienen.
- **Año 2023 en `reply_edges`.** El dataset va hasta el 2022-12-31, pero el año máximo de las aristas es 2023.
- **Facciones.** `faction_users.tsv` tiene 14.817 usuarios (9.278 en la facción 1, 5.539 en la 2), el 6,0 % de los 247.863 del fichero de usuarios (que incluye usuarios que solo votan).

