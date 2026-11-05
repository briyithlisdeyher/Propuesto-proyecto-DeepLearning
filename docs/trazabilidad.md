# Trazabilidad: requisitos de la actividad → entregables

Las secciones "§" remiten a los encabezados numerados del notebook `notebooks/Centinela_Fase1.ipynb`.

| Requisito (actividad 11, rúbrica v1.4) | Criterio | Dónde se cumple |
|---|---|---|
| Propuesta aprobada en compuerta (no Kaggle, no réplica, no escenario vetado) | Admisibilidad | `Propuesta_de_datos.md` + Anexo B · notebook §1.1–1.2 |
| Sin personas identificables; dato del anotador eliminado | Admisibilidad | Anexo C · notebook §1.3 (se elimina `Created By` del CSV y del JSON) |
| Cuaderno ejecutable con "Ejecutar todo" | Admisibilidad | Notebook ejecutado de inicio a fin con `nbconvert --execute` |
| Objetivo binario y cliente | C1 | Notebook, encabezado y §2.3 · Propuesta §1 · Informe §1 |
| Dos modalidades reales de instrumentos distintos | Compuerta | Propuesta §2–3 |
| Clave de alineación + 10 filas reales | Compuerta | Notebook §2.4 (fecha EXIF) y §5.1 · `resultados/acoplamiento_10_filas.csv` · Anexo A |
| EDA de cómo vienen los datos (plantas, hojas, balance, variables iniciales) | C1 | Notebook §2.1–2.6 |
| Huella de crudeza | Anexo B | Notebook §2.5 · `resultados.json → huella_crudeza` |
| Variables agregadas y su justificación | C1 | Notebook §3 |
| EDA de las variables agregadas, con cada hallazgo vinculado a una decisión | C1 | Notebook §4.1–4.4 · `resultados/eda_decisiones.csv` |
| Partición train/valid/test justificada (agrupada y estratificada) | C1 | Notebook §5.2 y §6 · `resultados/particion.csv` |
| Escalador ajustado después de partir, solo con train | C1 | Notebook §7 |
| Línea base: clase mayoritaria + escalar crudo, calculada en el cuaderno | C1, C4 | Notebook §11.1–11.2 |
| MLP en PyTorch, ≥ 2 capas ocultas, salida logit, BCEWithLogitsLoss, `y` (N,1) float | C2 | Notebook §7–8 · `src/modelo.py` |
| Activaciones justificadas con argumento propio | C2 | Notebook §8 · Informe §3 |
| Capacidad justificada con una comparación medida | C2 | R3a / R2 / R3b · notebook §10 |
| Bucle explícito (forward, pérdida, zero_grad, backward, step) | C2 | Notebook §9 (`entrenar`) |
| Semillas fijas y código comentado por secciones | C2 | Notebook §0 |
| Checkpoints cada 10 épocas | Paso 3 de la actividad | Notebook §9 |
| ≥ 2 corridas: una con sobreajuste y una regularizada, con época del mínimo | C3 | R1, R2 · notebook §10 |
| Modelo final = mínimo de validación restaurado; efecto cuantificado; ≥ 2 intervenciones en tabla | C3 | Notebook §10 · `resultados/tabla_corridas.csv` |
| Curvas train/valid con el mínimo marcado (línea discontinua) y rótulos | C3 | `resultados/figuras/curvas_*.png` |
| Umbral elegido en validación según el costo | C4 | Notebook §11.1 |
| Prueba evaluada una sola vez; matriz 2×2; P/R/F1 por clase | C4 | Notebook §11.2 |
| Errores por subgrupo | C4 | Notebook §11.3 |
| Marco Ético para la IA en Colombia → decisión concreta | C4 | Notebook §12.3 · Informe §5 |
| Bitácora con ≥ 3 entradas fechadas; cada una remite a una celda | C5 | `docs/Bitacora_IA.md` |
| Auditoría reproducible (celda original y corregida, misma semilla y métrica) | C5 | Rechazada: eliminar duplicados (§13, §2.5). Modificada: partición por hoja → por planta (§13.2). Modificada: paciencia de 10 → 25 (§13.1). Detalle en `docs/Auditoria_IA.md` |
| Informe PDF de ≤ 4 páginas, 5 secciones, APA 7 | C6 | `informe/Informe_Fase1.pdf` |
| Cifras del informe tomadas del cuaderno | C6 | `resultados/resultados.json` → `informe/generar_informe.py` |
| Continuidad con la Fase 2 (partición, semilla y línea base conservadas) | Actividad | `particion.csv` · `docs/propuesta_metodologica.md` §8 |
| Restricción del equipo: no eliminar duplicados byte a byte | Equipo | Notebook §2.5, §5.2 y §6 (`assert`) |
| Sustentación: cada integrante explica una sección | Compuerta de autoría | Reparto propuesto en `docs/Bitacora_IA.md` §5 |
