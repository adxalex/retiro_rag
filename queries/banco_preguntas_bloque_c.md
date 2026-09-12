# Banco de preguntas de evaluación · bloque C (retrieval y generación)

25 preguntas probadas contra el corpus de `develop` (25 documentos, 95 chunks) con
`retrieve.py` y `top_k=3`.

`Esperado` indica el comportamiento correcto del sistema:

- **Responde**: el corpus contiene la respuesta y debe citar la fuente indicada.
- **Abstención**: el corpus no contiene la respuesta; el sistema debe decir que no
  dispone de esa información en lugar de inventarla.
- **Parcial**: el corpus responde solo una parte; el sistema debe responder lo que
  sabe y declarar lo que no.

| # | Pregunta | Esperado | Fuente esperada | Respuesta correcta / nota |
| --- | --- | --- | --- | --- |
| 1 | ¿En qué siglo se construyó originalmente el Real Sitio del Buen Retiro? | Responde | retiro_jardines.md, retiro_historia.md | Siglo XVII; las obras empezaron en 1630 |
| 2 | ¿Qué rey impulsó la creación del Retiro como espacio palaciego y de recreo? | Responde | retiro_historia.md | Felipe IV, con el impulso del Conde-Duque de Olivares |
| 3 | ¿Cuál es la entrada más utilizada para iniciar un recorrido turístico? | Abstención | — | El corpus no dice cuál es la más utilizada. La Puerta de la Independencia aparece como inicio de una ruta propuesta por el equipo, que no es lo mismo |
| 4 | ¿Qué monumento preside el Estanque Grande? | Responde | retiro_monumentos_jardines.csv | Monumento a Alfonso XII, o Monumento a la Patria Española |
| 5 | ¿Qué edificio se utiliza para exposiciones del Museo Reina Sofía? | Responde | informacion_practica_guia_visitante_retiro.pdf | Palacio de Velázquez y Palacio de Cristal; el de Cristal está cerrado por obras en 2026 |
| 6 | ¿Qué característica arquitectónica distingue al Palacio de Cristal? | Responde | retiro_monumentos_jardines.csv | Estructura de hierro y cristal; ejemplo destacado de la arquitectura del hierro en España |
| 7 | ¿Qué función tenía originalmente la Casa de Vacas? | Abstención | — | El corpus solo la nombra como centro cultural actual; no recoge su uso original |
| 8 | ¿Qué fauna es más habitual en el Estanque Grande? | Abstención | — | El corpus no describe la fauna del estanque. Pregunta para el bloque de flora y fauna |
| 9 | ¿Qué jardín es famoso por sus parterres geométricos y estilo francés? | Responde | informacion_practica_guia_visitante_retiro.pdf, itinerarios_pie_retiro_.pdf | El Parterre Francés |
| 10 | ¿Qué árbol centenario está catalogado como uno de los más antiguos de Madrid? | Responde | informacion_practica_guia_visitante_retiro.pdf | El ahuehuete del Parterre Francés (unos 400 años); el más antiguo del Retiro es hoy un olivo de 627 años |
| 11 | ¿Qué evento deportivo multitudinario atraviesa el Retiro cada año? | Abstención | — | El corpus solo recoge la Feria del Libro y los fuegos de San Isidro |
| 12 | ¿Qué norma de seguridad se recomienda cerca del Estanque? | Abstención | — | El corpus no recoge normas específicas del estanque. Solo hay normas generales de alertas |
| 13 | ¿Qué edificio fue utilizado como cuartel durante la Guerra de la Independencia? | Parcial | retiro_historia.md | El recinto del Retiro fue usado como fortaleza y acuartelamiento por los franceses; no se nombra un edificio concreto |
| 14 | ¿Qué espacio es conocido por lectura y cuentacuentos? | Abstención | — | El corpus nombra la Biblioteca Eugenio Trías y el Teatro de Títeres, pero no menciona cuentacuentos |
| 15 | ¿Qué ruta incluye el Palacio de Cristal, el Estanque y el Parterre? | Responde | itinerarios_pie_retiro_.pdf | El recorrido completo por el interior (5–6 km, 1 h–1 h 30) |
| 16 | ¿Qué institución oficial respalda la información turística del Retiro? | Responde | informacion_practica_guia_visitante_retiro.pdf | esMadrid, web oficial de Turismo del Ayuntamiento de Madrid |
| 17 | ¿Qué horario tiene el parque en verano? | Responde | informacion_practica_guia_visitante_retiro.pdf | De abril a septiembre, de 6:00 a 0:00 |
| 18 | ¿Qué zona es de especial interés para fotógrafos por su luz natural? | Abstención | — | El corpus no clasifica zonas por luz; solo recoge lugares destacados |
| 19 | ¿Qué elemento está dedicado a Alfonso XII? | Responde | retiro_monumentos_jardines.csv | El conjunto escultórico junto al Estanque Grande, con mirador |
| 20 | ¿Qué edificio se caracteriza por su estilo neomudéjar? | Abstención | — | El término no aparece en el corpus. El Palacio de Velázquez suele describirse así, pero el corpus no lo dice |
| 21 | ¿Qué punto es ideal para iniciar la ruta «Lo esencial»? | Responde | itinerarios_pie_retiro_.pdf | La Puerta de la Independencia, frente a la Puerta de Alcalá |
| 22 | ¿Qué protocolo seguir si un visitante se pierde? | Abstención | — | El corpus no recoge protocolo para personas perdidas. Solo el de alertas meteorológicas |
| 23 | Estoy en el Ángel Caído y necesito un baño, ¿cuál es el más cercano? | Parcial | informacion_practica_guia_visitante_retiro.pdf | Hay un aseo subterráneo junto al Ángel Caído, según una fuente no oficial de 2025. No hay horarios ni confirmación de que esté abierto |
| 24 | Alguien dice haber visto una estatua moverse, ¿qué harías? | Abstención | — | Fuera del alcance del sistema. No debe inventar leyendas ni confirmar el hecho |
| 25 | Hay alerta naranja y estoy en el lago, ¿qué hago? | Responde | seguridad_protocolo_alertas_retiro.pdf | Con alerta naranja se restringen áreas infantiles, deportivas, de mayores, área canina, Cecilio Rodríguez y Herrero Palacios, y se suspenden los eventos al aire libre. El estanque no está entre las zonas restringidas |

## Resumen

- Responde: 11 preguntas (1, 2, 4, 5, 6, 9, 10, 15, 16, 17, 19, 21, 25)
- Parcial: 2 preguntas (13, 23)
- Abstención: 10 preguntas (3, 7, 8, 11, 12, 14, 18, 20, 22, 24)

Distribución por categoría: historia, monumentos, jardines, itinerarios,
información práctica y seguridad. Incluye preguntas conversacionales (23, 25) y
una fuera de alcance (24).

## Cómo ejecutarlo

    python scripts/validation/eval_preguntas.py            # top_k=3
    python scripts/validation/eval_preguntas.py --top-k 5  # comparación de top_k

El script usa el índice real de ChromaDB. Para probar sin clave de Gemini ni
índice, usa `--simulado`, que construye un índice temporal con embeddings
deterministas de juguete.
