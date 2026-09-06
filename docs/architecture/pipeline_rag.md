# Arquitectura del pipeline RAG · Retiro RAG

## 1. Objetivo

Construir un sistema RAG modular que permita preparar e indexar el corpus de El Retiro, recuperar contexto relevante y generar respuestas sustentadas exclusivamente en ese contexto. La lógica RAG debe poder utilizarse sin Streamlit.

## 2. Pipeline offline

```text
Documentos → carga y limpieza → chunking → embeddings → ChromaDB persistente
```

- `src/load.py`: carga PDF, Markdown y el tercer formato acordado; genera `LoadedDocument`.
- `src/chunk.py`: normaliza lo necesario para fragmentar y genera `ChunkRecord` trazables.
- `src/embed.py`: transforma el texto de cada chunk en un vector.
- `src/index.py`: guarda ID, texto, vector y metadata en ChromaDB.

Este pipeline se ejecuta para crear o regenerar el índice, no con cada pregunta.

## 3. Pipeline online

```text
Pregunta → retrieval top-k → contexto → prompt → LLM → respuesta y evidencias
```

- `src/retrieve.py`: consulta ChromaDB y genera `RetrievedChunk`.
- `src/generate.py`: construye el prompt, aplica grounding y gestiona la abstención.
- `respond()`: API interna común.
- `main.py`: expone `--query` y `--ask`.
- `app.py`: presenta Parterre mediante Streamlit.

## 4. Fronteras

### Alex · corpus e ingesta

Entrega a Alejandra `LoadedDocument` conformes al contrato. La carga se ocupa de extracción, páginas vacías, texto ilegible y metadata documental.

### Alejandra · chunking e indexación

Recibe `LoadedDocument`, realiza la normalización necesaria para fragmentar, genera IDs estables, embeddings y una colección ChromaDB persistente y regenerable.

### David · retrieval y aplicación

Recibe la colección, recupera chunks, adapta la distancia a `score`, genera la respuesta y expone CLI y Streamlit.

## 5. Configuración centralizada

Declarar en `config.py` o mediante variables de entorno documentadas:

```text
CHUNK_SIZE
CHUNK_OVERLAP
MAX_CHUNKS
TOP_K
EMBEDDING_MODEL
LLM_MODEL
CHROMA_PATH
COLLECTION_NAME
```

`MAX_CHUNKS` limita, si se utiliza, los chunks indexados. `TOP_K` determina cuántos solicita retrieval. Se debe comparar al menos dos valores de K.

## 6. Comandos previstos

```bash
python main.py --prepare
python main.py --index
python main.py --query "¿Qué es el Palacio de Cristal?"
python main.py --ask "¿Qué es el Palacio de Cristal?"
streamlit run app.py
```

Los nombres pueden variar, pero debe distinguirse indexación de consulta.

## 7. Regeneración del índice

Reconstruir la colección si cambia:

- Modelo o dimensión de embeddings.
- `CHUNK_SIZE` o `CHUNK_OVERLAP`.
- Separadores o estrategia de chunking.
- `MAX_CHUNKS` o selección del corpus.
- Contrato de metadata incompatible.

No deben mezclarse vectores de configuraciones diferentes.

## 8. Logging mínimo

Registrar pregunta, `top_k`, número de chunks, tiempo total, modelo de embeddings y modelo de generación. También es recomendable registrar la abstención. Nunca se registran claves.

## 9. Manejo de errores

- Una pregunta vacía produce un error sin llamar al LLM.
- Debe definirse un límite para preguntas excesivamente largas.
- Un corpus vacío no crea silenciosamente un índice inútil.
- Un documento ilegible se identifica con claridad.
- Sin evidencia suficiente, el sistema se abstiene.

## 10. Interfaz

Parterre mostrará chat, respuesta, fuentes, chunks recuperados y una tabla con K, número de chunks, tiempo y modelo. Streamlit llama a `respond()` y no reimplementa la lógica RAG.
