# Informe de decisiones · Retiro RAG

**Estado:** plantilla. Completar con resultados reales antes de la presentación.

## 1. Resumen

Describir el dominio, corpus, formatos y flujo RAG implementado.

## 2. Corpus

- Número final de documentos:
- Formatos:
- Categorías:
- Criterios de selección:
- Limitaciones:

## 3. Experimento de chunking

Comparar al menos dos configuraciones sobre los mismos documentos y preguntas.

### Configuración A

- `CHUNK_SIZE`:
- `CHUNK_OVERLAP`:
- Número de chunks:
- Preguntas:
- Resultados:

### Configuración B

- `CHUNK_SIZE`:
- `CHUNK_OVERLAP`:
- Número de chunks:
- Preguntas:
- Resultados:

### Decisión

Indicar la configuración adoptada y justificarla considerando contexto, ruido y coste.

# 4. Experimento de retrieval

### Cómo funciona el retrieval

`retrieve()` convierte la consulta en un vector con `embed_query()`, la busca en
la colección `retiro_madrid` de ChromaDB y devuelve los `top_k` chunks más
próximos, ordenados de mayor a menor relevancia.

Cada resultado conserva el chunk indexado completo (`chunk_id`, `document_id`,
`text`, `source`, `chunk_index`, `category`, `corpus_group` y `page` cuando
existe) y añade un campo `score`, según el contrato 3.

### De distancia a score

ChromaDB devuelve una distancia: cuanto menor, más parecido. El contrato exige
un `score` donde un valor mayor signifique más relevancia, así que se aplica:

    score = max(0.0, min(1.0, 1.0 - distancia))

El recorte entre 0 y 1 evita valores fuera de rango por errores de precisión. La
fórmula solo es válida con métrica coseno, que es la que usa la colección
(`HNSW_SPACE = "cosine"`). `retrieve.py` comprueba esa constante y lanza un error
explícito si alguien la cambia, para que la conversión no quede silenciosamente
mal.

### Filtro por metadata

`retrieve()` acepta un parámetro `where` que se traslada a ChromaDB, lo que
permite restringir la búsqueda a una categoría:

    python main.py --query "¿qué pasa con alerta roja?" --category seguridad

Es útil para depurar la cobertura por bloque temático y queda disponible para
futuras mejoras, como enrutar preguntas por tipo.

### Resultados por pregunta

Medición sobre el banco de 25 preguntas de `queries/banco_preguntas_bloque_c.md`.

| Pregunta | K | Mejor fuente | ¿Tiene sentido? | Ruido |
|---|---:|---|---|---|
| ¿Qué horario tiene el parque en verano? | 3 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` |
| ¿Qué rey impulsó la creación del Retiro? | 3 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` |
| Hay alerta naranja y estoy en el lago, ¿qué hago? | 3 | `[PENDIENTE]` | `[PENDIENTE]` | `[PENDIENTE]` |
| ¿Qué edificio es neomudéjar? (fuera de corpus) | 3 | `[PENDIENTE]` | No debe responder | `[PENDIENTE]` |

### Comparación de `TOP_K`

Métrica: en cuántas preguntas aparece la fuente esperada entre los `top_k`
recuperados. El denominador son las 15 preguntas con fuente declarada (13
respondibles y 2 parciales); las 10 de abstención no cuentan porque no tienen
fuente esperada.

| `TOP_K` | Recall con embeddings simulados | Recall con `gemini-embedding-001` |
|---:|---|---|
| 3 | 73 % (11/15) | `[PENDIENTE]` |
| 5 | 87 % (13/15) | `[PENDIENTE]` |

Las cifras de la columna central se obtuvieron con embeddings deterministas de
juguete (TF-IDF con hashing) para poder desarrollar y probar sin consumir la API.
Sirven para comparar configuraciones entre sí, no como medida de calidad final.

### Decisión sobre `TOP_K`

`TOP_K = 3` como valor predeterminado. `[PENDIENTE: confirmar o cambiar tras la
medición con embeddings reales.]`

Justificación: ampliar a 5 mejora el recall, pero cada chunk adicional añade
texto al contexto del LLM, lo que aumenta el coste por consulta y el riesgo de
que el modelo mezcle fragmentos poco relacionados. Con 3 chunks de 500
caracteres el contexto sigue siendo manejable y cubre la mayoría de las
preguntas. El valor es configurable por `.env` y por `--top-k`, de modo que
puede ajustarse sin tocar código.

---

## 5. Generación y grounding

### Diseño del prompt

`build_prompt()` construye un prompt con tres partes: instrucciones, contexto
numerado y pregunta. Las instrucciones obligan al modelo a responder solo desde
el contexto, a citar con `[1]`, `[2]`, a declarar cuándo un dato tiene fecha o
procede de una fuente no oficial, y a no inventar horarios, precios ni
distancias.

Cada chunk se presenta con su número, fuente, página y categoría, lo que permite
que las citas sean verificables y que el usuario sepa de qué documento sale cada
afirmación.

### La abstención tiene dos compuertas

Durante el desarrollo se comprobó que **ChromaDB siempre devuelve vecinos**,
también cuando el corpus no contiene la respuesta: ante una pregunta sin
cobertura devuelve igualmente los chunks menos lejanos. Por tanto, la abstención
no puede basarse en que la lista venga vacía. Se implementaron dos compuertas:

1. **Compuerta de retrieval.** Si el mejor `score` no alcanza `RAG_SCORE_MINIMO`,
   el sistema se abstiene sin llamar al LLM. Es determinista, reproducible y
   ahorra el coste de la llamada.
2. **Compuerta de generación.** El prompt obliga al modelo a devolver el
   centinela `SIN_EVIDENCIA` cuando el contexto no sostiene la respuesta;
   `responder()` lo detecta y lo sustituye por un mensaje claro para el usuario.

La salida de `responder()` incluye siempre `abstuvo` y `motivo_abstencion`, de
forma que se puede distinguir cuál de las dos compuertas actuó.

### Calibración del umbral

El umbral no se fijó a ojo. `scripts/validation/calibrar_umbral.py` ejecuta el
banco de preguntas, compara la distribución del `score` del mejor chunk en las
preguntas respondibles y en las de abstención, y propone el valor con más
aciertos.

Con embeddings simulados las dos distribuciones se solapan (mediana de 0,244 en
las respondibles frente a 0,205 en las de abstención) y el mejor umbral posible
solo acierta 18 de 25. Por eso `RAG_SCORE_MINIMO` se dejó en 0,0 hasta disponer
de embeddings reales: fijar un valor con datos solapados habría silenciado
respuestas correctas.

| Medida | Simulado | `gemini-embedding-001` |
|---|---|---|
| Mediana del score, preguntas respondibles | 0,244 | `[PENDIENTE]` |
| Mediana del score, preguntas de abstención | 0,205 | `[PENDIENTE]` |
| Umbral propuesto | 0,0 (sin calibrar) | `[PENDIENTE]` |
| Aciertos con ese umbral | 18/25 | `[PENDIENTE]` |

### Acierto in-corpus

- Pregunta: `[PENDIENTE: ejecutar con el índice real]`
- Respuesta: `[PENDIENTE]`
- Fuentes: `[PENDIENTE]`
- Evidencia: `[PENDIENTE: fragmento del documento que la sostiene]`
- Valoración: `[PENDIENTE]`

### Abstención fuera de corpus

- Pregunta: ¿Qué edificio del Retiro se caracteriza por su estilo neomudéjar?
- Resultado esperado: abstención. El término no aparece en ningún documento del
  corpus, pese a que es un dato real que un LLM conoce por su entrenamiento.
- Resultado obtenido: `[PENDIENTE]`
- ¿Se abstuvo correctamente?: `[PENDIENTE]`

Esta pregunta se eligió a propósito como caso difícil: si el sistema responde,
demuestra que está usando conocimiento propio del modelo en lugar del corpus.

---

## 6. Evaluación global

- Número de preguntas: 25
- Preguntas respondibles: 13
- Preguntas parciales: 2
- Preguntas de abstención: 10
- Categorías cubiertas: historia, monumentos, jardines, itinerarios,
  información práctica y seguridad

El banco está en `queries/banco_preguntas_bloque_c.md` y se ejecuta con
`scripts/validation/eval_preguntas.py`. Incluye dos preguntas conversacionales
(un visitante que busca un aseo y otro que pregunta qué hacer con alerta
naranja) y una fuera de alcance, para comprobar que el sistema no responde a lo
que no le corresponde.

### Criterios

- **Evidencia:** la fuente esperada debe aparecer entre los `top_k` chunks
  recuperados.
- **Grounding:** la respuesta debe apoyarse solo en el contexto recuperado y
  citar los fragmentos con `[n]`.
- **Abstención:** en las preguntas sin cobertura, la respuesta debe declarar que
  no dispone de esa información, sin ofrecer un dato alternativo.

### Resultados

`[PENDIENTE: tabla de resultados con el índice real: recall, tasa de abstención
correcta y falsos positivos.]`

---

## 7. Tres fallos conocidos

### Fallo 1 · Chroma siempre devuelve vecinos

- Caso: preguntas sin respuesta en el corpus, como la fauna del Estanque Grande
  o el estilo neomudéjar, para las que el retrieval devuelve igualmente tres
  chunks con score no nulo.
- Causa probable: una búsqueda por vecinos más próximos no tiene noción de
  "ninguno es relevante"; siempre devuelve los `k` menos lejanos.
- Impacto: sin una compuerta explícita, el LLM recibiría contexto irrelevante y
  podría construir una respuesta plausible pero infundada.
- Posible mejora: el umbral de score y el centinela ya mitigan el problema. Una
  mejora futura sería un reranking o un clasificador de relevancia previo al LLM.

### Fallo 2 · Preguntas con superlativos o comparaciones

- Caso: «qué fauna es *más habitual*», «cuál es la entrada *más utilizada*». El
  corpus puede contener los elementos, pero no la comparación.
- Causa probable: el retrieval semántico recupera fragmentos sobre el tema, pero
  ningún documento afirma cuál predomina.
- Impacto: riesgo de que el modelo deduzca un superlativo que ninguna fuente
  sostiene.
- Posible mejora: instruir al modelo para tratar los superlativos como
  afirmaciones que requieren evidencia explícita, y clasificar estas preguntas
  como parciales en el banco.

### Fallo 3 · Preguntas que mezclan ubicación y servicio

- Caso: «estoy en el Ángel Caído y necesito un baño, ¿cuál es el más cercano?».
  El retrieval recupera documentos sobre el Ángel Caído, pero no el fragmento
  que habla de los aseos.
- Causa probable: la pregunta contiene dos conceptos y domina el topónimo, que
  aparece en muchos más chunks.
- Impacto: se responde sobre el lugar, no sobre el servicio.
- Posible mejora: descomponer la consulta en dos búsquedas, o ampliar `top_k`
  cuando la pregunta contenga varias entidades.

---

## 8. Logging y métricas

`src/logging_utils.py` registra cada consulta en dos sitios: una línea legible
por consola y una línea JSON por consulta en `output/consultas.jsonl`.

Campos registrados: marca de tiempo, pregunta, `top_k`, número de chunks
recuperados, tiempo en segundos, modelo de generación, `abstuvo`,
`motivo_abstencion`, `score` del mejor chunk y fuentes citadas.

Se eligió el formato JSONL porque permite añadir líneas sin releer el fichero y
se carga en una instrucción:

    pandas.read_json("output/consultas.jsonl", lines=True)

El registro está conectado dentro de `responder()`, de modo que queda constancia
tanto de las consultas hechas desde la CLI como desde Streamlit. Un fallo de
escritura no interrumpe la consulta: se avisa y se continúa, porque un problema
de registro no debe dejar sin respuesta al usuario.

`resumen_de_consultas()` devuelve el total de consultas, el número de
abstenciones, la tasa de abstención y el tiempo medio.

### Métricas de la sesión de evaluación

- Consultas registradas: `[PENDIENTE]`
- Abstenciones: `[PENDIENTE]`
- Tasa de abstención: `[PENDIENTE]`
- Tiempo medio por consulta: `[PENDIENTE]`

## 9. Decisiones técnicas

- Modelo de embeddings:
- Modelo de generación:
- ChromaDB y ruta persistente:
- Estrategia de regeneración:
- API interna:
- Justificación:

## 10. Siguientes pasos

Describir mejoras razonables para Agentes y MLOps, diferenciándolas del MVP entregado.
