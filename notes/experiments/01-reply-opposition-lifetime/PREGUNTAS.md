# Experimento 01: posibles preguntas y respuestas

**Cómo usarlo:** tapa la respuesta, contesta con tus palabras y compara. Las respuestas están en primera persona para que las puedas adaptar. No hace falta repetirlas literalmente: lo que cuenta es que entiendas la idea.
**Base:** [[EXPLICACION]] (todo el detalle), [[RESULTS]] y [[NOTES]].

Las preguntas están ordenadas de lo general a lo técnico:
1. Visión general
2. Datos y limpieza
3. Modelo nulo
4. H1
5. H2
6. H3
7. Tiempo de vida
8. H4
9. Robustez
10. Interpretación
11. Uso de IA
12. Próximos pasos
13. Embeddings

---

## 1. Visión general

**P1. Explícame en un minuto qué has hecho y qué has encontrado.**
El dataset no tiene el texto de los comentarios, así que la postura la infiero de los votos. Miré quién responde a quién y si hay oposición en tres niveles: el comentario, la pareja de usuarios y la facción. Cada resultado lo comparo con un modelo nulo. Encontré que quien responde vota negativo el comentario mucho más que los otros votantes de ese comentario, que la hostilidad crece con la profundidad del hilo y que las facciones apenas se cruzan, pero cuando lo hacen es con hostilidad. Además, la mayoría de usuarios se queda poco tiempo, y los nuevos que reciben más hostilidad en su primer mes se van antes. Todo son asociaciones, no causas.

**P2. ¿Cuál es el resultado más importante?**
Para mí, el de H1: quien responde vota negativo el 53 % de las veces frente al 30 % de los demás votantes del mismo comentario (odds ratio 4,4). Es el resultado más limpio, estable por año y tema, y es la base de lo demás.

**P3. ¿Cómo has medido "posiciones opuestas" si no hay texto?**
Con votos, a tres niveles: si A votó negativo el comentario concreto al que respondió, si A suele votar negativo a B en todo el dataset, y si A y B están en facciones opuestas según FAULTANA. Es desaprobación expresada con votos, no ideología medida.

**P4. ¿Qué limitaciones tiene lo que has hecho?**
Cuatro principales. Uno: postura es voto negativo, no ideología. Dos: los votos no tienen marca de tiempo, así que no sé si el voto fue antes o después de responder. Tres: las facciones salen de los mismos votos y solo cubren usuarios estables, así que H3 es parcialmente circular. Cuatro: H4 es observacional, con posible causalidad inversa y sin poder separar baneos de abandonos.

---

## 2. Datos y limpieza

**P5. ¿Por qué eliminaste 259.521 comentarios?**
Eran duplicados exactos (mismo ID y todas las columnas iguales). Comprobé que cada ID tiene una sola versión de fila, así que quitarlos no pierde información. Si los dejara, cada duplicado generaría dos aristas de respuesta idénticas y contaría dos veces los votos. No he investigado por qué existen.

**P6. ¿Por qué descartaste 27 millones de votos?**
Son votos de cuentas borradas (votante NULL). No se puede saber quién votó, así que no sirven para nada entre pares de usuarios. Además, al principio parecían crear 1,33 M de votos contradictorios en un mismo comentario, pero era un artefacto: todos los votantes borrados se agrupan como un único "usuario" NULL. Sin ellos, hay cero contradicciones.

**P7. ¿Eso no puede sesgar los resultados?**
Puede. El 15 % de las respuestas y 27 M de votos tienen alguna cuenta borrada, y no sé si esos usuarios se comportan distinto. Es una pregunta abierta en mis notas. Si fueran, por ejemplo, más hostiles, mi H1 subestimaría el efecto; si fueran menos, lo sobrestimaría. No puedo saberlo sin datos de ellos.

**P8. ¿Cómo defines una respuesta?**
Solo cuando el `parent_id` del mensaje es el comentario de B y el autor es A. Hay respuestas "informales" (mencionar a alguien sin pulsar responder) que se pierden, pero solo puedo asegurar que es una respuesta si sigue la estructura del hilo.

**P9. ¿Por qué quitas las autorrespuestas?**
Porque no son una interacción entre dos usuarios; no tiene sentido hablar de oposición de A hacia sí mismo. Son 773.899 (1,4 %).

**P10. ¿Hay autovotos?**
No. Comprobé que no hay ninguno, en ninguno de los dos signos, y que el test podía detectarlos (el 92,6 % de los votos tiene autor conocido). La explicación probable es que la plataforma no deja votar tu propio comentario, aunque los datos no lo prueban. Importa porque un autovoto positivo inflaría el odds ratio de H1.

**P11. El dataset tiene 412 M de votos y usas 384 M. ¿Qué hay de los 28 M restantes?**
Son los 27,1 M con votante NULL, más los duplicados exactos colapsados a un voto por (comentario, votante).

---

## 3. Modelo nulo

**P12. ¿Por qué necesitas un modelo nulo?**
Porque un número suelto no significa nada. Si digo que el 31 % de las relaciones entre A y a quien responde son negativas, no sé si es mucho. El nulo me dice qué esperar si A hubiera respondido a otro autor que estaba en la misma discusión. La diferencia entre lo real y el nulo es lo que importa.

**P13. ¿Cómo construyes el nulo?**
Para cada respuesta real de A, elijo al azar el autor de un comentario anterior del mismo artículo (que no sea A). Se ordenan los comentarios del artículo por hora, y una respuesta en la posición k puede tener como nulo cualquiera de las posiciones 1 a k−1. El azar es reproducible: uso un hash del ID con una semilla fija.

**P14. ¿Qué controla el nulo y qué no?**
Controla el artículo, el momento y la exposición: B' estaba allí antes de la respuesta. No controla que A quizá solo leyera ciertos comentarios (los primeros o los más votados). Además, como muestreo uniforme sobre comentarios, no sobre autores, los autores prolíficos salen más veces en el nulo. Lo elegí así porque las respuestas se anclan a comentarios.

**P15. ¿Por qué comentarios y no autores?**
Una respuesta responde a un mensaje, no a una persona en abstracto. El conjunto de candidatos realista son los mensajes escritos antes en ese artículo. Si muestreara autores, daría el mismo peso a quien escribió un comentario que a quien escribió cien. Una comprobación que puedo hacer es repetirlo con un nulo uniforme sobre autores y ver si cambia la conclusión.

**P16. El nulo coincide con el objetivo real en el 4 % de los casos. ¿No es un problema?**
No. A veces B es la única o casi la única opción (por ejemplo, un artículo con pocos comentarios). Es legítimo: el nulo es "lo que podría haber pasado", y a veces es lo que pasó.

---

## 4. H1 (nivel de comentario)

**P17. Dices que quien responde vota negativo con un odds ratio de 4,4. ¿No será que los comentarios polémicos reciben más respuestas y más votos negativos?**
Eso lo controlo: comparo dentro de cada comentario, repliers contra otros votantes del mismo comentario, y combino con Mantel–Haenszel. Así que la polémica del comentario no explica la diferencia. Lo que no controlo es el tipo de votante: quien responde puede ser alguien más combativo en general. H2 y H3 tocan eso parcialmente al comparar con el nulo del mismo A, pero no lo eliminan.

**P18. ¿Qué es un odds ratio y qué significa 4,4?**
Las odds son P(negativo)/P(positivo). El odds ratio compara las odds de quien responde con las de quien no. OR = 1 es sin diferencia. OR = 4,4 es que las odds de votar negativo son 4,4 veces mayores entre quien responde. En proporciones es 53 % frente a 30 %. No son "4,4 veces más probable", sino 4,4 veces las odds.

**P19. ¿Por qué Mantel–Haenszel y no una regresión logística?**
MH es el estimador estándar para combinar muchas tablas 2×2 (una por comentario) en un único OR. Es sencillo, no necesita ajustar millones de parámetros y se calcula directamente. La alternativa, una logística con efectos fijos por comentario, sería equivalente en espíritu pero muy costosa con 8 M de comentarios. Es una de las decisiones que aún estoy revisando.

**P20. Explícame un ejemplo de por qué estratificar.**
Imagina dos comentarios. En uno tranquilo, los que responden votan algo más negativo que los demás (OR propio 9). En uno polémico, todos votan negativo (OR 1) y además atrae muchas respuestas. Si junto todos los votos, el comentario polémico domina y el OR sale 10,9. Con MH, que compara dentro de cada comentario, sale ≈ 2,05. El OR sin estratificar mide en parte "qué comentarios son polémicos", no "quién responde".

**P21. El intervalo es 4,42–4,44. ¿No es demasiado estrecho?**
Sí, y no hay que fiarse de él. Con 8 M de comentarios, cualquier cosa sale "significativa". Además, mi bootstrap es sobre comentarios, no agrupado por votante, así que no refleja que los mismos votantes aparecen en muchos comentarios. Me apoyo en la estabilidad: sale entre 4,1 y 4,7 en todos los años, entre 3,5 y 4,9 por tema.

**P22. ¿Qué pasa con quien responde pero no vota?**
No entra en el cálculo de H1. Solo cuentan los que responden y votan el comentario. Eso restringe el análisis, aunque es lo único que permite medir su postura.

**P23. ¿Por qué crece el odds ratio con la profundidad?**
Del nivel raíz (OR 3,5) al nivel 5 o más (OR 9,0). Mi lectura es que los intercambios largos son sobre todo ida y vuelta entre gente que discrepa. Es una hipótesis: puede ser también que los hilos profundos se queden solo con los más combativos (selección), no que la gente se vuelva más hostil.

---

## 5. H2 (nivel de pareja)

**P24. ¿Qué mide H2 que no mida H1?**
H1 mira un comentario. H2 mira la relación de A con B en todo el dataset: si A suele votar negativo a B. Responde a "¿respondes a gente a la que ya te opones?", y no solo "¿votaste mal ese comentario?".

**P25. ¿Por qué excluyes el voto al comentario concreto?**
Para que H2 no recuente H1. Si A votó negativo al comentario al que respondió, y ese voto cuenta en la relación A→B, estaría mezclando los dos niveles. Excluirlo hace que H2 solo use el resto de la historia de votos entre ambos.

**P26. ¿Qué es la distribución Beta y el E[p]?**
Resume la relación A→B con pocos datos de forma prudente. E[p] = (pos + α)/(pos + neg + α + β) es la probabilidad estimada de que A vote positivo a B, con un prior (α = 1, β = 2) que inclina un poco a lo negativo. Por ejemplo, con 3 positivos y 2 negativos, E[p] = 0,5; con 0 positivos y 5 negativos, E[p] = 0,125.

**P27. ¿Por qué ese prior y esos umbrales?**
Son los de FAULTANA, el trabajo previo del grupo. Aun así los varié en el multiverso: con prior (1,1), umbrales 0,7/0,3, mínimos de 1, 5 o 20 votos, y con o sin el voto concreto, la diferencia es siempre positiva (+11,7 a +20,6 pp). Es otra decisión que sigo revisando.

**P28. ¿Qué es una "arista negativa"?**
Una pareja con al menos 5 votos y E[p] < 0,4. La métrica es la fracción de aristas negativas entre las aristas con postura clara (negativas más positivas, E[p] > 0,6, con ≥ 5 votos). Salió 31,4 % para el objetivo real frente a 18,1 % para el nulo.

**P29. ¿Por qué no usas simplemente el porcentaje global de votos negativos entre A y B?**
Porque engaña. Lo dominan unas pocas parejas con miles de votos positivos mutuos. La mediana de una pareja es 1 o 2 votos y la media ~110. Con ese porcentaje global, el 7 % sale con picos del 40 % en 2013 y 20 % en 2022, que solo reflejan mega-parejas. Uso medidas por arista: cada respuesta cuenta una vez.

**P30. ¿Por qué el bootstrap está agrupado por quien responde?**
Porque las respuestas de un mismo A no son independientes: el mismo usuario, con las mismas costumbres de voto, aparece en muchas. Si remuestreara aristas sueltas, subestimaría la incertidumbre.

---

## 6. H3 (facciones)

**P31. ¿Qué son las facciones?**
Dos grupos de usuarios que identificó el trabajo FAULTANA (Fraxanet 2024) a partir de la red de votos. Solo hay etiquetas para 14.800 usuarios "estables" (votaron todos los años de 2014 a 2021): 9.278 en la facción 1 y 5.539 en la 2.

**P32. ¿Qué dicen los resultados de H3?**
Que las facciones casi no se cruzan: el 26 % de las respuestas va a la otra facción, frente al 47 % si se mezclaran al azar. Pero la mayor parte de esa segregación viene de quién comparte discusión (el nulo da 23 %); dentro de esa exposición, la gente elige un poco más de lo esperado al de fuera (+2,8 pp). Y cuando cruzan, lo hacen con hostilidad: el 65 % vota negativo el comentario frente al 37 % dentro de la misma facción.

**P33. ¿Por qué dices que H3 es circular?**
Porque las facciones se construyeron a partir de los mismos votos que ahora uso para medir hostilidad. Que haya muchos votos negativos entre facciones es, en parte, la definición de las facciones. Además solo cubren usuarios estables, que son supervivientes por construcción. Por eso trato H3b con cautela y no lo uso como prueba principal.

**P34. ¿Por qué no extendiste las facciones al resto de usuarios?**
Lo intenté con un score basado en a quién vota cada usuario, pero tiene un AUC de 0,63 (0,5 es azar) y la validación es dentro de la propia muestra. Demasiado débil. Lo dejé en un apéndice: apunta en la misma dirección (29,7 % frente a 24,5 % entre facciones) pero no lo uso en las conclusiones.

---

## 7. Tiempo de vida

**P35. ¿Cómo defines el tiempo de vida?**
Última actividad menos primera actividad, contando comentarios y votos. Si la última actividad es posterior a 2022-07-01, lo trato como censurado: no sé si el usuario se ha ido o sigue. Y si la primera actividad es anterior a 2013-07-01, la marco como censurada por la izquierda, porque puede haber llegado antes del dataset.

**P36. ¿Qué es la censura y por qué importa?**
Es información incompleta: sé que un usuario estaba activo hasta una fecha, pero no cuándo se va. Si los tratara como "se fue en esa fecha", subestimaría el tiempo de vida de quienes siguen activos. Los métodos de supervivencia (Kaplan–Meier, Cox) usan esa información correctamente.

**P37. ¿Qué es Kaplan–Meier?**
Un estimador de la curva de supervivencia: la fracción de usuarios que sigue activa tras t años, teniendo en cuenta a los censurados. Lo uso por cohorte de entrada.

**P38. ¿Qué dicen los resultados?**
Que la mayoría no se queda: el 27 % está activo menos de un día y el 20 % escribió un solo comentario. Y las cohortes nuevas se van más rápido: la mediana baja de 1,4 años (cohorte 2014) a 0,4 (cohorte 2020). Las curvas caen mucho en las primeras semanas y luego decaen despacio, así que quien pasa los primeros meses suele quedarse años.

**P39. ¿Cuál es el buffer de abandono (6 meses)?**
Considero que un usuario "se fue" si no hay actividad en los últimos 6 meses del dataset (desde 2022-07-01). Es una convención: con menos meses sobrestimo los abandonos; con más, pierdo usuarios recientes. Lo varié a 3, 6 y 12 meses en el multiverso.

---

## 8. H4

**P40. Explica el diseño de H4.**
Tomo comentaristas nuevos que siguen activos tras sus primeros 30 días. Mido su exposición a hostilidad en esos 30 días (votos negativos recibidos, respuestas hostiles recibidas y escritas, si recibió respuesta, cuánto comentó). Y miro cuánto tiempo siguen activos a partir del día 30, con un modelo de Cox estratificado por cohorte.

**P41. ¿Por qué un "hito" en el día 30?**
Para evitar el sesgo de tiempo inmortal. Si midiera la exposición durante 30 días y contara la supervivencia desde el día 0, quien se va el día 3 no ha podido acumular exposición, mientras que quien acumula mucha tuvo que sobrevivir esos días. Eso crea una relación falsa. Con el hito, mido antes y cuento la supervivencia después, solo entre los que siguen vivos.

**P42. ¿Qué es un hazard ratio de 1,11 por desviación estándar?**
Que un usuario con 1 desviación estándar más de cuota de votos negativos tiene un riesgo de irse un 11 % mayor en cada momento, comparado con uno medio y con las demás variables fijas. Es un efecto pequeño por unidad, pero consistente.

**P43. ¿Por qué estratificas por cohorte?**
Porque la tasa de abandono base cambia mucho entre cohortes (la mediana pasa de 1,4 a 0,4 años). Estratificar da a cada cohorte su propia línea base, así comparo usuarios de la misma generación.

**P44. ¿Por qué tiene un HR de 1,23 el número de comentarios tempranos? ¿No debería quedarse más quien participa más?**
Parece contraintuitivo, pero los que escriben más de 30 comentarios en el primer mes se van mucho antes (71 % se va, mediana 0,95 años, frente a 57 % y 2,35 años de los que escriben 1–2). Probablemente son cuentas de ráfaga, baneadas o duplicadas, no gente muy implicada. Es algo que merece un análisis aparte.

**P45. Explícame el error del "shrinkage" que encontraste.**
Las cuotas (por ejemplo, % de respuestas hostiles) las contraigo hacia un valor para no sobrerreaccionar con pocos datos. La primera versión contraía hacia 0,5. Pero la tasa real es mucho menor, así que un usuario sin ninguna respuesta recibía un valor de 0,5, y "no tener datos" parecía hostil. El signo del efecto cambiaba entre el modelo con una variable y el ajustado. Lo corregí contrayendo hacia la tasa de toda la población.

**P46. ¿Se cumple el supuesto de hazards proporcionales?**
Lo comprobé con el test de Schoenfeld sobre una muestra de 20.000 usuarios y ninguna covariable tuvo p < 0,05. Significa que el efecto de cada covariable es aproximadamente constante en el tiempo. Cuidado: la comprobación fue con una muestra, no con los 98.670.

**P47. ¿Puedes afirmar que la hostilidad hace que se vayan?**
No. Es observacional. Puede haber causalidad inversa: usuarios que ya se desenganchan pueden provocar o atraer hostilidad. Y no distingo entre irse voluntariamente y ser baneado. Digo que la hostilidad temprana se asocia con irse antes, de forma robusta, y que sería compatible con un efecto causal, pero no lo demuestra.

---

## 9. Robustez

**P48. ¿Qué es el análisis multiverso?**
En lugar de defender una sola elección razonable (prior, umbral, ventana…), ejecuto todas las combinaciones razonables y muestro cómo varía el resultado. Para H2 son 24 especificaciones; para H4, 18. Si el resultado va siempre en la misma dirección, es robusto a esas decisiones. Sigue el enfoque de Steegen 2016 y Simonsohn 2020.

**P49. ¿Qué dice?**
En H2 la diferencia entre parejas reales y nulas es positiva en las 24 especificaciones (de +11,7 a +20,6 pp). En H4, el intervalo de confianza excluye 1 en las 18 para las tres medidas de hostilidad, y el HR se mueve poco (1,10–1,12 en votos negativos recibidos; 1,05–1,08 en respuestas hostiles).

**P50. ¿Qué no cubre el multiverso?**
Solo varía las elecciones que yo consideré. No cubre cambios de diseño más profundos (otro nulo, otro modelo, texto en lugar de votos). Y no resuelve la causalidad: robustez no es validez.

**P51. Con tantos datos, ¿importan los p-valores?**
No. Con millones de observaciones casi cualquier diferencia sale significativa. Me apoyo en el tamaño del efecto y en la consistencia entre especificaciones.

---

## 10. Interpretación

**P52. ¿Qué significa que los veteranos votan negativo el 68 % a los recién llegados?**
Que de las respuestas de usuarios con más de 3 años de antigüedad a comentarios de usuarios de menos de 30 días, en el 68 % el que responde votó negativo. Entre veteranos es el 48 %. Es compatible con una dinámica de "gatekeeping", pero también podría ser que los novatos escriban comentarios peores o más polémicos. No puedo distinguirlo con votos.

**P53. ¿Qué pasa con que "no votar" sea igual de frecuente que votar negativo para recibir respuesta de vuelta?**
En reply-back, B responde de vuelta un 31,8 % si A votó negativo, un 29,8 % si A no votó y un 16,6 % si votó positivo. Lo informativo es la diferencia con el positivo. Que "no votó" se parezca a "votó negativo" puede reflejar que muchos que no votan responden por otros motivos (preguntas, correcciones). Lo trato con cautela.

**P54. ¿Se puede publicar esto?**
Andreas dijo que es publicable pero no mostró mucho interés. Para ser publicable haría falta mejorar los puntos débiles (identificar la causalidad, el orden de los votos, un control mejor de los votantes) y quizá añadir texto con embeddings.

---

## 11. Uso de IA

**P55. ¿Cuánto has hecho tú y cuánto la IA?**
Con honestidad: el análisis inicial lo ejecutó Claude Code en una sesión de una hora, incluido el diseño, el código, la limpieza y la interpretación. Yo lo estoy revisando decisión a decisión según un método que escribí (AI-USE). Las que ya he adoptado y justificado son el modelo nulo, la limpieza, la definición de respuesta y el test de autovotos. El resto las estoy estudiando y las considero preliminares.

**P56. ¿Y si te pregunto algo que no sabes?**
Digo que no lo sé y que lo compruebo. Por ejemplo, no he verificado si los contadores de votos de la tabla de comentarios, de donde salen los votos negativos recibidos en H4, incluyen votos de cuentas borradas, mientras que el resto del análisis los descarta. Lo apuntaré y lo miraré.

**P57. ¿Está permitido usar IA así en el TFG?**
Es una de mis tareas pendientes: preguntar a Carla Ràfols y a Andreas cuál es la política de uso de IA en el TFG y declararla correctamente. Llevo un registro de uso y etiquetas en cada decisión para poder hacer una declaración precisa.

---

## 12. Próximos pasos (para la proactividad)

**P58. ¿Qué harías ahora?**
En este orden:
1. **Usuarios puente:** los que responden entre facciones sin hostilidad. ¿Quiénes son? ¿Viven más? Es una de las ideas abiertas de la reunión anterior.
2. **Escalada como secuencia:** la probabilidad de que un intercambio sea hostil en el nivel k+1 si lo fue en k.
3. **Separar baneos de salidas voluntarias:** empezando por las cuentas de ráfaga y la caída del volumen de 2022.
4. **H2 y H3 por tema:** política frente a deportes.

**P59. ¿Qué te falta por hacer del análisis actual?**
Revisar y adoptar el resto de decisiones (D1–D14), comprobar la pregunta abierta de los usuarios borrados, hacer el bootstrap de H1 agrupado por votante, y verificar el origen de los contadores de votos en H4.

**P60. ¿Qué quieres preguntarnos?**
1. La caída del 45 % de comentarios y votos por mes desde febrero de 2022, mientras los usuarios activos se mantienen: ¿cambio de recogida o de plataforma?
2. La política de uso de IA en el TFG.
3. El acceso al clúster de la UPF (si Carla aún no ha contestado).

---

## 13. Embeddings

**P61. ¿Por qué no usaste los embeddings?**
Porque pesan 508 GB (el 94 % del volumen) y solo dan similitud semántica, no acuerdo ni desacuerdo. Con los votos puedo medir oposición a escala completa y con millones de pares. Los embeddings serían un indicador secundario y débil de postura. Si hace falta más adelante, se pueden descargar por meses.

**P62. ¿Se podría hacer con tu GPU?**
Sí. Los embeddings ya están calculados (896 dimensiones), así que no hace falta generarlos. Una RTX 3070 con 8 GB de VRAM puede con similitudes y clasificadores pequeños por lotes. El cuello de botella real es el disco (el TSV descomprimido es mucho mayor que los 508 GB) y la lectura de los archivos comprimidos, no la GPU. Habría que trabajar con un subconjunto o por meses. Detalles en [[EXPLICACION]], sección 17.

**P63. ¿Para qué servirían?**
Para preguntas de contenido, como si el contenido de tus mensajes en un foro predice tu ideología en otros (una de las ideas de Andreas), o si las respuestas son semánticamente más cercanas que el nulo. Es otro experimento, no una continuación directa de este.

---

## Preguntas de trampa (revisa que sabes responderlas)

**T1. "El odds ratio es 4,4, o sea que quien responde vota negativo 4,4 veces más."**
Incorrecto. Son las *odds* las que son 4,4 veces mayores; en proporción es 53 % frente a 30 %, es decir, 1,8 veces.

**T2. "p < 0,001, luego el efecto es real."**
Con millones de observaciones todo sale significativo. Importa el tamaño del efecto y que se mantenga en todas las variantes.

**T3. "Como el HR es 1,11, la hostilidad hace que se vayan un 11 % más."**
Incorrecto en dos cosas. Es el riesgo instantáneo por desviación estándar, no el porcentaje de gente que se va. Y no es causal.

**T4. "Las facciones se odian: el 65 % de las respuestas entre facciones es hostil."**
Cuidado: las facciones se construyeron con esos votos (circularidad), solo cubren usuarios estables, y "hostil" aquí significa que el que responde votó negativo el comentario.

**T5. "El nulo es el azar puro."**
No: es un azar *condicionado* a que B estuviera presente en la misma discusión antes de la respuesta.
