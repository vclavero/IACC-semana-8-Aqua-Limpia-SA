"""
Análisis modular del desempeño de AquaLimpia S. A.
"""

from pathlib import Path

from funciones_aqualimpia import (
    cargar_datos,
    limpiar_datos,
    calcular_eficiencia_dbo,
    agregar_estado_cumplimiento,
    calcular_resumen_por_planta,
    calcular_intervalo_confianza_dbo,
    guardar_resultados_joblib,
    exportar_resultados,
)


ARCHIVO_DATOS = "dataset_set_A_aguas_residuales.xlsx"


def main():
    print("AquaLimpia S. A. - Análisis modular")

    # 1. Carga
    datos = cargar_datos(ARCHIVO_DATOS)

    # 2. Limpieza
    datos = limpiar_datos(datos)

    # 3. Indicadores
    datos = calcular_eficiencia_dbo(datos)
    datos = agregar_estado_cumplimiento(datos)

    # 4. Resumen
    resumen = calcular_resumen_por_planta(datos)

    # 5. Intervalo de confianza con SciPy
    intervalo = calcular_intervalo_confianza_dbo(datos)

    # 6. Exportación de archivos
    exportar_resultados(
        datos,
        resumen,
        carpeta_salida="resultados"
    )

    # 7. Persistencia con Joblib
    guardar_resultados_joblib(
        resumen,
        intervalo,
        "resultados/resultados_aqualimpia.joblib"
    )

    print("\nResumen por planta:")
    print(resumen.to_string(index=False))

    print(
        "\nIntervalo de confianza del 95% para "
        "la DBO de salida promedio:"
    )
    print(
        f"{intervalo[0]:.2f} a {intervalo[1]:.2f} mg/L"
    )

    print("\nProceso terminado correctamente.")


if __name__ == "__main__":
    main()
