# Bitácora de IA · Proyecto Centinela

> **Nota para el equipo.** Esta bitácora la redactó el asistente a partir de lo que ocurrió en la sesión del 2026-11-04. Cada integrante debe revisarla, completar los campos `[ ]` (hora, integrante, captura) y **confirmar o cambiar la decisión**: la decisión y su justificación tienen que ser del equipo. Las entradas remiten a celdas con la etiqueta de sección del notebook.

## 1. Datos de la entrega

| Campo | Detalle |
|---|---|
| Integrantes | Briyith Lisdey Herrera Cruz · Juan Pablo Becerra Tirano · Johnatan Vélez Martínez |
| Proyecto | Centinela del Café (hoja afectada sí/no, RoCoLe) |
| Fase | 1 |
| Identificador inicial | E-1 |
| Fecha de entrega | `[2026-11-04]` |

## 2. Declaración de uso (Opción A)

| Herramienta | Modelo y versión | Propósito |
|---|---|---|
| Claude Code (aplicación de escritorio, Anthropic) | Claude Opus 5.5 (`claude-opus-5-5`) | Reestructurar el repositorio por el cambio de dataset; diseñar el flujo; escribir el notebook, el generador del informe y los documentos; inspeccionar los datos localmente |

- **Partes redactadas sin IA:** `[completar: p. ej., la decisión de las D1–D5, el contacto con los autores del dataset de cacao, la búsqueda en Kaggle]`.
- **Datos compartidos con la IA:** el asistente ejecutó código local sobre `data/raw/`. Vio nombres de archivo, conteos, la estructura de columnas y valores de ejemplo de las anotaciones (polígonos y URL de Labelbox). **Los valores de `Created By` se omitieron explícitamente** en todas las inspecciones y nunca se mostraron. No hay datos personales en las imágenes.
- **Firmas:** `[cada integrante, con fecha]`.

## 3. Registro de interacciones

### E-1 · Reestructuración inicial y primer flujo

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04 |
| Fase · paso | F1 · Paso 0 (Propuesta) |
| Herramienta y modelo | Claude Code · Claude Opus 5.5 |
| Celda o *commit* | `README.md`, `Propuesta_de_datos.md`, `docs/flujo_logico_fase1.md` · `# E-1` |
| Objetivo | Documentar el cambio de dataset (cacao → RoCoLe) y proponer el flujo de la Fase 1 |
| Indicación (resumen) | Ajustar el README por el cambio de dataset, aplicar las plantillas 11–14 y entregar el diagrama sin desarrollar la fase |
| Qué devolvió la IA | README v2, Propuesta v2 y diagrama de 19 pasos con las decisiones D1–D4. Propuso como objetivo "roya vs no roya" |
| Datos compartidos | Ninguno (solo URL públicas) |
| Decisión | **Modificada** |
| Justificación | El equipo cambió D1 a "hoja afectada" (sana vs ácaro o roya), D3 a 60 días y D5 a organizaciones de monitoreo fitosanitario, y pidió detallar el EDA |
| Cómo se verificó | Revisión del equipo contra la rúbrica v1.4 |
| Evidencia de origen | Salida literal de la IA: *"D1 · Objetivo binario: Roya (1–4) vs no roya (sana + ácaro)"* 
<img width="762" height="704" alt="image" src="https://github.com/user-attachments/assets/151cac32-dbef-4740-a013-4d52fdbf41d2" />
|

### E-2 · Afirmación no verificada sobre trabajos previos

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04 |
| Fase · paso | F1 · Paso 0 (Propuesta §4) |
| Celda o *commit* | `Propuesta_de_datos.md` §4 · `# E-2` |
| Objetivo | Argumentar por qué no es un reto resuelto |
| Qué devolvió la IA | *"No hay una solución pública que una RoCoLe con clima. Los trabajos publicados son clasificadores solo de imagen."* |
| Datos compartidos | Ninguno |
| Decisión | **Rechazada** (la afirmación) / **Modificada** (el texto) |
| Justificación | Era una afirmación sin búsqueda que la respaldara. Se reemplazó por la evidencia del Anexo B: los 3 notebooks de Kaggle que encontró el equipo |
| Cómo se verificó | Búsqueda del equipo en Kaggle → 3 coincidencias (Anexo B) |
| Evidencia de origen | Texto literal arriba (respuesta 1 de la sesión)
<img width="796" height="168" alt="image" src="https://github.com/user-attachments/assets/c9c762e4-3fc7-4abd-abb9-a0f2ec5bc1b2" />
|

### E-3 · Inspección del dataset descargado

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04 |
| Fase · paso | F1 · Paso 1 |
| Celda o *commit* | Notebook §1.2–1.3, §2.1–2.5 · `# E-3` |
| Objetivo | Verificar la clave temporal, la estructura de las anotaciones y los duplicados |
| Qué devolvió la IA | Encontró fechas EXIF en las 1.560 imágenes (5 días), 4 celulares, el patrón de nombre `C<n>P<n><H/E><n>`, 390 plantas × 4, 67 grupos de duplicados byte a byte, un nombre anómalo y 0 GPS. Detectó que los polígonos están en coordenadas crudas, comprobado con una superposición visual |
| Datos compartidos | Esquema y nombres de columnas; `Created By` omitido |
| Decisión | **Aceptada** |
| Justificación | Las cifras se reproducen en el notebook y coinciden con el artículo (791 / 344 / 166 / 62 / 30 / 167) |
| Cómo se verificó | El notebook §1.3 compara JSON y XLSX: la clase multiclase coincide en el 100 % de las fotos (`assert`) |
| Evidencia de origen | Salidas de las celdas §2.2, §2.4 y §2.5 |

### E-4 · Paciencia de la parada temprana (fallo real → auditoría)

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04 |
| Fase · paso | F1 · Pasos 3–4 |
| Celda o *commit* | Notebook §10 (`PACIENCIA`), §13.1 · `# E-4` |
| Objetivo | Configurar la parada temprana |
| Qué devolvió la IA | `PACIENCIA = 10` |
| Datos compartidos | Ninguno adicional |
| Decisión | **Modificada** → `PACIENCIA = 25` |
| Justificación | Con lote completo, una época es un solo paso de gradiente; 10 épocas detienen el entrenamiento en mesetas |
| Cómo se verificó | Celda §13.1, en validación. Paciencia 10: AUC 0,893 y costo 79. Paciencia 25: AUC 0,942 y costo 53 |
| Evidencia de origen | Primera ejecución: R2 y R4 detenidos en la época 57 con pérdida de validación ≈ 0,43
<img width="685" height="58" alt="image" src="https://github.com/user-attachments/assets/f0d5fab6-faed-404a-9b3b-0c99a3bb21fe" />
|

### E-5 · Partición desbalanceada por grupos grandes

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04 |
| Fase · paso | F1 · Paso 1 (partición) |
| Celda o *commit* | Notebook §6 · `# E-5` |
| Qué devolvió la IA | Asignó los pliegues 14/3/3 por índice con `StratifiedGroupKFold(20)` |
| Decisión | **Modificada** |
| Justificación | La partición resultó en 64,9 / 21,5 / 13,6 % porque hay un grupo de 92 imágenes. Se eligieron los pliegues por tamaño, sin usar la etiqueta |
| Cómo se verificó | Nueva partición: 70,0 / 14,9 / 15,1 %, con `assert` de cero grupos compartidos |
| Evidencia de origen | Salida de la primera ejecución: `pct_imagenes` 0,649 / 0,215 / 0,136
<img width="815" height="419" alt="image" src="https://github.com/user-attachments/assets/06bfd538-5f39-40ef-a023-39d6ce5dc7da" />
|

### E-6 · Auditoría inducida de la partición por imagen

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04 |
| Fase · paso | F1 · Paso 6 |
| Celda o *commit* | Notebook §13.2 · `# E-6` |
| Qué devolvió la IA | La celda reproducible que compara la partición ingenua con la agrupada |
| Decisión | **Aceptada** |
| Justificación | Cuantifica la fuga estructural (99,1 % de las imágenes de prueba con una hermana en entrenamiento; 20 copias exactas) |
| Cómo se verificó | Misma semilla y misma regla de umbral; ver `resultados.json → auditoria` |
| Evidencia de origen | Salida de la celda §13.2 |

### E-7 · Simplificación del notebook y exploración inicial

| Campo | Contenido |
|---|---|
| Fecha y hora | 2026-11-04|
| Fase · paso | F1 · Pasos 1–2 |
| Celda o *commit* | Notebook completo (§1–§3 rehechas) · `# E-8` |
| Objetivo | Que el flujo empiece por cómo vienen los datos y explique qué variables se agregan y por qué |
| Qué devolvió la IA (versión anterior) | Un EDA que empezaba directamente por los 28 rasgos derivados, sin mostrar cuántas plantas, hojas o fotos sanas y afectadas había, y con código denso (funciones genéricas, reasignación de variables globales) |
| Decisión | **Modificada** a pedido del equipo |
| Justificación | El EDA debe partir de los datos crudos. Ahora muestra 12 cultivos, 390 plantas, 1.560 fotos, unas 780 hojas inferidas, el balance 791/769 y la tabla de variables iniciales antes de construir los rasgos |
| Cómo se verificó | Ejecución completa desde cero sin errores. Las métricas finales son idénticas a las de la versión anterior (R3a, umbral 0,22, costo 54, AUC 0,936) |
| Evidencia de origen | Solicitud del equipo en la sesión del 2026-11-05 <img width="868" height="346" alt="image" src="https://github.com/user-attachments/assets/2644eb32-222a-45f4-9615-f6c8f86e5248" />|

### E-8 · Eliminar duplicados (rechazada)

| Campo | Contenido |
|---|---|
| Fecha y hora | `[2026-11-04]` |
| Fase · paso | F1 · Paso 1 (datos) |
| Celda o *commit* | Notebook §2.5 y §5.2 · `# E-9` |
| Qué devolvió la IA | Identificar los duplicados de las imágenes y eliminarlos para evitar posibles fugas byte a byte |
| Datos compartidos | Ninguno |
| Decisión | **Rechazada** |
| Justificación | Con datos tabulares no es recomendable eliminar duplicados. La comparación de filas no reconoce el contexto ni las vecindades, como sí se hace en las imágenes, y es potencialmente riesgoso eliminar registros que no son realmente duplicados. Además, 27 de los 67 grupos de copias exactas tienen clases distintas |
| Cómo se verificó | El notebook conserva las 1.560 fotos. Los duplicados solo se usan para agrupar la partición (`assert` en §6) |
| <img width="809" height="203" alt="image" src="https://github.com/user-attachments/assets/ca8e3468-dd3c-4430-a310-1d17db7fa967" />
| <img width="741" height="441" alt="image" src="https://github.com/user-attachments/assets/ebfff1d0-ebc1-4ef4-a19e-c54539ad59ee" />|


