# Work log

One entry per working day: what was done, by whom ([me] / [AI]), what changed on disk, what is pending. Newest first.

---

## 2026-11-21

**Decisión del día [me]:** todo lo que se use como base del trabajo tiene que estar verificado. Las afirmaciones de la literatura llevan cita precisa (archivo, página, sección, tabla o figura) y las cifras de datos, su script guardado. Lo que no se puede verificar se elimina. Sobre esa base escribiré el resumen para Andreas y Emma.

**Hecho**
1. [me] Ejercicio de Mantel–Haenszel (RR y OR, proporciones, tabla sumada).
2. [AI, a petición mía] Repaso de `notes/dataset/` y de README y PLAN del experimento 01: lista de 11 problemas del planteamiento inicial; yo decido qué hacer con cada uno (`BASE-VERIFICADA.md`, §4).
3. [AI] Comprobación de las afirmaciones sobre FAULTANA y el artículo del dataset en los PDF, con página (`BASE-VERIFICADA.md`, §2). El criterio de usuarios estables del PLAN era correcto; el «≈ 900–2.500 interacciones» no lo era.
4. [AI] Código: el diseño antiguo a `code/_obsoleto/`; `00_to_parquet.py` y `01_reply_edges.py` a `code/dataset-prep/`; los chequeos de duplicados y autovotos se repiten (mismo resultado) y pasan a `code/dataset-checks/`. Verificados los IDs hexadecimales y `First_Comment = 0` (H10, H11).
5. [AI] Comparé la versión de *Sci Data* del artículo del dataset con la de arXiv: sin diferencias de contenido. Borré la de *Sci Data*; se cita la de arXiv.
6. [AI] Git: `.gitignore` deja de ignorar los `.log` (son fuente). Commits `4106db3` (estado antes del barrido) y `09f5f80` (preparación de datos).
7. [AI] Eliminado el libro-guía y barrido de todo el proyecto (detalle en `BASE-VERIFICADA.md`, §8).

**Cambios en disco:** los de arriba. Ningún análisis nuevo; solo se repitieron los dos chequeos del dataset.

**Pendiente**
- Rellenar las notas de la reunión del 2026-11-09.
- Tareas de `BASE-VERIFICADA.md`, §6.
- Escribir el resumen para Andreas y Emma a partir de `BASE-VERIFICADA.md`.

---

## 2026-11-19

**Decisión del día [me]:** volver al inicio del proyecto y rehacer el planteamiento yo mismo. La IA pasa a ser ejecutora: no propone ideas ni diseños; explica conceptos cuando se lo pido, cuestiona mis respuestas y ejecuta lo que yo decido (siguiendo lo acordado con Andreas el 2026-11-09: "que la IA no te dé las ideas, que solo las ejecute").

**Hecho**
1. [me] Rediseño del experimento desde cero respondiendo preguntas (pregunta, medida, comparación, refutación), sin mirar `PLAN.md`, y comparación posterior con el diseño de la IA. Resultado: el resumen de abajo, escrito por mí.
2. [AI, ejecutado a petición mía] Consulta de cobertura de facciones sobre `reply_edges.parquet` + `factions.parquet` (LEFT JOIN por replier y por target): 44.350.672 respuestas; 11.302.013 (25,5 %) con los dos usuarios etiquetados; 33.042.310 (74,5 %) con al menos uno. `factions.parquet`: 14.817 usuarios, sin duplicados. Script temporal, no guardado en el repositorio. **Descartado el 2026-11-21:** sin script guardado.
3. [AI] Comprobaciones en las fuentes (artículo y SI de FAULTANA, tesis de Lan Ceqin).

**Correcciones a cosas que dábamos por ciertas**
- Mis recuerdos de H3 no coincidían con los datos: las respuestas entre facciones son el 26,0 % (null del mismo artículo: 23,2 %; mezcla aleatoria: 46,8 %). No son "mayoritariamente entre facciones opuestas". La conclusión cambia de signo según la comparación.
- FAULTANA **sí** compara con un nulo de signos barajados (partición fija, 1.000 réplicas; SAI_G = 0,396 [0,3951, 0,3961], Tabla S3 del SI). *[Frase eliminada el 2026-11-21: sin cita. Lo verificado es que el nulo mantiene la estructura de la red y la partición; `BASE-VERIFICADA.md`, F5.]* Corrige la entrada del 2026-11-03.
- FAULTANA construye sus relaciones solo con votos (en las dos direcciones), nunca con respuestas, y exige Var[p] < 1e-4 (≈ 900–2.500 interacciones por pareja). H2 de la IA usa ≥ 5 votos: no es "heredado de FAULTANA". Añadir a la tabla D de `AI-USE.md`. **Corregido el 2026-11-21:** el «nunca» y el rango de interacciones no tienen cita; ver `BASE-VERIFICADA.md` (F1, F2 y la cifra derivada).
- FAULTANA ya midió antagonismo y alineamiento por tema en DerStandard (Fig. 3; solo votos, 2014–2021).
- El OR = 3,49 por votante sale de `CODE-REVIEW.md`; su script (`h1_voter_strata.py`) no está en el repositorio, así que no es reproducible. Descartado como resultado de referencia.

**Resumen del planteamiento [me]**

### Tema central: quién responde a quién entre facciones

¿Cuándo alguien responde a un comentario, el autor del comentario es de su propia facción o de la otra, y cómo se compara con lo que cabría esperar?

La pregunta no es circular por construcción, aunque las dos fuentes de datos (votos y respuestas) no son independientes.

Usamos las facciones definidas en FAULTANA a partir de los votos. En FAULTANA se construyen las facciones según los votos del usuario A a los comentarios del usuario B y viceversa.

Ejemplo: en FAULTANA si A ha contestado a B 100 veces los dos usuarios no tienen relación, pero si A ha votado negativamente a B 3000 veces sí. Los votos y las respuestas tienen relación, así que las facciones reflejan indirectamente también el patrón de las respuestas.

Medimos si las respuestas cruzan facciones. Como las facciones no se construyeron por respuestas no hay un resultado por construcción. Para la negatividad hay construcción porque las facciones están definidas como mayoritariamente negativas entre ellas.

### Población: usuarios estables

Limpiamos la base de datos de respuestas con metadatos inconsistentes y los usuarios borrados y las respuestas a uno mismo (44.35M). Si los usuarios borrados eran más conflictivos, el foro parecerá más tranquilo de lo real.

14817 usuarios (6%) con etiqueta de FAULTANA. Se tendría que considerar si es un grupo suficientemente representativo de la conversación en DerStandard. *(Redacción cambiada el 2026-11-21; quitada la cobertura en respuestas, que no tenía script guardado.)*

### De momento es descriptivo

No hay una hipótesis definida a confirmar o refutar. De momento los resultados se darán con sus intervalos de confianza y lo interpretaré con palabras de manera analítica. No tengo criterio para definir qué diferencia es relevante.

### Votos negativos al responder

¿Quien responde a un comentario tiende a votarlo en contra, más que cuando esa misma persona vota un comentario parecido sin responderlo? La unidad a usar es el voto, que está clasificado segun si la persona respondió o no a ese comentario.

Comparamos cada votante consigo mismo para eliminar el efecto de las personas que votan negativo a todo

No usamos la proporcion de votos negativos de otros para medir la polémica porque es la misma variable que el resultado.

Clasificamos cada comentario en niveles de polémica según el número de respuestas y de votos que recibió de otras personas (excluyendo la propia respuesta y el propio voto). Uno de los niveles es "0 respuestas de otros", de modo que los comentarios a los que la persona fue la única en responder se comparan con los comentarios que votó y que nadie respondió. Así no hace falta excluir los comentarios sin respuestas: se comparan dentro de su propio nivel.

Para estimar el valor, usamos el riesgo relativo de Mantel Haenszel, que responde "cuántas veces es más probable un voto negativo cuando responde". Tendremos la medida secundaria del odds ratio porque se usa en la literatura consultada.También usaremos las proporciones simples.
Los estratos serán las combinaciones de votante y nivel de polémica, así que cada votante genera una tabla por cada nivel de polémica.

Se hace bootstrap por votante.

Hay que decidir cuantos cortes en niveles de polémica, el número de votos por votante para incluirlo y como se mide la robustez del valor medido. El nivel 0 tendrá muchos votos sin respuesta y relativamente pocos con respuesta, así que conviene comprobar que cada estrato tiene votos en los dos lados. Los estratos que solo tengan un lado no aportan nada a Mantel–Haenszel.

La tesis principal busca quién responde a quién, y esta sección busca si responder va acompañado de desaprobación. Si la pregunta la formulamos entre facciones caemos en un razonamiento circular.

### Preguntas pendientes

- Análisis del tiempo de vida de los usuarios y si es influenciado por las interacciones negativas que reciban
- Como mido la negatividad sin votos?
- Qué uso de referencia para medir la proporcion de respuestas que cruzan facciones?
- FAULTANA midió el antagonismo por tema. Podría extender la pregunta del quién responde a quién por tema? Se reduciria demasiado el tamaño del sample?
- Qué subdivisiones puedo hacer en los datos que mantengan suficientes usuarios en cada celda.
- ¿Como defino el umbral para interpretar los resultados al pasar de un trabajo descriptivo a uno que pretende testear una hipotesis?

**Pendiente de estudiar [me]**
- Mantel–Haenszel: ejercicio de los comentarios X (8, 2, 40, 10) e Y (1, 9, 10, 90): OR dentro de cada uno, OR de la tabla sumada y OR_MH.
- Tesis de Lan Ceqin: 2.2 (p. 11) limpieza; 2.5 (p. 16) y 3.4.5 (p. 55) reciprocidad; 2.6 (p. 17), 3.2 y 4.2 temas; 2.10 (p. 24) y 3.7 test de permutación; 3.6 (p. 63) periodos; 4.6 (p. 74) limitaciones; p. 79 declaración de uso de IA; apéndice A.1 (p. 89) modelo generativo de threads.

**Mañana [me]**
- Releer todo el proyecto y repasar los métodos.
- Empezar un documento que explique la idea principal y lo decidido hoy (para Andreas y Emma).

**Cambios en disco:** solo esta entrada del log. Ningún análisis rerun, ningún archivo de código ni de resultados modificado.

---

## 2026-11-03

**Decision of the day [me]:** do not run the new analyses or any recomputation yet, because I am not ready to interpret the results. Use the session to improve the documentation so that I can understand and extend the work myself.

**Done [AI, not yet reviewed by me]**
1. **Book-style guide** in `notes/guide/book/` (`main.pdf`, 50 pp.): preface, purpose, data, four primer ideas, methods H1-H4 with toy examples, pipeline and the 18 choices, results with figure-reading boxes, critical review, sources, building on the work, glossary, exercises with answers, file map. Sources: `main.tex`, `ch00..ch09`, `app-*.tex`, `snippets/` (three tested toy scripts). `notes/guide/README.md` says the book supersedes `tfg-guide` and `methods-study-guide` (kept).
2. **Papers downloaded** into `notes/papers/` (15 PDFs, open access): Cheng 2014 and 2015, Leskovec 2010 (two), Danescu-Niculescu-Mizil 2013, Gomez 2008 and 2013, Kunegis 2009, Wang 2022 (immortal time), Easley and Kleinberg ch. 5, Aref and Wilson 2018, Gonzalez-Bailon 2010, Kumar 2018, Garimella 2018.
3. **Summaries** appended to `notes/papers/PAPERS-SUMMARY.md`: section D (D1-D15, first pass), section E (E1-E7, second pass over the previously unread parts of Lan Ceqin, Simonsohn SI, Cheng 2014 and 2015, Danescu-Niculescu-Mizil, Gomez 2013, Leskovec WWW), section F (six consolidated methodological implications).
4. **Book updated** with the findings of the reading passes (null model from Gomez/Lan Ceqin, faction baseline check, H4 additions, joint inference procedure, Lan Ceqin periods, glossary).
5. Memory index updated (papers summary location).

**Findings that matter for the thesis** *[Eliminado en el barrido del 2026-11-21: afirmaciones de la literatura sin cita precisa. Recuperable en el commit `4106db3`.]*

**Not done / not obtained**
- Hernan and Robins, *What If* (Harvard server blocked the download); Muchnik et al. 2013 (no free full text); Andreas's reply-behaviour papers (titles unknown). FAULTANA figures never inspected.
- No analysis, pipeline run or commit. Everything in the repo is still untracked.

**Pending (waiting for my go-ahead)**
- Small fixes that rerun computation; the new analyses (periods, topics, both directions, activity strata, Beta propagation, thread-level and model-based nulls, voter-level H1, equal-coverage H2, long-lived group redefinition, faction baseline check, joint inference).
- Choices still open: defaults for the periods, topic list and activity strata; headline definition of the long-lived group (options A/B/C); whether to draft the pre-specification note.
- My own tasks: read the book (about 6-8 h), the five priority papers, review items C17 and C18, make a first git commit.
- Separate future experiment: bridging users.
