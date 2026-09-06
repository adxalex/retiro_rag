# Contrato compartido del MVP Â· Retiro RAG

**Estado:** propuesta corregida para aprobaciÃ³n del equipo  
**Alcance:** arquitectura RAG del Project Break, ajustada al MVP del bootcamp  
**Objetivo:** permitir que carga, chunking, embeddings, indexaciÃ³n, retrieval, generaciÃ³n e interfaz se desarrollen de forma autÃ³noma sin romper la integraciÃ³n.

## 1. Principios del contrato

1. Cada etapa recibe y devuelve estructuras conocidas por todo el equipo.
2. Los identificadores deben ser estables y reproducibles con la misma entrada y configuraciÃ³n.
3. Cada chunk debe poder rastrearse hasta su documento, pÃ¡gina y fuente.
4. La clasificaciÃ³n temÃ¡tica del contenido no debe confundirse con el reparto de trabajo.
5. ChromaDB solo recibirÃ¡ metadata plana y sin valores `None`.
6. `respond()` serÃ¡ la interfaz interna comÃºn para CLI, Streamlit y posibles consumidores posteriores.
7. Un cambio en campos, tipos o significado exige actualizar fixtures, productores, consumidores y pruebas de contrato.

## 2. Flujo compartido

```text
PDF / TXT / MD / CSV
        â”‚
        â–¼
     load.py
        â”‚  LoadedDocument
        â–¼
    chunk.py
        â”‚  ChunkRecord
        â–¼
     embed.py
        â”‚  vectores
        â–¼
     index.py â”€â”€â”€â”€â”€â”€â–º ChromaDB
                         â”‚
                         â–¼
                    retrieve.py
                         â”‚  RetrievedChunk[]
                         â–¼
                    generate.py
                         â”‚
                         â–¼
                      respond()
                         â”‚  RAGResponse
                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”
                â–¼        â–¼        â–¼
               CLI   Streamlit  tests
```

## 3. Contrato 1: documento cargado

Intercambio entre `load.py` y `chunk.py`.

```json
{
  "document_id": "mock-folleto-retiro",
  "text": "El parque permanece abierto todos los dÃ­as...",
  "source": "mock_folleto_retiro.pdf",
  "category": "informacion_practica",
  "corpus_group": "itinerarios_informacion_practica_seguridad",
  "page": 1
}
```

### Reglas

- `document_id`: obligatorio, Ãºnico y estable dentro del corpus.
- `text`: obligatorio y no vacÃ­o despuÃ©s de aplicar `strip()`.
- `source`: obligatorio; nombre mostrable del documento original.
- `category`: obligatorio; tema semÃ¡ntico real del contenido.
- `corpus_group`: obligatorio en el MVP; identifica el bloque organizativo del corpus.
- `page`: entero positivo y 1-based cuando el elemento procede de una pÃ¡gina. Si no aplica, la clave se omite completamente.
- Para PDF, `load.py` devuelve preferentemente un `LoadedDocument` por pÃ¡gina. AsÃ­, los chunks pueden heredar una pÃ¡gina inequÃ­voca.

## 4. Contrato 2: chunk

Intercambio entre `chunk.py` y `embed.py` / `index.py`. TambiÃ©n es la estructura serializable en JSONL.

```json
{
  "chunk_id": "mock-folleto-retiro__0000",
  "document_id": "mock-folleto-retiro",
  "text": "El parque permanece abierto todos los dÃ­as...",
  "source": "mock_folleto_retiro.pdf",
  "chunk_index": 0,
  "category": "informacion_practica",
  "corpus_group": "itinerarios_informacion_practica_seguridad",
  "page": 1
}
```

### Reglas

- `chunk_id`: obligatorio y Ãºnico.
- `document_id`: se hereda sin cambios del documento cargado.
- `text`: contiene exclusivamente el texto del fragmento.
- `chunk_index`: entero 0-based, consecutivo dentro del documento completo; no se reinicia en cada pÃ¡gina.
- `source`, `category`, `corpus_group` y `page` se heredan del documento.
- Si `page` no existe en el documento, tampoco se incluye en el chunk.
- Con la misma entrada y la misma configuraciÃ³n de chunking, se deben producir los mismos IDs.

## 5. Identificadores

### `document_id`

Se genera como un slug estable, sin espacios, tildes ni dependencia del orden de carga:

```text
mock_folleto_retiro.pdf â†’ mock-folleto-retiro
```

El corpus o manifiesto debe impedir colisiones entre dos documentos que produzcan el mismo slug. Si existe una colisiÃ³n, deberÃ¡ resolverse antes de indexar aÃ±adiendo un sufijo estable acordado por el equipo.

### `chunk_id`

```python
chunk_id = f"{document_id}__{chunk_index:04d}"
```

Ejemplos:

```text
mock-folleto-retiro__0000
mock-folleto-retiro__0001
mock-folleto-retiro__0002
```

Si cambia el tamaÃ±o, overlap, separadores o estrategia de chunking, se reconstruye la colecciÃ³n. No se mezclan chunks generados con configuraciones incompatibles.

## 6. ClasificaciÃ³n del corpus

Se separan dos conceptos que antes estaban mezclados:

- `category`: describe el tema real y permite filtros semÃ¡nticos Ãºtiles.
- `corpus_group`: conserva los tres bloques utilizados para repartir la curaciÃ³n del corpus.

### Valores de `category`

Vocabulario inicial cerrado para el MVP:

```text
historia
monumentos
jardines
flora_fauna
arte_cultura
actividades
itinerarios
informacion_practica
seguridad
```

### Valores de `corpus_group`

```text
historia_monumentos_jardines
flora_fauna_arte_cultura_actividades
itinerarios_informacion_practica_seguridad
```

Cada documento recibe exactamente un valor de cada vocabulario. La clasificaciÃ³n debe corresponder al contenido, no a la persona que lo haya recopilado.

## 7. Persistencia en ChromaDB

Cada `ChunkRecord` se traduce asÃ­:

- `chunk_id` â†’ ID del registro en ChromaDB.
- `text` â†’ `document` que se convierte en embedding.
- Los demÃ¡s campos â†’ metadata plana.

Ejemplo de metadata:

```json
{
  "document_id": "mock-folleto-retiro",
  "source": "mock_folleto_retiro.pdf",
  "chunk_index": 0,
  "category": "informacion_practica",
  "corpus_group": "itinerarios_informacion_practica_seguridad",
  "page": 1
}
```

Antes de indexar se eliminan las claves cuyo valor sea `None`. La colecciÃ³n utilizarÃ¡ distancia coseno de forma explÃ­cita:

```python
metadata={"hnsw:space": "cosine"}
```

La indexaciÃ³n debe ser repetible. Ejecutarla dos veces con los mismos IDs no puede crear duplicados; se utilizarÃ¡ `upsert` o una reconstrucciÃ³n controlada de la colecciÃ³n.

## 8. Contrato 3: resultado de retrieval

Intercambio entre `retrieve.py` y `generate.py`.

```json
{
  "chunk_id": "mock-folleto-retiro__0000",
  "document_id": "mock-folleto-retiro",
  "text": "El parque permanece abierto todos los dÃ­as...",
  "source": "mock_folleto_retiro.pdf",
  "chunk_index": 0,
  "category": "informacion_practica",
  "corpus_group": "itinerarios_informacion_practica_seguridad",
  "page": 1,
  "score": 0.83
}
```

### Reglas

- Retrieval devuelve el chunk original y aÃ±ade `score`.
- `score` representa relevancia normalizada: cuanto mayor sea, mÃ¡s relevante es el resultado.
- ChromaDB devuelve una distancia. Como la colecciÃ³n se fija en coseno, `retrieve.py` realizarÃ¡ la adaptaciÃ³n:

```python
score = max(0.0, min(1.0, 1.0 - distance))
```

- Esta conversiÃ³n pertenece a `retrieve.py`, no a `chunk.py` ni a `index.py`.
- Los resultados se devuelven ordenados de mayor a menor `score`.
- Si en el futuro se cambia la mÃ©trica de Chroma, tambiÃ©n deberÃ¡ cambiar el adaptador. No se aplicarÃ¡ `1 - distance` de forma genÃ©rica a otras mÃ©tricas.

## 9. Contrato 4: respuesta final

Salida pÃºblica de `respond()` y Ãºnica estructura que necesitan CLI, Streamlit u otro consumidor.

```json
{
  "respuesta": "El parque abre a las 06:00...",
  "fuentes": ["mock_folleto_retiro.pdf"],
  "chunks": [
    {
      "chunk_id": "mock-folleto-retiro__0000",
      "document_id": "mock-folleto-retiro",
      "text": "El parque permanece abierto todos los dÃ­as...",
      "source": "mock_folleto_retiro.pdf",
      "chunk_index": 0,
      "category": "informacion_practica",
      "corpus_group": "itinerarios_informacion_practica_seguridad",
      "page": 1,
      "score": 0.83
    }
  ],
  "abstuvo": false
}
```

Firma interna mÃ­nima:

```python
def respond(question: str, top_k: int = 3) -> RAGResponse:
    ...
```

### Reglas

- Siempre devuelve `respuesta`, `fuentes`, `chunks` y `abstuvo`.
- `fuentes` no contiene duplicados.
- `abstuvo` es `true` cuando el sistema no dispone de contexto suficiente para responder con fundamento.
- CLI y Streamlit llaman a la misma funciÃ³n; no duplican la lÃ³gica RAG.
- El MVP no necesita una API HTTP entre mÃ³dulos para que este contrato sea vÃ¡lido.
- Las mÃ©tricas pueden aÃ±adirse posteriormente como campo opcional o registrarse mediante logging sin romper el contrato mÃ­nimo.

## 10. Reparto simplificado

### Integrante A: Alex Â· corpus e ingesta

- CuraciÃ³n de historia, monumentos y jardines.
- BÃºsqueda y documentaciÃ³n de fuentes.
- ImplementaciÃ³n de `load.py`.
- Lectura de PDF, Markdown y un segundo formato acordado.
- ProducciÃ³n y validaciÃ³n de la metadata mÃ­nima.
- Pruebas de carga.

**Entregable:** los formatos elegidos cargan correctamente y conservan su fuente.

### Integrante B: Alejandra Â· chunking e indexaciÃ³n

- CuraciÃ³n de flora/fauna, arte/cultura y actividades.
- ImplementaciÃ³n de `chunk.py`, `embed.py` e `index.py`.
- Chunking configurable.
- GeneraciÃ³n de embeddings.
- ChromaDB persistente.
- ComparaciÃ³n de dos configuraciones de chunking.
- Pruebas de reindexado.

**Entregable:** el corpus produce chunks trazables y un Ã­ndice regenerable.

### Integrante C: David Â· retrieval y aplicaciÃ³n

- CuraciÃ³n de itinerarios, informaciÃ³n prÃ¡ctica y seguridad.
- ImplementaciÃ³n de `retrieve.py` y `generate.py`.
- API interna `respond()`.
- Estrategia de abstenciÃ³n.
- CLI con `--query` y `--ask`.
- AplicaciÃ³n Parterre en Streamlit.

**Entregable:** una pregunta devuelve respuesta, chunks, fuentes y mÃ©tricas.

### Trabajo compartido

- Crear entre 8 y 15 preguntas de evaluaciÃ³n.
- Comparar al menos dos valores de `top_k`.
- Revisar las pull requests de otros integrantes.
- Acordar y aplicar logging bÃ¡sico.
- Completar el README.
- Redactar el informe de decisiones.
- Preparar la presentaciÃ³n final.

## 11. Responsabilidades detalladas y lÃ­mites

### 11.1. Integrante A: Alex Â· corpus e ingesta

**Rama propuesta:** `feature/corpus-loaders`

#### Entrada de A

- Fuentes documentales seleccionadas y registradas.
- Archivos de historia, monumentos y jardines.
- Vocabulario de metadata aprobado en este contrato.

#### Trabajo de A

1. Buscar y documentar fuentes fiables para sus bloques del corpus.
2. Registrar el origen y el criterio de selecciÃ³n de cada documento.
3. Preparar archivos utilizables en PDF, Markdown y un segundo formato acordado.
4. Implementar `load.py` para los tres formatos.
5. Extraer el texto sin perder la relaciÃ³n con el archivo de origen.
6. Generar `document_id` estable y asignar `source`, `category` y `corpus_group`.
7. En PDF, devolver preferentemente un `LoadedDocument` por pÃ¡gina con `page` 1-based.
8. Omitir `page` cuando el formato no tenga pÃ¡ginas.
9. Validar los campos obligatorios y rechazar documentos vacÃ­os o ilegibles con errores claros.
10. Crear fixtures de `LoadedDocument` con y sin pÃ¡gina para desbloquear a B.
11. AÃ±adir pruebas unitarias, de integraciÃ³n y de contrato para la carga.

#### Salida de A

- Corpus documentado de historia, monumentos y jardines.
- Secuencia de `LoadedDocument` conforme al contrato.
- Fixtures representativos para desarrollar chunking.
- Pruebas que demuestren carga, metadata y trazabilidad.

#### Fuera del alcance de A

- Decidir cÃ³mo se fragmenta el texto o generar `chunk_id`: bloque B.
- Generar embeddings o escribir en ChromaDB: bloque B.
- Recuperar contexto, convertir distancias o generar respuestas: bloque C.
- Implementar CLI o Streamlit: bloque C.

#### Criterios de aceptaciÃ³n de A

1. Los tres formatos elegidos cargan correctamente.
2. Cada salida contiene `document_id`, texto no vacÃ­o, fuente y clasificaciÃ³n vÃ¡lida.
3. Los PDF conservan su pÃ¡gina real conforme a la decisiÃ³n del equipo.
4. Los formatos sin pÃ¡ginas no contienen `page` ni valores `None` destinados a ChromaDB.
5. Los fixtures de A pasan las pruebas de contrato y pueden ser consumidos por `chunk.py`.

### 11.2. Integrante B: Alejandra Â· chunking e indexaciÃ³n

**Rama propuesta:** `feature/chunking-embeddings-index`

#### Entrada de B

Una secuencia de `LoadedDocument` vÃ¡lidos producidos por el bloque A.

#### Trabajo de B

1. Implementar `chunk.py` con la estrategia y configuraciÃ³n acordadas.
2. Conservar toda la metadata recibida y generar `chunk_index` y `chunk_id` estables.
3. Omitir `page` cuando no aplique, sin enviar `None` a ChromaDB.
4. Permitir la serializaciÃ³n de los chunks a JSONL si el repositorio mantiene esa salida intermedia.
5. Implementar `embed.py` con el modelo provisional acordado por el equipo.
6. Configurar la colecciÃ³n ChromaDB con mÃ©trica coseno.
7. Implementar `index.py` y traducir correctamente cada chunk a ID, texto y metadata.
8. Garantizar que reindexar los mismos chunks no genera duplicados.
9. Entregar fixtures pequeÃ±os para que el bloque C pueda desarrollar retrieval sin esperar al corpus definitivo.
10. AÃ±adir pruebas unitarias, de integraciÃ³n y de contrato correspondientes a este bloque.

#### Salida de B

- `ChunkRecord[]` conformes al contrato.
- Embeddings generados con un Ãºnico modelo y configuraciÃ³n conocidos.
- ColecciÃ³n ChromaDB creada e indexada.
- Fixtures y tests que permitan verificar la integraciÃ³n con el bloque C.

#### Fuera del alcance de B

- ExtracciÃ³n y carga de PDF: bloque A.
- CuraciÃ³n o clasificaciÃ³n manual del corpus: responsabilidad de quien prepara cada documento.
- ConversiÃ³n de distancia a `score`: bloque C, dentro de `retrieve.py`.
- GeneraciÃ³n de la respuesta, abstenciÃ³n y fuentes finales: bloque C.
- CLI, Streamlit y API central del proyecto: bloque C o integraciÃ³n conjunta segÃºn el reparto final.
- Extensiones que no formen parte del MVP acordado.

#### Criterios de aceptaciÃ³n de B

1. Recibe los fixtures de `LoadedDocument` acordados con A.
2. Devuelve chunks vÃ¡lidos y trazables conforme a este documento.
3. Compara dos configuraciones de chunking con los mismos documentos y mÃ©tricas acordadas.
4. Genera embeddings reproducibles con el modelo y versiÃ³n fijados.
5. Construye una colecciÃ³n ChromaDB persistente, consultable y sin duplicados.
6. Pasa las pruebas unitarias, de integraciÃ³n y de reindexado del bloque.
7. Entrega a C una rutina de indexaciÃ³n y fixtures suficientes para implementar retrieval.
8. Documenta tamaÃ±o, overlap, separadores, modelo, nombre de colecciÃ³n, ruta persistente y mÃ©trica.

### 11.3. Integrante C: David Â· retrieval y aplicaciÃ³n

**Rama propuesta:** `feature/retrieval-application`

#### Entrada de C

- ColecciÃ³n ChromaDB o rutina de construcciÃ³n proporcionada por B.
- `ChunkRecord` y metadata conformes al contrato.
- Pregunta del usuario y valor de `top_k`.

#### Trabajo de C

1. Implementar `retrieve.py` contra la colecciÃ³n persistente.
2. Recuperar `top_k` resultados conservando IDs, texto, fuente y metadata.
3. Convertir la distancia coseno de ChromaDB al `score` definido por el contrato.
4. Ordenar los resultados de mayor a menor relevancia.
5. Implementar `generate.py` usando Ãºnicamente el contexto recuperado.
6. Definir y probar una regla sencilla y documentada de abstenciÃ³n.
7. Implementar la API interna `respond(question, top_k)`.
8. Devolver siempre `respuesta`, `fuentes`, `chunks` y `abstuvo`.
9. Exponer CLI con `--query` y `--ask` reutilizando `respond()`.
10. Implementar Parterre en Streamlit sin duplicar la lÃ³gica RAG.
11. Mostrar respuesta, fuentes, chunks y mÃ©tricas exigidas por el enunciado.
12. AÃ±adir pruebas unitarias, de integraciÃ³n y de contrato para retrieval y respuesta.

#### Salida de C

- Lista de `RetrievedChunk` conforme al contrato.
- `RAGResponse` consumible sin Streamlit.
- CLI funcional.
- AplicaciÃ³n Parterre funcional en Streamlit.
- Pruebas de retrieval, abstenciÃ³n y presentaciÃ³n de fuentes.

#### Fuera del alcance de C

- Modificar cÃ³mo A interpreta o clasifica los documentos.
- Modificar IDs, texto o metadata ya indexados por B.
- Cambiar el modelo de embeddings sin reconstruir el Ã­ndice y coordinarlo con B.
- Duplicar la lÃ³gica de retrieval o generaciÃ³n dentro de CLI o Streamlit.

#### Criterios de aceptaciÃ³n de C

1. Una pregunta devuelve una estructura `RAGResponse` vÃ¡lida.
2. Cada chunk recuperado conserva su trazabilidad y tiene un `score` coherente.
3. Las fuentes finales se deduplican y corresponden a los chunks utilizados.
4. El sistema se abstiene cuando no dispone de contexto suficiente.
5. CLI y Streamlit consumen la misma funciÃ³n `respond()`.
6. Se muestran las mÃ©tricas mÃ­nimas acordadas por el equipo.
7. Las pruebas funcionan con los fixtures de B y con la colecciÃ³n integrada.

## 12. Pruebas mÃ­nimas por bloque

### Bloque A: carga

- Carga correctamente PDF, Markdown y el tercer formato acordado.
- Rechaza archivos vacÃ­os, ilegibles o con metadata obligatoria ausente.
- Genera `document_id` estable.
- Conserva `source`, `category` y `corpus_group`.
- Informa la pÃ¡gina PDF como entero 1-based y omite la clave cuando no aplica.
- Sus fixtures cumplen el contrato de `LoadedDocument`.

### Bloque B: chunking, embeddings e indexaciÃ³n

#### Chunking

- Rechaza un documento sin `document_id`, sin `source`, sin categorÃ­a o con texto vacÃ­o.
- Produce chunks no vacÃ­os.
- Respeta la configuraciÃ³n de tamaÃ±o y overlap.
- Mantiene `document_id`, `source`, `category`, `corpus_group` y `page`.
- Mantiene `page` ausente cuando no existe en la entrada.
- Produce IDs iguales al repetir la operaciÃ³n con la misma entrada y configuraciÃ³n.
- Mantiene `chunk_index` consecutivo a travÃ©s de las pÃ¡ginas de un mismo PDF.

#### Embeddings

- Produce un vector por chunk.
- Todos los vectores tienen la misma dimensiÃ³n.
- No mezcla modelos o dimensiones dentro de una colecciÃ³n.
- Informa claramente si el texto o el modelo no son vÃ¡lidos.

#### ChromaDB

- Indexa ID, documento y metadata segÃºn el contrato.
- No contiene metadata con valores `None`.
- Indexar dos veces no duplica registros.
- Permite filtrar por `category`, `corpus_group`, `source` y `document_id`.
- Una consulta mÃ­nima devuelve el `chunk_id` y la metadata original.

#### IntegraciÃ³n con C

- C puede abrir o recibir la colecciÃ³n sin conocer detalles internos de chunking.
- El resultado bruto de Chroma conserva todos los campos necesarios para reconstruir un `RetrievedChunk`.
- Un fixture compartido permite probar el flujo antes de disponer del corpus completo.

### Bloque C: retrieval y aplicaciÃ³n

- Recupera como mÃ¡ximo `top_k` resultados y conserva todos los campos contractuales.
- Ordena los resultados de mayor a menor `score`.
- Convierte la distancia coseno sin alterar la metadata del chunk.
- Devuelve una respuesta con fuentes deduplicadas.
- Activa la abstenciÃ³n ante una pregunta sin contexto suficiente.
- `respond()` funciona independientemente de CLI y Streamlit.
- CLI y Streamlit muestran una salida coherente para la misma pregunta.
- Las pruebas pueden ejecutarse con los fixtures compartidos sin depender de todo el corpus real.

## 13. Secuencia inicial de Git y pull requests

Como el contrato es una dependencia comÃºn y todavÃ­a no estÃ¡ en `develop`, se recomienda fusionarlo antes de abrir las ramas tÃ©cnicas.

1. Crear desde `develop` una rama documental, por ejemplo `docs/shared-contract`.
2. AÃ±adir `docs/contracts/contrato_compartido_mvp_retiro.md` y, si corresponde, sus fixtures iniciales.
3. Abrir una PR pequeÃ±a hacia `develop`, revisada por los otros dos integrantes.
4. Corregir y congelar las decisiones contractuales pendientes.
5. Fusionar la PR documental.
6. Cada integrante actualiza su copia local de `develop`.
7. A, B y C crean entonces sus ramas tÃ©cnicas desde el mismo commit de `develop`.

Esto evita que cada rama implemente una versiÃ³n distinta del contrato. Si el equipo decide empezar cÃ³digo antes de fusionar la PR, todos deberÃ¡n basarse temporalmente en el mismo commit documental y asumir una integraciÃ³n mÃ¡s delicada.

## 14. Fixtures compartidos

El repositorio debe conservar al menos:

```text
tests/fixtures/loaded_documents.json
tests/fixtures/chunks.json
tests/fixtures/retrieved_chunks.json
tests/fixtures/rag_response.json
```

Los cuatro archivos actuarÃ¡n como ejemplos ejecutables del contrato. Una modificaciÃ³n de su estructura deberÃ¡ revisarse en equipo antes de fusionarse.

## 15. Decisiones pendientes antes de congelar el contrato

El equipo debe confirmar expresamente:

- [ ] A entrega un `LoadedDocument` por pÃ¡gina para los PDF.
- [ ] Se aceptan `category` y `corpus_group` como campos separados.
- [ ] `chunk_index` es consecutivo dentro del documento completo.
- [ ] La colecciÃ³n ChromaDB utiliza distancia coseno.
- [ ] El modelo y la versiÃ³n de embeddings quedan fijados en configuraciÃ³n.
- [ ] La estrategia ante cambios de chunking serÃ¡ reconstruir la colecciÃ³n.
- [ ] Los cuatro fixtures se aprueban como referencia compartida.

Una vez marcadas estas decisiones, el contrato puede considerarse congelado para el MVP.

