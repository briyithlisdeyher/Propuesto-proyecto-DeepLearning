# Prompt mejorado (dos iteraciones)

## Iteración 1 — ordenar y desambiguar

> Actúa como experto en Deep Learning y en la rúbrica del Proyecto Centinela (USTA).
>
> **Contexto.** Nuestro equipo (Briyith Lisdey Herrera Cruz, Juan Pablo Becerra Tirano, Johnatan Vélez Martínez) propuso el dataset de mazorcas de cacao con monilia (Mendeley `ykbtpsyfv9/1`) en el repositorio `johnatan123456789-cmd/Propuesto-proyecto-DeepLearning`. Los autores nos respondieron que las fotos se tomaron en Tocache, Huallaga y Rioja, pero ninguna imagen trae su ubicación individual, así que no podemos construir la clave de alineación espaciotemporal. Cambiamos a RoCoLe (Mendeley `c5yvn32dzg/2`).
>
> **Tareas, en este orden:**
> 1. Reescribe el `README.md` explicando el cambio de dataset y su motivo.
> 2. Reescribe `Propuesta_de_datos.md` para RoCoLe siguiendo la plantilla 12, el catálogo 14 y la actividad 11.
> 3. Entrega un diagrama lógico del notebook de la Fase 1 y **detente** hasta que yo lo apruebe.
> 4. Tras la aprobación: notebook, informe, bitácora (plantilla 13) y auditoría.
>
> **Restricción:** no elimines duplicados byte a byte.

## Iteración 2 — añadir criterios verificables y puntos de control

> *(Todo lo de la iteración 1, más:)*
>
> - **Fuente de verdad:** la rúbrica v1.4 de la actividad 11. Cada decisión del flujo debe nombrar el criterio (C1–C6) que cubre.
> - **No inventar datos.** Lo que solo se conoce tras descargar el dataset (hash SHA-256, las 10 filas de acoplamiento, el conteo de duplicados, las fechas EXIF) queda marcado `[POR VERIFICAR]`. Nunca se rellena con cifras supuestas.
> - **Duplicados:** se detectan (SHA-256 y pHash) y se reportan, pero **se conservan**. Los duplicados o casi duplicados se fuerzan a caer en el mismo subconjunto de la partición, para evitar fugas sin borrar ninguna imagen.
> - **Riesgos del nuevo dataset:** señala explícitamente cualquier riesgo que repita el problema que motivó el cambio (por ejemplo, la falta de fecha por imagen).
> - **Decisiones abiertas:** las que me tocan a mí (objetivo binario, cliente, clave temporal) van como preguntas con una opción recomendada.
> - **Publicación:** no hagas *push* a GitHub. Entrega los archivos listos para que yo los suba.
