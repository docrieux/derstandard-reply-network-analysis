# 01. Quién responde a quién entre facciones

**Estado:** idea. Planteamiento del 2026-11-19 [me]; todavía sin análisis.
**Código:** todavía no hay código propio. La preparación de datos está en `code/dataset-prep/` y las comprobaciones del dataset en `code/dataset-checks/`.
**Documentos:** [[PLAN]] · [[NOTES]]
**Historia:** este experimento empezó con otro diseño (PLAN del 2026-10-06, H1–H4, escrito y ejecutado por la IA). Ese diseño, su código y sus resultados se eliminaron el 2026-11-21 y solo se pueden recuperar en el historial de git (commit `e65ba4c`). Sus problemas están en `notes/method/BASE-VERIFICADA.md`, §4.

## Pregunta
**Tema central.** ¿Cuándo alguien responde a un comentario, el autor del comentario es de su propia facción o de la otra, y cómo se compara con lo que cabría esperar?

**Votos negativos al responder.** ¿Quien responde a un comentario tiende a votarlo en contra, más que cuando esa misma persona vota un comentario parecido sin responderlo?

## Mi predicción (antes de ver nada, con mis palabras)
No hay una hipótesis definida a confirmar o refutar. De momento los resultados se darán con sus intervalos de confianza y lo interpretaré con palabras de manera analítica. No tengo criterio para definir qué diferencia es relevante.

## Datos que usa
Limpiamos la base de datos de respuestas con metadatos inconsistentes y los usuarios borrados y las respuestas a uno mismo (44.35M). Pregunta abierta: ¿los usuarios borrados eran más conflictivos que el resto? Si lo eran, excluirlos hace que el foro parezca más tranquilo de lo que fue. *(Reformulada el 2026-11-21.)*

14817 usuarios (6%) con etiqueta de FAULTANA. Se tendría que considerar si es un grupo suficientemente representativo de la conversación en DerStandard.

- Respuestas A→B: `data/derstandard/derived/reply_edges.parquet` (44.350.672), generado por `code/dataset-prep/01_reply_edges.py`.
- Facciones: `factions.parquet` (14.817 usuarios), de `summary_files/faction_users.tsv`.
- Votos: `votes_clean` (383.858.436), generado por `code/dataset-prep/00_to_parquet.py`.
- Tratamiento aplicado: [[data-treatment]].

## Uso de IA en este experimento
| Fecha | Qué hizo la IA | Modo (`CLAUDE.md`) | Qué decidí yo | Qué aprendí |
|---|---|---|---|---|
| 2026-11-21 | Reorganizó el experimento al planteamiento del 2026-11-19, copiando mi texto | Ejecutor | Eliminar el diseño antiguo y rehacer README, PLAN y NOTES | |
