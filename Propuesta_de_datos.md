# Propuesta de Datos · Proyecto Centinela · Fase 1

## 0. Encabezado

| Campo | Detalle |
|---|---|
| Título del proyecto | Centinela del Café: alerta temprana de hojas de café robusta afectadas (ácaro rojo o roya) |
| Integrantes | Briyith Lisdey Herrera Cruz · Juan Pablo Becerra Tirano · Johnatan Vélez Martínez |
| Fecha | 2026-11-04 |
| Versión | v2 (Fase 1). Sustituye a la v1 del 2026-10-30 (cacao/monilia) |
| Fecha de aprobación en compuerta | `[AAAA-MM-DD — la registra el docente]` |

> **Motivo del cambio de v1 a v2.** Los autores del dataset de cacao (doi:10.17632/ykbtpsyfv9.1) confirmaron que las fotos se tomaron en las provincias de Tocache, Huallaga y Rioja. Pero ninguna imagen registra dónde se tomó, así que no existe una clave de alineación por imagen con la serie climática. RoCoLe proviene de un único sitio georreferenciado y conserva la fecha de captura en el EXIF de cada imagen. El detalle está en [docs/justificacion_cambio_dataset.md](docs/justificacion_cambio_dataset.md).

## 1. Problema, cliente y objetivo binario

- **Evento y cliente.** Las **organizaciones de monitoreo fitosanitario** necesitan que sus **técnicos de sanidad vegetal** sepan qué hojas de café revisar primero. El sistema les entrega una alerta a partir de una foto de la hoja tomada con celular.
- **Impacto.** Una hoja con roya o ácaro que no se detecta sigue esporulando o reproduciéndose y contagia el lote. Detectarla temprano permite actuar de forma focalizada.
- **Objetivo binario: ¿hoja afectada? sí/no.** RoCoLe trae 6 clases: sana, ácaro rojo y roya de niveles 1 a 4. Se agrupan así:
  - `afectada = 0` si la hoja está **sana** (791 hojas).
  - `afectada = 1` si tiene **ácaro rojo o roya de cualquier nivel** (769 hojas).
  - *Información que se pierde:* el tipo de afección y su severidad. Se conservan como columnas para el análisis por subgrupo.
- **Unidad de análisis:** la hoja. Hay una hoja anotada por imagen.
- **Error más costoso: el falso negativo.** Se asume FN:FP = **5:1**, dentro del rango de 3 a 8 veces que cuesta dejar pasar un defecto en un control de calidad. Meta: *recall* de la clase afectada ≥ 0,90, con el umbral elegido en validación.

## 2. Las dos modalidades del sistema

| Rama | Qué representa | Instrumento | Frecuencia | Señal |
|---|---|---|---|---|
| Imagen | Foto RGB del haz o el envés de una hoja | Celulares Samsung de 5 MP (SM-J200M, SM-J700M, SM-G610M, SM-J320H) a 200–300 mm | Una foto por hoja | Pústulas anaranjadas, clorosis, bronceado y textura |
| Temporal | Clima diario: `T2M`, `RH2M`, `PRECTOTCORR`, `WS2M` | NASA POWER (reanálisis y satélite; comunidad AG) | Diaria | Condiciones favorables a la roya y al ácaro (humedad, temperatura, lluvia) |

**¿La imagen contiene algo que un número no?** Sí. El clima indica si las condiciones *favorecen* la afección, pero no si *esta* hoja está afectada.

## 3. Fuentes

| Modalidad | Fuente (productor primario) | Enlace o DOI | Licencia y versión | Dónde se verificó | ¿Datos personales? |
|---|---|---|---|---|---|
| Imagen | Parraga-Alava, Cusme, Loor y Santander (ESPAM MFL / USACH) | https://doi.org/10.17632/c5yvn32dzg.2 | CC BY 4.0 · v2 (2019-05-17) | Página de Mendeley Data y API pública de Mendeley | Solo el campo `Created By` (identifica al anotador) → **se elimina** (Anexo C). Las imágenes no contienen personas identificables |
| Temporal | NASA Langley Research Center, POWER Project | https://power.larc.nasa.gov/ | Uso libre con atribución | Página *Data Access / Citation* de POWER | No |

## 4. Por qué NO es un reto resuelto

- **Datos crudos.**
  - No traen partición ni tabla de rasgos: el notebook extrae 28 rasgos de la hoja a partir del polígono anotado.
  - El CSV de anotaciones llega con 1.560 × 18 celdas y 23,5 % de faltantes.
  - Hay **67 grupos de imágenes idénticas byte a byte** entre plantas distintas; en 27 de ellos las copias tienen clase multiclase distinta.
  - Los nombres de archivo y el EXIF hay que parsearlos.
- **Estructura dependiente.** Hay 4 fotos por planta y duplicados que encadenan plantas, así que la partición debe ser agrupada.
- **Kaggle:** existen notebooks que usan RoCoLe (Anexo B). Por los títulos que se pudieron leer, son clasificadores de imagen. **Ninguno de esos tres cruza RoCoLe con clima** ni construye la clave `(sitio, fecha EXIF)`. Los datos de este proyecto se descargan de la **fuente primaria** (Mendeley) y se verifican contra ella por SHA-256.
- RoCoLe aparece en el catálogo del curso como fuente permitida. No es el escenario vetado (tulipán/KNMI).

## 5. Plan de la Fase 1, clave de alineación y prueba de acoplamiento

- **Modalidad que se aplana en la Fase 1:** la **imagen**. Cada hoja se convierte en 28 rasgos de color, lesión, índices, textura y forma; 27 de ellos entran a un MLP de PyTorch con dos capas ocultas.
- **Paso a la Fase 2:**
  - Rama de imagen: CNN con *transfer learning*.
  - Rama temporal: LSTM/GRU sobre los **60 días previos** de NASA POWER.
  - Fusión por concatenación de *embeddings*.
- **Clave de alineación (por muestra):** `(sitio = CIIDEA [−0,834206; −80,177159], fecha de captura = EXIF DateTimeOriginal)`.
  - La ventana climática va de `d−60` a `d−1`, sin incluir el día de captura.
  - Se verificó en el notebook (§1.4): las 1.560 imágenes tienen fecha, y hay 5 días distintos (2019-04-09, 04-10, 04-11, 05-01 y 05-02).
- **Limitación declarada:** las 5 ventanas de 60 días son casi idénticas (T2M de 25,66 a 25,80 °C; RH2M de 85,8 a 86,2 %). El clima aportará contexto de riesgo, no señal por hoja.
- **Prueba de acoplamiento:** 10 filas reales en el Anexo A.

## 6. Línea base comprometida

Resultados en el **conjunto de prueba** (n = 236), con el umbral elegido en validación. Fuente: `resultados/metricas_prueba.csv`.

| Modelo | Exactitud | *Recall* afectada | Costo 5·FN+FP |
|---|---|---|---|
| Clase mayoritaria (sana) | 0,496 | 0,000 | 595 |
| Escalar crudo `pct_lesion` (umbral 0,0045) | 0,631 | 0,992 | 91 |
| **MLP R3a (umbral 0,22)** | **0,822** | **0,975** | **54** |

- **Partición:** 70,0 / 14,9 / 15,1 %, estratificada y **agrupada** por `id_grupo` (planta ∪ duplicados), con semilla 42.
- Los duplicados **no se eliminan**.
- La partición, la semilla, el umbral y las líneas base se conservan para la Fase 2 (`resultados/particion.csv`).

## 7. Riesgos éticos y protección de datos

| Riesgo | Daño al cliente | Mitigación |
|---|---|---|
| Sesgo de muestreo: un solo sitio, solo robusta, 5 días, 4 celulares | Mal desempeño en arábica o en fincas colombianas | Declarar el dominio de validez; piloto local antes de usarlo |
| Falsa alarma (FP) | Visitas o aplicaciones innecesarias | Umbral por costo; confirmación del técnico; tasa de FP reportada por celular (va de 0,10 a 0,54) |
| Omisión de alarma (FN) | Foco no tratado | *Recall* ≥ 0,90 (se obtuvo 0,975); aviso "sin alerta ≠ sana"; *recall* por severidad |
| Ruido de etiqueta (27 grupos de duplicados con clase distinta) | Métricas ruidosas | Se reporta, no se corrige a mano y se agrupa en la partición |
| Dato del anotador (`Created By`) | Exposición de un dato personal | Se elimina al cargar (Anexo C) |

## 8. Citas APA 7

- Parraga-Alava, J., Cusme, K., Loor, A., & Santander, E. (2019). *RoCoLe: A robusta coffee leaf images dataset* (Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/c5yvn32dzg.2
- NASA Langley Research Center. (2026). *Prediction of Worldwide Energy Resources (POWER) Project: Daily agroclimatology data* [Data set]. https://power.larc.nasa.gov/

---

## Anexo A · Prueba de acoplamiento (10 filas reales)

- **Generadas por:** notebook §3.2, a partir de `df.groupby("fecha").sample(2, random_state=42)` y la API de NASA POWER (`/api/temporal/daily/point`, comunidad AG).
- **Archivo:** `resultados/acoplamiento_10_filas.csv`.

| # | Clave (sitio, fecha) | Imagen · rasgo `pct_lesion` · clase | T2M media 60 d (°C) | RH2M media 60 d (%) | PRECTOTCORR suma 60 d (mm) | WS2M media 60 d (m/s) |
|---|---|---|---|---|---|---|
| 1 | CIIDEA, 2019-04-09 | C9P20H1.jpg · 0,012 · roya 1 | 25,80 | 85,82 | 643,78 | 1,57 |
| 2 | CIIDEA, 2019-04-09 | C9P15E1.jpg · 0,212 · roya 3 | 25,80 | 85,82 | 643,78 | 1,57 |
| 3 | CIIDEA, 2019-04-10 | C6P14E2.jpg · 0,002 · sana | 25,79 | 85,88 | 641,95 | 1,57 |
| 4 | CIIDEA, 2019-04-10 | C10P2E2.jpg · 0,012 · sana | 25,79 | 85,88 | 641,95 | 1,57 |
| 5 | CIIDEA, 2019-04-11 | C11P28H1.jpg · 0,024 · sana | 25,79 | 85,80 | 627,27 | 1,56 |
| 6 | CIIDEA, 2019-04-11 | C3P5E2.jpg · 0,177 · ácaro rojo | 25,79 | 85,80 | 627,27 | 1,56 |
| 7 | CIIDEA, 2019-05-01 | C5P13E1.jpg · 0,042 · sana | 25,67 | 86,15 | 518,38 | 1,53 |
| 8 | CIIDEA, 2019-05-01 | C5P28E1.jpg · 0,329 · roya 1 | 25,67 | 86,15 | 518,38 | 1,53 |
| 9 | CIIDEA, 2019-05-02 | C1P14H1.jpg · 0,024 · sana | 25,66 | 86,21 | 517,76 | 1,54 |
| 10 | CIIDEA, 2019-05-02 | C1P35E1.jpg · 0,040 · sana | 25,66 | 86,21 | 517,76 | 1,54 |

## Anexo B · Prueba de origen

**1. Cadena de procedencia.**
- **Productor:** Parraga-Alava et al., en Mendeley Data (DOI 10.17632/c5yvn32dzg.2).
- **Descarga local:** `data/raw/` el 2026-11-03 (mtime de los archivos). Verificación en el notebook el 2026-11-04.
- **SHA-256:** el de cada archivo está en `resultados/manifiesto_sha256.csv`. Las anotaciones:

| Archivo | Bytes | SHA-256 local = API Mendeley |
|---|---|---|
| RoCoLE-csv.csv | 2.220.101 | `a9aa6b411569dba7e9ba56fed79e5cd82af04a0ef092e56309158d632ac5205b` ✔ |
| RoCoLE-json.json | 2.488.394 | `286b73725b7c027a6bc9a1118a281b026e1ec9e35c3510398ed6bbc0e579cf99` ✔ |
| RoCoLE-coco.json | 1.813.080 | `beac06144c2865cd0ceb2ef3f81791334cf1674400184ff1aa123d1e67f7ec4f` ✔ |
| RoCoLe-classes.xlsx | 39.437 | `0040a57ffd441bd69ead997309d14c8d7f6fdfc83c5dbdc47805e0bc4da05ef2` ✔ |

- **Fotos:** 1.000 de 1.560 coinciden con el hash que publica la API. Las 560 restantes no aparecen en la lista de la API, que devuelve como máximo 1.000 archivos por carpeta (`content-range: items 0-999/1560`). Su hash local queda registrado.

**2. Descarga trazable.**
- Celda §1.1 del notebook. Busca primero `data/raw/` y, si no hay datos, descarga de `https://data.mendeley.com/public-api/zip/c5yvn32dzg/download/2`.
- Celda §1.2: verifica los hashes contra `https://data.mendeley.com/public-api/datasets/c5yvn32dzg/files`.
- No se usa `kaggle datasets download` ni rutas `/kaggle/input/`.

**3. Búsqueda de espejos en Kaggle** (registrada el 2026-11-04; fecha de búsqueda del equipo: `[completar]`).

| # | Coincidencia | Tipo | Observación |
|---|---|---|---|
| 1 | [Plant Disease Classification Train Dataset](https://www.kaggle.com/code/nirmalsankalana/plant-disease-classification-train-dataset) | Notebook (*code*) | Clasificación de enfermedades por imagen |
| 2 | [leaf_disease_2](https://www.kaggle.com/code/nksusth/leaf-disease-2) | Notebook (*code*) | Clasificación de enfermedad de hoja |
| 3 | [TensorFlow2. Image Classification. RoCoLe](https://www.kaggle.com/code/diegopgonzlez/tensorflow2-image-classification-rocole) | Notebook (*code*) | Clasificación de imágenes de RoCoLe con TensorFlow 2 |

El contenido de esos notebooks no se pudo leer automáticamente (la página exige JavaScript). Las observaciones salen de sus títulos. `[El equipo debe confirmar con capturas qué dataset usa cada uno y qué métrica reporta.]`

**4. Huella cruda (antes de limpiar).**
- CSV de anotaciones: 1.560 filas × 18 columnas, con 23,5 % de celdas vacías. `Benchmark Agreement`, `Benchmark ID` y `Benchmark Reference ID` están 100 % vacías.
- Imágenes: 1.560 JPEG en 3 resoluciones (1280×720, 2048×1152 y 4128×2322), de 4 dispositivos, con EXIF de orientación 6/8 y sin GPS.
- Balance: 791 sanas / 769 afectadas.
- Duplicados: 67 grupos byte a byte (134 imágenes); 27 con clase multiclase distinta y 1 con clase binaria distinta.
- 8 imágenes con `state` del polígono inconsistente con su clase.
- 1 nombre de archivo anómalo (`C11P11HE.jpg`).

**5. Contraste con espejos.**
- Los datos usados coinciden byte a byte con la **fuente primaria** (hash de Mendeley).
- Se conservan las columnas originales de Labelbox, salvo `Created By`, y los metadatos EXIF (fecha y dispositivo). Esos metadatos son los que hacen posible la clave temporal.
- `[Si un espejo de Kaggle redistribuye las imágenes, el equipo debe anotar si conserva el EXIF y las anotaciones originales.]`

## Anexo C · Checklist de protección de datos (Ley 1581 de 2012)

### Fuente 1: RoCoLe (Mendeley Data)

| Sección | Verificación | Estado |
|---|---|---|
| A. Identificadores directos e indirectos | La columna **`Created By`** de `RoCoLE-csv.csv` y el campo `Created By` de `RoCoLE-json.json` identifican al anotador de Labelbox. **Se eliminan al cargar** (notebook §1.3, con `assert`) y no aparecen en ninguna salida ni exportación. Las imágenes muestran hojas; en algunas se ve parcialmente una mano o un dedo, que no es identificable. Ninguna tiene GPS | ☑ |
| B. Datos sensibles (salud, biometría, etc.) | No aplica: son datos agronómicos | ☑ |
| C. Datos de menores | No aplica | ☑ |
| D. Base legal para datos de terceros | Datos públicos con licencia CC BY 4.0 | ☑ |
| E. Finalidad declarada | Uso académico: alerta fitosanitaria | ☑ |
| F. Desidentificación y riesgo de reidentificación | Al eliminar `Created By` se elimina el único identificador personal. Las columnas `Masks` y `View Label` contienen URL con *tokens* de Labelbox que no se usan ni se exportan | ☑ |
| G. Obligaciones de la licencia (BY) | Se cita a los autores (APA 7) en el README, la Propuesta y el informe | ☑ |
| H. Transferencia internacional | No se transfieren datos personales. Al asistente de IA solo se le compartieron esquemas y nombres de columnas, nunca valores de `Created By` | ☑ |
| I. Minimización y retención | Del JSON solo se usan `External ID` y `Label`. Los datos crudos quedan locales (`data/raw/` está en `.gitignore`) | ☑ |
| J. Publicación en el repositorio | Se publican rasgos derivados, hashes y nombres de archivo. No se publican imágenes, `Created By` ni *tokens* | ☑ |

### Fuente 2: NASA POWER

No contiene datos personales (A–C y F no aplican). Uso libre con atribución (G ☑). Se publica la serie diaria descargada (`data/external/`) con su cita.

### Firmas

| Integrante | Declaro que revisé esta lista | Fecha |
|---|---|---|
| Briyith Lisdey Herrera Cruz | `[firma]` | `[AAAA-MM-DD]` |
| Juan Pablo Becerra Tirano | `[firma]` | `[AAAA-MM-DD]` |
| Johnatan Vélez Martínez | `[firma]` | `[AAAA-MM-DD]` |
