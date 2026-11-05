# Auditoría a la IA · Proyecto Centinela · Fase 1

Se documentan tres sugerencias de la IA que el equipo **no aceptó tal cual**:

| Caso | Sugerencia de la IA | Decisión | Dónde se ve en el notebook |
|---|---|---|---|
| 1 | Eliminar los duplicados detectados (byte a byte y casi duplicados) para evitar fugas | **Rechazada** | §2.5 y §5.2: se detectan, pero no se elimina ninguna foto |
| 2 | Partir los datos por hoja o foto | **Modificada** → partición por planta | §6 (partición) y §13.2 (reproducción) |
| 3 | Paciencia de 10 épocas en la parada temprana | **Modificada** → 25 épocas | §10 y §13.1 (reproducción) |

Las cifras provienen de `resultados/resultados.json` (claves `huella_crudeza`, `auditoria` y `auditoria_paciencia`).

## Caso 1: eliminar duplicados (RECHAZADA)

| Campo | Contenido |
|---|---|
| Entrada relacionada | E-9 |
| Contexto | Notebook §2.5 (huella de crudeza) y §5.2 (grupos) |
| Qué dijo la IA | Identificar los duplicados de las imágenes y eliminarlos para evitar posibles fugas byte a byte entre entrenamiento y prueba |
| Evidencia de origen | `[Captura del equipo con la salida literal de la IA, fecha y herramienta]` |
| Por qué se rechazó | Con datos tabulares no es recomendable eliminar duplicados. La comparación de filas no reconoce el contexto ni las vecindades, como sí ocurre al analizar las imágenes, y es potencialmente riesgoso eliminar registros que en realidad no son duplicados |
| Evidencia que respalda el rechazo | De los 67 grupos de fotos idénticas byte a byte, **27 tienen clases multiclase distintas** entre sus copias y 1 tiene clase binaria distinta. Eliminar una copia obligaría a escoger una etiqueta sin criterio, y se perdería información de la fuente |
| Qué se hizo en su lugar | Los duplicados se **detectan y se reportan**, y las **1.560 fotos se conservan**. La detección solo se usa para que las copias queden en el mismo subconjunto de la partición (`assert` en §6) |
| Lección | Detectar no es lo mismo que eliminar: la detección sirve para controlar la fuga sin perder datos |

## Caso 2: partición por hoja en lugar de por planta (MODIFICADA)

| Campo | Contenido |
|---|---|
| Entrada relacionada | E-10 (sugerencia) y E-6 (celda de reproducción) |
| Contexto | Notebook §6 (partición) y §13.2 (reproducción) |
| Qué dijo la IA | Partir los datos por hoja o foto, con `train_test_split(..., stratify=y)` |
| Evidencia de origen | `[Captura del equipo con la salida literal de la IA, fecha y herramienta]` |
| Por qué se modificó | Cada planta tiene 4 fotos: 2 hojas × 2 caras (§2.2). Partir por foto deja en prueba fotos de plantas que el modelo ya vio en entrenamiento, así que la prueba deja de ser independiente |
| Corrección aplicada | Partición **agrupada por planta** con `StratifiedGroupKFold`. Se verifica con `assert` que ninguna planta quede en dos subconjuntos |
| Reproducción | Celda §13.2: la partición por foto, con la misma semilla, la misma configuración y la misma regla de umbral |
| Resultado de medición | Partición por foto: el **99,1 %** de las fotos de prueba tiene una hermana en entrenamiento, y **20** son copias exactas. Métricas en su propia prueba: AUC 0,914, *recall* 0,948, costo 80. Partición por planta: AUC 0,936, *recall* 0,975, costo 54 |
| Lección | En esta semilla la fuga no infló la métrica. Por eso se controla por construcción, y no se espera a ver una cifra sospechosa |

## Caso 3: paciencia de la parada temprana (MODIFICADA, fallo real con métrica)

| Campo | Contenido |
|---|---|
| Entrada relacionada | E-4 |
| Contexto | Notebook §9 (bucle) y §10 (corridas regularizadas) |
| Qué dijo la IA | Claude Opus 5.5 generó `PACIENCIA = 10`, tomando el rango de 5 a 10 épocas que sugiere la actividad |
| Evidencia de origen | Historial de la sesión del 2026-11-04. En la primera ejecución, R2 y R4 se detuvieron en la época 57 con pérdida de validación ≈ 0,43. `[Captura del equipo]` |
| Por qué estaba mal | Con lote completo, 1 época = 1 paso de Adam. 10 épocas sin mejora son solo 10 actualizaciones, así que el entrenamiento se detiene en mesetas cortas |
| Cómo se detectó | Por un resultado inverosímil: configuraciones casi iguales terminaron muy distintas (0,43 frente a 0,32–0,34) |
| Corrección aplicada | `PACIENCIA = 25` en §10, con la justificación en el texto |
| Reproducción | Celda §13.1: R2 con la misma semilla, paciencia 10 frente a 25. La métrica se mide en **validación** |
| Resultado de medición | Paciencia 10: se detiene en la época 57, **AUC 0,893**, costo **79**. Paciencia 25: se detiene en la época 153, **AUC 0,942**, costo **53** |
| Lección | Un hiperparámetro "recomendado" se traduce a la unidad real del algoritmo: pasos de gradiente, no épocas |
