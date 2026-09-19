import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
DATASET = "dataset_set_A_aguas_residuales.xlsx"
OUTPUT_DIR = Path("outputs")
GRAFICOS_DIR = Path("graficos")

OUTPUT_DIR.mkdir(exist_ok=True)
GRAFICOS_DIR.mkdir(exist_ok=True)


def cargar_datos(ruta):
    """Carga el archivo Excel y valida columnas mínimas."""
    df = pd.read_excel(ruta)

    columnas_requeridas = [
        "fecha_registro",
        "planta",
        "caudal_entrada_m3_d",
        "DBO_entrada_mg_L",
        "energia_aeracion_kWh",
        "lodos_generados_kg_d",
        "DBO_salida_mg_L",
        "cumplimiento_norma",
    ]

    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")

    return df


def limpiar_y_preparar(df):
    """Limpia registros y crea indicadores derivados."""
    df = df.copy()

    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], errors="coerce")
    df = df.drop_duplicates()

    columnas_numericas = [
        "caudal_entrada_m3_d",
        "DBO_entrada_mg_L",
        "energia_aeracion_kWh",
        "lodos_generados_kg_d",
        "DBO_salida_mg_L",
        "cumplimiento_norma",
    ]

    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Se eliminan solo registros que impiden los cálculos principales.
    df = df.dropna(
        subset=[
            "fecha_registro",
            "planta",
            "DBO_entrada_mg_L",
            "DBO_salida_mg_L",
            "cumplimiento_norma",
        ]
    )

    # Eficiencia de remoción de DBO
    df["eficiencia_DBO_pct"] = np.where(
        df["DBO_entrada_mg_L"] > 0,
        (
            (df["DBO_entrada_mg_L"] - df["DBO_salida_mg_L"])
            / df["DBO_entrada_mg_L"]
        )
        * 100,
        np.nan,
    )

    # Etiqueta más comprensible para informes
    df["estado_cumplimiento"] = np.where(
        df["cumplimiento_norma"] == 1,
        "CUMPLE",
        "NO CUMPLE",
    )

    # Alerta operativa simple y reproducible
    df["alerta_operacional"] = np.where(
        (df["cumplimiento_norma"] == 0)
        | (df["eficiencia_DBO_pct"] < 85),
        "REVISAR",
        "NORMAL",
    )

    return df


def generar_resumen(df):
    """Calcula indicadores por planta."""
    resumen = (
        df.groupby("planta")
        .agg(
            registros=("planta", "size"),
            caudal_promedio_m3_d=("caudal_entrada_m3_d", "mean"),
            dbo_entrada_promedio_mg_L=("DBO_entrada_mg_L", "mean"),
            dbo_salida_promedio_mg_L=("DBO_salida_mg_L", "mean"),
            eficiencia_promedio_pct=("eficiencia_DBO_pct", "mean"),
            energia_promedio_kWh=("energia_aeracion_kWh", "mean"),
            lodos_promedio_kg_d=("lodos_generados_kg_d", "mean"),
            cumplimiento_pct=("cumplimiento_norma", lambda x: x.mean() * 100),
        )
        .round(2)
        .reset_index()
    )
    return resumen


def exportar_archivos(df, resumen):
    """Genera archivos de salida para Operaciones y Gestión Ambiental."""

    operaciones = df[
        [
            "fecha_registro",
            "planta",
            "caudal_entrada_m3_d",
            "DBO_entrada_mg_L",
            "DBO_salida_mg_L",
            "energia_aeracion_kWh",
            "lodos_generados_kg_d",
            "eficiencia_DBO_pct",
            "alerta_operacional",
        ]
    ].copy()

    ambiental = df[
        [
            "fecha_registro",
            "planta",
            "DBO_salida_mg_L",
            "cumplimiento_norma",
            "estado_cumplimiento",
        ]
    ].copy()

    operaciones.to_csv(
        OUTPUT_DIR / "operaciones_aqualimpia.csv",
        index=False,
        encoding="utf-8-sig",
    )
    ambiental.to_csv(
        OUTPUT_DIR / "gestion_ambiental_aqualimpia.csv",
        index=False,
        encoding="utf-8-sig",
    )
    resumen.to_csv(
        OUTPUT_DIR / "resumen_por_planta.csv",
        index=False,
        encoding="utf-8-sig",
    )


def generar_graficos(df):
    """Genera gráficos básicos para revisión rápida."""

    # DBO de salida en el tiempo
    datos = df.sort_values("fecha_registro")
    plt.figure(figsize=(10, 5))
    for planta, grupo in datos.groupby("planta"):
        plt.plot(
            grupo["fecha_registro"],
            grupo["DBO_salida_mg_L"],
            marker="o",
            linewidth=1,
            label=planta,
        )
    plt.title("Evolución de DBO de salida")
    plt.xlabel("Fecha")
    plt.ylabel("DBO salida (mg/L)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / "dbo_salida_tiempo.png", dpi=150)
    plt.close()

    # Cumplimiento por planta
    cumplimiento = (
        df.groupby("planta")["cumplimiento_norma"].mean() * 100
    ).sort_values()

    plt.figure(figsize=(8, 5))
    cumplimiento.plot(kind="bar")
    plt.title("Porcentaje de cumplimiento normativo por planta")
    plt.xlabel("Planta")
    plt.ylabel("Cumplimiento (%)")
    plt.tight_layout()
    plt.savefig(GRAFICOS_DIR / "cumplimiento_por_planta.png", dpi=150)
    plt.close()


def main():
    print("=== AquaLimpia S. A. - Análisis de aguas residuales ===")

    df = cargar_datos(DATASET)
    print(f"Registros cargados: {len(df)}")

    df = limpiar_y_preparar(df)
    print(f"Registros válidos después de limpieza: {len(df)}")

    resumen = generar_resumen(df)

    print("\nResumen por planta:")
    print(resumen.to_string(index=False))

    exportar_archivos(df, resumen)
    generar_graficos(df)

    print("\nArchivos generados correctamente:")
    print("- outputs/operaciones_aqualimpia.csv")
    print("- outputs/gestion_ambiental_aqualimpia.csv")
    print("- outputs/resumen_por_planta.csv")
    print("- graficos/dbo_salida_tiempo.png")
    print("- graficos/cumplimiento_por_planta.png")


if __name__ == "__main__":
    main()
