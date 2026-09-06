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
