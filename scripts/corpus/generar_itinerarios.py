"""Genera los PDF del bloque itinerarios / información práctica del corpus Retiro RAG.

Diseño pensado para el pipeline load -> chunk:
- Un documento por modalidad (una sola category por documento, según el contrato).
- Sin pies de página numerados ni marcadores de lista (evita ruido en los chunks).
- Sin imágenes: los mapas no se extraen como texto y solo añaden peso.
- Cada sección empieza con su título, su fuente y una ficha de datos clave,
  para que el nombre de la ruta y sus cifras caigan en el mismo chunk.

Uso (desde la raíz del repo):
    pip install reportlab
    python scripts/corpus/generar_itinerarios.py
    python scripts/corpus/generar_itinerarios.py --salida otra/carpeta
"""

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer

# Referencia breve dentro del PDF (URL completa y fecha de consulta en docs/corpus/alcance_y_fuentes.md).
# Mantenerlas cortas: todo lo que se escribe aquí ocupa espacio en los chunks.
FUENTES = {
    "esmadrid_retiro": "esMadrid (Turismo de Madrid), «Parque de El Retiro», actualizado el 19/08/2026.",
    "puertas": "Una Ventana desde Madrid, «El Retiro, sus puertas y entradas»; Rutas Tranquilas "
               "Madrileñas, «Las puertas del Retiro» (2021); Wikipedia; esMadrid.",
    "vgrunning": "VG Running, «Correr en el Parque del Retiro» (2017, actualizado en 2018).",
    "ordenanza": "Ayuntamiento de Madrid (nota de prensa de 23/10/2018) y Madrid 360 (2022), "
                 "Ordenanza de Movilidad Sostenible.",
    "zonaretiro": "Zona Retiro, «Montar en bicicleta por el Retiro» (23/05/2017), CC BY-NC 3.0 ES.",
}


def origen_recorrido_propio() -> str:
    return (
        "Origen: recorrido propuesto por el equipo del proyecto a partir de los lugares que destaca "
        f"{FUENTES['esmadrid_retiro']} El orden de las paradas, la distancia y la duración son "
        "orientativos y no proceden de esa fuente."
    )


def documentos() -> dict[str, list[tuple[str, str]]]:
    return {
        "itinerarios__rutas_a_pie__retiro__v01.pdf": [
            ("h1", "Rutas a pie por el Parque del Retiro (Madrid)"),
            ("p", "Tres recorridos a pie: dos por el interior del parque y uno por el exterior "
                  "que pasa por sus 18 puertas."),

            ("h2", "Ruta a pie: Lo esencial del Retiro"),
            ("src", origen_recorrido_propio()),
            ("ficha", "Ficha de la ruta Lo esencial del Retiro (datos orientativos del equipo). "
                      "Distancia aproximada: 2,5 km. Duración aproximada: 30–35 minutos. Dificultad: "
                      "muy suave. Terreno: llano. Apta para cualquier acompañante."),
            ("p", "Paso 1 de 6 — Entrada por la Puerta de la Independencia, en la Plaza de la "
                  "Independencia, frente a la Puerta de Alcalá."),
            ("p", "Paso 2 de 6 — Seguir el paseo hasta el Estanque Grande, que ofrece barcas de remo "
                  "y la Escuela Municipal de Piragüismo, dirigida a niños y jóvenes de 7 a 17 años "
                  "(según esMadrid)."),
            ("p", "Paso 3 de 6 — Bordear el Estanque hasta el Monumento a Alfonso XII, proyectado por "
                  "el arquitecto José Grases Riera, con un mirador sobre la ciudad (según esMadrid)."),
            ("p", "Paso 4 de 6 — Subir hacia el Paseo de las Estatuas (Paseo de la Argentina), un "
                  "paseo corto flanqueado por esculturas de reyes."),
            ("p", "Paso 5 de 6 — Cruzar hacia el Parterre Francés, donde está el ahuehuete, del que "
                  "se dice que podría tener unos 400 años. Según esMadrid, el árbol más antiguo del "
                  "Retiro es hoy un olivo de 627 años plantado cerca de la Puerta del Ángel Caído."),
            ("p", "Paso 6 de 6 — Salida por la Puerta de Felipe IV, en la calle de Alfonso XII, "
                  "frente al Casón del Buen Retiro."),
            ("p", "Qué se ve en la ruta Lo esencial del Retiro: Estanque Grande, Monumento a "
                  "Alfonso XII, Paseo de las Estatuas y Parterre Francés."),

            ("h2", "Ruta a pie: las 18 puertas del Retiro"),
            ("src", f"Fuentes: {FUENTES['puertas']}"),
            ("ficha", "Ficha de la ruta de las 18 puertas. Recorrido: perimetral, por el exterior "
                      "del parque, en el sentido de las agujas del reloj, con inicio y final en la "
                      "Puerta de la Independencia. Calles que se recorren: Alcalá y O'Donnell "
                      "(norte), avenida de Menéndez Pelayo (este) y calle de Alfonso XII (oeste). "
                      "El perímetro del parque ronda los 4,5 km, según VG Running."),
            ("p", "Clasificación de las 18 puertas. Monumentales (4): España, Felipe IV, Madrid e "
                  "Independencia. Con valor patrimonial (5): Ángel Caído, Dante, Hernani, Granada y "
                  "O'Donnell. Secundarias (9): América Española, Doce de Octubre, Herrero Palacios, "
                  "Lagasca, Mariano de Cavia, Murillo, Niño Jesús, Reina Mercedes y Sainz de Baranda."),
            ("h3", "Puertas del lado norte (calles de Alcalá y O'Donnell)"),
            ("p", "Puerta de la Independencia: en la Plaza de la Independencia, frente a la Puerta "
                  "de Alcalá. La instaló José Urioste en 1885 reutilizando la puerta del jardín del "
                  "Casino de la Reina."),
            ("p", "Puerta de Hernani: en la calle de Alcalá, a la altura de la calle Lagasca; da al "
                  "Paseo del Salón del Estanque. La puerta metálica original de 1888 fue sustituida "
                  "por otra más monumental de Cecilio Rodríguez."),
            ("p", "Puerta de Lagasca: unos 30 metros después de la de Hernani, frente a la calle "
                  "Lagasca. Es secundaria y suele estar cerrada."),
            ("p", "Puerta de Madrid: en el cruce de la calle de Alcalá con la calle de O'Donnell. "
                  "Monumental, obra de José Urioste fechada en 1900, abre al Paseo de Coches o del "
                  "Duque de Fernán Núñez."),
            ("p", "Puerta de O'Donnell: en la esquina de la calle de O'Donnell con la avenida de "
                  "Menéndez Pelayo."),
            ("h3", "Puertas del lado este (avenida de Menéndez Pelayo)"),
            ("p", "Puerta de la América Española: acceso secundario."),
            ("p", "Puerta de la Reina Mercedes: acceso secundario frente a la calle de Ibiza."),
            ("p", "Puerta de Sainz de Baranda: acceso secundario a la altura de la calle del "
                  "Alcalde Sainz de Baranda."),
            ("p", "Puerta del Doce de Octubre: acceso secundario a la altura de la calle del Doce "
                  "de Octubre."),
            ("p", "Puerta de Herrero Palacios: acceso secundario."),
            ("p", "Puerta de Granada: puerta con valor patrimonial."),
            ("p", "Puerta del Niño Jesús: acceso secundario frente al Hospital Infantil "
                  "Universitario Niño Jesús."),
            ("p", "Puerta de Dante: cerca de la plaza de Mariano de Cavia; fue ornamentada y "
                  "dedicada a Dante en 1969."),
            ("h3", "Puertas de los lados sur y oeste (plaza de Mariano de Cavia y calle de Alfonso XII)"),
            ("p", "Puerta de Mariano de Cavia: en la plaza del mismo nombre, con escaleras por el "
                  "desnivel entre la calle y el parque."),
            ("p", "Puerta del Ángel Caído: construida en 2001, es la más cercana a la estación de "
                  "Atocha. Da acceso al Paseo del Duque de Fernán Núñez, que lleva a la Fuente del "
                  "Ángel Caído."),
            ("p", "Puerta de Murillo: en la calle de Alfonso XII, unos 300 metros al norte de la "
                  "Puerta del Ángel Caído."),
            ("p", "Puerta de Felipe IV: en la calle de Alfonso XII, frente al Casón del Buen Retiro, "
                  "y da entrada al Jardín del Parterre. Se levantó en 1680 junto al Paseo del Prado "
                  "y se trasladó a su emplazamiento actual en 1880."),
            ("p", "Puerta de España: en la calle de Alfonso XII, obra de José Urioste. Tras ella, "
                  "unos 400 metros al norte, se cierra la vuelta en la Puerta de la Independencia."),

            ("h2", "Ruta a pie: recorrido completo por el interior"),
            ("src", origen_recorrido_propio()),
            ("ficha", "Ficha del recorrido completo por el interior (datos orientativos del equipo). "
                      "Distancia aproximada: 5–6 km. Duración aproximada: entre 1 hora y 1 hora y 30 "
                      "minutos. Apto para cualquier acompañante."),
            ("p", "Tramo 1 de 6 — Entrada por la Puerta de la Independencia y paseo hasta el Estanque "
                  "Grande."),
            ("p", "Tramo 2 de 6 — Vuelta completa al Estanque Grande, con las barcas de remo y el "
                  "Monumento a Alfonso XII en su orilla."),
            ("p", "Tramo 3 de 6 — Subida por los caminos interiores hasta el Palacio de Cristal, "
                  "pabellón creado para la Exposición de Filipinas de 1887 y uno de los principales "
                  "ejemplos de la arquitectura del hierro en España (según esMadrid)."),
            ("p", "Tramo 4 de 6 — Del Palacio de Cristal al Palacio de Velázquez, ambos salas de "
                  "exposiciones del Museo Reina Sofía, y después a los Jardines de Cecilio Rodríguez, "
                  "jardines clasicistas con aires andaluces (según esMadrid)."),
            ("p", "Tramo 5 de 6 — Paso por la Rosaleda, con su colección de rosas, y continuación por "
                  "el Paseo de Coches."),
            ("p", "Tramo 6 de 6 — Paso por el Parterre Francés y salida por la Puerta de Felipe IV, "
                  "frente al Casón del Buen Retiro."),
            ("p", "Qué se ve en el recorrido completo por el interior: Estanque Grande, Monumento a "
                  "Alfonso XII, Palacio de Cristal, Palacio de Velázquez, Jardines de Cecilio "
                  "Rodríguez, Rosaleda, Paseo de Coches y Parterre Francés."),
        ],

        "itinerarios__circuitos_running__retiro__v01.pdf": [
            ("h1", "Circuitos para correr en el Parque del Retiro (Madrid)"),
            ("src", f"Fuente de todo el documento: {FUENTES['vgrunning']}"),
            ("p", "Según VG Running, el perímetro del parque ronda los 4,5 km y ofrece terrenos "
                  "variados (tierra, césped, asfalto y escaleras), con zonas llanas y cuestas. La "
                  "escuela lo considera especialmente adecuado para series, fartlek y cambios de "
                  "ritmo."),
            ("p", "Nota: los momentos del día que recomienda la fuente se refieren a la iluminación "
                  "de cada circuito y deben entenderse siempre dentro del horario de apertura del "
                  "parque, que este documento no recoge."),

            ("h2", "Circuito de running: perímetro (4,0 km)"),
            ("ficha", "Ficha del circuito de perímetro. Distancia: 4,0 km. Mejor momento: cualquiera, "
                      "de día o de noche, porque está iluminado casi en su totalidad. Terreno: casi "
                      "todo tierra, con un tramo de asfalto en la cuesta del Ángel."),
            ("p", "Es el circuito más clásico para correr en el Retiro. Bordea prácticamente todo el "
                  "parque pegado a la valla, por lo que no tiene pérdida; esa franja junto a la "
                  "valla es también la de más tránsito. El tramo de asfalto coincide con la llamada "
                  "cuesta del Ángel, la más pronunciada del parque, de algo menos de 500 metros."),

            ("h2", "Circuito de running: Parterre (5,2 km)"),
            ("ficha", "Ficha del circuito del Parterre. Distancia: 5,2 km. Mejor momento: con luz "
                      "natural, porque algunos tramos no tienen iluminación artificial. Terreno: casi "
                      "todo tierra; se puede completar entero sin pisar asfalto."),
            ("p", "Es una variante más larga del circuito de perímetro que aprovecha rectas largas para "
                  "sumar kilómetros y pasa por el Parterre Francés. Poder hacerlo entero por tierra "
                  "lo hace recomendable, según la fuente, para corredores con problemas de lesiones."),

            ("h2", "Tramo de running para series cortas (500 m)"),
            ("ficha", "Ficha del tramo de series cortas. Distancia: 500 metros exactos. Ubicación: "
                      "Paseo de Coches, entre el Paseo de Venezuela y el Paseo de Uruguay. Terreno: "
                      "asfalto o franja de tierra paralela. Mejor momento: cualquiera; está iluminado "
                      "y señalizado."),
            ("p", "La recta permite hacer series rápidas de 500 metros o más cortas (200, 300 o "
                  "400 metros). Si la tierra no está en buenas condiciones, se puede correr por el "
                  "asfalto del Paseo de Coches."),

            ("h2", "Tramo de running para series medias y largas (1.000 m)"),
            ("ficha", "Ficha del tramo de series medias y largas. Distancia: 1.000 metros exactos. "
                      "Ubicación: Paseo de Coches, desde el Paseo de Venezuela hasta la glorieta del "
                      "Ángel Caído. Terreno: prácticamente llano, asfalto o tierra. Mejor momento: "
                      "cualquiera; la tierra es especialmente buena por las mañanas."),
            ("p", "Combinando idas y vueltas por este tramo se pueden hacer series de 2.000, 3.000 o "
                  "4.000 metros."),

            ("h2", "Tramo de running para cuestas (475 m)"),
            ("ficha", "Ficha del tramo de cuestas. Distancia: 475 metros, desde la puerta de entrada "
                      "del parque (justo pasadas las barreras de coches) hasta la glorieta del Ángel "
                      "Caído. Terreno: asfalto o laterales de tierra. Mejor momento: cualquiera, de "
                      "mañana, tarde o noche; está iluminado y señalizado."),
            ("p", "La fuente aconseja subir por el asfalto y hacer la recuperación bajando por la "
                  "tierra a ritmo suave, para no sobrecargar. Se puede ajustar la longitud y la "
                  "inclinación de cada cuesta y combinar el trabajo con carrera continua por el "
                  "parque."),
        ],

        "informacion_practica__bicicleta__retiro__v01.pdf": [
            ("h1", "Montar en bicicleta en el Parque del Retiro (Madrid)"),
            ("p", "Normativa municipal sobre bicicletas en parques, carril bici y alquiler en el "
                  "entorno del Retiro."),

            ("h2", "Bicicleta en el Retiro: normativa municipal"),
            ("src", f"Fuentes: {FUENTES['ordenanza']}"),
            ("p", "Según el Ayuntamiento de Madrid, la Ordenanza de Movilidad Sostenible, en vigor "
                  "desde octubre de 2018, solo permite a las bicicletas circular por los parques en "
                  "los itinerarios en los que estén autorizadas, y limita la velocidad a 5 km/h en "
                  "las sendas compartidas con peatones."),
            ("p", "Según Madrid 360, tras la modificación de la ordenanza las bicicletas pueden "
                  "circular por parques y jardines públicos urbanos en caminos de más de 3 metros de "
                  "ancho."),
            ("p", "Antes de circular conviene respetar la señalización del propio parque y comprobar "
                  "el texto vigente de la ordenanza."),

            ("h2", "Bicicleta en el Retiro: carril bici (dato de 2017)"),
            ("src", f"Fuente: {FUENTES['zonaretiro']}"),
            ("p", "En mayo de 2017, Zona Retiro describía un carril bici que recorre todo el lado "
                  "este del parque, desde la calle de O'Donnell hasta la zona del Ángel Caído, "
                  "pasando por el Paseo de Uruguay."),

            ("h2", "Bicicleta en el Retiro: alquiler (dato de 2017)"),
            ("src", f"Fuente: {FUENTES['zonaretiro']}"),
            ("p", "Según el mismo artículo de mayo de 2017, en el entorno del Retiro había empresas "
                  "de alquiler de bicicletas como Biciretiro, Bybike o 27Bikes, con un precio de "
                  "alrededor de 24 euros por día. Es un dato de 2017: la oferta y los precios "
                  "actuales pueden ser distintos."),
        ],
    }


def estilos() -> dict[str, ParagraphStyle]:
    base = ParagraphStyle("base", fontName="Helvetica", fontSize=10.5, leading=15,
                          alignment=TA_LEFT, spaceAfter=6)
    return {
        "h1": ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=17,
                             leading=22, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=13,
                             leading=17, spaceBefore=14, spaceAfter=4),
        "h3": ParagraphStyle("h3", parent=base, fontName="Helvetica-Bold", fontSize=11,
                             leading=15, spaceBefore=8, spaceAfter=3),
        "src": ParagraphStyle("src", parent=base, fontName="Helvetica-Oblique", fontSize=9,
                              leading=12),
        "ficha": ParagraphStyle("ficha", parent=base, fontName="Helvetica-Bold", fontSize=10,
                                leading=14),
        "p": base,
    }


def construir(nombre: str, bloques: list[tuple[str, str]], salida: Path) -> Path:
    est = estilos()
    ruta = salida / nombre
    doc = SimpleDocTemplate(str(ruta), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title=bloques[0][1],
                            author="Equipo Retiro RAG")
    story, grupo = [], []
    for tipo, texto in bloques:
        parrafo = Paragraph(escape(texto), est[tipo])
        if tipo in ("h2", "h3"):
            if grupo:
                story.append(KeepTogether(grupo))
            grupo = [parrafo]
        elif grupo and len(grupo) < 3:
            grupo.append(parrafo)
        else:
            if grupo:
                story.append(KeepTogether(grupo))
                grupo = []
            story.append(parrafo)
    if grupo:
        story.append(KeepTogether(grupo))
    story.append(Spacer(1, 1))
    doc.build(story)
    return ruta


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera los PDF de itinerarios del corpus.")
    parser.add_argument("--salida", default="data/processed/itinerarios_informacion_practica_seguridad")
    args = parser.parse_args()
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, bloques in documentos().items():
        print(f"[OK] {construir(nombre, bloques, salida)}")


if __name__ == "__main__":
    main()
