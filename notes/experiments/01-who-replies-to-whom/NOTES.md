# Registro de decisiones y ejecución

## Decisiones
Todas del planteamiento del 2026-11-19; el texto completo está en [[PLAN]].

| # | Decisión | Alternativas | Justificación | Estado |
|---|---|---|---|---|
| 1 | Usar las facciones de FAULTANA (14.817 usuarios) | | Ver PLAN, «Tema central» | [me] |
| 2 | Población: respuestas limpias (44.350.672) | | Ver PLAN, «Población» | [me] |
| 3 | Trabajo descriptivo: resultados con intervalos de confianza, sin hipótesis a confirmar | | Ver README, «Mi predicción» | [me] |
| 4 | Votos negativos al responder: la unidad es el voto, clasificado según si el votante respondió o no al comentario | | Ver PLAN | [me] |
| 5 | Comparar cada votante consigo mismo | | Eliminar el efecto de las personas que votan negativo a todo | [me] |
| 6 | Polémica por número de respuestas y votos de otras personas (sin la propia respuesta ni el propio voto), con un nivel «0 respuestas de otros»; no usar la proporción de votos negativos de otros | | Es la misma variable que el resultado | [me] |
| 7 | Estratos = votante × nivel de polémica; medida: RR de Mantel–Haenszel, más las proporciones simples | OR de Mantel–Haenszel como secundaria (quitada el 2026-11-21: su justificación no tenía fuente, `BASE-VERIFICADA.md`, L1) | El RR responde «cuántas veces es más probable un voto negativo cuando responde» | [me] |
| 8 | Bootstrap por votante | | | [me] |
| 9 | No formular la pregunta de los votos entre facciones | | Sería un razonamiento circular | [me] |
| 10 | Población de la pregunta central: las respuestas limpias en las que quien responde (A) y el autor del comentario respondido (B) están etiquetados en FAULTANA: 11.302.013 (25,48 % de 44.350.672; `BASE-VERIFICADA.md`, H12). Decidido el 2026-11-21 | Asignar facción a usuarios sin etiqueta (el diseño antiguo lo intentó y dio AUC 0,63) | Sin las dos etiquetas no se puede decir si la respuesta es entre facciones o dentro de una | [me] |

## Limitaciones de los datos
Apuntadas en el repaso del 2026-11-21 [AI, a petición mía]. Son hechos de los datos, no decisiones. Fuentes en `notes/method/BASE-VERIFICADA.md`, §3.
- **Los votos no tienen fecha** (solo el mes del archivo). No se puede saber si un voto es anterior o posterior a la respuesta del mismo usuario.
- **Usuarios borrados.** Se excluyen 7.976.578 respuestas (14,9 %) y 27,1M de votos. Pregunta abierta: ¿los usuarios borrados eran más conflictivos que el resto? Si lo eran, excluirlos hace que el foro parezca más tranquilo de lo que fue.
- **26 respuestas con el padre posterior a la respuesta.** El filtro de `inconsistent_comment_metadata` («Inconsistent timestamp», 1.208 comentarios) no las detecta. Se mantienen en `reply_edges`.
- **Año 2023 en `reply_edges`.** El dataset va hasta el 2022-12-31, pero el año máximo de las aristas es 2023.
- **Facciones.** `faction_users.tsv` tiene 14.817 usuarios (9.278 en la facción 1, 5.539 en la 2), el 6,0 % de los 247.863 del fichero de usuarios (que incluye usuarios que solo votan).

## Incidencias y bugs encontrados

## Cómo ejecutar
Todavía no hay código propio. Preparación de datos: `uv run python dataset-prep/00_to_parquet.py` y `dataset-prep/01_reply_edges.py`, desde `tfg/code`.
