# RAG Parque de El Retiro

Sistema RAG end-to-end (Project Break 1 - RAG Engineering) sobre el Parque de El Retiro (Madrid): normativa de uso, folletos/guias y datos abiertos de parques y puntos de interes.

## Equipo

- Alex - Parte 3 (generacion, evaluacion, API interna)
- Alejandra - Parte 2 (indexacion y retrieval)
- David - Parte 1 (tema y corpus)

## Tema del corpus

TODO (David): tema en 2-3 lineas, alcance (que preguntas si/no responde el asistente).

## Fuentes del corpus

TODO (David): tabla de fuentes con enlace y fecha de descarga, formatos (>=2).

## Instalacion

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # editar la API key del proveedor elegido
```

## Como indexar el corpus

```bash
python main.py --index
```

## Como preguntar

```bash
python main.py --query "pregunta de ejemplo"   # solo retrieval
python main.py --ask "pregunta de ejemplo"     # respuesta RAG completa
```

## Streamlit

```bash
streamlit run app.py
```

## Preguntas de ejemplo

TODO (David, Parte 1): 5 preguntas de ejemplo del dominio.

## Capturas

TODO (Parte 4): capturas de la app de Streamlit.
