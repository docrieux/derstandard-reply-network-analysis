# Plan

Texto del planteamiento del 2026-11-19 [me], copiado del WORKLOG sin cambios salvo dos frases reformuladas el 2026-11-21 (representatividad y usuarios borrados) y el odds ratio quitado el mismo día.

## Hipótesis
Ninguna de momento: el trabajo es descriptivo (ver README, «Mi predicción»).

## Opciones consideradas (con sus trade-offs)
*(por escribir [me])*

## Diseño elegido y por qué [me]

### Tema central: quién responde a quién entre facciones
¿Cuándo alguien responde a un comentario, el autor del comentario es de su propia facción o de la otra, y cómo se compara con lo que cabría esperar?

La pregunta no es circular por construcción, aunque las dos fuentes de datos (votos y respuestas) no son independientes.

Usamos las facciones definidas en FAULTANA a partir de los votos. En FAULTANA se construyen las facciones según los votos del usuario A a los comentarios del usuario B y viceversa.

Ejemplo: en FAULTANA si A ha contestado a B 100 veces los dos usuarios no tienen relación, pero si A ha votado negativamente a B 3000 veces sí. Los votos y las respuestas tienen relación, así que las facciones reflejan indirectamente también el patrón de las respuestas.

Medimos si las respuestas cruzan facciones. Como las facciones no se construyeron por respuestas no hay un resultado por construcción. Para la negatividad hay construcción porque las facciones están definidas como mayoritariamente negativas entre ellas.

### Población: usuarios estables
Limpiamos la base de datos de respuestas con metadatos inconsistentes y los usuarios borrados y las respuestas a uno mismo (44.35M). Pregunta abierta: ¿los usuarios borrados eran más conflictivos que el resto? Si lo eran, excluirlos hace que el foro parezca más tranquilo de lo que fue. *(Reformulada el 2026-11-21.)*

14817 usuarios (6%) con etiqueta de FAULTANA. Participan, respondiendo o recibiendo respuesta, en 33.042.310 de las 44.350.672 respuestas limpias (74,5 %; `BASE-VERIFICADA.md`, H12). *(Dato añadido el 2026-11-21.)* Se tendría que considerar si es un grupo suficientemente representativo de la conversación en DerStandard.

### Votos negativos al responder
¿Quien responde a un comentario tiende a votarlo en contra, más que cuando esa misma persona vota un comentario parecido sin responderlo? La unidad a usar es el voto, que está clasificado segun si la persona respondió o no a ese comentario.

Comparamos cada votante consigo mismo para eliminar el efecto de las personas que votan negativo a todo

No usamos la proporcion de votos negativos de otros para medir la polémica porque es la misma variable que el resultado.

Clasificamos cada comentario en niveles de polémica según el número de respuestas y de votos que recibió de otras personas (excluyendo la propia respuesta y el propio voto). Uno de los niveles es "0 respuestas de otros", de modo que los comentarios a los que la persona fue la única en responder se comparan con los comentarios que votó y que nadie respondió. Así no hace falta excluir los comentarios sin respuestas: se comparan dentro de su propio nivel.

Para estimar el valor, usamos el riesgo relativo de Mantel Haenszel, que responde "cuántas veces es más probable un voto negativo cuando responde". También usaremos las proporciones simples. *(2026-11-21: quitado el odds ratio como medida secundaria; su justificación, «se usa en la literatura consultada», no tenía respaldo en los papers guardados, ver `BASE-VERIFICADA.md`, L1.)*
Los estratos serán las combinaciones de votante y nivel de polémica, así que cada votante genera una tabla por cada nivel de polémica.

Se hace bootstrap por votante.

Hay que decidir cuantos cortes en niveles de polémica, el número de votos por votante para incluirlo y como se mide la robustez del valor medido. El nivel 0 tendrá muchos votos sin respuesta y relativamente pocos con respuesta, así que conviene comprobar que cada estrato tiene votos en los dos lados. Los estratos que solo tengan un lado no aportan nada a Mantel–Haenszel.

La tesis principal busca quién responde a quién, y esta sección busca si responder va acompañado de desaprobación. Si la pregunta la formulamos entre facciones caemos en un razonamiento circular.

## Comprobaciones previstas (sanity checks)
- Que cada estrato (votante × nivel de polémica) tenga votos en los dos lados (con respuesta y sin respuesta); los que solo tengan un lado no aportan nada a Mantel–Haenszel. *(De «Votos negativos al responder».)*

## Decisiones pendientes
- Cuántos cortes en niveles de polémica.
- El número de votos por votante para incluirlo.
- Cómo se mide la robustez del valor medido.

## Preguntas pendientes
- Análisis del tiempo de vida de los usuarios y si es influenciado por las interacciones negativas que reciban
- Como mido la negatividad sin votos?
- Qué uso de referencia para medir la proporcion de respuestas que cruzan facciones?
- FAULTANA midió el antagonismo por tema. Podría extender la pregunta del quién responde a quién por tema? Se reduciria demasiado el tamaño del sample?
- Qué subdivisiones puedo hacer en los datos que mantengan suficientes usuarios en cada celda.
- ¿Como defino el umbral para interpretar los resultados al pasar de un trabajo descriptivo a uno que pretende testear una hipotesis?
