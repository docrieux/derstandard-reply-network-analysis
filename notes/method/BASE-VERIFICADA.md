# Base verificada del proyecto

Archivo de trabajo. Contiene solo afirmaciones verificadas, cada una con su fuente. A partir de aquí escribo el resumen para Andreas y Emma [me].

Creado el 2026-11-21. Lo mantiene la IA a petición mía; el contenido lo decido yo.

## Regla de verificación [me, 2026-11-21]
- Toda afirmación de la literatura, o derivada de ella, que se use para justificar una decisión se cita de forma precisa: archivo, página del PDF, sección, tabla o figura.
- Toda cifra de los datos indica cómo se obtuvo (script o consulta) y si ese script está guardado.
- Lo que no cumpla esto no entra en esta base. Va a «Pendiente de verificar».
- Lo que no se pueda verificar se **elimina** también de los demás documentos del proyecto al repasarlos, y se apunta en la sección 8 [me, 2026-11-21].
- Las páginas se citan como **página del PDF** en `notes/papers/`, no como página de la revista.

---

## 1. Cronología

| Fecha | Qué pasó | Fuente |
|---|---|---|
| 2026-09-30 | Reunión 1. Mis ideas (deriva semántica, *bridging users*, contenido → ideología) despiertan poco interés. Andreas encarga: *quién responde a quién, si sus posiciones son opuestas, y el lifetime de los usuarios* (para el 19/10). | `notes/meetings/2026-09-30.md` |
| 2026-10-06 | La IA descarga el dataset (19:31–19:42), escribe el PLAN (H1–H4), se aprueba el mismo día y se ejecuta todo esa tarde (embudo de respuestas registrado a las 20:08). | `notes/dataset/NOTES.md` («Result»); `notes/dataset/prep-results/run.log`; el PLAN y su aprobación, en `e65ba4c:notes/experiments/01-reply-opposition-lifetime/PLAN.md` |
| 2026-10-16 | Comprobaciones de duplicados y autovotos (el test de autovotos lo diseño yo). | `notes/dataset/data-treatment.md` |
| 2026-10-19 | Reunión 2. Andreas aprueba método y resultados. Pide: votos positivos, top 10 % por lifetime, entender los métodos, leer sobre redes con signo. | `notes/meetings/2026-10-19.md` |
| 2026-11-02 | La IA ejecuta los scripts 08 (votos positivos) y 09 (top 10 %). No revisados por mí. | `e65ba4c:notes/experiments/01-reply-opposition-lifetime/NOTES.md`, decisión 10 |
| 2026-11-03 | La IA escribe el libro-guía y los resúmenes de papers (ambos eliminados el 2026-11-21). Decido no ejecutar nada nuevo hasta entender lo hecho. | `notes/method/WORKLOG.md` |
| 2026-11-09 | Reunión 3 (online, ~20 min). Le digo a Andreas que no siento el TFG mío. Acuerdo: usar la IA solo como ejecutora de mis ideas. Para él, un buen TFG es la pregunta central «quién responde a quién» analizada en profundidad; espera autonomía de nivel máster, con él como acompañante y revisor. | `notes/meetings/2026-11-09.md`, Notes (escritas de memoria el 2026-11-21) |
| 2026-11-19 | Rehago yo el planteamiento desde cero. Corrijo varias cosas que se daban por ciertas. | `WORKLOG.md`, 2026-11-19 |
| 2026-11-21 | Repaso del proyecto. Archivo el código antiguo en `code/_obsoleto/` (después eliminado); saco la preparación de datos (`code/dataset-prep/`) y los chequeos (`code/dataset-checks/`, repetidos con el mismo resultado). Adopto la regla de verificación. Primer commit de git (`4106db3`). Elimino el libro-guía y hago un barrido de todo lo que no tiene fuente. | Este archivo; `code/_obsoleto/README.md`; `git log` |

---

## 2. Hechos de la literatura

### FAULTANA: Fraxanet et al. 2024, *PNAS Nexus* 3, pgae276
Archivo: `notes/papers/Fraxanet2024_faultana-antagonism-alignment.pdf` (12 pp.; la p. 1 del PDF es una portada de descarga) y `…_SI.pdf`. En este proyecto «FAULTANA» y «Fraxanet 2024» son el mismo trabajo [me].

- **F1. Las interacciones son valoraciones (votos).** En DerStandard, una interacción es la valoración positiva o negativa de un usuario (*rater*) a un comentario de otro (*author*). Las aristas son relaciones **no dirigidas** que agregan las interacciones entre los dos usuarios. PDF p. 4, «Network creation: from interactions to edges». El artículo del dataset lo resume como «positive and negative interactions (i.e., comment votes)» (ver D1).
- **F2. Criterio de arista.** Modelo Beta-Bernoulli. Solo hay arista si E[p] > 0,6 o E[p] < 0,4 **y** Var[p] < 10⁻⁴. Signo = sign(E[p] − ½). PDF p. 4, misma sección.
- **F3. Prior en DerStandard: α = 1, β = 2.** Favorece ligeramente lo negativo porque los votos negativos están infrarrepresentados. PDF p. 5, primer párrafo de la columna izquierda.
- **F4. Población de usuarios estables.** Usuarios que votaron **al menos una vez cada año** entre principios de 2014 y finales de 2021: unos 14,8k usuarios y ~76M interacciones. PDF p. 4, apartado «DerStandard».
- **F5. Nulo del Global Alignment.** SAI_G compara el número de aristas frustradas con el de un nulo que **redistribuye los signos manteniendo fijas la estructura de la red y la partición**. PDF p. 5, «Normalized Frustration Index» (ec. 1). Para el Local Alignment, el nulo baraja los signos manteniendo la red y los grupos (PDF p. 6).
- **F6. Resultados globales de DerStandard.** K* = 2; tamaños 62/37; 29 % de aristas frustradas; SAI_G = 0,396, IC 95 % 0,3951–0,3961, obtenido con 1.000 instancias del nulo; Divisiveness 0,2899 y Cohesiveness 0,1409 (normalizadas). SI, PDF p. 6, Tabla S3. El texto principal da SAI_G = 0,3955 (PDF p. 7).
- **F7. Antagonismo y alineamiento por tema.** FAULTANA ya los midió por tema en DerStandard, a partir de los votos. PDF p. 7 (texto) y Fig. 3 (figura en PDF p. 9). Correlación entre ambos a través de temas: r = −0,0016.

**Cifra derivada de F2 y F3 [AI, 2026-11-21].** Con posterior Beta(α, β) y N = α + β, Var[p] = E(1 − E)/(N + 1). Var < 10⁻⁴ exige N + 1 > E(1 − E)·10⁴. Con el prior (1, 2), n = N − 3 interacciones:
- E[p] = 0,6 o 0,4 (el límite para que haya arista): n > 2.396.
- E[p] = 0,9 o 0,1: n > 896.
- E[p] = 0,99: n > 95.

El «≈ 900–2.500 interacciones por pareja» del WORKLOG del 19/11 es por tanto aproximado. El mínimo depende de E[p], y 2.500 corresponde a E[p] = 0,5, que nunca es arista.

### Uso del odds ratio en los PDF de `notes/papers/` [Verificador, 2026-11-21]
- **L1.** Busqué en los 25 PDF de la carpeta, página a página, «odds ratio», «odds», «log-odds», «Mantel», «relative risk» y «risk ratio» (`pdftotext`). **Ninguno usa el odds ratio ni el riesgo relativo como medida de resultado.** La única mención del odds ratio es de pasada, en Wang et al. 2022 (`Wang2022_immortal-time-methods-review.pdf`, PDF p. 14): una regresión logística agrupada da un odds ratio que imita al hazard ratio, en el contexto de los ensayos secuenciales. Las demás coincidencias son «at odds with» (Leskovec 2010, CHI, PDF pp. 1 y 3) y la referencia a Mantel y Byar 1974 en la bibliografía de Wang (PDF p. 26).
- Por tanto, la frase del PLAN «Tendremos la medida secundaria del odds ratio porque se usa en la literatura consultada» **no tiene respaldo en los papers guardados**. Decisión [me, 2026-11-21]: se quita el OR; el diseño usa el RR de Mantel–Haenszel y las proporciones simples.

### Artículo del dataset: Fraxanet, Gómez, Kaltenbrunner, Pellert, *A Decade of News Forum Interactions*
Archivo: `notes/papers/Fraxanet2025_derstandard-dataset.pdf`, versión **arXiv:2506.22224v2 (10 mar 2026)**, 21 pp. Existe la versión publicada en *Scientific Data* (2026) 13:1193, doi:10.1038/s41597-026-07267-3. El 2026-11-21 la comparé frase a frase con la de arXiv, no encontré diferencias de contenido y la borré [me]. Se cita la de arXiv.

- **D1. `faction_users`.** Asigna 14.817 usuarios a las dos facciones del trabajo previo (FAULTANA, ref. [27]), en el periodo 2014–2021; ~62 % en la facción mayor. La asignación es **estática**: no recoge cambios de posición en el tiempo. PDF p. 11.
- **D2. «Missing article».** Unos 1.000 identificadores de artículo que aparecen en los comentarios no están en los metadatos de artículos, y la mayoría tampoco son accesibles en la web. Afecta a 382.167 comentarios (0,5 %). El texto lo llama «Article deleted»; en el fichero aparece como «Missing article». PDF p. 11.
- **D3. «Inconsistent timestamp».** 1.208 comentarios con fecha **anterior a la de su artículo**. Pueden afectar al lifetime de menos del 0,15 % de los 247.863 usuarios. PDF pp. 11–12.
- **D4. Usuarios borrados.** De media, el 8,46 % (± 3,78) de los autores de comentarios son NA; en los votos, el 8,33 % (± 3,66) de los autores y el 7,27 % (± 3,35) de los votantes. PDF p. 11.
- **D5. Recuento de votos.** Donde el recuento del fichero de comentarios no coincidía con el de votos, los autores sustituyeron el primero por el agregado del fichero de votos. PDF p. 11.

---

## 3. Hechos de los datos

| # | Hecho | Cómo se obtuvo | ¿Script guardado? |
|---|---|---|---|
| H1 | Los votos no tienen fecha: el fichero de votos solo tiene `Comment_Id`, `Voter_Id`, `Author_Id`, `Pos`, `Neg`. | Cabecera del TSV y `Codebook.md` (2026-11-21) | n/a |
| H2 | `faction_users.tsv`: 14.817 usuarios (9.278 en la facción 1, 5.539 en la 2) = 6,0 % de los 247.863 de `users_file` (que incluye usuarios que solo votan). Coherente con D1 y F6 (62/37). | `wc` / `uniq -c` sobre los TSV (2026-11-21) | No, consulta de una línea |
| H3 | `inconsistent_comment_metadata.tsv`: 382.167 «Missing article» + 1.208 «Inconsistent timestamp». | `uniq -c` (2026-11-21) | No, consulta de una línea |
| H4 | Embudo de respuestas: 53.427.803 → 44.350.672 (inconsistentes 326.643; padre ausente 11; autor borrado 7.976.578; autorrespuestas 773.899). | `notes/dataset/prep-results/run.log`, 2026-10-06 20:08 | Sí, `code/dataset-prep/01_reply_edges.py` |
| H5 | Votos: 27,1M con votante NULL descartados; 383.858.436 votos limpios. | `data-treatment.md`; `notes/dataset/prep-results/run.log` | Sí, `code/dataset-prep/00_to_parquet.py` |
| H6 | 0 autovotos en `votes` (412.511.165) y `votes_clean` (383.858.436), en los dos signos; 0 de 54.044.269 comentarios votados. Lee las tablas Parquet generadas por `code/dataset-prep/00_to_parquet.py`. | `check_self_votes.py`, 2026-10-16; repetido el 2026-11-21 | Sí, `code/dataset-checks/` |
| H6b | Comentarios: 75.644.850 filas crudas; 75.385.329 `Comment_Id` distintos = 75.385.329 filas distintas, así que los 259.521 duplicados son idénticos en todas las columnas. Lee los TSV crudos. | `check_duplicate_comments.py`, 2026-10-16; repetido el 2026-11-21 (filas distintas con `--buckets 16`) | Sí, `code/dataset-checks/` |
| H7 | 26 respuestas tienen el comentario padre con fecha posterior. No están en la lista de D3, que trata otro problema (comentario anterior al artículo). | `prep-results/run.log`, comprobación de `reply_edges` | Sí, `code/dataset-prep/01_reply_edges.py` |
| H8 | El año máximo en `reply_edges` es 2023, aunque el dataset acaba el 2022-12-31. | `prep-results/run.log` | Sí |
| H10 | Todos los identificadores de los TSV crudos son 16 caracteres hexadecimales en minúscula: `Comment_Id`, `Author_Id`, `Parent_Id`, `Origin_Parent_Id` (75.644.850 comentarios); `Comment_Id`, `Voter_Id`, `Author_Id` (412.511.165 votos); `User_Id`; `userid` de facciones; `Comment_Id` de inconsistencias. 0 excepciones (sin contar NA). Por tanto, la conversión a entero de 64 bits de `00_to_parquet.py` no pierde información. En los votos, `Pos`/`Neg` es siempre (1,0) o (0,1). | Consulta DuckDB con `regexp_full_match(id, '[0-9a-f]{16}')` (2026-11-21) | No, consulta puntual |
| H11 | En `users_file`, `First_Comment = 0` ⇔ `N_comments = 0` (36.755 usuarios, también `Last_Comment = 0`). `First_vote = 0` en 47.992 usuarios, ninguno ha dado votos. El 0 significa «sin actividad de ese tipo», así que el NULL de `00_to_parquet.py` es correcto. | Consulta DuckDB sobre `users_file` (2026-11-21) | No, consulta puntual |

---

## 4. Problemas del planteamiento inicial y decisión sobre cada uno
El planteamiento inicial es el `PLAN.md` del 2026-10-06, escrito por la IA; desde el 2026-11-21 solo está en git: `git show e65ba4c:notes/experiments/01-reply-opposition-lifetime/PLAN.md`. Los problemas los señaló la IA en el repaso del 2026-11-21 o los había detectado yo el 19/11; las decisiones son mías.

| # | Problema | Decisión [me, 2026-11-21] |
|---|---|---|
| P1 | El PLAN se escribió, aprobó y ejecutó el mismo día (ver cronología), antes de que yo entendiera el problema. | (Contexto de la narrativa.) |
| P2 | La pregunta pedía «posiciones opuestas» y el PLAN la sustituyó por «desaprobación medida con votos» sin discutirlo. | **Limitación para el resumen.** Discutirlo con Andreas y Emma. |
| P3 | H3b (hostilidad entre facciones) es circular: las facciones se construyen con votos y son negativas entre ellas (F1, F2). | **Eliminada.** |
| P4 | H3 se interpretó en una sola dirección: 0,260 observado frente a 0,232 del nulo y 0,468 de la mezcla aleatoria (`e65ba4c:notes/experiments/01-reply-opposition-lifetime/results/05_h3_factions.csv`). La conclusión depende de la referencia elegida, y esa elección nunca se justificó. | **Marcar en el resumen.** Sigue como pregunta abierta. |
| P5 | H2 afirma usar parámetros «como en FAULTANA», pero usa ≥ 5 votos. FAULTANA exige Var[p] < 10⁻⁴ (F2). | **Repetirlo con los parámetros correctos** (F2, F3). |
| P6 | La comprobación de facciones del PLAN («la red debe reproducir el patrón de FAULTANA») se cumple por construcción. | **Error de base.** No puede repetirse. |
| P7 | H1 compara a quien responde con *otros* votantes del mismo comentario, así que el efecto se mezcla con la tendencia general de cada votante. | **No olvidarlo en el resumen.** El diseño nuevo compara a cada votante consigo mismo. |
| P8 | Como los votos no tienen fecha (H1 de la sección 3), el balance de la pareja en H2 y la «oposición temprana» de H4 pueden incluir votos posteriores. | **Descartadas de momento.** Apuntadas para analizar y replantear. |
| P9 | La novedad («nadie cruza respuestas × posición × lifetime») no se comprobó contra la literatura. FAULTANA ya mide antagonismo por tema (F7). | **Tarea:** búsqueda exhaustiva de literatura. |
| P10 | El multiverso (24 + 18 especificaciones) varía umbrales de un diseño que nadie justificó. | **Descartado de momento.** |
| P11 | El PLAN afirma que los usuarios con facción son los que «votaron todos los años 2014–2021», sin citar fuente. | **Comprobado el 2026-11-21: es correcto** (F4, D1). Se mantiene, ahora con cita. |

---

## 5. Limitaciones para el resumen
- P2: posición = votos, no ideología.
- P4: la conclusión de H3 depende de la referencia.
- P7: el H1 antiguo comparaba a personas distintas.
- H1 (sección 3): los votos no tienen fecha, así que no se puede saber si un voto es anterior o posterior a una respuesta.
- Usuarios borrados: el 14,9 % de las respuestas y 27,1M de votos quedan fuera (H4, H5, D4). No se ha comprobado si se comportan distinto.
- D1: las facciones son estáticas (2014–2021) y solo cubren a usuarios estables (F4).

## 6. Tareas abiertas
- [ ] Repetir H2 con los parámetros de FAULTANA (P5). El código antiguo está archivado, así que sería código nuevo.
- [ ] Búsqueda exhaustiva de literatura sobre la novedad (P9).
- [ ] Replantear H2 y H4 teniendo en cuenta que los votos no tienen fecha (P8).
- [x] Rellenar las notas de la reunión del 2026-11-09 (hecho el 2026-11-21).
- [ ] Averiguar por qué aparece el año 2023 en `reply_edges` (H8).

## 7. Pendiente de verificar
Afirmaciones en uso que todavía no cumplen la regla:
(Vacío por ahora.)

## 8. Descartado por no tener fuente [me, 2026-11-21]
Regla: toda conclusión o dato sin fuente (literatura citada o resultado de código guardado) se descarta. Se apunta aquí para dejar constancia.

| Qué | Por qué se descarta | Fecha |
|---|---|---|
| OR = 3,49 por votante (`CODE-REVIEW.md`) | Su script (`h1_voter_strata.py`) no está en el repositorio. | 2026-11-19 |
| Cobertura de facciones en las respuestas: 25,5 % con los dos usuarios etiquetados, 74,5 % con al menos uno | Consulta del 19/11 en un script temporal no guardado. | 2026-11-21 |
| «FAULTANA **nunca** usa respuestas» (WORKLOG 19/11) | Lo verificado es F1: las interacciones son votos. El «nunca» no tiene cita. | 2026-11-21 |
| «≈ 900–2.500 interacciones por pareja» (WORKLOG 19/11) | Sustituido por la cifra derivada de F2 y F3 (sección 2). | 2026-11-21 |
| Explicación del año 2023 por zona horaria | Era una conjetura. Queda solo el hecho (H8, sección 3). | 2026-11-21 |
| Dos controles del test de autovotos (77,2 % de votantes que también son autores; muestra de 5M votos) y la explicación «la plataforma no permite autovotos» | Consultas no guardadas; la explicación era una conjetura. | 2026-11-21 |

### Barrido del 2026-11-21 [me decidí el criterio; la IA lo ejecutó]
Todo lo eliminado se puede recuperar en el commit `4106db3`.
- **Eliminados enteros:** el libro-guía y las dos guías anteriores (`notes/guide/`); `RESULTS.md`, `EXPLICACION.md`, `EXPLICACION-RESUMEN.md`, `PREGUNTAS.md` y `CODE-REVIEW.md` del experimento 01 (interpretaciones del diseño antiguo); los resúmenes de `PAPERS-SUMMARY.md` (sin cita precisa), que queda como lista de PDF.
- **Resultados del diseño antiguo:** se conservan solo los CSV, figuras y `run.log`, con un índice en `results/README.md` que indica el script de cada archivo y las cifras principales leídas de los CSV.
- **Reescritos:** `NOTES.md` del experimento 01 (solo decisiones con fuente); `PLAN.md` (aviso de diseño antiguo, texto sin tocar como registro); `AI-USE.md` (recortado y después **eliminado**: su método pasa a `/CLAUDE.md`, con los modos de trabajo de la IA); `dataset/NOTES.md` (fuera las razones sin fuente); `data-treatment.md` (fuera los controles sin consulta guardada); WORKLOG (fuera los hallazgos sin cita del 2026-11-03 y una frase del 2026-11-19).
- **Reorganización del experimento 01 (2026-11-21, después del barrido):** se eliminaron del árbol `code/_obsoleto/`, los resultados del diseño antiguo (`results/`) y su `PLAN.md` y `NOTES.md`; todo está en el commit `e65ba4c`. `run.log` y `01_reply_funnel.csv`, que son fuente de hechos vigentes, pasan a `notes/dataset/prep-results/`. README, PLAN y NOTES del experimento se rehicieron con el planteamiento del 2026-11-19. Se borraron también las tablas derivadas del diseño antiguo (`null_edges`, `dyads`, `edges_stance`, `factions_projected`), que estaban fuera de git: se regeneran con los scripts 02, 03 y 05 de `e65ba4c`.
- **Renombrado (2026-11-21):** `notes/experiments/01-reply-opposition-lifetime/` pasa a `notes/experiments/01-who-replies-to-whom/`. Las referencias a commits anteriores usan la ruta antigua.
- **No tocados:** `dataset/README.md` y `Codebook.md` (documentación oficial de los autores) y las notas de reunión (registro de lo que pasó).
