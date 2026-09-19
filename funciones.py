"""
Funciones reutilizables para el análisis de AquaLimpia S. A.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from joblib import dump


def cargar_datos(ruta_archivo):
    """
    Carga el dataset desde Excel y convierte la fecha de registro.
    """
    datos = pd.read_excel(ruta_archivo)
    datos["fecha_registro"] = pd.to_datetime(
        datos["fecha_registro"],
        errors="coerce"
    )
    return datos


def limpiar_datos(datos):
    """
    Elimina duplicados y registros sin variables esenciales.
    """
    datos = datos.copy()
    datos = datos.drop_duplicates()

    columnas_esenciales = [
        "fecha_registro",
        "planta",
        "DBO_entrada_mg_L",
        "DBO_salida_mg_L",
        "cumplimiento_norma",
    ]

    datos = datos.dropna(subset=columnas_esenciales)
    return datos


def calcular_eficiencia_dbo(datos):
    """
    Calcula el porcentaje de remoción de DBO.
    """
    datos = datos.copy()

    datos["eficiencia_DBO_pct"] = np.where(
        datos["DBO_entrada_mg_L"] > 0,
        (
            (
                datos["DBO_entrada_mg_L"]
                - datos["DBO_salida_mg_L"]
            )
            / datos["DBO_entrada_mg_L"]
        ) * 100,
        np.nan,
    )

    return datos


def agregar_estado_cumplimiento(datos):
    """
    Convierte el indicador 0/1 en una etiqueta comprensible.
    """
    datos = datos.copy()

    datos["estado_cumplimiento"] = np.where(
        datos["cumplimiento_norma"] == 1,
        "CUMPLE",
        "NO CUMPLE",
    )

    return datos


def calcular_resumen_por_planta(datos):
    """
    Calcula indicadores operacionales y ambientales por planta.
    """
    resumen = (
        datos.groupby("planta")
        .agg(
            registros=("planta", "size"),
            caudal_promedio_m3_d=("caudal_entrada_m3_d", "mean"),
            dbo_entrada_promedio_mg_L=("DBO_entrada_mg_L", "mean"),
            dbo_salida_promedio_mg_L=("DBO_salida_mg_L", "mean"),
            eficiencia_promedio_pct=("eficiencia_DBO_pct", "mean"),
            energia_promedio_kWh=("energia_aeracion_kWh", "mean"),
            lodos_promedio_kg_d=("lodos_generados_kg_d", "mean"),
            cumplimiento_pct=(
                "cumplimiento_norma",
                lambda x: x.mean() * 100
            ),
        )
        .round(2)
        .reset_index()
    )

    return resumen


def calcular_intervalo_confianza_dbo(datos, confianza=0.95):
    """
    Calcula el intervalo de confianza de la media de DBO de salida
    utilizando SciPy.
    """
    serie = datos["DBO_salida_mg_L"].dropna()

    if len(serie) < 2:
        return (np.nan, np.nan)

    media = serie.mean()
    error = stats.sem(serie)

    intervalo = stats.t.interval(
        confianza,
        df=len(serie) - 1,
        loc=media,
        scale=error,
    )

    return (float(intervalo[0]), float(intervalo[1]))


def guardar_resultados_joblib(resumen, intervalo, ruta_salida):
    """
    Guarda resultados calculados para reutilizarlos posteriormente.
    """
    resultados = {
        "resumen_por_planta": resumen,
        "intervalo_confianza_dbo_salida": intervalo,
    }

    dump(resultados, ruta_salida)


def exportar_resultados(datos, resumen, carpeta_salida="resultados"):
    """
    Exporta archivos para Operaciones, Gestión Ambiental y resumen general.
    """
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(exist_ok=True)

    operaciones = datos[
        [
            "fecha_registro",
            "planta",
            "caudal_entrada_m3_d",
            "DBO_entrada_mg_L",
            "DBO_salida_mg_L",
            "energia_aeracion_kWh",
            "lodos_generados_kg_d",
            "eficiencia_DBO_pct",
        ]
    ].copy()

    ambiental = datos[
        [
            "fecha_registro",
            "planta",
            "DBO_salida_mg_L",
            "cumplimiento_norma",
            "estado_cumplimiento",
        ]
    ].copy()

    operaciones.to_csv(
        carpeta / "operaciones_aqualimpia.csv",
        index=False,
        encoding="utf-8-sig"
    )

    ambiental.to_csv(
        carpeta / "gestion_ambiental_aqualimpia.csv",
        index=False,
        encoding="utf-8-sig"
    )

    resumen.to_csv(
        carpeta / "resumen_por_planta.csv",
        index=False,
        encoding="utf-8-sig"
    )
