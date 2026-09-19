# AquaLimpia S. A. - Proyecto de análisis de datos

## 1. Objetivo del proyecto

El objetivo de este proyecto es analizar el desempeño de las plantas de tratamiento de aguas residuales de AquaLimpia S. A., con énfasis en el comportamiento de la DBO, la eficiencia del tratamiento y el cumplimiento normativo.

El análisis busca identificar patrones que puedan estar relacionados con variaciones en el caudal de entrada, la carga contaminante, el consumo de energía en aireación, la generación de lodos y las diferencias de operación entre plantas.

## 2. Datos utilizados

El proyecto utiliza el archivo:

`dataset_set_A_aguas_residuales.xlsx`

Entre las principales variables analizadas se encuentran:

- Fecha de registro.
- Planta de tratamiento.
- Caudal de entrada.
- DBO de entrada.
- DBO de salida.
- Energía utilizada en aireación.
- Lodos generados.
- Estado de cumplimiento normativo.

## 3. Proceso analítico

El flujo de trabajo se desarrolló mediante las siguientes etapas:

1. Carga del dataset.
2. Revisión y limpieza de los datos.
3. Conversión y validación de fechas y variables numéricas.
4. Revisión de valores faltantes y registros duplicados.
5. Cálculo de la eficiencia de remoción de DBO.
6. Análisis descriptivo y comparación entre plantas.
7. Evaluación del cumplimiento normativo.
8. Análisis de relaciones entre variables operacionales.
9. Generación de gráficos y visualizaciones.
10. Construcción de un dashboard exploratorio.
11. Creación de archivos de salida para Operaciones y Gestión Ambiental.

## 4. Indicador de eficiencia

La eficiencia de remoción de DBO se calcula mediante:

**Eficiencia DBO (%) = ((DBO entrada - DBO salida) / DBO entrada) × 100**

Este indicador permite evaluar qué proporción de la carga contaminante fue removida durante el tratamiento.

## 5. Resultados generados

El proyecto genera los siguientes archivos:

### Área de Operaciones

`operaciones_aqualimpia.csv`

Incluye información relacionada con:

- Fecha.
- Planta.
- Caudal de entrada.
- DBO de entrada y salida.
- Energía de aireación.
- Lodos generados.
- Eficiencia de remoción de DBO.
- Alertas operacionales.

### Área de Gestión Ambiental

`gestion_ambiental_aqualimpia.csv`

Incluye:

- Fecha.
- Planta.
- DBO del efluente.
- Cumplimiento normativo.
- Estado de cumplimiento.

## 6. Dashboard exploratorio

El dashboard permite visualizar de manera interactiva:

- Cumplimiento normativo.
- DBO promedio del efluente.
- Eficiencia promedio de remoción.
- Caudal promedio de entrada.
- Evolución de la DBO en el tiempo.
- Comparación entre plantas.
- Relación entre caudal y DBO de salida.
- Relación entre energía de aireación y eficiencia.
- Matriz de correlación.
- Registros con incumplimiento normativo.

## 7. Estructura del proyecto

```text
AquaLimpia/
│
├── datos/
│   └── dataset_set_A_aguas_residuales.xlsx
│
├── scripts/
│   ├── analisis_aqualimpia.py
│   └── dashboard_aqualimpia.py
│
├── resultados/
│   ├── operaciones_aqualimpia.csv
│   └── gestion_ambiental_aqualimpia.csv
│
├── graficos/
│
└── README.md
```

## 8. Conclusión

La documentación técnica permite comprender cómo se desarrolló el análisis, qué datos se utilizaron, qué procedimientos se aplicaron y qué resultados fueron generados. Además, facilita que otros integrantes del equipo puedan revisar, repetir y continuar el proyecto, manteniendo la trazabilidad y la reproducibilidad del proceso analítico.
