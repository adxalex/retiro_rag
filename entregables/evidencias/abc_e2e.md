# Validación ABC end-to-end

## Objetivo

Validar el funcionamiento integrado de los bloques A, B y C desde un entorno reproducible, utilizando el índice Chroma preconstruido y sin regenerar embeddings ni reconstruir la colección.

## Entorno de validación

- Rama: `validation/abc-e2e`
- Base: `feature/prebuilt-index-bootstrap`
- Índice: `index-v1`
- Colección: `retiro_madrid`
- Modelo de embeddings: `gemini-embedding-001`
- Reconstrucción del índice: no
- Regeneración de embeddings del corpus: no

## Pruebas realizadas

- Descarga del índice preconstruido en una ruta temporal.
- Retrieval mediante CLI.
- Respuesta RAG completa.
- Comportamiento de abstención.
- Salida con contexto.
- Salida JSON.
- Ejecución de Streamlit.
- Ejecución de la suite completa de tests.

## Descarga del índice preconstruido

Comando:

```bash
python -m scripts.download_index
```

Resultado:

- Descarga completada correctamente.
- Índice instalado en `chroma_abc_test`.
- No se modificó el índice local original.
- No se regeneraron embeddings.
- No se reconstruyó la colección.

Evidencias:

![Índice preconstruido descargado](capturas/01_indice_preconstruido_descargado.png.png)
![Colección chroma_abc_test](capturas/02_chroma_abc_test.png.png)

Conclusión: OK. El índice preconstruido puede instalarse en una ruta independiente sin modificar la colección local existente.

## Respuesta RAG completa

Comando:

```bash
python main.py --ask "¿A qué hora abre el Retiro?"
```

Resultado:

- Retrieval ejecutado correctamente con `top_k=3`.
- Se recuperaron 3 chunks.
- El modelo generativo utilizado fue `gemini-3.6-flash`.
- La respuesta se generó correctamente a partir del contexto recuperado.
- La salida incluyó referencias numeradas y fuentes.
- Fuente principal utilizada: `informacion_practica_guia_visitante_retiro.pdf`.
- También se recuperó: `flora_fauna__senda_botanica__madrid__v01.pdf`.
- Tiempo total registrado: 8.15 s.
- No hubo abstención.

Respuesta observada:

> El Parque del Retiro abre todos los días a las 6:00 de la mañana [1]. De octubre a marzo su horario es de 6:00 a 22:00, mientras que de abril a septiembre abre de 6:00 a 0:00 [1].

Evidencia:

![Respuesta RAG completa](capturas/03_respuesta_rag_completa.png.png)

Conclusión: OK. El flujo retrieval → contexto → generación → fuentes funciona utilizando el índice preconstruido.

## Abstención ante una pregunta sin evidencia

Comando:

```bash
python main.py --ask "¿Hay elefantes viviendo en libertad en El Retiro?"
```

Resultado:

- Retrieval ejecutado correctamente con `top_k=3`.
- Se recuperaron 3 chunks.
- El modelo generativo utilizado fue `gemini-3.6-flash`.
- El sistema no generó una respuesta afirmativa sin respaldo documental.
- Se activó correctamente el mecanismo de abstención.
- Motivo registrado: `el_modelo_no_vio_evidencia`.
- Tiempo total registrado: 7.67 s.

Respuesta observada:

> No he encontrado esa información en los documentos del Parque del Retiro que tengo disponibles. Puedes consultarlo en la web municipal (madrid.es) o en esmadrid.com.

Evidencia:

![Respuesta de abstención](capturas/04_respuesta_abstencion.png.png)

Conclusión: OK. La abstención generativa funciona cuando el retrieval devuelve chunks, pero el contexto recuperado no contiene evidencia suficiente para responder.

## Respuesta con contexto recuperado

Comando:

```bash
python main.py --ask "¿A qué hora abre el Retiro?" --contexto
```

Resultado:

- Retrieval ejecutado correctamente con `top_k=3`.
- Se recuperaron 3 chunks.
- El modelo utilizado fue `gemini-3.6-flash`.
- La respuesta incluyó referencias numeradas a las fuentes.
- Se mostró el contexto recuperado con:
  - score de relevancia;
  - nombre de la fuente;
  - página;
  - categoría;
  - fragmento textual recuperado.
- El mejor resultado obtuvo un score de 0.773.
- Los dos primeros chunks procedieron de `informacion_practica_guia_visitante_retiro.pdf`.
- El tercer chunk procedió de `flora_fauna__senda_botanica__madrid__v01.pdf`.
- Tiempo total registrado: 8.06 s.

Respuesta observada:

> El Parque del Retiro abre a las 6:00 de la mañana todos los días [1]. Su horario de cierre es a las 22:00 en otoño e invierno (de octubre a marzo) y a las 0:00 en primavera y verano (de abril a septiembre) [1].

Evidencia:

![Respuesta con contexto recuperado](capturas/05_respuesta_contexto_recuperado.png.png)

Conclusión: OK. La opción `--contexto` expone correctamente los chunks utilizados y permite verificar la relación entre retrieval, fuentes y respuesta generada.

## Salida JSON

Comando:

```bash
python main.py --ask "¿A qué hora abre el Retiro?" --json
```

Resultado:

- Retrieval ejecutado correctamente con `top_k=3`.
- Se recuperaron 3 chunks.
- El modelo utilizado fue `gemini-3.6-flash`.
- La salida se serializó correctamente en JSON.
- La estructura incluyó:
  - `respuesta`
  - `fuentes`
  - `citas`
  - `chunks`
  - `abstuvo`
  - `motivo_abstencion`
- `abstuvo` fue `false`.
- `motivo_abstencion` fue `null`.
- Las citas incluyeron metadatos enriquecidos:
  - `titulo`
  - `organismo`
  - `oficial`
  - `etiqueta`
  - `texto`
- El mejor chunk obtuvo un score aproximado de 0.773.
- Los chunks conservaron metadata como:
  - `document_id`
  - `chunk_index`
  - `source`
  - `page`
  - `category`
  - `corpus_group`
  - `embedding_model`
  - `embedding_dimension`
- Tiempo total registrado: 7.12 s.

Observación:

El campo `chunk_id` de las entradas de citas apareció como `null` en esta ejecución, aunque la información de los chunks recuperados conserva el resto de la metadata necesaria para su identificación y trazabilidad.

Evidencias:

![Salida JSON, parte 1](capturas/06_respuesta_json_parte1.png.png)
![Salida JSON, parte 2](capturas/07_respuesta_json_parte2.png.png)

Conclusión: OK con observación. La opción `--json` expone correctamente la respuesta estructurada del RAG y mantiene la metadata de retrieval y el enriquecimiento de citas.

## Aplicación Streamlit

Comando:

```bash
streamlit run app.py
```

Resultado:

- El servidor de Streamlit arrancó correctamente.
- La aplicación quedó disponible en entorno local.
- No se produjeron errores de inicialización.
- La aplicación utilizó el índice configurado mediante `CHROMA_DIR`.

Validaciones realizadas desde la interfaz:

- Pregunta con respuesta respaldada por el corpus.
- Visualización de la respuesta generada.
- Visualización de fuentes/citas.
- Comportamiento de abstención ante una pregunta sin evidencia suficiente.

Evidencia:

![Aplicación Streamlit](capturas/08_streamlit.png.png)

Conclusión: OK. La capa de aplicación Streamlit arranca correctamente y consume el mismo flujo RAG validado previamente desde CLI.

## Suite completa de tests

Comando:

```bash
python -m pytest -q --disable-warnings
```

Resultado:

- Suite completa ejecutada correctamente.
- 338 passed.
- 2 warnings no bloqueantes.
- Tiempo total: 8.12 s.
- No se produjeron fallos.

Durante la suite también se ejecutó la evaluación de retrieval con embeddings deterministas de prueba:

- Recall@3 = 47%
- Recall@5 = 60%
- Recall@5: 9/15 preguntas recuperaron la fuente esperada.

Estos valores corresponden a los tests con embeddings de juguete y no sustituyen la validación realizada anteriormente contra el índice real `index-v1`.

Evidencia:

![Suite completa de tests](capturas/09_suite_completa.png.png)

Conclusión: OK. La suite completa del proyecto pasa en el entorno de validación con 338 tests correctos.

## Resultado final

La validación end-to-end confirma que el sistema integrado puede:

- utilizar un índice Chroma preconstruido sin regenerar embeddings;
- realizar retrieval sobre la colección persistente;
- generar respuestas fundamentadas;
- abstenerse cuando no existe evidencia suficiente;
- exponer el contexto recuperado;
- producir salida estructurada en JSON;
- ejecutarse mediante Streamlit;
- superar la suite completa de tests.

La validación se realizó en una rama independiente para no modificar la lógica productiva ni el índice local original.
