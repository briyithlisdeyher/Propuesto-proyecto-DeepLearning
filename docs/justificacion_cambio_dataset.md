# Justificación formal del cambio de conjunto de datos

**Proyecto:** Centinela · Fase 1 · **Versión:** v2 · **Fecha:** 2026-11-04
**Equipo:** Briyith Lisdey Herrera Cruz · Juan Pablo Becerra Tirano · Johnatan Vélez Martínez

## 1. Dataset original (v1, 2026-10-30)

Rengifo-Lozano, D., & Sánchez-Flores, J. (2026). *Image dataset of healthy and monilia-infected cocoa pods for disease classification* (v1) [Data set]. Mendeley Data. https://doi.org/10.17632/ykbtpsyfv9.1

- 2.184 imágenes: 1.342 con monilia y 842 sanas. Licencia CC BY 4.0.
- La propuesta v1 planteaba la clave de alineación `(región, mes de captura)`, tomada del EXIF.

## 2. Hallazgo

Contactamos a los autores para conocer la ubicación de captura de las imágenes. Respondieron que las fotografías se tomaron en las provincias de **Tocache, Huallaga y Rioja** (Perú). Sin embargo, **ninguna imagen registra su ubicación**, así que no se puede saber en cuál de las tres provincias se tomó cada fotografía.

## 3. Por qué el hallazgo descalifica el dataset para el proyecto

| Requisito (actividad 11 / plantilla 12) | Efecto del hallazgo |
|---|---|
| Condición 3 de la compuerta: "clave de alineación con evidencia de acoplamiento" | Sin región por imagen no se puede asignar a cada foto su serie climática. La prueba de las 10 filas (Anexo A) no podría hacerse con datos verificables. |
| Fase 2: fusión CNN + RNN sobre la misma entidad y ventana espaciotemporal | Habría que asignar el clima por suposición. Las tres provincias tienen climas distintos y no hay forma de saber cuál corresponde a cada foto. |
| Criterio 6: "conclusión apoyada en cifra que el cuaderno no respalda" → tope Inicial | Cualquier resultado de la fusión dependería de una alineación sin respaldo. |

**Alternativas descartadas:**
- Usar el clima promedio de las tres provincias: introduce ruido sin control.
- Asignar una provincia al azar a cada foto: es inventar datos.

## 4. Dataset sustituto (v2)

Parraga-Alava, J., Cusme, K., Loor, A., & Santander, E. (2019). *RoCoLe: A robusta coffee leaf images dataset* (v2) [Data set]. Mendeley Data. https://doi.org/10.17632/c5yvn32dzg.2

| Atributo | Valor | Fuente |
|---|---|---|
| Sitio | CIIDEA, ESPAM MFL, Calceta, Manabí, Ecuador (lat −0,834206; lon −80,177159) | Artículo de Data in Brief, 25, 104414 |
| Muestras | 390 plantas × 4 imágenes = 1.560 JPEG | Artículo + verificación en el notebook |
| Clases | Sana 791 · ácaro rojo 167 · roya 1: 344 · roya 2: 166 · roya 3: 62 · roya 4: 30 | Artículo + anotaciones |
| Anotaciones | Labelbox: polígono de la hoja y clase; formatos JSON, CSV, XLSX, COCO y VOC | Mendeley |
| Fecha por imagen | `DateTimeOriginal` del EXIF: 5 días entre el 2019-04-09 y el 2019-05-02 | **Verificado en el notebook** (paso 1.4) |
| Licencia | CC BY 4.0 | Mendeley |

**Qué resuelve:**
- La ubicación es exacta y común a todas las imágenes.
- La fecha está en cada imagen.
- Así la clave `(CIIDEA, fecha)` es verificable y la serie de NASA POWER se consulta sin suposiciones.

## 5. Limitaciones que se mantienen (declaradas)

- **Solo 5 fechas distintas.** La rama temporal de la Fase 2 tendrá 5 ventanas climáticas diferentes, una por día de captura. El clima no distinguirá entre hojas del mismo día: servirá como contexto de riesgo, no como señal por hoja.
- **Un único sitio y solo robusta.** Los resultados no se pueden generalizar a arábica ni a Colombia sin un piloto local.
