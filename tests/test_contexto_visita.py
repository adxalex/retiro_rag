"""Tests del saludo contextual: no hacen ninguna llamada real a AEMET."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.contexto_visita import (  # noqa: E402
    estado_del_parque,
    nivel_de_viento,
    obtener_observacion,
    saludo_contextual,
    texto_de_bienvenida,
)


class RespuestaFalsa:
    def __init__(self, datos, error=None):
        self._datos = datos
        self._error = error

    def raise_for_status(self):
        if self._error:
            raise self._error

    def json(self):
        return self._datos


class SesionFalsa:
    """Imita las dos llamadas de AEMET: primero la URL, luego los datos."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.urls = []

    def get(self, url, **_kwargs):
        self.urls.append(url)
        return self.respuestas.pop(0)


def sesion_ok(temperatura=18.4, viento_ms=2.5, racha_ms=5.0, precipitacion=0.0):
    return SesionFalsa([
        RespuestaFalsa({"estado": 200, "datos": "https://opendata.aemet.es/datos/x"}),
        RespuestaFalsa([{
            "ubi": "MADRID, RETIRO",
            "fint": "2026-09-14T10:00:00",
            "ta": temperatura,
            "hr": 55,
            "prec": precipitacion,
            "vv": viento_ms,
            "vmax": racha_ms,
        }]),
    ])


# --- horario del parque ----------------------------------------------------


def test_horario_de_verano_y_de_invierno():
    assert estado_del_parque(datetime(2026, 7, 10, 12))["hora_cierre"] == 24
    assert estado_del_parque(datetime(2026, 1, 10, 12))["hora_cierre"] == 22


def test_parque_cerrado_de_madrugada():
    assert estado_del_parque(datetime(2026, 7, 10, 3))["abierto"] is False


def test_parque_abierto_a_media_tarde():
    assert estado_del_parque(datetime(2026, 7, 10, 18))["abierto"] is True


def test_a_las_23_abierto_en_verano_y_cerrado_en_invierno():
    assert estado_del_parque(datetime(2026, 7, 10, 23))["abierto"] is True
    assert estado_del_parque(datetime(2026, 1, 10, 23))["abierto"] is False


# --- umbrales de viento ----------------------------------------------------


@pytest.mark.parametrize("racha,esperado", [
    (10.0, "verde"),
    (44.9, "verde"),
    (45.0, "naranja"),
    (59.9, "naranja"),
    (60.0, "rojo"),
    (85.0, "rojo"),
    (None, "desconocido"),
])
def test_nivel_segun_los_umbrales_del_protocolo(racha, esperado):
    assert nivel_de_viento(racha)["nivel"] == esperado


def test_el_mensaje_de_alerta_roja_menciona_el_cierre():
    assert "cierra" in nivel_de_viento(70.0)["mensaje"]


def test_sin_viento_fuerte_no_hay_mensaje():
    assert nivel_de_viento(12.0)["mensaje"] is None


# --- llamada a AEMET -------------------------------------------------------


def test_convierte_el_viento_de_ms_a_kmh():
    observacion = obtener_observacion(api_key="clave", sesion=sesion_ok(viento_ms=10.0))
    assert observacion["viento_kmh"] == 36.0


def test_usa_la_estacion_del_retiro():
    sesion = sesion_ok()
    obtener_observacion(api_key="clave", sesion=sesion)
    assert "estacion/3195" in sesion.urls[0]


def test_sin_api_key_devuelve_none():
    assert obtener_observacion(api_key="") is None


def test_un_error_de_red_no_lanza_excepcion():
    sesion = SesionFalsa([RespuestaFalsa(None, error=RuntimeError("timeout"))])
    assert obtener_observacion(api_key="clave", sesion=sesion) is None


def test_respuesta_sin_campo_datos_devuelve_none():
    sesion = SesionFalsa([RespuestaFalsa({"estado": 404})])
    assert obtener_observacion(api_key="clave", sesion=sesion) is None


def test_lista_vacia_devuelve_none():
    sesion = SesionFalsa([
        RespuestaFalsa({"datos": "https://x"}),
        RespuestaFalsa([]),
    ])
    assert obtener_observacion(api_key="clave", sesion=sesion) is None


# --- saludo completo -------------------------------------------------------


def test_saludo_segun_la_hora():
    manana = saludo_contextual(api_key="", momento=datetime(2026, 9, 14, 9))
    tarde = saludo_contextual(api_key="", momento=datetime(2026, 9, 14, 17))
    noche = saludo_contextual(api_key="", momento=datetime(2026, 9, 14, 23))
    assert manana["saludo"].startswith("Buenos dias")
    assert tarde["saludo"].startswith("Buenas tardes")
    assert noche["saludo"].startswith("Buenas noches")


def test_sin_api_key_el_saludo_sigue_funcionando():
    contexto = saludo_contextual(api_key="", momento=datetime(2026, 9, 14, 10))
    assert contexto["observacion"] is None
    assert contexto["saludo"]
    assert contexto["peculiaridades"], "El horario se muestra aunque no haya tiempo."


def test_el_viento_fuerte_aparece_como_peculiaridad_con_su_aviso():
    contexto = saludo_contextual(
        api_key="clave",
        sesion=sesion_ok(racha_ms=18.0),  # 64.8 km/h
        momento=datetime(2026, 9, 14, 10),
    )
    assert contexto["viento"]["nivel"] == "rojo"
    texto = " ".join(contexto["peculiaridades"])
    assert "cierra" in texto
    assert "orientativa" in texto.lower(), "Debe avisar de que no es oficial."


def test_la_lluvia_aparece_como_peculiaridad():
    contexto = saludo_contextual(
        api_key="clave",
        sesion=sesion_ok(precipitacion=1.2),
        momento=datetime(2026, 9, 14, 10),
    )
    assert any("lloviendo" in p for p in contexto["peculiaridades"])


def test_el_parque_cerrado_se_avisa():
    contexto = saludo_contextual(
        api_key="", momento=datetime(2026, 1, 14, 4)
    )
    assert any("cerrado" in p for p in contexto["peculiaridades"])


def test_la_fuente_siempre_acompana_al_dato():
    contexto = saludo_contextual(
        api_key="clave", sesion=sesion_ok(), momento=datetime(2026, 9, 14, 10)
    )
    assert "AEMET" in contexto["fuente"]
    assert "3195" in contexto["fuente"]


def test_texto_de_bienvenida_incluye_temperatura_y_fuente():
    contexto = saludo_contextual(
        api_key="clave", sesion=sesion_ok(temperatura=21.3),
        momento=datetime(2026, 9, 14, 10),
    )
    texto = texto_de_bienvenida(contexto)
    assert "21.3" in texto
    assert "AEMET" in texto


def test_texto_de_bienvenida_sin_datos_lo_declara():
    contexto = saludo_contextual(api_key="", momento=datetime(2026, 9, 14, 10))
    assert "Sin datos meteorologicos" in texto_de_bienvenida(contexto)
