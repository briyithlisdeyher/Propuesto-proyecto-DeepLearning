# ☕ Centinela Café · Deep Learning

Sistema de alerta temprana de **hojas de café robusta afectadas**, ya sea por ácaro rojo o por roya (*Hemileia vastatrix*), a partir de fotos de hojas y, en una segunda fase, de datos climáticos.

Es el proyecto del curso **Deep Learning** de la Maestría en Ciencia de Datos de la Universidad Santo Tomás (Proyecto Centinela). El proyecto se desarrolla en **dos fases**.

## Equipo

- Briyith Lisdey Herrera Cruz
- Juan Pablo Becerra Tirano
- Johnatan Vélez Martínez

## ⚠️ Cambio de conjunto de datos (v1 → v2)

La versión v1 de la propuesta (2026-10-30) usaba el dataset de mazorcas de cacao con monilia de Rengifo-Lozano y Sánchez-Flores (2026), [doi:10.17632/ykbtpsyfv9.1](https://doi.org/10.17632/ykbtpsyfv9.1).

Contactamos a los autores para conocer la ubicación de captura. Nos dieron una **respuesta general**: las fotos se tomaron en las provincias de **Tocache, Huallaga y Rioja** (Perú). Sin embargo, **ninguna imagen registra el lugar donde se tomó**. Sin ubicación por imagen no se puede construir una clave de alineación espaciotemporal verificable entre cada foto y su serie climática. Esa clave es la condición 3 de la compuerta de la Propuesta de Datos y la base de la fusión de la Fase 2.

Por eso **cambiamos al dataset RoCoLe** (Parraga-Alava et al., 2019), [doi:10.17632/c5yvn32dzg.2](https://doi.org/10.17632/c5yvn32dzg.2). Sus fotos vienen de **un único sitio georreferenciado**: CIIDEA, ESPAM MFL, Calceta, Manabí, Ecuador (lat −0,834206; lon −80,177159). Además, cada imagen conserva su **fecha de captura en el EXIF**. El detalle está en [docs/justificacion_cambio_dataset.md](docs/justificacion_cambio_dataset.md).

## Descripción

| Fase | Contenido | Estado |
|---|---|---|
| Propuesta de Datos | [Propuesta_de_datos.md](Propuesta_de_datos.md) (v2, RoCoLe) | Enviada a compuerta |
| **Fase 1** | MLP en PyTorch sobre 27 rasgos tabulares extraídos de cada hoja. En prueba: *recall* de la clase afectada 0,975 y AUC 0,936. El notebook es [notebooks/Centinela_Fase1.ipynb](notebooks/Centinela_Fase1.ipynb) y el informe [informe/Informe_Fase1.pdf](informe/Informe_Fase1.pdf) | Desarrollada |
| Fase 2 | CNN (imagen) + LSTM/GRU (60 días de NASA POWER) + fusión | Pendiente |

**Objetivo binario:** `afectada = 1` si la hoja tiene ácaro rojo o roya de cualquier nivel, y `0` si está sana. El cliente son las organizaciones de monitoreo fitosanitario, a través de sus técnicos de sanidad vegetal.

## Datos

Las imágenes **no están en este repositorio**. Tienen licencia CC BY 4.0 y se descargan de la fuente primaria. El notebook busca los datos en `data/raw/`, luego en Google Drive y, si no los encuentra, descarga el zip de Mendeley.

| Fuente | Contenido | Licencia |
|---|---|---|
| Parraga-Alava, Cusme, Loor y Santander (2019). RoCoLe, Mendeley Data v2 | 1.560 fotos JPEG de 390 plantas (4 por planta, haz y envés). Hay 791 sanas, 167 con ácaro rojo y 602 con roya de niveles 1–4. Anotaciones de Labelbox | CC BY 4.0 |
| NASA POWER (NASA Langley Research Center) | Clima diario en CIIDEA: `T2M`, `RH2M`, `PRECTOTCORR`, `WS2M` | Uso libre con atribución |

Estructura esperada de `data/raw/`:

```
data/raw/
├── Annotations/   RoCoLE-csv.csv · RoCoLE-json.json · RoCoLE-coco.json · RoCoLe-classes.xlsx
└── Photos/        1.560 archivos C<n>P<n><H|E><n>.jpg
```

**Duplicados.** El notebook **no elimina duplicados byte a byte**. Los detecta con SHA-256 y pHash, los reporta y obliga a que cada grupo de duplicados y cada planta caigan en un solo subconjunto. Así no hay fuga de información sin borrar ninguna imagen.

**Datos personales.** La columna `Created By` de `RoCoLE-csv.csv` y el campo `Created By` de `RoCoLE-json.json` identifican al anotador. Se eliminan al cargar y nunca se exportan (ver el Anexo C).

## Estructura del repositorio

```
├── README.md
├── Propuesta_de_datos.md               # Plantilla 12 (v2) + anexos A, B y C
├── requirements.txt · .gitignore
├── notebooks/Centinela_Fase1.ipynb     # Se ejecuta de inicio a fin ("Ejecutar todo")
├── src/modelo.py                       # Clase MLP (idéntica a la del notebook)
├── data/processed/rocole_tabular_features_fase1.csv   # Tabla de rasgos (entrada del EDA)
├── data/external/nasa_power_ciidea_diario.csv         # Clima diario de NASA POWER
├── resultados/                         # Figuras, tablas, particion.csv, resultados.json
├── informe/Informe_Fase1.pdf           # Informe técnico-ético (5 secciones, ≤ 4 páginas + referencias)
└── docs/
    ├── justificacion_cambio_dataset.md
    ├── propuesta_metodologica.md
    ├── flujo_logico_fase1.md           # Diagrama aprobado del notebook
    ├── trazabilidad.md                 # Requisito → criterio → entregable
    ├── Bitacora_IA.md                  # Plantilla 13
    └── Auditoria_IA.md
```

## Reproducibilidad

Se puede ejecutar en Google Colab o en local con Python 3.10 o superior (`pip install -r requirements.txt`). Usa semilla 42 en `torch`, `numpy` y `random`, y `torch.use_deterministic_algorithms(True)`.

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/Centinela_Fase1.ipynb
```

## Referencias (APA 7)

- Guío Español, A., Tamayo Uribe, E., Gómez Ayerbe, P., & Mujica, M. P. (2021). *Marco ético para la inteligencia artificial en Colombia*. Consejería Presidencial para Asuntos Económicos y Transformación Digital.
- NASA Langley Research Center. (2026). *Prediction of Worldwide Energy Resources (POWER) Project: Daily agroclimatology data* [Data set]. https://power.larc.nasa.gov/
- Parraga-Alava, J., Cusme, K., Loor, A., & Santander, E. (2019a). *RoCoLe: A robusta coffee leaf images dataset* (Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/c5yvn32dzg.2
- Parraga-Alava, J., Cusme, K., Loor, A., & Santander, E. (2019b). RoCoLe: A robusta coffee leaf images dataset for evaluation of machine learning based methods in plant diseases recognition. *Data in Brief, 25*, 104414. https://doi.org/10.1016/j.dib.2019.104414
- Rengifo-Lozano, D., & Sánchez-Flores, J. (2026). *Image dataset of healthy and monilia-infected cocoa pods for disease classification* (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/ykbtpsyfv9.1 *(dataset descartado; se cita como antecedente)*

Proyecto académico, sin fines comerciales.
