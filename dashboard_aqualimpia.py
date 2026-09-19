from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------
st.set_page_config(
    page_title="AquaLimpia S. A.",
    page_icon="💧",
    layout="wide",
)

# Oculta elementos propios de Streamlit que aparecen en inglés
st.markdown(
    """
    <style>
        /* Ocultar encabezado superior, menú, botón Deploy y pie de Streamlit */
        header[data-testid="stHeader"] {
            display: none;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        [data-testid="stToolbar"] {
            display: none;
        }

        [data-testid="stStatusWidget"] {
            display: none;
        }

        [data-testid="stDecoration"] {
            display: none;
        }

        /* Quitar espacio superior que queda al ocultar el encabezado */
        .block-container {
            padding-top: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💧 AquaLimpia S. A.")
st.subheader("Panel exploratorio del desempeño de las plantas de tratamiento")

ARCHIVO_DATOS = "dataset_set_A_aguas_residuales.xlsx"


# ---------------------------------------------------------
# CARGA Y PREPARACIÓN DE LOS DATOS
# ---------------------------------------------------------
@st.cache_data
def cargar_datos(ruta_archivo):
    datos = pd.read_excel(ruta_archivo)

    datos = datos.rename(
        columns={
            "fecha_registro": "fecha",
            "planta": "planta",
            "caudal_entrada_m3_d": "caudal_afluente_m3_dia",
            "DBO_entrada_mg_L": "dbo_afluente_mg_l",
            "SST_entrada_mg_L": "sst_afluente_mg_l",
            "pH_entrada": "ph_afluente",
            "energia_aeracion_kWh": "energia_aireacion_kwh",
            "lodos_generados_kg_d": "lodos_generados_kg_dia",
            "DBO_salida_mg_L": "dbo_efluente_mg_l",
            "cumplimiento_norma": "cumplimiento_normativo",
        }
    )

    datos["fecha"] = pd.to_datetime(datos["fecha"], errors="coerce")

    datos["eficiencia_remocion_dbo_pct"] = np.where(
        datos["dbo_afluente_mg_l"] > 0,
        (
            (
                datos["dbo_afluente_mg_l"]
                - datos["dbo_efluente_mg_l"]
            )
            / datos["dbo_afluente_mg_l"]
        )
        * 100,
        np.nan,
    )

    datos["estado_cumplimiento"] = np.where(
        datos["cumplimiento_normativo"] == 1,
        "CUMPLE",
        "NO CUMPLE",
    )

    return datos.dropna(subset=["fecha", "planta"])


# ---------------------------------------------------------
# CARGA AUTOMÁTICA DEL ARCHIVO
# ---------------------------------------------------------
if not Path(ARCHIVO_DATOS).exists():
    st.error(
        f"No se encontró el archivo '{ARCHIVO_DATOS}'. "
        "Debe estar en la misma carpeta que este programa."
    )
    st.stop()

datos = cargar_datos(ARCHIVO_DATOS)


# ---------------------------------------------------------
# FILTROS
# ---------------------------------------------------------
st.sidebar.header("Filtros")

plantas_disponibles = sorted(
    datos["planta"].dropna().unique().tolist()
)

plantas_seleccionadas = st.sidebar.multiselect(
    "Planta de tratamiento",
    plantas_disponibles,
    default=plantas_disponibles,
)

fecha_minima = datos["fecha"].min().date()
fecha_maxima = datos["fecha"].max().date()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_minima, fecha_maxima),
    min_value=fecha_minima,
    max_value=fecha_maxima,
)

datos_filtrados = datos[
    datos["planta"].isin(plantas_seleccionadas)
].copy()

if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
    fecha_inicio = pd.Timestamp(rango_fechas[0])
    fecha_termino = pd.Timestamp(rango_fechas[1])

    datos_filtrados = datos_filtrados[
        (datos_filtrados["fecha"] >= fecha_inicio)
        & (datos_filtrados["fecha"] <= fecha_termino)
    ]

if datos_filtrados.empty:
    st.warning("No existen registros para los filtros seleccionados.")
    st.stop()


# ---------------------------------------------------------
# INDICADORES PRINCIPALES
# ---------------------------------------------------------
porcentaje_cumplimiento = (
    datos_filtrados["cumplimiento_normativo"].mean() * 100
)

dbo_promedio_efluente = datos_filtrados["dbo_efluente_mg_l"].mean()

eficiencia_promedio = datos_filtrados[
    "eficiencia_remocion_dbo_pct"
].mean()

caudal_promedio = datos_filtrados[
    "caudal_afluente_m3_dia"
].mean()

columna_1, columna_2, columna_3, columna_4 = st.columns(4)

columna_1.metric(
    "Cumplimiento normativo",
    f"{porcentaje_cumplimiento:.1f}%",
)

columna_2.metric(
    "DBO promedio del efluente",
    f"{dbo_promedio_efluente:.1f} mg/L",
)

columna_3.metric(
    "Eficiencia promedio de remoción de DBO",
    f"{eficiencia_promedio:.1f}%",
)

columna_4.metric(
    "Caudal promedio de entrada",
    f"{caudal_promedio:,.0f} m³/día",
)

st.divider()


# ---------------------------------------------------------
# GRÁFICOS
# ---------------------------------------------------------
columna_izquierda, columna_derecha = st.columns(2)

with columna_izquierda:
    figura = px.line(
        datos_filtrados.sort_values("fecha"),
        x="fecha",
        y="dbo_efluente_mg_l",
        color="planta",
        markers=True,
        title="Evolución de la DBO del efluente",
        labels={
            "fecha": "Fecha",
            "dbo_efluente_mg_l": "DBO del efluente (mg/L)",
            "planta": "Planta",
        },
    )
    st.plotly_chart(figura, use_container_width=True)

with columna_derecha:
    resumen_cumplimiento = (
        datos_filtrados.groupby(
            "planta",
            as_index=False
        )["cumplimiento_normativo"]
        .mean()
    )

    resumen_cumplimiento["porcentaje_cumplimiento"] = (
        resumen_cumplimiento["cumplimiento_normativo"] * 100
    )

    figura = px.bar(
        resumen_cumplimiento,
        x="planta",
        y="porcentaje_cumplimiento",
        title="Cumplimiento normativo por planta",
        labels={
            "planta": "Planta",
            "porcentaje_cumplimiento": "Cumplimiento (%)",
        },
    )
    st.plotly_chart(figura, use_container_width=True)


columna_izquierda_2, columna_derecha_2 = st.columns(2)

with columna_izquierda_2:
    figura = px.scatter(
        datos_filtrados,
        x="dbo_afluente_mg_l",
        y="dbo_efluente_mg_l",
        color="planta",
        hover_data=["fecha"],
        title="DBO del afluente versus DBO del efluente",
        labels={
            "dbo_afluente_mg_l": "DBO del afluente (mg/L)",
            "dbo_efluente_mg_l": "DBO del efluente (mg/L)",
            "planta": "Planta",
        },
    )
    st.plotly_chart(figura, use_container_width=True)

with columna_derecha_2:
    figura = px.scatter(
        datos_filtrados,
        x="caudal_afluente_m3_dia",
        y="dbo_efluente_mg_l",
        color="planta",
        hover_data=["fecha", "estado_cumplimiento"],
        title="Caudal de entrada versus DBO del efluente",
        labels={
            "caudal_afluente_m3_dia": "Caudal de entrada (m³/día)",
            "dbo_efluente_mg_l": "DBO del efluente (mg/L)",
            "planta": "Planta",
        },
    )
    st.plotly_chart(figura, use_container_width=True)


columna_izquierda_3, columna_derecha_3 = st.columns(2)

with columna_izquierda_3:
    figura = px.box(
        datos_filtrados,
        x="planta",
        y="eficiencia_remocion_dbo_pct",
        points="all",
        title="Eficiencia de remoción de DBO por planta",
        labels={
            "planta": "Planta",
            "eficiencia_remocion_dbo_pct": "Eficiencia de remoción (%)",
        },
    )
    st.plotly_chart(figura, use_container_width=True)

with columna_derecha_3:
    figura = px.scatter(
        datos_filtrados,
        x="energia_aireacion_kwh",
        y="eficiencia_remocion_dbo_pct",
        color="planta",
        hover_data=["fecha"],
        title="Energía de aireación versus eficiencia de remoción",
        labels={
            "energia_aireacion_kwh": "Energía de aireación (kWh)",
            "eficiencia_remocion_dbo_pct": "Eficiencia de remoción (%)",
            "planta": "Planta",
        },
    )
    st.plotly_chart(figura, use_container_width=True)


# ---------------------------------------------------------
# MATRIZ DE CORRELACIÓN
# ---------------------------------------------------------
st.subheader("Matriz de correlación")

variables_correlacion = [
    "caudal_afluente_m3_dia",
    "dbo_afluente_mg_l",
    "energia_aireacion_kwh",
    "lodos_generados_kg_dia",
    "dbo_efluente_mg_l",
    "eficiencia_remocion_dbo_pct",
]

matriz_correlacion = datos_filtrados[
    variables_correlacion
].corr(numeric_only=True)

nombres_visibles = {
    "caudal_afluente_m3_dia": "Caudal afluente",
    "dbo_afluente_mg_l": "DBO afluente",
    "energia_aireacion_kwh": "Energía aireación",
    "lodos_generados_kg_dia": "Lodos generados",
    "dbo_efluente_mg_l": "DBO efluente",
    "eficiencia_remocion_dbo_pct": "Eficiencia DBO",
}

matriz_correlacion = matriz_correlacion.rename(
    index=nombres_visibles,
    columns=nombres_visibles,
)

figura = px.imshow(
    matriz_correlacion,
    text_auto=".2f",
    aspect="auto",
    title="Relación entre variables operacionales",
)

st.plotly_chart(figura, use_container_width=True)


# ---------------------------------------------------------
# REGISTROS CON INCUMPLIMIENTO
# ---------------------------------------------------------
st.subheader("Registros con incumplimiento normativo")

registros_incumplimiento = datos_filtrados[
    datos_filtrados["cumplimiento_normativo"] == 0
][
    [
        "fecha",
        "planta",
        "caudal_afluente_m3_dia",
        "dbo_afluente_mg_l",
        "dbo_efluente_mg_l",
        "eficiencia_remocion_dbo_pct",
        "energia_aireacion_kwh",
        "lodos_generados_kg_dia",
        "estado_cumplimiento",
    ]
].sort_values("fecha", ascending=False)

registros_incumplimiento = registros_incumplimiento.rename(
    columns={
        "fecha": "Fecha",
        "planta": "Planta",
        "caudal_afluente_m3_dia": "Caudal entrada (m³/día)",
        "dbo_afluente_mg_l": "DBO afluente (mg/L)",
        "dbo_efluente_mg_l": "DBO efluente (mg/L)",
        "eficiencia_remocion_dbo_pct": "Eficiencia DBO (%)",
        "energia_aireacion_kwh": "Energía aireación (kWh)",
        "lodos_generados_kg_dia": "Lodos generados (kg/día)",
        "estado_cumplimiento": "Estado",
    }
)

st.dataframe(
    registros_incumplimiento,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Afluente: agua residual que ingresa a la planta. "
    "Efluente: agua tratada que sale de la planta."
)
