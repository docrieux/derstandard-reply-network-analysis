# Tratamiento del dataset

Decisiones de limpieza y definiciones comunes a los experimentos. Cada decisión: qué se hace, por qué, alternativas, coste/sesgo posible, dónde está en el código y estado. Las cifras citan su fuente.

## Embudo de datos
Dos tablas, porque la base cambia: primero los comentarios (donde se quitan los duplicados) y después las respuestas (donde se aplican las exclusiones).

### Comentarios
Fuente: `notes/dataset/prep-results/run.log` y `code/dataset-checks/check_duplicate_comments.py`.

| Paso | N | % de filas crudas |
|---|---|---|
| Filas crudas de comentarios | 75.644.850 | 100 |
| Duplicados exactos (mismo `Comment_Id`, todas las columnas iguales) | 259.521 | 0,343 |
| **Comentarios únicos** | **75.385.329** | **99,657** |

### Respuestas
Fuente: `notes/dataset/prep-results/01_reply_funnel.csv` (última ejecución, `run.log`).

| Paso | N | % de respuestas |
|---|---|---|
| Respuestas (`is_reply`) | 53.427.803 | 100 |
| Inconsistentes (hijo o padre marcado) | 326.643 | 0,611 |
| Padre ausente | 11 | ~0 |
| Autor borrado (cualquier lado) | 7.976.578 | 14,930 |
| Autorrespuestas | 773.899 | 1,448 |
| **Aristas finales** | **44.350.672** | **83,010** |

Votos: 27,1M con votante NULL descartados; 383.858.436 votos limpios.

## Decisiones
Plantilla de cada una:

### Dxx. Título
- **Qué se hace:**
- **Por qué:**
- **Alternativas:**
- **Coste / sesgo posible (y cómo comprobarlo):**
- **Código:**
- **Estado:** [me] / [AI, reviewed] / [AI, not yet reviewed]

### D15. Respuesta = estructura del hilo (`parent_id`)
**Estado:** [AI, reviewed]

Se define a un mensaje como respuesta de A a B únicamente cuando su `parent_id` es B y su autor es A. Se tiene en cuenta que hay posibles respuestas a mensajes que no usen el formato de respuesta (post de A que menciona el post de B) pero se asume la pérdida de esos datos ya que consideramos que solo se puede asegurar que el mensaje es una respuesta si cumple las condiciones estrictas de seguir el formato de hilo.

### D7. Limpieza (duplicados, votantes borrados, exclusiones de aristas)
**Estado:** [AI, reviewed]

Eliminamos los comentarios duplicados porqué son duplicados exactos (coinciden en todas las columas). La presencia de duplicados generaria dos aristas de respuesta idénticas, contaría dos veces el número de votos y no se podrían aplicar modelos estadísticos ya que habría observaciones no independientes.

**Comprobación (2026-10-16):** en los TSV crudos, nº de `Comment_Id` distintos = nº de filas distintas (10 columnas) = 75.385.329, sobre 75.644.850 filas. Cada `Comment_Id` tiene una sola versión de fila, así que los 259.521 duplicados (0,343 %) son idénticos y `DISTINCT` no pierde información. Script: `code/dataset-checks/check_duplicate_comments.py` (repetido el 2026-11-21 con el mismo resultado). No se ha investigado por qué aparecen duplicados.

**Pregunta abierta:** ¿los usuarios borrados (15 % de las respuestas, 27M de votos) se comportan distinto del resto? Si es así, excluirlos podría sesgar H1.

### Autovotos
**Estado:** [me] (diseño del test y decisión) · test ejecutado el 2026-10-16 · texto adaptado al planteamiento del 2026-11-19 [AI, a petición mía, 2026-11-21]

**Definición.** Un voto es un autovoto si `voter_id = author_id` (el autor del comentario vota su propio comentario). Si cualquiera de los dos es `NULL` (usuario borrado), la comparación no es verdadera y la fila no cuenta.

**Por qué importa para el análisis de votos al responder.** El autor B nunca responde a su propio comentario (las autorrespuestas se excluyen). Si B votara a favor de su comentario, ese voto caería en sus propias tablas como votante, en la celda «no responde, voto +». Bajaría la proporción de votos negativos sin respuesta, y el RR (y el OR) saldrían inflados. El sesgo va en la dirección del efecto buscado (falso positivo), no es ruido.

> **Cambio de método (2026-11-21).** Este razonamiento se escribió para el H1 antiguo: estratos por comentario, OR como medida principal y un ejemplo de juguete (OR de 2,67 a 2,83). Ahora la unidad es el voto, cada votante se compara consigo mismo dentro de cada nivel de polémica, y la medida principal es el RR. El sesgo funciona igual y la conclusión no cambia.

**Test.** Recuento de autovotos y proporción sobre el total, desglosado por signo y por tabla (`votes` y `votes_clean`), y número de comentarios afectados. Script: `code/dataset-checks/check_self_votes.py` (repetido el 2026-11-21 con el mismo resultado). Predicción previa: menos del 1 % de los votos.

| Tabla | Votos | Autovotos | Downvotes propios | Upvotes propios |
|---|---|---|---|---|
| `votes` | 412.511.165 | 0 | 0 de 93.357.034 | 0 de 319.154.131 |
| `votes_clean` | 383.858.436 | 0 | 0 de 85.945.669 | 0 de 297.912.767 |

Ninguno de los 54.044.269 comentarios votados tiene un voto de su propio autor.

**Control (el cero no es un fallo del test).** Sobre `votes_clean` (los otros dos controles que había se eliminaron el 2026-11-21 porque su consulta no se guardó):
- `author_id` no es nulo en 355.359.586 de 383.858.436 votos (92,6 %; `run.log`, comprobación de `votes_clean`), así que el test sí podía detectar autovotos.

**Conclusión.**
- No hay autovotos en el dataset, en ninguno de los dos signos. No hay nada que excluir y el análisis de votos al responder no sufre este sesgo.
- Limitación: el 7,4 % de los votos tiene `author_id` nulo. Un autovoto de un usuario borrado sería indetectable (votante y autor `NULL`; además `00_to_parquet.py` elimina los votantes `NULL`).
- Decisión: no se añade ningún filtro. Si en el futuro se actualiza el dataset, repetir `check_self_votes.py`.
