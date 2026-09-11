# Retiro RAG

Sistema RAG sobre el parque de El Retiro. Carga y fragmenta un corpus propio, genera embeddings, construye un índice ChromaDB persistente y responde mostrando fuentes y contexto.

## Estado

Proyecto en desarrollo para el Project Break 1 de RAG Engineering.

## Arquitectura

```text
Documentos → load → chunk → embed → ChromaDB
                                      ↓
Pregunta → retrieve → generate → respond → CLI / Streamlit
```

Documentación:

- [Contrato compartido](docs/contracts/contrato_compartido_mvp_retiro.md)
- [Pipeline](docs/architecture/pipeline_rag.md)
- [Alcance y fuentes](docs/corpus/alcance_y_fuentes.md)
- [Flujo Git](docs/contributing/flujo_git.md)
- [Informe](entregables/informe_decisiones.md)

## Requisitos

- Python 3.10 o superior.
- Git.
- Clave del proveedor elegido.

## Instalación

```bash
git clone https://github.com/adxalex/retiro_rag.git
cd retiro_rag
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

En PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Editar `.env` para añadir la clave. Nunca debe subirse.

## Configuración

Documentar los valores definitivos:

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

## Uso

Mantener estos ejemplos sincronizados con `main.py`.

```bash
python main.py --prepare
python main.py --index
python main.py --query "¿Qué es el Palacio de Cristal?"
python main.py --ask "¿Qué es el Palacio de Cristal?"
streamlit run app.py
```

Los flags pueden variar; el enunciado evalúa el comportamiento.

## Corpus

Cubrirá historia, monumentos, jardines, flora/fauna, arte/cultura, actividades, itinerarios, información práctica y seguridad, usando al menos dos formatos.

Las fuentes, enlaces y fechas se registran en [alcance_y_fuentes.md](docs/corpus/alcance_y_fuentes.md).

## Evaluación

- Entre 8 y 15 preguntas.
- Al menos una fuera del corpus.
- Dos o más valores de K.
- Evidencia, grounding y abstención.
- Dos configuraciones de chunking.

Las preguntas vivirán en `queries/` y los resultados en `entregables/informe_decisiones.md`.

## Equipo

- Alex: corpus e ingesta.
- Alejandra: chunking, embeddings e indexación.
- David: retrieval, generación y aplicación.

```text
PR de Alejandra → revisa David
PR de Alex      → revisa Alejandra
PR de David     → revisa Alex
```

## Seguridad

- No subir `.env` ni claves.
- No versionar `.venv/`.
- No versionar Chroma si pesa demasiado.
- Documentar cómo reconstruir el índice.

## Capturas pendientes

- Respuesta correcta en Streamlit.
- Chunks y fuentes visibles.
- Tabla de métricas.
- Ejemplo de abstención.


### Modelos de Gemini

El proyecto utiliza modelos distintos para generación y embeddings:

- `gemini-2.5-flash` para generar respuestas.
- `gemini-embedding-001` para crear los vectores del corpus y las consultas.

Se utiliza `gemini-embedding-001` porque el pipeline actual procesa los chunks
por lotes y espera recibir un vector independiente por cada texto enviado.
Esto permite mantener una correspondencia directa entre `chunk_id` y vector.

`gemini-embedding-2` se considera una posible evolución multimodal, pero no se
adopta en el MVP porque su tratamiento de múltiples contenidos requiere revisar
la estrategia de lotes y el formato de respuesta.

La disponibilidad se comprueba mediante:

    python -m scripts.validation.validate_gemini_models

El validador consulta los modelos accesibles para la clave configurada y
comprueba que admitan `generateContent` o `embedContent`. No modifica
automáticamente la configuración.

Si se cambia `EMBEDDING_MODEL`, debe regenerarse la colección de ChromaDB,
porque pueden cambiar tanto la dimensión como el espacio semántico de los
vectores.

### Validación de modelos de Gemini

Los modelos disponibles en Gemini pueden cambiar o quedar obsoletos. Para evitar que el pipeline falle por utilizar un identificador retirado, el proyecto incluye un validador que consulta los modelos disponibles para la clave configurada.

El validador comprueba por separado que:

- `LLM_MODEL` admite `generateContent`.
- `EMBEDDING_MODEL` admite `embedContent`.
- La autenticación mediante `GEMINI_API_KEY` funciona.
- Los modelos configurados están disponibles para la cuenta utilizada.

Antes de ejecutarlo, configura las variables en `.env`:

```dotenv
GEMINI_API_KEY=
LLM_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001

Ejecuta la validación desde la raíz del repositorio:

`python -m scripts.validation.validate_gemini_models`

Para mostrar el informe completo y las alternativas disponibles:

`python -m scripts.validation.validate_gemini_models --json`

Si ambos modelos son compatibles, el comando finaliza correctamente. Si falta la clave, un modelo no existe o no admite la operación requerida, muestra un error y termina con código de salida 1.

El validador no modifica automáticamente config.py ni sustituye modelos. La selección debe revisarse manualmente porque cambiar el modelo de embeddings puede alterar la dimensión y el espacio semántico de los vectores.

Cuando se cambie EMBEDDING_MODEL, debe regenerarse la colección persistente de ChromaDB para evitar mezclar embeddings incompatibles.

Para el MVP se utiliza gemini-embedding-001 porque devuelve un vector independiente por cada texto y mantiene la correspondencia entre chunks y vectores esperada por embed.py. Los modelos multimodales más recientes podrán evaluarse posteriormente como una evolución del sistema.

