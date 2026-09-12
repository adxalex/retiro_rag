# Alcance y fuentes del corpus · Retiro RAG

## 1. Tema

Asistente RAG sobre el parque de El Retiro. Combina información histórica, cultural, natural y práctica para responder con apoyo en documentos públicos y trazables.

## 2. Debe responder sobre

- Historia, monumentos y jardines.
- Flora, fauna, arte y cultura.
- Actividades y deporte.
- Itinerarios e información práctica.
- Normas, seguridad y emergencias.

## 3. Fuera de alcance

- Asuntos ajenos a El Retiro.
- Información no sustentada por el corpus.
- Datos actuales presentados como vigentes sin una fuente vigente.
- Sustitución de instrucciones oficiales de seguridad.
- Datos personales o fuentes obtenidas mediante scraping agresivo.

Sin evidencia suficiente, el asistente indicará que la información no está en los documentos disponibles.

## 4. Formatos y volumen

- PDF.
- Markdown.
- Un tercer formato acordado, preferiblemente CSV si aporta información estructurada.

El corpus debe contener al menos dos formatos. Como orientación, se seleccionarán entre 5 y 20 documentos relevantes, evitando redundancias.

## 5. Reparto

- Alex: historia, monumentos y jardines.
- Alejandra: flora/fauna, arte/cultura y actividades.
- David: itinerarios, información práctica y seguridad.

## 6. Ficha de cada fuente

```markdown
### Título

- Institución o autor: Ayuntamiento de Madrid — Patrimonio y Paisaje, iniciativa "Pasea Madrid".
- URL: https://patrimonioypaisaje.madrid.es/FWProjects/monumenta/contenidos/ficheros/folleto_Jardines_Retiro_ESP.pdf
- Fecha de consulta o descarga: 12/09/2026.
- Formato: PDF (folleto oficial de turismo).
- Nombre del archivo local: 'retiro_jardines_monumentos_folleto.pdf'
- Categoría: monumentos
- `corpus_group`: `historia_monumentos_jardines`
- Motivo de inclusión: recorrido oficial con 16 puntos de interés del parque (Palacio de Cristal, Palacio de Velázquez, Fuente del Ángel Caído, La Rosaleda, entre otros) y contexto histórico de origen del parque como Real Sitio del Buen Retiro, incluida su declaración UNESCO en 2021.
- Fecha de vigencia: contenido institucional sin fecha de actualización visible en el documento; información histórica estable.
- Observaciones de calidad: es un folleto breve (1-2 páginas) orientado a visitantes, con duración estimada de recorrido, mapa y accesibilidad. No profundiza en detalles históricos extensos de cada monumento, es un resumen de itinerario.
```

## 7. Inventario

### Jardines y monumentos del Parque del Retiro

| Archivo local | Categoría   | Formato | Fuente    | Descarga  | Responsable | Estado      |
| ------------- | ----------- | ------- | --------- | --------- | ----------- | ----------- |
| retiro_jardines_monumentos_folleto.pdf | monumentos | PDF | Ayuntamiento de Madrid (Patrimonio y Paisaje) | 12/09/2026 | Alex | Por revisar |
| Pendiente     | flora_fauna | PDF     | Pendiente | Pendiente | Alejandra   | Por revisar |
| Pendiente     | itinerarios | MD/CSV  | Pendiente | Pendiente | David       | Por revisar |

Estados: `candidato`, `por revisar`, `aceptado` y `excluido`.

## 8. Criterios de aceptación

Una fuente entra en el corpus cuando:

1. Su procedencia y URL están documentadas.
2. Tiene relación directa con el alcance.
3. Su contenido puede cargarse correctamente.
4. No duplica innecesariamente otra fuente.
5. Su vigencia se entiende.
6. No contiene secretos ni datos personales innecesarios.
7. Puede utilizarse con fines educativos.

Si se excluye, se registra el motivo.

## 9. Cinco preguntas iniciales

1. ¿Qué función tuvo históricamente el parque de El Retiro?
2. ¿Qué es el Palacio de Cristal?
3. ¿Qué interés tiene la Rosaleda?
4. ¿Qué actividades se pueden realizar en el parque?
5. ¿Qué accesos o normas debe conocer una persona visitante?

Las preguntas formales de evaluación vivirán en `queries/` e incluirán al menos una fuera del corpus.

## 10. Declaración de uso

El equipo utilizará información pública con finalidad educativa. Las claves se guardarán únicamente en `.env`, fuera del control de versiones.
