# Retiro RAG

Sistema RAG sobre el Parque de El Retiro. El proyecto carga y fragmenta un corpus documental curado, genera embeddings con Gemini, construye un índice persistente en ChromaDB y recupera contexto trazable para responder preguntas con fuentes.

## Estado del proyecto

El proyecto se encuentra en fase de integración.

Actualmente están implementados:

- Carga de documentos PDF, Markdown y CSV.
- Validación del contrato documental.
- Chunking configurable y trazable.
- Generación de embeddings por lotes.
- Indexación persistente en ChromaDB.
- Retrieval con distancia coseno, filtros de metadata y `top_k`.
- Autenticación compartida para Gemini.
- Validación de disponibilidad de modelos.
- Orquestación del pipeline offline.
- Pruebas unitarias y de integración.
- Experimento con dos configuraciones de chunking.

Continúan pendientes o en desarrollo:

- Generación final de respuestas.
- Abstención calibrada con resultados reales.
- Integración mediante `respond()`.
- Interfaz de Streamlit.
- Evaluación definitiva con el corpus completo y embeddings reales.

## Arquitectura

```text
Pipeline offline

Documentos
    → load
    → chunk
    → embed
    → index
    → ChromaDB

Pipeline online

Pregunta
    → embed_query
    → retrieve
    → generate
    → respond
    → CLI / Streamlit
```

El pipeline offline se coordina desde `src/pipeline.py`. La interfaz de terminal para construir el índice está en `scripts/index_corpus.py`.

## Estructura principal

```text
data/
└── processed/
    ├── historia_monumentos_jardines/
    ├── flora_fauna/
    ├── flora_fauna_arte_cultura_actividades/
    └── itinerarios_informacion_practica_seguridad/

docs/
├── architecture/
├── contracts/
├── contributing/
├── corpus/
└── evaluation/

entregables/
├── experimentos/
└── informe_decisiones.md

queries/
├── banco_preguntas_bloque_b.md
└── banco_preguntas_bloque_c.md

scripts/
├── corpus/
├── etl/
├── experiments/
├── validation/
└── index_corpus.py

src/
├── load.py
├── chunk.py
├── embed.py
├── index.py
├── pipeline.py
├── retrieve.py
├── generate.py
└── gemini_auth.py

tests/
├── fixtures/
├── test_chunk.py
├── test_embed.py
├── test_index.py
├── test_pipeline.py
├── test_retrieve.py
└── test_block_b_pipeline.py
```

## Documentación

- [Contrato compartido](docs/contracts/contrato_compartido_mvp_retiro.md)
- [Arquitectura del pipeline](docs/architecture/pipeline_rag.md)
- [Alcance y fuentes](docs/corpus/alcance_y_fuentes.md)
- [Flujo de trabajo con Git](docs/contributing/flujo_git.md)
- [Informe de decisiones](entregables/informe_decisiones.md)

## Requisitos

- Python 3.10 o superior.
- Git.
- Una clave válida para la API de Gemini.
- Dependencias incluidas en `requirements.txt`.
- `pytest` y dependencias de desarrollo para ejecutar las pruebas.

## Instalación

```bash
git clone https://github.com/adxalex/retiro_rag.git
cd retiro_rag

python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para instalar también las dependencias de testing:

```bash
python -m pip install -r requirements-dev.txt
```

### Activación del entorno

En Linux o macOS:

```bash
source .venv/bin/activate
```

En PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Variables de entorno

Copia `.env.example` como `.env` y añade una clave válida:

```dotenv
GEMINI_API_KEY=
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
```

También se admite `GOOGLE_API_KEY` como nombre alternativo para la clave.

El archivo `.env` contiene información sensible y no debe subirse al repositorio.

## Configuración

La configuración común se encuentra en `config.py`.

Valores principales:

```text
DATA_DIR=data
CHROMA_DIR=chroma
COLLECTION_NAME=retiro_madrid

CHUNK_SIZE=500
CHUNK_OVERLAP=50

EMBED_BATCH_SIZE=32
INDEX_BATCH_SIZE=100
HNSW_SPACE=cosine

TOP_K=3
MAX_CHUNKS=None

LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
```

`MAX_CHUNKS=None` indica que el pipeline normal procesa el corpus completo. La limitación de chunks queda reservada para experimentos y no se utiliza para construir el índice definitivo.

## Modelos de Gemini

El proyecto utiliza modelos diferentes para generación y embeddings:

- `gemini-2.5-flash`: generación de respuestas.
- `gemini-embedding-001`: embeddings de documentos y consultas.

`gemini-embedding-001` genera un vector independiente por cada texto y mantiene la correspondencia directa entre `chunk_id` y vector esperada por el pipeline.

Antes de utilizar los modelos, se recomienda validar su disponibilidad:

```bash
python -m scripts.validation.validate_gemini_models
```

Para mostrar el informe completo:

```bash
python -m scripts.validation.validate_gemini_models --json
```

El validador comprueba:

- La autenticación.
- Que el modelo generativo admita `generateContent`.
- Que el modelo de embeddings admita `embedContent`.
- Qué alternativas están disponibles para cada operación.

El validador no modifica automáticamente `config.py`. Si cambia el modelo de embeddings, debe reconstruirse la colección de Chroma porque pueden cambiar la dimensión y el espacio semántico de los vectores.

## Corpus

El corpus cubre:

- Historia.
- Monumentos.
- Jardines.
- Flora y fauna.
- Arbolado.
- Arte y cultura.
- Actividades.
- Itinerarios.
- Información práctica.
- Seguridad.

Los documentos destinados al RAG se encuentran en `data/processed/`. Las fuentes originales, archivos de trabajo y documentos descartados pueden mantenerse fuera del corpus indexable.

Los bancos de preguntas se almacenan en `queries/`; no forman parte del corpus documental.

### Contrato documental

Cada documento cargado debe conservar como mínimo:

```text
document_id
text
source
category
corpus_group
```

Los PDF incorporan además `page` cuando la página contiene texto extraíble.

Todas las páginas de un mismo PDF conservan el mismo `document_id`. La página se diferencia mediante `page`.

Los chunks incorporan:

```text
chunk_id
document_id
text
source
chunk_index
category
corpus_group
page, cuando existe
```

El patrón contractual del identificador de chunk es:

```text
document-id__0000
document-id__0001
```

El doble guion bajo es obligatorio para separar el identificador del documento y el índice del chunk. No es obligatorio utilizarlo en los nombres originales de los archivos.

## Validación segura del corpus

Antes de llamar a Gemini puede ejecutarse el pipeline en modo `dry-run`:

```bash
python -m scripts.index_corpus --dry-run
```

Este modo realiza:

```text
load → chunk → resumen
```

No genera embeddings y no modifica ChromaDB.

Para obtener el resumen como JSON:

```bash
python -m scripts.index_corpus --dry-run --json
```

En la fotografía actual del corpus, el resultado esperado es aproximadamente:

```text
254 registros cargados
16 fuentes diferentes
1171 chunks
```

Estas cifras deben actualizarse cuando se incorporen nuevos documentos.

## Construcción del índice

Para generar los embeddings de todo el corpus y reconstruir la colección persistente:

```bash
python -m scripts.index_corpus
```

La reconstrucción completa es el comportamiento predeterminado. Evita conservar chunks correspondientes a documentos eliminados o versiones anteriores del corpus.

Para realizar un `upsert` sin eliminar previamente la colección:

```bash
python -m scripts.index_corpus --keep-existing
```

`--keep-existing` puede utilizarse durante el desarrollo, pero no sustituye a la reconstrucción final. Un `upsert` actualiza identificadores presentes, pero no elimina registros antiguos que hayan desaparecido del corpus.

La colección debe reconstruirse cuando cambie cualquiera de estos elementos:

- Corpus.
- Estrategia de chunking.
- `CHUNK_SIZE`.
- `CHUNK_OVERLAP`.
- Modelo de embeddings.
- Dimensión de los vectores.
- Métrica de ChromaDB.
- Convención de `chunk_id`.

## Retrieval

Una vez construida la colección, `src/retrieve.py`:

1. Valida la consulta.
2. Genera su embedding con `RETRIEVAL_QUERY`.
3. Consulta ChromaDB.
4. Recupera los `top_k` chunks.
5. Convierte la distancia coseno en un `score`.
6. Ordena los resultados de mayor a menor relevancia.
7. Conserva la metadata utilizada para trazabilidad y citas.

La conversión aplicada es:

```text
score = max(0, min(1, 1 - distance))
```

El retrieval admite filtros opcionales de metadata mediante `where`.

## Evaluación

Los bancos de preguntas se encuentran en `queries/`.

La evaluación debe incluir:

- Preguntas respondibles.
- Preguntas parcialmente respondibles.
- Preguntas fuera del corpus.
- Comprobación de fuentes esperadas.
- Comparación de al menos dos valores de `top_k`.
- Abstención.
- Grounding.
- Citas.
- Análisis de fallos.

El banco de retrieval puede ejecutarse con un índice simulado:

```bash
python -m scripts.validation.eval_preguntas --simulado --top-k 3
python -m scripts.validation.eval_preguntas --simulado --top-k 5
```

Con el corpus ampliado, los embeddings simulados han obtenido provisionalmente:

```text
Recall@3 = 47 %
Recall@5 = 60 %
```

Estas cifras no representan la calidad definitiva del sistema. El índice simulado utiliza vectores deterministas de juguete y sirve únicamente para validar el flujo.

La evaluación final debe repetirse con:

- Corpus definitivo.
- `gemini-embedding-001`.
- Colección Chroma completa.
- `top_k=3`.
- `top_k=5`.

## Experimento de chunking

El proyecto compara dos configuraciones:

```text
500 caracteres con overlap 50
800 caracteres con overlap 100
```

Para reproducir el experimento:

```bash
python -m scripts.experiments.compare_chunking \
  --input tests/fixtures/loaded_documents_chunking_experiment.json \
  --config 500:50 \
  --config 800:100 \
  --output entregables/experimentos/comparacion_chunking.json
```

En PowerShell:

```powershell
python -m scripts.experiments.compare_chunking `
  --input "tests\fixtures\loaded_documents_chunking_experiment.json" `
  --config "500:50" `
  --config "800:100" `
  --output "entregables\experimentos\comparacion_chunking.json"
```

Resultado del fixture representativo:

| Configuración | Chunks | Longitud media | Mediana | Máximo |
| ------------- | -----: | -------------: | ------: | -----: |
| 500:50        |     21 |         398,90 |     450 |    491 |
| 800:100       |     13 |         667,38 |     723 |    777 |

La configuración `500:50` produce fragmentos más pequeños y numerosos. La configuración `800:100` reduce el número de fragmentos y conserva contextos más extensos.

Este experimento no limita el corpus utilizado en la indexación final.

## Pruebas

Para ejecutar toda la batería:

```bash
python -m pytest -q
```

Para mostrar cada prueba:

```bash
python -m pytest -v
```

La batería actual incluye pruebas de:

- Contrato de documentos y chunks.
- Configuración de chunking.
- Trazabilidad.
- Determinismo.
- Procesamiento de embeddings por lotes.
- Dimensión y validez de vectores.
- Conservación de metadata.
- Sanitización para ChromaDB.
- Idempotencia.
- Reconstrucción de la colección.
- Orquestación del pipeline.
- Retrieval.
- Filtros.
- Conversión de distancia a score.
- Evaluación simulada.

La rama de integración ha superado:

```text
208 tests
```

Los tests unitarios utilizan dobles, clientes simulados o colecciones temporales. No consumen la API salvo en los smoke tests explícitamente diseñados para ello.

## Validaciones auxiliares

### Validación de modelos

```bash
python -m scripts.validation.validate_gemini_models
```

### Smoke test real de embeddings

```bash
python -m scripts.validation.smoke_test_embeddings --count 35
```

Este comando consume la API y requiere una clave válida.

### Validación del corpus

```bash
python -m scripts.validation.validate_corpus
```

### Cobertura documental del retrieval

```bash
python -m scripts.validation.retrieval_coverage
```

La cobertura documental es una herramienta diagnóstica. Que un documento no aparezca en una pregunta no implica necesariamente que esté mal indexado: también puede indicar que el banco no contiene una pregunta que lo cubra.

## Limitaciones conocidas

- Algunos PDF generan el aviso recuperable `incorrect startxref pointer`.
- Esos PDF continúan siendo legibles y sus páginas contienen texto extraíble.
- Los PDF sin texto en una página omiten esa página durante la carga.
- El bloque de flora, fauna y arbolado representa una parte grande del corpus.
- La guía de aves contiene información general de la Comunidad de Madrid y no constituye un inventario específico del Retiro.
- El recall actual procede de embeddings simulados.
- La abstención definitiva requiere calibración con scores reales.
- `generate.py`, `respond()` y Streamlit continúan en desarrollo.
- El corpus puede cambiar antes de la indexación definitiva.

## Seguridad

- No subir `.env`.
- No incluir claves en código, logs o capturas.
- No versionar `.venv/`.
- No versionar `__pycache__/`.
- No versionar `.pytest_cache/`.
- No compartir la colección Chroma si contiene datos locales o tiene un tamaño excesivo.
- Documentar siempre cómo reconstruir el índice.
- Validar manualmente cualquier cambio de modelo.

## Flujo recomendado antes de la entrega

1. Integrar el corpus definitivo.
2. Validar el manifiesto.
3. Ejecutar el modo `dry-run`.
4. Ejecutar todas las pruebas.
5. Validar los modelos Gemini.
6. Reconstruir la colección completa.
7. Evaluar retrieval con embeddings reales.
8. Comparar `top_k=3` y `top_k=5`.
9. Calibrar la abstención.
10. Comprobar fuentes y citas.
11. Ejecutar el smoke test completo.
12. Actualizar el informe de decisiones.
13. Preparar las capturas de la aplicación.

## Reparto técnico

- Bloque A: corpus e ingesta.
- Bloque B: chunking, embeddings, indexación y pipeline offline.
- Bloque C: retrieval, generación, respuesta y aplicación.

Las modificaciones que afecten a la interfaz entre bloques deben revisarse contra el contrato compartido.

## Capturas pendientes

- Construcción correcta del índice.
- Consulta con recuperación relevante.
- Respuesta final con fuentes.
- Chunks y metadata recuperados.
- Comparación de valores de `top_k`.
- Ejemplo de abstención.
- Aplicación Streamlit.
