# Propuesta-proyecto-DeepLearning
# Centinela del Cacao

Alerta temprana de monilia (*Moniliophthora roreri*) en mazorcas de cacao para la **Federación Nacional de Cacaoteros (Fedecacao)**.
Proyecto Centinela · Deep Learning · USTA.

- 📄 **[Propuesta de Datos · Fase 1](PROPUESTA_DE_DATOS_FASE1.md)** (compuerta de aprobación)
- Imagen: [Rengifo-Lozano y Sánchez-Flores (2026), Mendeley Data](https://doi.org/10.17632/ykbtpsyfv9.1), CC BY 4.0
- Serie: [NASA POWER](https://power.larc.nasa.gov/), clima diario

## Alcance (delimitado)

| Incluye | No incluye |
| --- | --- |
| Alerta binaria de **una mazorca por foto**: monilia sí/no | Detección de varias mazorcas por imagen (YOLO) o segmentación |
| Un solo conjunto de imágenes y un solo punto climático (la región de origen) | Recolección de fotos propias en fincas colombianas (queda para la Fase 3) |
| Fase 2: CNN (imagen, 3 categorías) + LSTM/GRU (clima) + fusión intermedia + ablación | Transformers, modelos de video, *dashboard* interactivo |
| Métricas por subgrupo (no hay territorios ni poblaciones: son mazorcas) | Otras enfermedades del cacao (escoba de bruja, mazorca negra) |

## Cronograma

### Fase 1: 1 día (unas 8 h)

| Bloque | Tarea | Tiempo |
| --- | --- | --- |
| 1 | Descargar los `.rar` en Colab (`wget` + `unrar`), SHA-256 (anexo B), inventario EXIF y prueba de acoplamiento (anexo A) | 1 h |
| 2 | Reducir a 256 px **una sola vez** y guardar en `.npy`; extraer unos 24 rasgos (RGB/HSV, ExG, % lesión, % micelio, GLCM) en un CSV | 1,5 h |
| 3 | EDA: balance, resoluciones, ilegibles, casi duplicados (pHash). Partición 70/15/15 agrupada, `seed = 42` | 1 h |
| 4 | MLP 24→16→8→1, bucle explícito, curvas, sobreajuste inducido (300 muestras, red grande) y corrección con Dropout y parada temprana | 2 h |
| 5 | Umbral en validación (*recall* ≥ 0,90), matriz de confusión en prueba y líneas base (mayoritaria y % lesión) | 0,5 h |
| 6 | Informe técnico-ético (4 p.) y Bitácora de IA | 2 h |

### Fase 2: 5 días (CNN + LSTM/GRU + fusión)

| Día | Rama | Entregable del día |
| --- | --- | --- |
| 1 | A · CNN | Mañana: subdividir `monilia` en *temprana* y *avanzada* (unas 3 h, protocolo + kappa con 100 fotos). Tarde: `Dataset`/`DataLoader` con la partición de la Fase 1 y ResNet-18 preentrenada **congelada** + cabeza de 3 clases |
| 2 | A · CNN | *Fine-tuning* de las últimas capas, aumento de datos (giro, brillo, recorte), Grad-CAM sobre FN y FP. Comparación con el MLP de la Fase 1 |
| 3 | B · LSTM/GRU | NASA POWER 2001–2026 (unos 9.400 días), ventanas de 60 días → «semana siguiente favorable», partición cronológica, LSTM frente a GRU |
| 4 | C · Fusión | *Embedding* de la CNN ⊕ estado de la LSTM (60 días previos al mes de captura) → cabeza densa. Partición por mes y ablación solo imagen / solo clima / fusión. Umbral por costo |
| 5 | Cierre | Informe, visualizaciones para Fedecacao, pesos `.pth`, bitácora y ensayo de la sustentación |

## Estructura

```
centinela-cacao/
├── PROPUESTA_DE_DATOS_FASE1.md
├── src/
│   ├── anexo_a_acoplamiento.py   # EXIF → (región, mes) ⨝ NASA POWER: 10 filas reales
│   └── anexo_b_procedencia.py    # SHA-256 de cada archivo descargado
└── data/                         # ignorada por git (datos crudos)
```

## Reproducir los anexos

```bash
pip install pillow pandas requests
python src/anexo_b_procedencia.py data/raw/Monilia.rar data/raw/Sanos.rar
python src/anexo_a_acoplamiento.py --fotos data/raw --region <municipio>
```

Licencias: imágenes CC BY 4.0 (Rengifo-Lozano y Sánchez-Flores, 2026); datos de NASA LaRC POWER. Este repositorio **no redistribuye** las imágenes.
