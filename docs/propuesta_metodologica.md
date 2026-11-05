# Propuesta metodológica · Fase 1

Versión aprobada el 2026-11-04 con las decisiones D1–D5 del equipo. Las cifras de resultados vienen de `resultados/resultados.json`.

## 1. Decisiones del equipo

| # | Decisión |
|---|---|
| D1 | **Objetivo: ¿hoja afectada? sí/no.** Sana = 0 (791 hojas); ácaro rojo o roya de cualquier nivel = 1 (769 hojas) |
| D2 | **Unidad de análisis:** la hoja. Los rasgos se calculan solo sobre los píxeles del polígono de la hoja |
| D3 | **Ventana climática:** los 60 días previos a la fecha de captura (de `d−60` a `d−1`) |
| D4 | **Costo FN:FP = 5:1**, dentro del rango de 3 a 8 veces que cuesta dejar pasar un defecto en un control de calidad |
| D5 | **Cliente:** las organizaciones de monitoreo fitosanitario, a través de sus técnicos de sanidad |

## 2. Duplicados: se detectan, no se eliminan

| Tipo | Detección | Resultado | Acción |
|---|---|---|---|
| Exactos, byte a byte | SHA-256 | 67 grupos (134 imágenes), todos entre plantas distintas; 27 con clase multiclase distinta | **Se conservan** con su etiqueta original y se unen en `id_grupo` |
| Casi duplicados | pHash con distancia de Hamming ≤ 5 | 15 pares adicionales | Se unen en `id_grupo` |
| Misma planta | Nombre de archivo `C<n>P<n>` | 390 plantas × 4 imágenes | Mismo `id_grupo` |

Resultado: 342 grupos. El más grande reúne 92 imágenes, porque los duplicados encadenan plantas.

## 3. De imagen a tabla

Se usa el polígono de Labelbox, que está en coordenadas crudas del JPEG; se verificó que no hay que aplicar la rotación EXIF. La hoja se recorta, se redimensiona a 256 px y se calculan **28 rasgos**:

| Familia | Rasgos |
|---|---|
| Color | Media y desviación de R, G, B, H, S, V; media de a* y b* |
| Lesión | `pct_verde`, `pct_naranja`, `pct_amarillo`, `pct_oscuro`, `pct_lesion` |
| Índices | ExG, VARI, R/G |
| Textura | GLCM: contraste, disimilitud, homogeneidad, energía, correlación |
| Forma | `fraccion_hoja` |

**Al modelo entran 27**, porque `pct_verde` es igual a `1 − pct_lesion` por construcción. El escalar crudo de la línea base es `pct_lesion`.

## 4. Partición y fugas

- `StratifiedGroupKFold` con 20 pliegues sobre `id_grupo` y semilla 42.
- Se eligen 3 pliegues de validación y 3 de prueba según su tamaño, para acercarse al 15 % cada uno; en esa elección no se usa la etiqueta. Resultado: 70,0 / 14,9 / 15,1 %.
- Se verifica con `assert` que no hay grupos ni duplicados exactos compartidos entre subconjuntos.
- `StandardScaler` se ajusta solo con entrenamiento.

## 5. Modelo, entrenamiento y regularización

- **MLP:** salida logit + `BCEWithLogitsLoss`, `y` en forma (N, 1) float.
- **Optimización:** Adam con lr 1e-2 y lote completo. Checkpoint cada 10 épocas.
- **Parada temprana con paciencia 25.** Con lote completo, 1 época equivale a 1 paso de gradiente. Con paciencia 10, R2 y R4 se detenían en una meseta temprana.

| Corrida | Configuración | Pérdida mín. de validación (época) | Brecha en el mínimo |
|---|---|---|---|
| R0 | 16 → 8, 50 épocas | 0,419 (42) | 0,028 |
| R1 | 256 → 128, sin dropout, 1.500 épocas | 0,370 (30) | 0,135 (en la época 1.500: 1,99) |
| R1-ES | R1 + parada temprana | 0,370 (30) | 0,135 |
| R2 | 16 → 8, Dropout 0,3 + PT | 0,361 (128) | 0,056 |
| **R3a** | **8 → 4, Dropout 0,3 + PT** | **0,324 (165)** | **0,002** |
| R3b | 64 → 32, Dropout 0,3 + PT | 0,327 (97) | 0,111 |
| R4 | R2 + L2 1e-3 | 0,359 (123) | 0,046 |

**Modelo final: R3a**, el de menor pérdida mínima de validación; la elección se hizo solo con validación.

## 6. Evaluación

- **Umbral** fijado en validación: el de menor `5·FN + FP` con *recall* ≥ 0,90 → **0,22**.
- **Prueba** (una sola vez, n = 236):

| Modelo | *Recall* afectada | Precisión afectada | F1 | AUC | Costo |
|---|---|---|---|---|---|
| MLP R3a | 0,975 | 0,748 | 0,847 | 0,936 | 54 |
| Escalar crudo `pct_lesion` | 0,992 | 0,578 | 0,731 | 0,789 | 91 |
| Clase mayoritaria | 0 | 0 | 0 | 0,5 | 595 |

- **Subgrupos:**
  - Detección de 0,964 en ácaro rojo y en roya 1, y de 1,0 en roya 2–4. Los n de roya 3 y roya 4 son muy pequeños.
  - La tasa de falsa alarma en hojas sanas va de 0,10 a 0,54 según el celular. Dispositivo y fecha están confundidos.

## 7. Riesgos

| Tipo | Riesgo | Mitigación |
|---|---|---|
| Metodológico | Las ventanas climáticas son casi idénticas (5 fechas) | Declararlo: en la Fase 2 el clima es contexto, no señal por hoja |
| Metodológico | Fuga por plantas o duplicados | Partición agrupada con `assert` (ver la auditoría en el notebook §13.2) |
| Metodológico | Ruido de etiqueta en duplicados | Se reporta y se agrupa; no se corrige a mano |
| Metodológico | La máscara viene de la anotación humana | En la Fase 2 la CNN trabajará sobre la imagen; la segmentación automática queda como trabajo futuro |
| Ético | Dominio estrecho | No extrapolar sin un piloto |
| Ético | FN | *Recall* ≥ 0,90 y el aviso "sin alerta ≠ sana" |
| Ético | FP | Confirmación humana y seguimiento por celular |
| Datos | `Created By` (dato personal) | Se elimina al cargar |

## 8. Evolución hacia la Fase 2

| Elemento | Fase 1 | Fase 2 |
|---|---|---|
| Imagen | 27 rasgos hechos a mano → MLP | CNN con *transfer learning* sobre la hoja |
| Clima | Solo se verifica el acoplamiento (Anexo A) | LSTM/GRU sobre 60 días diarios de NASA POWER |
| Fusión | — | Concatenación de *embeddings* → cabeza binaria |
| Se conserva | `particion.csv`, semilla 42, regla de umbral (costo 5:1 con *recall* ≥ 0,90), líneas base | Punto de comparación |
