# Experimento 01: resumen para la reunión (lectura de ~7 min)

Versión comprimida de [[EXPLICACION]]. Si te preguntan algo con más detalle, está ahí con el número de sección.

---

## 1. La historia en 30 segundos

Andreas pidió (30-09): **quién responde a quién, si sus posturas son opuestas, y cuánto tiempo viven los usuarios en el foro.**
El dataset (DerStandard.at, 2013–2022, 75 M de comentarios, 384 M de votos) **no tiene texto**, así que la postura se infiere de los **votos**. Todo lo que sigue es "desaprobación expresada con votos", no ideología.

---

## 2. Qué hice (5 pasos)

1. **Limpieza.** Quité duplicados (0,3 %), votos de cuentas borradas (27 M) y tres tipos de respuestas: las marcadas como inconsistentes, las autorrespuestas (alguien que se responde a sí mismo) y las que tienen un autor borrado (A o B), porque sin saber quién es no hay pareja. Quedan **44,3 M de respuestas A→B**. "Respuesta" = mensaje cuyo `parent_id` es el comentario de B.
2. **Modelo nulo.** Para cada respuesta real, elijo un autor B' que **ya había escrito antes, en el mismo artículo**. Es lo que A podría haber elegido. Sirve para saber qué esperar por casualidad. (Decisión mía, aprobada el 16-10.)
3. **Tres niveles a los que medimos si A se opone a B: el comentario, la persona y el grupo**, de lo más local a lo más global. En los tres, "oponerse" significa que A **desaprueba con su voto**:
   - **Comentario (H1: los votantes que responden a un comentario lo votan negativo más a menudo que los votantes que no responden).**
     - *Pregunta:* ¿A está en desacuerdo con *este* comentario?
     - *Medida:* el voto de A al comentario concreto al que responde, comparado con el de otros votantes de ese mismo comentario.
     - *Ejemplo:* A responde a un comentario de B y le puso un voto negativo; C lo votó pero no respondió y puso positivo.
   - **Pareja de usuarios (H2: las parejas que se responden, A→B, tienen un balance de votos más negativo que las parejas nulas, A→B', formadas por A con un autor que estaba presente antes en el mismo artículo).**
     - *Pregunta:* ¿A está en contra de *esta persona* en general?
     - *Medida:* los votos de A a **todos** los comentarios de B en el dataset, resumidos con una distribución Beta. Se resta el voto al comentario concreto para que H2 no repita H1.
     - *Ejemplo:* A ha votado 4 comentarios de B, 1 positivo y 3 negativos. Es una relación negativa, aunque el comentario al que responde hoy no sea el peor.
   - **Facción (H3: entre las respuestas en que A y B tienen facción asignada, la proporción que cruza facciones supera tanto a la mezcla aleatoria según el tamaño de las facciones como al mismo nulo de H2).**
     - *Pregunta:* ¿A y B están en lados opuestos de la línea de falla de la plataforma?
     - *Medida:* la etiqueta de facción de FAULTANA (dos facciones, 14.800 usuarios estables). Se separan las respuestas en misma facción (cohesivas) y entre facciones (divisivas).
     - *Ejemplo:* A está en la facción 1 y responde a B de la facción 2, y A votó negativo el comentario de B.
   - **Por qué los tres:** responden a preguntas distintas y se complementan. H1 puede deberse a un comentario concreto que molesta, H2 a una relación personal, H3 a un conflicto de grupo. Si salieran en direcciones distintas, sabríamos en qué nivel está el efecto.
4. **Tiempo de vida** (última actividad − primera, contando comentarios y votos) y **H4: los usuarios nuevos que reciben más votos negativos y más respuestas hostiles en sus primeros 30 días dejan el foro antes.**
5. **Multiverso:** repetir H2 y H4 con muchas variantes razonables para ver si aguanta.

---

## 3. Resultados (los números que importan)

| Hipótesis | Resultado | En una frase |
|---|---|---|
| **H1** comentario | **53 % vs 30 %** de votos negativos; OR = 4,4 | Quien responde a un comentario lo vota negativo mucho más que el resto de votantes **de ese mismo comentario** |
| **H1** por profundidad | OR 3,5 (raíz) → 9,0 (profundidad ≥ 5) | La hostilidad **escala** cuanto más profundo es el hilo |
| **H2** pareja | **31 % vs 18 %** de relaciones negativas (B real vs nulo), +13 pp | A responde más a gente con quien ya tenía historial negativo que a un autor al azar de la misma discusión. Positivo en **24/24** variantes (+12 a +21 pp) |
| **H3** facciones | 26,0 % de respuestas cruzan facción (nulo: 23,2 %; mezcla aleatoria: 46,8 %) | Las facciones **casi no se cruzan**, y quien cruza lo hace con hostilidad (65 % vs 37 % de voto negativo al padre) |
| **Tiempo de vida** | 27 % activos < 1 día; cohortes nuevas viven menos (mediana 1,4 años en 2014; 0,4 en 2020) | Casi todos se van pronto; quien pasa los primeros meses suele quedarse |
| **H4** | HR 1,11 por DE de votos negativos recibidos en el primer mes; HR 1,06 por respuestas hostiles | Los novatos más votados en contra se van antes. Aguanta en 18/18 variantes |

**Extras:**
- **Reply-back:** si A votó negativo tu comentario, respondes de vuelta el 32 % de las veces; si votó positivo, el 17 %.
- **Antigüedad:** los veteranos (3+ años) votan negativo al 68 % de las respuestas a novatos, y solo al 48 % entre veteranos. Hipótesis compatible con *gatekeeping*, **no probada**.

---

## 4. Cómo explicar los conceptos clave (sin tecnicismos)

- **Odds ratio (razón de odds, OR).** Compara cuánto más probable (en odds) es votar negativo entre quienes responden que entre quienes no. OR = 1: sin diferencia. OR = 4,4: mucho más. **No significa "4,4 veces más probable"**; para eso están los porcentajes 53 % vs 30 %.
- **Mantel–Haenszel.** Forma de combinar un OR por comentario en uno solo, **comparando siempre dentro del mismo comentario**. Así la polémica del comentario no infla el resultado. Ejemplo de juguete: sin estratificar el OR sale 10,9; con MH, 2,05.
- **Modelo nulo.** "¿Qué pasaría si A hubiera respondido a otro que estaba allí?". Es la referencia; sin ella, el 31 % no se sabe si es mucho o poco.
- **Beta (H2).** Resumen de la relación entre dos usuarios a partir de sus votos pasados, con un prior que evita sacar conclusiones con 1 solo voto. "Negativa" = ≥ 5 votos y probabilidad esperada de voto positivo < 0,4. **La elección de la Beta no es mía ni de la IA: es la de FAULTANA** (Fraxanet et al. 2024, el trabajo previo del grupo), que modela así la relación entre usuarios. Se hereda con su prior (α = 1, β = 2) y sus umbrales (0,6 / 0,4) para que las relaciones sean comparables con las suyas. Es una distribución natural para una probabilidad (la de que A vote positivo a B) y se actualiza sumando votos. Lo que sí decidimos aquí es relajar su criterio a "≥ 5 votos" y comprobar en el multiverso que otros priors y umbrales dan lo mismo.
- **Kaplan–Meier.** Curva de "qué fracción sigue activa tras *t* años", contando también a los que aún no se han ido (censurados).
- **Cox / hazard ratio.** HR = 1,11 → un usuario con 1 DE más de votos negativos tiene un **11 % más de riesgo de irse en cada momento**.
- **Landmark (día 30).** Mido la exposición en los primeros 30 días y cuento la supervivencia **desde el día 30**, solo en los que siguen vivos. Evita el sesgo del tiempo inmortal (quien se va el día 3 no tiene tiempo de acumular exposición).
- **Multiverso.** En vez de defender una elección, ejecuto todas las razonables y enseño cómo se mueve el resultado.

---

## 5. Lo que puedes y no puedes decir

| ✅ Puedes decir | ❌ No puedes decir |
|---|---|
| Quien responde vota negativo más que los demás en ese comentario | Que responde *porque* discrepa (no hay marca de tiempo del voto) |
| Las respuestas van a gente con peor historial que un objetivo al azar | Que atacan a "la otra ideología" (facciones ≠ ideología) |
| Los novatos con más hostilidad temprana se van antes | Que la hostilidad *causa* la salida (causalidad inversa, baneos) |
| Las cohortes nuevas viven menos | Que el foro "se ha vuelto más tóxico" |

---

## 6. Limitaciones que debes decir tú primero

1. **Postura = voto negativo.** Puede ser desacuerdo, tono o antipatía hacia el usuario.
2. **Los votos no tienen marca de tiempo.** H1–H3 son asociaciones.
3. **H3 es en parte circular:** las facciones (FAULTANA) salen de esos mismos votos y solo cubren usuarios estables (14,8 k).
4. **H4 es observacional:** no se distinguen baneos de abandonos voluntarios.
5. **Caída del ~45 % del volumen desde feb-2022:** no sé si es un cambio de recogida. **Preguntar a Andreas o Emma.**
6. **Con millones de datos los p-valores no informan:** hay que mirar el tamaño del efecto y la estabilidad.
7. **H1 controla el comentario, no el tipo de votante:** quien responde puede ser más combativo en general.

**Detalles que te pueden pillar:**
- El bootstrap de H1 es por comentarios, no por votante (el plan decía por votante).
- Los repliers de H1 son los que respondieron **y votaron**.
- En H2, "31 %" es *de las relaciones con postura clara* (≥ 5 votos y E[p] < 0,4 o > 0,6), no de todas.
- No he comprobado si los contadores de votos recibidos de H4 incluyen cuentas borradas.

---

## 7. Honestidad sobre el uso de IA

> *"El análisis lo implementó Claude Code; estoy revisando las decisiones una a una. Las que ya he adoptado son el modelo nulo, la limpieza, la definición de respuesta y el test de autovotos. El resto las estoy estudiando y las marco como preliminares."*

Estado a 2026-10-18: aprobadas por mí D3 (nulo), D7 (limpieza), D15 (definición de respuesta). Pendientes de revisar: D4 (MH), D5 (prior Beta y umbrales), D6, D8–D14.

---

## 8. Qué proponer / preguntar

**Proponer:**
1. **Usuarios puente:** los que responden entre facciones sin hostilidad. ¿Quiénes son? ¿Viven más? (idea abierta del 30-09)
2. **Escalada como secuencia:** P(hostil en el nivel k+1 | hostil en el k).
3. **Separar baneos de abandonos** y entender la caída de 2022.
4. **H2 y H3 por tema** (política frente a deportes).

**Preguntar:**
- ¿Hay un cambio de recogida de datos en 2022?
- Acceso al clúster de la UPF (Carla Ràfols) y política de uso de IA del TFG (con Carla y Andreas).
- Embeddings (508 GB): no son prioridad. Con tu GPU no hay problema; limita el disco. Se haría con un subconjunto por meses.
