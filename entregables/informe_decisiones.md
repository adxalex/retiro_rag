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

## 4. Experimento de retrieval

| Pregunta | K | Mejor fuente/chunk | ¿Tiene sentido? | Ruido |
|---|---:|---|---|---|
| Pendiente | 1 | Pendiente | Pendiente | Pendiente |
| Pendiente | 3 | Pendiente | Pendiente | Pendiente |

### Decisión sobre `TOP_K`

Indicar el valor predeterminado y justificar el equilibrio entre evidencia y ruido.

## 5. Generación y grounding

### Acierto in-corpus

- Pregunta:
- Respuesta:
- Fuentes:
- Evidencia:
- Valoración:

### Abstención fuera de corpus

- Pregunta:
- Resultado esperado:
- Resultado obtenido:
- ¿Se abstuvo correctamente?:

## 6. Evaluación global

- Número de preguntas:
- Preguntas in-corpus:
- Preguntas fuera de corpus:
- Criterio de evidencia:
- Criterio de grounding:
- Criterio de abstención:

## 7. Tres fallos conocidos

### Fallo 1

- Caso:
- Causa probable:
- Impacto:
- Posible mejora:

### Fallo 2

- Caso:
- Causa probable:
- Impacto:
- Posible mejora:

### Fallo 3

- Caso:
- Causa probable:
- Impacto:
- Posible mejora:

## 8. Logging y métricas

Documentar pregunta, K, número de chunks, tiempo, modelos y abstención si aplica.

## 9. Decisiones técnicas

- Modelo de embeddings:
- Modelo de generación:
- ChromaDB y ruta persistente:
- Estrategia de regeneración:
- API interna:
- Justificación:

## 10. Siguientes pasos

Describir mejoras razonables para Agentes y MLOps, diferenciándolas del MVP entregado.
