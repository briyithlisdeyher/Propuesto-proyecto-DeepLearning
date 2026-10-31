# 🍫 CentinelaCacaoDeepLearning

Sistema de alerta temprana de **monilia** (*Moniliophthora roreri*) en mazorcas de cacao, con *deep learning* sobre fotos y datos climáticos.

Proyecto del curso **Deep Learning** de la **Maestría en Ciencia de Datos** de la **Universidad Santo Tomás**.

## Equipo

- Briyith Lisdey Herrera Cruz
- Juan Pablo Becerra Tirano
- Johnatan Vélez Martínez


## Descripción

A partir de la foto de una mazorca, el sistema dice si tiene monilia. En una segunda fase combina esa foto con el clima de las semanas anteriores para emitir una alerta más temprana. Está pensado como apoyo para los técnicos de la Federación Nacional de Cacaoteros (Fedecacao).

El detalle del problema, los datos y las decisiones de diseño está en la **El detalle del problema, los datos y las decisiones de diseño está en la [Propuesta de Datos](<Propuesta_de_datos.md>).**.

## Estado del proyecto

- [x] Propuesta de Datos (Fase 1)
- [ ] **Fase 1:** línea base con un MLP sobre rasgos extraídos de las imágenes
- [ ] **Fase 2:** CNN (imagen) + LSTM/GRU (clima) + fusión

## Datos

Las imágenes **no están en este repositorio** porque pesan 8,24 GB. Para usarlas:

Descarga `Monilia.rar` y `Sanos.rar` de [Mendeley Data](https://doi.org/10.17632/ykbtpsyfv9.1).

El clima se descarga automáticamente desde la API de [NASA POWER](https://power.larc.nasa.gov/).

| Fuente | Contenido | Licencia |
| --- | --- | --- |
| [Rengifo-Lozano y Sánchez-Flores (2026)](https://doi.org/10.17632/ykbtpsyfv9.1) | 2.184 fotos de mazorcas: 1.342 con monilia y 842 sanas | CC BY 4.0 |
| [NASA POWER](https://power.larc.nasa.gov/) | Clima diario: temperatura, humedad, lluvia y viento | Libre uso con atribución |

## Créditos y licencia de los datos

- Imágenes: Rengifo-Lozano, D., & Sánchez-Flores, J. (2026). *Image dataset of healthy and Monilia-infected cocoa pods for disease classification* (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/ykbtpsyfv9.1. Licencia CC BY 4.0.
- Clima: datos obtenidos del proyecto POWER del NASA Langley Research Center (LaRC), financiado por el programa NASA Earth Science/Applied Science.

Proyecto académico, sin fines comerciales.
