# Experimento 01: guía para entender y explicar el análisis

**Para qué sirve este archivo:** entender el proceso de principio a fin y poder explicar los resultados con tus palabras. No hace falta memorizar cifras; sí saber qué se hizo, por qué y qué se puede y no se puede concluir.
**Complementos:** [[RESULTS]] (resultados), [[NOTES]] (registro de decisiones), [[PLAN]] (plan original), [[data-treatment]] (limpieza), [[AI-USE]] (método de uso de IA), [[PREGUNTAS]] (preguntas y respuestas de ensayo).
**Estado de la información:** revisada contra el código de `code/_obsoleto/01-reply-opposition-lifetime/` el 2026-10-18. Las cifras salen de `results/`.

---

## 0. En una página

**Tarea de Andreas (2026-09-30):** analizar quién responde a quién y si sus posturas son opuestas, y complementarlo con el tiempo de vida de los usuarios en el dataset.

**Problema central:** el dataset no tiene el texto de los comentarios. Hay que inferir la postura de los **votos** (positivos y negativos).

**Qué hice (en una frase por paso):**
1. Limpiar los datos y construir las **aristas de respuesta** (A responde a un comentario de B).
2. Construir un **modelo nulo**: para cada respuesta real, imaginar que A hubiera respondido a otro autor que estaba presente en el mismo artículo antes. Así sé qué esperar "por casualidad".
3. Medir si A se opone a B en tres niveles: el **comentario** (H1), la **pareja de usuarios** (H2) y la **facción** (H3), y comparar con el nulo.
4. Medir el **tiempo de vida** de los usuarios (cuánto tiempo siguen activos) y comprobar si la hostilidad recibida en el primer mes predice que se vayan antes (H4).
5. Repetir H2 y H4 con muchas variantes razonables para ver si el resultado aguanta (análisis multiverso).

**Qué encontré:**
- Quien responde a un comentario lo vota negativo mucho más que el resto de votantes de ese mismo comentario (53 % vs 30 %; odds ratio 4,4).
- Esa hostilidad crece conforme el hilo se hace más profundo.
- Las facciones casi no se cruzan, y cuando lo hacen, es con hostilidad.
- La mayoría de usuarios se queda poco tiempo, y las cohortes nuevas se van más rápido.
- Los recién llegados que reciben más votos negativos y respuestas hostiles en su primer mes se van antes.

**Qué no puedo decir:** que la hostilidad *cause* la salida, ni que el voto negativo sea *desacuerdo ideológico*. Son asociaciones basadas en votos sin marca de tiempo.

---

## 1. Los datos

| Qué | Detalle |
|---|---|
| Fuente | Foro de DerStandard.at (Austria), 2013–2022. Dataset de Fraxanet, Kaltenbrunner, Gómez y Pellert (doi:10.82201/RVQGUG) |
| Comentarios | 75.644.850 filas; **75.385.329 únicos** tras quitar duplicados exactos |
| Votos | 412,5 M filas; **383.858.436 utilizables** |
| Usuarios | 247.863 (211.108 comentan; 36.755 solo votan) |
| Identificadores | Hashes anonimizados de 16 caracteres hexadecimales (pasados a enteros para ir más rápido) |
| Tiempo | Comentarios con marca de tiempo (segundos unix). **Los votos no tienen marca de tiempo**, solo el mes del archivo |
| Texto | **No hay texto de comentarios.** Solo hay embeddings precalculados (508 GB), que no se han descargado |
| Facciones | `faction_users.tsv`: 14.800 usuarios etiquetados por el trabajo FAULTANA (9.278 en la facción 1; 5.539 en la 2). Son usuarios "estables": votaron todos los años 2014–2021 |

**Herramientas:** DuckDB (SQL sobre archivos Parquet, procesa sin cargar todo en memoria), Python (pandas, scipy, statsmodels, lifelines, matplotlib).

**Pipeline de scripts** (en `code/_obsoleto/01-reply-opposition-lifetime/`, se ejecutan en orden con `uv run python`):

| Script | Qué hace |
|---|---|
| `00_to_parquet.py` | Convierte los TSV a Parquet con tipos explícitos, `NA` → NULL, quita duplicados y votantes nulos |
| `01_reply_edges.py` | Construye las aristas A→B y la tabla de exclusiones |
| `02_null_pairs.py` | Asigna a cada respuesta su "autor nulo" |
| `03_dyads.py` | Calcula los votos de A hacia B (y hacia el autor nulo) |
| `04_h1_comment_level.py` | H1: odds ratio de Mantel–Haenszel |
| `05_h2_h3_dyad_faction.py` | H2, H3, proyección de facciones y reply-back |
| `06_lifetime.py` + `h4.py` | Tiempo de vida, Kaplan–Meier y Cox (H4) |
| `07_multiverse.py` | Robustez de H2 y H4 |

---

## 2. Limpieza de datos (y por qué cada paso)

### 2.1 Embudo de comentarios
| Paso | N | % de las filas crudas |
|---|---|---|
| Filas crudas | 75.644.850 | 100 |
| Duplicados exactos | 259.521 | 0,343 |
| **Comentarios únicos** | **75.385.329** | 99,657 |

*Por qué:* un duplicado generaría dos aristas de respuesta iguales y contaría dos veces los votos. Comprobado el 2026-10-16: cada `Comment_Id` tiene una sola versión de fila, así que `DISTINCT` no pierde información. No se ha investigado por qué hay duplicados.

### 2.2 Embudo de respuestas
| Paso | N | % |
|---|---|---|
| Respuestas (`is_reply`) | 53.427.803 | 100 |
| Marcadas como inconsistentes (hijo o padre) | 326.643 | 0,611 |
| Padre ausente | 11 | ~0 |
| Autor borrado (A o B) | 7.976.578 | 14,930 |
| Autorrespuestas | 773.899 | 1,448 |
| **Aristas finales** | **44.350.672** | 83,010 |

Una "respuesta" es **solo** un mensaje cuyo `parent_id` es el comentario de B (D15). Se pierden menciones sin usar el botón de responder; se asume.

### 2.3 Votos
- **27,1 M de votos con votante NULL (cuenta borrada) se descartan.** Parecían crear 1,33 M de "votos contradictorios" para el mismo comentario, pero era un artefacto: todos los votantes borrados se agrupan en un único "usuario" NULL. Una vez quitados, hay **0** pares (comentario, votante) con signos contradictorios.
- **Autovotos:** hay 0. Se comprobó (`check_self_votes.py`) que el test podía detectarlos. Probablemente la plataforma no deja votar el propio comentario.

### 2.4 Otros
- 26 aristas tienen `parent_ts > reply_ts` (el padre aparece posterior a la respuesta). Se mantienen; es un número despreciable.
- 21 usuarios tienen votos fechados en 2007–2012 (artículos antiguos aún abiertos). Su primera actividad se recorta a 2013-01-01 para el análisis del tiempo de vida.
- **Pregunta abierta** (en [[data-treatment]]): ¿los usuarios borrados (15 % de las respuestas, 27 M de votos) se comportan distinto del resto? Si sí, excluirlos podría sesgar H1.

---

## 3. Qué significa "postura opuesta" aquí

Sin texto, la oposición se mide con **votos**, a tres niveles (comentario, persona y grupo) que van de lo local a lo global:

| Nivel | Medida | Pregunta que responde | Hipótesis |
|---|---|---|---|
| **Comentario** | ¿A votó positivo o negativo el comentario concreto al que respondió? | ¿Estoy en desacuerdo con *este* comentario? | H1 |
| **Pareja de usuarios** | Balance de votos de A hacia B en *todo* el dataset (con una distribución Beta) | ¿Estoy en contra de *esta persona* en general? | H2 |
| **Facción** | ¿A y B están en facciones opuestas según FAULTANA? | ¿Estamos en *lados opuestos* de la línea de falla de la plataforma? | H3 |

**Importante para defender:** "postura opuesta" = **desaprobación expresada con votos**, no ideología medida. Un voto negativo puede ser desacuerdo, pero también molestia con el tono, o con el usuario.

---

## 4. El modelo nulo (la pieza más importante conceptualmente)

**El problema:** si digo "el 31 % de las parejas A→B son negativas", no sé si es mucho o poco. Hace falta una referencia.

**La idea:** para cada respuesta real A→B, buscar un **objetivo alternativo B'** que A *podría haber elegido*: el autor de un comentario escrito **antes** que la respuesta, **en el mismo artículo**. Compararlo con B responde a: "¿A eligió a B por algo más que estar los dos en la misma discusión?".

**Cómo se construye (`02_null_pairs.py`):**
1. En cada artículo se ordenan los comentarios por hora (posición 1, 2, 3…).
2. Una respuesta en la posición *k* puede tener como nulo cualquier comentario de las posiciones 1 a *k*−1.
3. Se elige uno al azar de forma **reproducible** (se usa un hash del ID del comentario con una semilla fija, 20261006, en vez de un generador aleatorio). Hasta 5 intentos por respuesta, y el primero válido se queda.
4. "Válido" = el autor no es A. Si no hay candidato (por ejemplo, k = 1), esa respuesta no tiene nulo.

**Qué controla:** el artículo, el momento y la exposición (B' estaba allí antes que la respuesta).
**Qué no controla:** que A quizá solo leyera ciertos comentarios (los primeros, los más votados). También que se muestrea **uniforme sobre comentarios**, no sobre autores, así que los autores prolíficos salen más a menudo (decisión D3, tuya: replicar "un mensaje cualquiera").

**Comprobaciones hechas:** cobertura del 99,998 %; 0 comentarios nulos posteriores a la respuesta, 0 en otro artículo, 0 autorrespuestas. El nulo coincide con el objetivo real en el 4 % de los casos; es legítimo (a veces B es la única opción).

---

## 5. H1: quien responde, ¿vota negativo lo que responde?

### 5.1 Idea
Tomo un comentario concreto *c*. Algunas personas lo votaron y respondieron (repliers); otras lo votaron y no respondieron. Si los que responden votan negativo más a menudo que los que no, hay una asociación entre responder y desaprobar.

### 5.2 Procedimiento (`04_h1_comment_level.py`)
1. Para cada comentario con al menos una respuesta, cuento los votos en una tabla 2×2:

| | Negativo | Positivo |
|---|---|---|
| Votó **y respondió** | a | b |
| Votó **y no respondió** | c | d |

2. Me quedo solo con comentarios que tienen al menos un votante-que-respondió **y** uno que no (8.117.960 comentarios "informativos").
3. Calculo el **odds ratio** de cada comentario: (a·d)/(b·c), y combino todos con **Mantel–Haenszel (MH)**.
4. Intervalo de confianza: fórmula de Robins–Breslow–Greenland, más un **bootstrap de Poisson** sobre comentarios (200 repeticiones).

### 5.3 Qué es un odds ratio (con un ejemplo hecho a mano)
Odds = P(negativo)/P(positivo). El odds ratio compara las odds de los que responden con las de los que no. OR = 1 significa sin diferencia; OR = 4,4 significa que las odds de votar negativo son 4,4 veces mayores entre los que responden.

**Por qué estratificar por comentario (MH) y no juntar todos los votos.** Ejemplo de juguete con dos comentarios:

| Comentario | a (resp., neg.) | b (resp., pos.) | c (no resp., neg.) | d (no resp., pos.) | OR propio |
|---|---|---|---|---|---|
| X (tranquilo) | 1 | 1 | 2 | 18 | (1·18)/(1·2) = **9** |
| Y (polémico) | 18 | 2 | 9 | 1 | (18·1)/(2·9) = **1** |
| Juntos sin estratificar | 19 | 3 | 11 | 19 | 361/33 = **10,9** |
| Mantel–Haenszel | | | | | **≈ 2,05** |

En el comentario polémico todo el mundo vota negativo, y además atrae muchas respuestas. Si junto los votos, esa mezcla infla el OR (10,9). MH compara dentro de cada comentario y pondera, así que no se deja arrastrar por que unos comentarios sean más polémicos.

#### El estimador de Mantel–Haenszel
Es un estimador de un **OR común** a partir de muchas tablas 2×2 (una por estrato; aquí, una por comentario). Se asume que el efecto "responder → votar negativo" es parecido en todos los comentarios, y se busca un único número que lo resuma.

$$OR_{MH} = \frac{\sum_i a_i d_i / n_i}{\sum_i b_i c_i / n_i}, \qquad n_i = a_i + b_i + c_i + d_i$$

- **Numerador:** suma de los "casos a favor" (negativo entre los que responden × positivo entre los que no), cada uno dividido por el tamaño de su comentario.
- **Denominador:** suma de los "casos en contra" (positivo entre los que responden × negativo entre los que no), con el mismo reparto.
- **Peso:** al dividir por n_i, cada comentario aporta en proporción a lo informativo que es. Un comentario con 2 votos pesa poco; uno con 500, mucho. Los comentarios sin variación (nadie respondió, o nadie no-respondió) aportan 0 a ambos lados, por eso se filtran.
- **Comprobación con el ejemplo:** X aporta 18/22 = 0,818 arriba y 2/22 = 0,091 abajo; Y aporta 18/30 = 0,6 arriba y 18/30 = 0,6 abajo. Entonces OR_MH = (0,818 + 0,6) / (0,091 + 0,6) = 1,418 / 0,691 ≈ **2,05**.
- **Por qué no la media de los OR individuales:** con tablas pequeñas aparecen ceros (división por 0) y los OR pequeños y ruidosos pesarían igual que los grandes. MH no tiene ese problema y funciona bien con muchísimos estratos pequeños, que es justo nuestro caso (8,1 M).
- **Origen:** Mantel y Haenszel (1959), *J. Natl. Cancer Inst.*, para estudios caso-control en epidemiología. El intervalo de confianza analítico es el de Robins–Breslow–Greenland (1986).
- **Supuesto y límite:** asume un OR común. Si el efecto cambia mucho entre comentarios, MH da un promedio ponderado. Por eso se mira también por año y por tema (4,1–4,7 y 3,5–4,9). Controla el comentario, no el tipo de votante.

#### Alternativas a esta métrica
| Alternativa | Qué ofrece | Inconveniente |
|---|---|---|
| **Diferencia de riesgos** (53,3 % − 30,1 % = 23,2 puntos) | Fácil de interpretar y en unidades naturales. Lo que cambia en la práctica | Depende del nivel base de votos negativos, no es comparable entre temas con base distinta |
| **Razón de riesgos** (53,3 / 30,1 ≈ 1,77) | Más intuitiva que el OR: "1,8 veces más probable" | Con estratificación, la versión MH existe, pero no se puede modelar tan fácilmente con covariables. Además, depende del nivel base |
| **Regresión logística con efectos fijos por comentario** (o logística condicional) | Mismo OR, pero permite añadir covariables (año, tema, antigüedad del votante) | Con 8 M de efectos fijos es pesada. Con logística condicional es casi equivalente a MH |
| **Modelo mixto** (intercepto aleatorio por comentario) | Estima además cuánto varía la polémica entre comentarios | Más supuestos (distribución del efecto aleatorio) y mucho coste computacional |
| **Estandarización directa** | Da una diferencia de riesgos ajustada a una distribución común de comentarios | Hay que elegir la población de referencia |
| **Diferencia / razón sin estratificar** | Trivial de calcular | Confundida por la polémica del comentario (ver el ejemplo: 10,9 frente a 2,05) |

**Por qué el OR en este proyecto:** es la medida natural cuando se estratifica, tiene estimador cerrado (MH) y no depende de lo frecuente que sea el voto negativo en cada comentario. Su coste es la interpretación: el OR de 4,43 *no* significa "4,4 veces más probable". Por eso conviene dar siempre al lado los porcentajes (53,3 % frente a 30,1 %).

### 5.4 Resultados
| | % de votos negativos |
|---|---|
| Votantes que **respondieron** | **53,3 %** |
| Otros votantes **del mismo comentario** | 30,1 % |
| **OR (MH)** | **4,43** [IC 95 % 4,42–4,44] |

- **Estable por año:** entre 4,1 y 4,7 de 2013 a 2022.
- **Estable por tema:** entre 3,5 (deportes) y 4,9 (economía).
- **Escalada con la profundidad** del comentario respondido: 3,48 (raíz) → 5,73 → 6,89 → 7,77 → 8,20 → **9,00** (profundidad ≥ 5). La cuota de votos negativos de los que responden sube de 49 % a ~63 %.

![[results/04_h1_by_year.png]]

### 5.5 Cuidado al explicarlo
- El IC es muy estrecho (4,42–4,44) porque hay millones de comentarios. **No te apoyes en el p-valor ni en el IC**; lo informativo es el tamaño del efecto y que sea estable por año, tema y profundidad.
- El bootstrap es sobre comentarios, **no agrupado por votante** (el plan decía por votante; el código usa comentarios). No refleja que los mismos votantes aparecen en muchos comentarios.
- Estratificar por comentario controla los efectos del comentario, pero **no los del votante**: quien responde puede ser un tipo de persona más combativa en general. H2 y H3 tocan esta cuestión parcialmente (comparan con el nulo del mismo A), pero no la eliminan.
- Solo cuentan los que respondieron **y votaron**. Quien respondió sin votar no entra.
- Sin marca de tiempo del voto no se sabe si el voto negativo fue antes o después de responder.

---

## 6. H2: ¿respondes a gente a la que sueles votar negativo?

### 6.1 Idea
H1 mira un comentario. H2 mira la **relación entre dos personas**: A hacia B en todo el dataset, no solo en ese comentario. Se compara con A hacia B' (el autor nulo).

### 6.2 Procedimiento (`03_dyads.py`, `05_h2_h3_dyad_faction.py`)
1. Para cada pareja (A,B) y (A,B') se cuentan los votos de A a comentarios de B: positivos y negativos.
2. **Se resta el voto de A al comentario concreto** (el padre, o el comentario nulo). Así H2 no recuenta H1 (variante `excl`).
3. Se resume la relación con una **distribución Beta**. Esta elección viene de FAULTANA (Fraxanet et al. 2024), que modela así las relaciones entre usuarios; la hereda el proyecto, junto con su prior y umbrales, para ser comparable: E[p] = (pos + α) / (pos + neg + α + β), con prior α = 1, β = 2 (el de FAULTANA, que inclina ligeramente hacia lo negativo). *p* es la probabilidad de que A vote positivo a B.

Ejemplos de E[p] (con prior 1,2):

| pos | neg | E[p] | ¿Qué es? |
|---|---|---|---|
| 0 | 5 | 1/8 = 0,125 | negativa |
| 1 | 4 | 2/8 = 0,25 | negativa |
| 2 | 3 | 3/8 = 0,375 | negativa (< 0,4) |
| 3 | 2 | 4/8 = 0,50 | indefinida (entre 0,4 y 0,6) |
| 5 | 0 | 6/8 = 0,75 | positiva |
| 0 | 0 | 1/3 | sin datos; el prior solo ya empuja a negativo, por eso se exige un mínimo de votos |

4. **Arista negativa** (definición principal): pareja con **≥ 5 votos** y E[p] < 0,4. **Arista positiva:** ≥ 5 votos y E[p] > 0,6. La métrica es **la fracción de aristas negativas entre las aristas definidas** (negativas + positivas con ≥ 5 votos).
5. **Definición estricta de FAULTANA:** además exige que la varianza posterior sea < 10⁻⁴, lo que requiere muchos votos.
6. **Intervalos:** bootstrap de Poisson **agrupado por A** (200 repeticiones), porque las respuestas del mismo A no son independientes.

### 6.3 Resultados (variante que excluye el voto concreto)
| Medida | Objetivo real (B) | Nulo (B') | Diferencia [IC 95 %] |
|---|---|---|---|
| Aristas negativas (≥ 5 votos) | **31,4 %** | 18,1 % | **+13,3 pp** [12,6; 14,0] |
| Aristas negativas, definición estricta FAULTANA | 9,4 % | 3,8 % | +5,6 pp [4,2; 7,6] |
| E[p] medio (parejas con algún voto) | 0,53 | 0,59 | −0,058 [−0,061; −0,056] |
| Hay algún historial de votos entre ambos | 59,4 % | 55,6 % | +3,8 pp |

- La diferencia **crece con la profundidad** del hilo.
- **Robustez (24 especificaciones):** prior (1,2) o (1,1); umbrales 0,6/0,4 o 0,7/0,3; mínimo de votos 1, 5 o 20; con o sin el voto concreto. La diferencia siempre es positiva, entre **+11,7 y +20,6 pp**.

![[results/05_h2_dyad.png]]

### 6.4 Por qué métricas "por arista" y no el porcentaje global de votos negativos
El porcentaje global (votos negativos / votos totales entre A y B) engaña: lo dominan unos pocos "mega-díadas" con miles de votos positivos mutuos. La mediana de una pareja es 1–2 votos y la media ~110. Por eso los titulares usan una medida por arista.

### 6.5 Detalle de redacción para no tropezar
[[RESULTS]] dice "negative relationships among user pairs with ≥5 votes (E[p] < 0.4)". En el código, el denominador es **parejas con ≥ 5 votos y E[p] < 0,4 *o* > 0,6** (las "definidas"), no todas las parejas con ≥ 5 votos. Si te lo preguntan, di: *"de las relaciones con postura clara, el 31 % son negativas"*.

---

## 7. H3: facciones

**Idea:** según FAULTANA hay dos facciones de usuarios. ¿Las respuestas cruzan la línea? ¿Cómo son esas respuestas?

**Procedimiento:** solo respuestas donde A y B tienen etiqueta de facción (11,3 M de aristas). Se comparan tres cosas: lo observado, el nulo co-presente y la mezcla aleatoria por tamaño de facción (63 % / 37 %).

| | % de respuestas entre facciones |
|---|---|
| Mezcla aleatoria por tamaño | 46,8 % |
| Nulo co-presente (quién coincide realmente en las discusiones) | 23,2 % |
| **Observado** | **26,0 %** |

**Cómo leerlo:**
1. **La exposición está muy segregada:** los usuarios comparten discusiones sobre todo con su facción (23 % vs 47 %).
2. **Dentro de esa exposición, se elige al de fuera ligeramente más de lo esperado** (+2,8 pp, +12 % relativo). El exceso viene de la facción 1 (16,7 % vs 13,7 %). La facción 2 responde a la 1 el 84 % de las veces, igual que su nulo (al ser minoría ya comparte casi todo con la 1).
3. **Las respuestas entre facciones son mucho más hostiles:**

| Tipo de respuesta | A votó negativo el padre | % de votos negativos entre ambos usuarios |
|---|---|---|
| Misma facción | 37,0 % | 2,5 % |
| **Entre facciones** | **64,6 %** | **53,1 %** |

**Advertencia importante (circularidad):** las facciones de FAULTANA se construyeron **a partir de esos mismos votos**, y solo existen para usuarios estables (supervivientes). Que haya más votos negativos entre facciones es en parte esperable por construcción. Por eso H3b se presenta con cautela.

**Proyección de facciones a todos los usuarios:** se intentó extender la etiqueta con un score basado en a quién vota cada usuario (aprobación hacia F1 menos aprobación hacia F2). Resultado: AUC 0,63 y exactitud 0,68, y es validación *dentro* de la muestra. **Demasiado débil, no se usa en las conclusiones.** Apunta en la misma dirección (29,7 % vs 24,5 % entre facciones).

---

## 8. Más resultados de respuestas

### 8.1 Reply-back: ¿la hostilidad mantiene la conversación?
Se mira si B responde a la respuesta de A según lo que A votó sobre el comentario de B.

| Voto de A sobre el comentario de B | P(B responde de vuelta) |
|---|---|
| Positivo | 16,6 % |
| No votó | 29,8 % |
| **Negativo** | **31,8 %** |

Interpretación prudente: recibir una respuesta de alguien que te votó negativo se asocia con responder el doble. Que no votar sea similar a votar negativo es un detalle a mirar (puede haber muchas respuestas sin voto por otros motivos).

### 8.2 Hostilidad por antigüedad (desde 2016-07)
Porcentaje de respuestas donde el que responde votó negativo el comentario padre:

| Quien responde \ Objetivo | < 30 días | 30 d – 1 año | 1 – 3 años | 3+ años |
|---|---|---|---|---|
| < 30 días | 59 % | 62 % | 62 % | 62 % |
| 30 d – 1 año | 62 % | 57 % | 56 % | 53 % |
| 1 – 3 años | 65 % | 60 % | 57 % | 52 % |
| **3+ años** | **68 %** | 61 % | 57 % | **48 %** |

Los veteranos son los más hostiles con los recién llegados (68 %) y los menos entre sí (48 %). Se usa desde 2016-07 para que la antigüedad no esté distorsionada por el inicio del dataset (D14). Lectura posible: "gatekeeping". Es una hipótesis, no está probado.

---

## 9. Tiempo de vida de los usuarios

### 9.1 Definiciones (`06_lifetime.py`)
- **Tiempo de vida** = última actividad − primera actividad, contando comentarios **y votos**.
- **Censura por la derecha:** si la última actividad es posterior a 2022-07-01, no sabemos si el usuario "se fue" o sigue; se trata como **censurado** (no ha tenido el evento). La ventana de 6 meses antes del final del dataset (2022-12-31) es el "buffer de abandono": si no aparece en 6 meses, se asume que se fue.
- **Censura por la izquierda:** si la primera actividad es anterior a 2013-07-01, puede ser que el usuario ya existiera antes del dataset. Se marca y se excluye de los análisis por cohorte.
- **Cohorte** = año de la primera actividad.

### 9.2 Kaplan–Meier
Es un estimador de la **curva de supervivencia**: la fracción de usuarios que sigue activa tras *t* años. Usa también a los censurados (en lugar de tirarlos), contando que estuvieron "a salvo" al menos hasta su último dato.

### 9.3 Resultados
| | Valor |
|---|---|
| Usuarios | 247.863 |
| Activos **menos de 1 día** | **26,7 %** |
| Activos menos de 30 días | 37,9 % |
| Escribieron **un solo comentario** | 20,3 % |
| Siguen activos al final (censura derecha) | 30,3 % |
| Pueden ser anteriores al dataset (censura izquierda) | 16,6 % |

| Cohorte | n | Mediana de vida | Siguen tras 1 año | Tras 3 años |
|---|---|---|---|---|
| 2014 | 20.274 | **1,36 años** | 53 % | 41 % |
| 2016 | 16.018 | 0,81 | 48 % | 36 % |
| 2018 | 14.752 | 0,41 | 44 % | 30 % |
| 2020 | 21.462 | **0,39** | 41 % | 28 % |

Cada cohorte nueva se va más rápido. Todas las curvas caen en picado las primeras semanas y luego decaen despacio: quien supera los primeros meses suele quedarse años.

![[results/06_lifetime_ccdf_km.png]]

---

## 10. H4: la hostilidad temprana, ¿predice irse antes?

### 10.1 Diseño
- **Población:** comentaristas nuevos entre 2013-07 y 2022-04 que **siguen activos tras sus primeros 30 días** → 98.670 usuarios, el 59 % de los cuales se va antes de 2022-07.
- **Exposiciones**, medidas **solo en los primeros 30 días**:
  1. *Cuota de votos negativos recibidos* en sus comentarios.
  2. *Cuota de respuestas hostiles recibidas* (el que respondió votó negativo su comentario).
  3. *Cuota de respuestas hostiles escritas.*
  4. *Si recibió alguna respuesta* (sí/no).
  5. *Número de comentarios tempranos* (logaritmo).
- **Resultado:** cuánto tiempo sigue activo **desde el día 30**.

### 10.2 Por qué el "landmark" (el hito del día 30)
**Sesgo de tiempo inmortal:** si mido las exposiciones durante 30 días pero cuento la supervivencia desde el día 0, quien se va el día 3 no ha tenido tiempo de acumular exposición, mientras que quien llega a acumular mucha *necesariamente* sobrevivió esos días. Eso crea una relación falsa. Solución: **fijar un hito en el día 30**, medir las exposiciones antes y empezar a contar la supervivencia después, solo entre los que siguen vivos en el hito.

### 10.3 Modelo de Cox
Modela el **riesgo instantáneo** (hazard) de irse. La salida es un **hazard ratio (HR)**: HR = 1,11 por desviación estándar significa que un usuario con 1 DE más de cuota de votos negativos tiene un **riesgo de irse un 11 % mayor en cada momento**, con lo demás fijo. Está **estratificado por cohorte** (cada cohorte tiene su propia línea base), y los HR son "por DE" excepto "alguna respuesta", que es binaria.

### 10.4 Reducción de cuotas (shrinkage)
Un usuario con 1 comentario y 1 voto negativo tendría "100 % negativos" con solo 1 dato. Para no sobrerreaccionar, las cuotas se **contraen hacia la tasa poblacional** con un pseudo-recuento M = 2: (k + M·tasa) / (n + M). Quien no tiene datos queda en la media poblacional.

**El error que se encontró y se arregló:** la primera versión contraía hacia 0,5 (prior Beta(1,1)). La tasa real de negativos es menor, así que "no tener datos" parecía hostil, y el signo cambiaba entre el modelo univariante y el ajustado. Se corrigió contrayendo hacia la tasa poblacional. También se descartó `log_articles` por estar muy correlacionada (r = 0,95) con `log_comments`.

### 10.5 Resultados
| Exposición (primeros 30 días) | HR por DE [IC 95 %] | Lectura |
|---|---|---|
| **Cuota de votos negativos recibidos** | **1,11** [1,10; 1,12] | más votado en contra → se va antes |
| **Respuestas hostiles recibidas** | **1,06** [1,05; 1,07] | más respuestas hostiles → se va antes |
| Respuestas hostiles escritas | 1,04 [1,03; 1,05] | ser hostil también predice irse, débilmente |
| Recibió alguna respuesta (sí/no) | 0,95 [0,93; 0,96] | que te respondan → te quedas algo más |
| Comentarios tempranos (log) | 1,23 [1,22; 1,24] | ver nota |

- **Hazards proporcionales:** se comprobó con el test de Schoenfeld sobre una muestra de 20 k; ningún p < 0,05. Es el supuesto del modelo de Cox: que el efecto de una covariable es constante en el tiempo.
- **Nota sobre la actividad temprana:** los que escriben más de 30 comentarios en el primer mes se van mucho antes (71 % se va, mediana 0,95 años restantes, frente a 57 % y 2,35 años de quienes escriben 1–2). Probablemente son cuentas de ráfaga, baneadas o duplicadas, no gente "muy implicada".

![[results/06_h4_cox.png]]

---

## 11. Análisis multiverso (robustez)

Idea (Steegen 2016; Simonsohn 2020): en lugar de defender *una* elección razonable, ejecuto *todas* las razonables y muestro cómo se mueve el resultado.

| Para | Se varía | Nº de especificaciones | Resultado |
|---|---|---|---|
| **H2** | prior (1,2)/(1,1) × umbrales 0,6–0,4/0,7–0,3 × mín. votos 1/5/20 × con/sin voto concreto | 24 | diferencia entre +11,7 y +20,6 pp, **positiva en 24/24** |
| **H4** | buffer de abandono 3/6/12 meses × ventana 14/30/60 días × shrinkage M = 2/10 | 18 | HR votos negativos 1,10–1,12; HR hostiles recibidas 1,05–1,08; **IC excluye 1 en 18/18** |

Desviación del plan: se planeó "30 días vs primeros 10 comentarios"; se usó una rejilla de ventanas para reutilizar el mismo constructor de variables (`h4.py`).

**Con millones de observaciones los p-valores no informan.** Por eso las conclusiones se apoyan en el tamaño del efecto y en estas curvas de especificación.

![[results/07_multiverse.png]]

---

## 12. Qué puedes afirmar y qué no

| Puedes decir | No puedes decir |
|---|---|
| "Quien responde a un comentario tiende a votarlo negativo mucho más que los demás votantes." | "La gente responde *porque* discrepa." (no se sabe el orden de los votos) |
| "Las respuestas se concentran en usuarios con relaciones previas más negativas que un objetivo al azar de la misma discusión." | "Las respuestas atacan a la gente de la otra ideología." (facciones ≠ ideología medida) |
| "Los recién llegados con más votos negativos y respuestas hostiles tempranas se van antes." | "La hostilidad hace que se vayan." (causalidad inversa posible; baneos mezclados con salidas) |
| "Los veteranos votan negativo más a los novatos (68 %)." | "Hay gatekeeping." (es una hipótesis compatible, no probada) |
| "Las cohortes recientes tienen vida más corta." | "El foro se ha vuelto más tóxico." (no se ha medido eso) |

---

## 13. Limitaciones y cosas a vigilar

**Las que debes decir tú antes de que te las pregunten:**
1. **Postura = voto negativo, no ideología.**
2. **Los votos no tienen marca de tiempo.** H1–H3 son asociaciones.
3. **H3 es en parte circular:** las facciones salen de los mismos votos y solo cubren usuarios estables.
4. **H4 es observacional:** causalidad inversa posible, y no se distinguen baneos de abandonos voluntarios.
5. **Caída del volumen en 2022:** comentarios y votos por mes bajan ~45 % desde febrero de 2022, aunque los usuarios activos se mantienen. Puede ser un cambio de recogida o de plataforma; **pregunta a Andreas o Emma.**
6. **Con N en millones, p-valores sin información.**

**Detalles técnicos que has de conocer (no son errores, pero te pueden pillar):**
- El bootstrap de H1 es sobre comentarios, no agrupado por votante (el plan decía por votante).
- En H1 solo entran quienes respondieron **y votaron**.
- La redacción de [[RESULTS]] sobre "≥ 5 votos" resume mal el denominador (ver 6.5).
- En H4, "respuesta hostil" = el que respondió **votó negativo**. Una respuesta sin voto cuenta como no hostil.
- La "cuota de votos negativos recibidos" de H4 sale de los contadores de votos de la tabla de comentarios. **No he verificado si esos contadores incluyen votos de cuentas borradas**, mientras que el resto del análisis los descarta. Conviene comprobarlo si te preguntan.
- Las facciones de FAULTANA solo cubren 14,8 k usuarios; la proyección es débil.

---

## 14. Quién decidió cada cosa (para ser honesto con el uso de IA)

El análisis lo ejecutó Claude Code en una sesión de ~1 hora el 2026-10-06 y ahora lo estás revisando según [[AI-USE]]. Estado según las notas a 2026-10-18 (corrígelo si has revisado más):

| # | Decisión | Estado |
|---|---|---|
| D1 | No descargar los 508 GB de embeddings | IA (delegado por ti). Sin revisar |
| D2 | Postura = desaprobación por votos, a 3 niveles | IA. Sin revisar |
| D3 | Nulo = autor de un comentario anterior al azar del mismo artículo, uniforme sobre comentarios | **[me]**, aprobada el 2026-10-16 |
| D4 | H1 = Mantel–Haenszel dentro de cada comentario | IA. Sin revisar |
| D5 | Prior Beta(1,2), umbrales 0,6/0,4, "≥ 5 votos" | IA. Sin revisar |
| D6 | Excluir el voto al comentario concreto en H2 | IA. Sin revisar |
| D7 | Limpieza (duplicados, votantes nulos, autores borrados, inconsistentes) | **[AI, reviewed]** |
| D8 | Tiempo de vida = última − primera actividad; censuras en 2022-07 y 2013-07 | IA. Sin revisar |
| D9 | Diseño H4: landmark de 30 días, Cox estratificado por cohorte | IA. Sin revisar |
| D10 | Shrinkage hacia la tasa poblacional (M = 2) | IA. Sin revisar |
| D11 | Proyección de facciones (luego descartada) | IA. Sin revisar |
| D12 | Rejillas del multiverso | IA. Sin revisar |
| D13 | Métricas por arista y no globales | IA. Sin revisar |
| D14 | Antigüedad solo desde 2016-07 | IA. Sin revisar |
| D15 | Respuesta = estructura del hilo (`parent_id`) | **[AI, reviewed]** |
| — | Test de autovotos | **[me]**, ejecutado el 2026-10-16 |

**Frase honesta para la reunión:** *"El análisis lo implementó Claude Code; estoy revisando las decisiones una a una. Las que ya he adoptado son el modelo nulo, la limpieza, la definición de respuesta y el test de autovotos. El resto las estoy estudiando y las marco como preliminares."*

---

## 15. Mapa de archivos

| Qué | Dónde |
|---|---|
| Scripts | `code/_obsoleto/01-reply-opposition-lifetime/` |
| Tablas y figuras | `notes/experiments/01-reply-opposition-lifetime/results/` |
| Log de ejecución con tiempos y recuentos | `results/run.log` |
| Datos derivados (Parquet) | `data/derstandard/derived/` (fuera de git) |
| H1 | `04_h1_comment_level.csv`, `04_h1_by_year.png` |
| H2 | `05_h2_dyad.csv`, `05_h2_by_depth_year.csv`, `07_multiverse_h2.csv`, `05_h2_dyad.png` |
| H3 | `05_h3_factions.csv`, `05_h3_stance_by_faction_relation.csv`, `05_h3_projected_factions.csv`, `05_projection_validation.csv` |
| Reply-back y antigüedad | `05_reply_back.csv`, `06_opposition_by_tenure.csv` |
| Tiempo de vida | `06_lifetime_descriptives.csv`, `06_km_by_cohort.csv`, `06_lifetime_ccdf_km.png` |
| H4 | `06_h4_cox.csv`, `06_h4_cox_univariate.csv`, `06_h4_ph_test.csv`, `06_h4_by_early_activity.csv`, `07_multiverse_h4.csv`, `06_h4_cox.png` |
| Multiverso | `07_multiverse.png` |

---

## 16. Siguientes pasos que puedes proponer

1. **Usuarios puente:** los que responden entre facciones sin hostilidad. ¿Quiénes son y viven más? (idea abierta de la reunión del 30-09).
2. **Escalada como secuencia:** P(hostil en el nivel k+1 | hostil en el nivel k) dentro de un hilo.
3. **Separar baneos de salidas voluntarias:** cuentas de ráfaga y la caída de volumen de 2022.
4. **H2 y H3 por tema:** política frente a deportes. H1 por tema ya está en `04_h1_comment_level.csv`.

Preguntas pendientes de la reunión anterior: acceso al clúster de la UPF (Carla Ràfols) y la política de uso de IA del TFG (también con Carla y Andreas).

---

## 17. Los embeddings y la GPU (no es prioridad ahora)

**Pregunta:** ¿se pueden hacer los experimentos con el dataset de embeddings con una RTX 3070?

**Respuesta corta: sí, la GPU no es el problema. Lo serán el disco y la lectura de los datos.**

**Qué son:** vectores de **896 dimensiones** (modelo KaLM-embedding-multilingual-mini-v1) ya calculados para cada comentario, en TSV (`Post_Id`, `dim_1`…`dim_896`), comprimidos en `.tar.xz` por mes. Descargados ocupan **507,8 GB**. No hay que generarlos tú; **tampoco podrías**, porque el dataset no incluye el texto.

**Por qué la 3070 sirve:**
- La 3070 tiene 8 GB de VRAM. Un bloque de 1 M de vectores de 896 floats ocupa unos 3,6 GB, así que cabe y se procesa por trozos (lotes).
- Las operaciones útiles (similitud coseno entre pares, promediar por usuario, entrenar una regresión logística o un clasificador pequeño sobre 896 dimensiones) son ligeras para una GPU de este tamaño. Muchas se podrían hacer incluso en CPU.

**Dónde está el problema real:**
1. **Disco:** el TSV descomprimido es mucho mayor que los 508 GB comprimidos (estimación mía, sin comprobar: de orden 0,7–1 TB, porque son 896 números decimales por fila). Tu disco libre ronda los 730 GB. **No cabe todo descomprimido a la vez.**
2. **Lectura:** descomprimir `.xz` y parsear texto a flotantes es lento y suele limitar más que la GPU; son horas de CPU.
3. **Memoria:** 32 GB de RAM obligan a trabajar por meses o por lotes.

**Estrategia sensata cuando toque:**
- Descargar y procesar **un subconjunto** (un año, o unos meses) o una muestra, no todo.
- Procesar por meses en *streaming*: descomprimir un mes → calcular lo que necesites → guardar solo el resultado (por ejemplo, vectores en float16 en Parquet o un `.npy`) → borrar el TSV.
- Convertir una vez a un formato binario compacto (float16, un tercio del tamaño de float32) para repetir experimentos rápido.

**Aviso sobre tu máquina:** el portátil donde se ejecuta esto muestra una **RTX 3060 Laptop con 6 GB de VRAM**, no una 3070. Si la 3070 está en otro equipo, mismo plan; con 6 GB solo hay que usar lotes más pequeños.

**Qué aportarían los embeddings al TFG:** dan similitud semántica, no acuerdo ni desacuerdo. Sirven, por ejemplo, para la pregunta de Andreas de si "el contenido de tus posts en un foro predice tu ideología en otros", o para ver si las respuestas son semánticamente más cercanas que el nulo. Eso es otro experimento.
