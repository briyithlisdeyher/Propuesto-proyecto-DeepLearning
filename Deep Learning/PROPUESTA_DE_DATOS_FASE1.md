# Propuesta de Datos · Proyecto Centinela · Fase 1

> Formato oficial del curso: secciones 0 a 8 (una página) y anexos A, B y C (no cuentan en la extensión).
> Los campos marcados con **⚠ POR VERIFICAR** se llenan después de correr `src/` sobre los datos descargados. No se inventan.

## 0. Encabezado

| Campo | Detalle |
| --- | --- |
| Título del proyecto | **Centinela del Cacao: alerta temprana de monilia (*Moniliophthora roreri*) en mazorcas** |
| Integrantes | _Briyith Lisdey Herrera Cruz_  _Juan Pablo Becerra Tirano_  _Johnatan Vélez Martínez_|
| Fecha | 2026-10-30 |
| Versión | v1 (Fase 1) |

## 1. Problema, cliente y objetivo binario

- **Evento de riesgo y cliente:** dar una **alerta de monilia** para la **Federación Nacional de Cacaoteros (Fedecacao)** y sus técnicos de extensión, combinando dos preguntas: *¿la mazorca fotografiada ya muestra monilia?* (lo que se **ve**) y *¿el clima de las últimas semanas favoreció la infección?* (lo que **viene**, porque los síntomas aparecen semanas después del contagio).
- **Impacto:** la monilia puede destruir una parte grande de la cosecha. Retirar a tiempo las mazorcas enfermas, antes de que esporulen, y reforzar la vigilancia cuando el clima es favorable reduce el contagio en el lote. La herramienta apoya al técnico; no lo reemplaza.
- **Objetivo binario:** `monilia = 1` (mazorca con síntomas de monilia) / `monilia = 0` (mazorca sana). Es el mismo objetivo en la Fase 1 (solo imagen) y en la fusión de la Fase 2 (imagen + clima). En la Fase 2 la rama de imagen se entrena con **3 categorías** (sana / monilia temprana / monilia avanzada) para cumplir el requisito por rama, y la alerta se vuelve binaria agrupando «temprana + avanzada = monilia». Se pierde el estadio, que se reporta aparte como información para el técnico. Error más costoso: el **falso negativo**, porque una mazorca enferma que no se retira esporula y contagia el lote. El falso positivo cuesta una revisión manual o una mazorca sana retirada. Por eso el umbral se elige en validación con un *recall* mínimo de 0,90 para la clase monilia.

## 2. Las dos modalidades del sistema completo

- **Rama de imagen:** foto RGB de una mazorca individual, tomada con cámara digital o celular. Muestra los síntomas visibles: gibas, manchas marrones aceitosas y el micelio blanco de la esporulación.
- **Rama temporal:** clima diario de **NASA POWER** (satélite + reanálisis MERRA-2): temperatura a 2 m (`T2M`), humedad relativa (`RH2M`), lluvia corregida (`PRECTOTCORR`) y viento (`WS2M`). Va de 2001 a 2026, unas 9.400 observaciones por punto, por encima del mínimo de 1.000 que exige la Fase 2.
- **Pregunta de control: ¿la imagen contiene algo que un número no contenga?** **Sí.** El clima dice si las condiciones *favorecen* la infección, pero no si *esta* mazorca está enferma. La lesión y la esporulación solo se ven en la imagen. Son dos instrumentos físicamente independientes: una cámara y un satélite/reanálisis.

## 3. Fuentes (con enlaces y licencia)

| Modalidad | Fuente (productor primario) | Enlace o DOI | Licencia y versión | Dónde se verificó la licencia | ¿Datos de personas? |
| --- | --- | --- | --- | --- | --- |
| Imagen | Rengifo-Lozano y Sánchez-Flores, *Image Dataset of Healthy and Monilia-Infected Cocoa Pods* (Mendeley Data, v1, 2026-10-08) | https://doi.org/10.17632/ykbtpsyfv9.1 | CC BY 4.0 | Ficha del DOI en Mendeley Data (2026-10-30) | No previstos (mazorcas). ⚠ Revisar manos/rostros en las fotos y GPS en el EXIF (anexo C) |
| Temporal | NASA Langley Research Center, POWER Project (API diaria, comunidad AG) | https://power.larc.nasa.gov/ | Datos NASA de libre uso, con atribución | Página de la fuente | No |

## 4. Por qué NO es un reto resuelto

- **Dato crudo:** 8,24 GB en dos archivos `.rar` (`Monilia.rar` 5,32 GB y `Sanos.rar` 2,93 GB), con imágenes en resolución original, unos 3,8 MB por foto. No trae partición, CSV de rasgos ni balanceo: 1.342 con monilia (61,4 %) y 842 sanas (38,6 %). Exige EDA: archivos corruptos, resoluciones heterogéneas, fondos de campo y posibles **casi duplicados** (ráfagas de la misma mazorca), que se detectan con pHash.
- **No es Kaggle:** publicado el 2026-10-08 directamente en Mendeley Data. Búsqueda preliminar de espejos el 2026-10-30: sin coincidencias (se confirma en kaggle.com/datasets en el anexo B).
- **Sin solución pública:** no hay artículo ni cuaderno asociado en la ficha. Tampoco existe una versión emparejada con clima: ese acoplamiento es aporte propio.
- **No es el escenario vetado** (tulipán/KNMI) ni el de referencia (café/RoCoLe).

## 5. Plan de la Fase 1, clave de alineación y prueba de acoplamiento

- **Modalidad que se modela en la Fase 1 (aplanada a tabla): la imagen.** Cada foto se reduce a 256 px y se resume en unos 24 rasgos: media y desviación por canal RGB y HSV, índice de exceso de verde (ExG), % de píxeles «marrón lesión» y «blanco micelio» (umbrales HSV), y contraste, homogeneidad y entropía GLCM. Esa tabla entra a un MLP de dos capas ocultas en PyTorch.
- **Paso a la Fase 2 (CNN + LSTM/GRU + fusión, como pide la guía):**
  - **Rama A (imagen, CNN):** CNN con aprendizaje por transferencia (ResNet-18 o MobileNetV3) sobre las fotos crudas, más Grad-CAM. Reemplaza los rasgos de la Fase 1. Usa **3 categorías**: *sana* (842), *monilia temprana* (gibas o mancha marrón **sin** micelio) y *monilia avanzada* (micelio blanco visible). La subdivisión de las 1.342 fotos con monilia se hace a mano en unas 3 h con un protocolo escrito. Se reetiquetan 100 fotos al azar días después para medir la consistencia (kappa de Cohen), y se declara que la etiqueta la puso el estudiante, no un fitopatólogo.
  - **Rama B (serie, LSTM o GRU):** NASA POWER diario 2001–2026 (unos 9.400 días). Entrada: ventanas de 60 días con `T2M`, `RH2M`, `PRECTOTCORR` y `WS2M`. Salida: «¿la semana siguiente será de alta favorabilidad climática para monilia?», definida como ≥ 5 de 7 días con `RH2M` ≥ 85 % y `PRECTOTCORR` ≥ 1 mm; el umbral se justifica con literatura en la v2. La partición es cronológica (entrenamiento hasta 2018, validación 2019–2021, prueba 2022–2026) y el escalado se ajusta solo con entrenamiento. Se declara que esta etiqueta es un **indicador climático**, no una incidencia observada de la enfermedad.
  - **Rama C (fusión intermedia):** por cada foto se concatenan el *embedding* de la CNN y el estado final de la LSTM, calculado sobre los 60 días previos al mes de captura según la clave de alineación. Una cabeza densa predice `monilia` sí/no. **Ablación:** solo imagen / solo clima / fusión, todas con la misma partición. Si el clima no aporta (rasgo casi constante), se reporta como hallazgo.
- **Clave de alineación:**
  - [x] **Agregada: (región de origen de las fotos, mes de captura).** El mes sale de `DateTimeOriginal` del EXIF y la región, del EXIF GPS (redondeado a municipio) o de la confirmación de los autores. **⚠ POR VERIFICAR** con `src/anexo_a_acoplamiento.py`.
  - **Salvedad de fuga:** todas las fotos de un mismo mes heredan la misma ventana climática. Por eso, en la fusión de la Fase 2 la partición se hace **por mes**, no por foto. Además, los años de prueba de la rama B no se usan para entrenar la LSTM que alimenta la fusión.
  - **Salvedad de rasgo casi constante:** si todas las fotos son de pocos meses, el clima casi no varía y no discrimina. Se reporta así.
  - **Si el EXIF no trae fecha ni lugar:** se escribe a los autores y la v1 declara la clave como (región declarada, periodo de publicación), con la limitación explícita.
  - **Retardo biológico:** los síntomas visibles aparecen semanas después de la infección. Por eso la ventana climática asociada a cada foto son los **60 días previos** al mes de captura, no el mismo día.
- **Prueba de acoplamiento:** diez filas reales en el anexo A.

## 6. Línea base comprometida

| Referencia | Detalle |
| --- | --- |
| Clase mayoritaria | La clase mayoritaria es **monilia** (61,4 %), así que la línea base predice todo como enfermo: exactitud aproximada de 0,61 y *recall* de monilia de 1,00, con todas las sanas como falsa alarma. El MLP debe superar esa exactitud **sin** bajar el *recall* de 0,90. Ambas cifras se reportan en el conjunto de prueba. |
| ¿La modalidad aplanada resume un escalar? | Sí: **% de píxeles «marrón lesión»** (umbral HSV) |
| Escalar crudo usado solo | Clasificador de un solo umbral sobre ese %, con el umbral elegido en validación y el desempeño reportado en prueba. |
| Partición y semilla | Partición estratificada 70/15/15, `seed = 42`. Los casi duplicados (pHash ≤ 5) quedan **en el mismo subconjunto** (`GroupShuffleSplit`). Se conserva para la Fase 2. |

## 7. Riesgos éticos y protección de datos

| Riesgo | Daño para el cliente | Mitigación |
| --- | --- | --- |
| Sesgo de muestreo o representatividad: las fotos son de un origen no colombiano o desconocido, con clones y luz distintos a los de las fincas de Fedecacao | El modelo falla en campo colombiano y el técnico confía en una herramienta que no se validó allí | Declarar el origen; reportar el desempeño por resolución y cámara si el EXIF lo permite; recomendar una validación piloto con fotos de Fedecacao antes de usarla (Fase 3) |
| Falsa alarma (mazorca sana marcada como enferma) | El productor retira mazorcas sanas o aplica fungicida sin necesidad: costo y daño ambiental | Umbral elegido por costo; la alerta pide confirmación visual del técnico; se reporta la tasa de falsos positivos |
| Etiqueta de estadio (temprana/avanzada) puesta por un no experto (Fase 2) | El modelo aprende el criterio del estudiante, no el de un fitopatólogo, y el estadio que se informa puede estar equivocado | Protocolo escrito con fotos de referencia, kappa de reetiquetado reportado y la alerta binaria (que usa la etiqueta original de los autores) como salida principal |
| Alarma omitida (mazorca enferma marcada como sana) | La mazorca esporula y contagia el lote, con pérdida de cosecha y de ingreso del pequeño productor | Exigir *recall* de monilia ≥ 0,90 en validación; analizar los falsos negativos con Grad-CAM (Fase 2); mensaje al usuario: «sin alerta ≠ sano» |

El checklist de protección de datos va en el anexo C, uno por fuente. Principio del Marco Ético para la IA en Colombia que se discute: **transparencia y explicación** (informar al cliente la tasa de falsos negativos y positivos en lenguaje claro).

## 8. Cita APA 7 de cada fuente

- Rengifo-Lozano, D., & Sánchez-Flores, J. (2026). *Image dataset of healthy and Monilia-infected cocoa pods for disease classification* (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/ykbtpsyfv9.1
- NASA Langley Research Center. (2026). *Prediction of Worldwide Energy Resources (POWER) Project: Daily agroclimatology data* [Data set]. https://power.larc.nasa.gov/

---

## Anexo A · Prueba de acoplamiento

Clave: **(región, mes de captura)** → clima medio de los 60 días previos (NASA POWER).
Generado con `python src/anexo_a_acoplamiento.py --fotos data/raw --lat <LAT> --lon <LON>`.

| N.º | Clave (región, mes) | Dato de la rama de imagen (archivo, clase) | Dato de la serie (RH2M media 60 d, %) |
| --- | --- | --- | --- |
| 1 | ⚠ | ⚠ | ⚠ |
| 2 | ⚠ | ⚠ | ⚠ |
| 3 | ⚠ | ⚠ | ⚠ |
| 4 | ⚠ | ⚠ | ⚠ |
| 5 | ⚠ | ⚠ | ⚠ |
| 6 | ⚠ | ⚠ | ⚠ |
| 7 | ⚠ | ⚠ | ⚠ |
| 8 | ⚠ | ⚠ | ⚠ |
| 9 | ⚠ | ⚠ | ⚠ |
| 10 | ⚠ | ⚠ | ⚠ |

> ⚠ Se llena con la salida real del script (`anexo_a.csv`). Si el EXIF no trae fecha, se reemplaza esta tabla por la clave de respaldo de la sección 5 y se declara.

## Anexo B · Evidencias del test de procedencia

1. **Cadena de procedencia** (generada por `src/anexo_b_procedencia.py`):

| Archivo (nombre exacto) | URL o DOI del productor primario | Fecha de descarga | Huella SHA-256 |
| --- | --- | --- | --- |
| `Monilia.rar` | https://doi.org/10.17632/ykbtpsyfv9.1 | ⚠ AAAA-MM-DD | ⚠ |
| `Sanos.rar` | https://doi.org/10.17632/ykbtpsyfv9.1 | ⚠ AAAA-MM-DD | ⚠ |
| `power_daily.csv` | https://power.larc.nasa.gov/api/temporal/daily/point | ⚠ AAAA-MM-DD | ⚠ |

2. **Descarga trazable:** las celdas descargan desde Mendeley Data y la API de NASA POWER. `grep -inE "kaggle|kagglehub|/kaggle/input" *.ipynb` → sin resultados.
3. **Búsqueda declarada de espejos:** ⚠ fecha · `site:kaggle.com "Monilia-Infected Cocoa Pods"` y búsqueda en kaggle.com/datasets de «cocoa monilia» → _(sin coincidencias / lista de hasta 3 URL)_. Nota: existen en Kaggle otros conjuntos de cacao (*cacao-diseases*, *Cocoa Localisation*) de **origen distinto**. Se muestra que no coinciden (punto 5).
4. **Huella de crudeza (antes de limpiar):** 2.184 imágenes × (archivo, clase, ancho, alto, MB, EXIF fecha, EXIF GPS) · ⚠ % de archivos ilegibles · ⚠ % sin fecha EXIF · ⚠ n.º de casi duplicados · balance 61,4 / 38,6.
5. **Contraste con el espejo:** los conjuntos de cacao de Kaggle tienen otro número de imágenes y otras clases (p. ej., 4.291 imágenes sanas/podridas en *cacao-diseases*), y ninguna huella coincide con `Monilia.rar` ni con `Sanos.rar`.

## Anexo C · Checklist de protección de datos (Ley 1581 de 2012)

**Fuente 1: imágenes de mazorcas (Mendeley).** Resultado: ☐ Sin datos de personas ☐ Anonimizados por la fuente.

- **A.** Se revisaron las imágenes en busca de rostros o manos identificables, y el EXIF en busca de GPS exacto (las coordenadas de una finca identifican a su dueño). ⚠
- **B, C.** No hay datos sensibles ni de menores.
- **D.** Fuente pública con licencia CC BY 4.0.
- **E.** Finalidad: uso académico para entrenar y evaluar un modelo en el curso; no se toman decisiones sobre personas identificadas.
- **F.** Se **borra el EXIF** y el GPS se redondea a municipio **antes** de subir a Colab, Drive o GitHub, o de mostrarlo a un asistente de IA.
- **G.** CC BY 4.0: atribuir a los autores e indicar los cambios («rasgos tabulares derivados»).
- **H.** A Colab, Drive y GitHub solo se suben datos sin personas identificables.
- **I.** Los datos crudos se borran al terminar la Fase 3.
- **J.** `data/` va en `.gitignore`; el repositorio trae solo los scripts de descarga.

**Fuente 2: NASA POWER.** Resultado: ☑ Sin datos de personas. Datos de una cuadrícula climática, sin titulares. Atribución a NASA LaRC POWER.

| Integrante | Firma | Fecha |
| --- | --- | --- |
| | | |
