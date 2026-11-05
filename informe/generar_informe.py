"""Genera informe/Informe_Fase1.pdf a partir de resultados/resultados.json y resultados/figuras/.

Todas las cifras del informe se leen del JSON que exporta el notebook (paso 14):
ningún número se escribe a mano.
Uso:  python informe/generar_informe.py
"""
import csv
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "resultados" / "resultados.json").read_text(encoding="utf-8"))
FIG = ROOT / "resultados" / "figuras"
SALIDA = ROOT / "informe" / "Informe_Fase1.pdf"


def n(x, d=3):
    """Número con coma decimal."""
    return f"{x:.{d}f}".replace(".", ",")


def pct(x, d=1):
    return f"{100 * x:.{d}f}".replace(".", ",") + " %"


h = R["huella_crudeza"]
pr = R["prueba"]
mlp, esc, may = pr["mlp"], pr["escalar"], pr["mayoritaria"]
cor = {c["corrida"]: c for c in R["corridas"]}
fin = R["modelo_final"]
part = {p["subconjunto"]: p for p in R["particion"]}
sub = R["subgrupos"]
aud = R["auditoria"]
ap10, ap25 = ({a["paciencia"]: a for a in R["auditoria_paciencia"]}[k] for k in (10, 25))
clima = R["clima_ventanas_60d"]
disp_fp = {k.replace("samsung ", ""): v["tasa_FP_sanas"] for k, v in sub["por_dispositivo"].items()}
imp = R["importancia_top5"]
with open(ROOT / "resultados" / "eda_auditoria_iqr.csv", encoding="utf-8") as fh:
    AUD_IQR = {r["rasgo"]: r for r in csv.DictReader(fh)}
am = AUD_IQR["pct_amarillo"]
roya24 = min(sub["por_clase"][k] for k in ("roya 2", "roya 3", "roya 4"))

# Fuente TTF con soporte de símbolos (→, ≥, ρ, −). Si no está disponible, se usa Helvetica.
FUENTE, FUENTE_N = "Helvetica", "Helvetica-Bold"
try:
    from reportlab.lib.fonts import addMapping
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for nombre, archivo in [("Arial", "arial.ttf"), ("Arial-Bold", "arialbd.ttf"), ("Arial-Italic", "ariali.ttf"),
                            ("Arial-BoldItalic", "arialbi.ttf")]:
        pdfmetrics.registerFont(TTFont(nombre, str(Path("C:/Windows/Fonts") / archivo)))
    addMapping("Arial", 0, 0, "Arial"); addMapping("Arial", 1, 0, "Arial-Bold")
    addMapping("Arial", 0, 1, "Arial-Italic"); addMapping("Arial", 1, 1, "Arial-BoldItalic")
    FUENTE, FUENTE_N = "Arial", "Arial-Bold"
except Exception:
    pass

base = getSampleStyleSheet()
for s in base.byName.values():
    if not hasattr(s, "fontName"):
        continue
    s.fontName = FUENTE_N if "Bold" in s.fontName or s.name.startswith(("Heading", "Title")) else FUENTE
st = {
    "titulo": ParagraphStyle("t", parent=base["Title"], fontSize=14.5, leading=17, spaceAfter=2),
    "sub": ParagraphStyle("s", parent=base["Normal"], fontSize=8.5, leading=10.5, textColor=colors.HexColor("#555555"), alignment=1),
    "h": ParagraphStyle("h", parent=base["Heading2"], fontSize=11, leading=13, spaceBefore=6, spaceAfter=2, textColor=colors.HexColor("#1f4e3d"), keepWithNext=1),
    "p": ParagraphStyle("p", parent=base["Normal"], fontSize=9, leading=11.4, alignment=TA_JUSTIFY, spaceAfter=3),
    "pie": ParagraphStyle("pie", parent=base["Normal"], fontSize=7.6, leading=9, textColor=colors.HexColor("#444444"), spaceAfter=4),
    "ref": ParagraphStyle("r", parent=base["Normal"], fontSize=8.4, leading=10.4, leftIndent=12, firstLineIndent=-12, spaceAfter=3),
    "tab": ParagraphStyle("tb", parent=base["Normal"], fontSize=7.8, leading=9.2),
}
P = lambda t: Paragraph(t, st["p"])


def figura(nombre, ancho_cm, pie):
    ruta = FIG / nombre
    from PIL import Image as PILImage
    w, hh = PILImage.open(ruta).size
    img = Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * hh / w)
    return KeepTogether([img, Paragraph(pie, st["pie"])])


def tabla(filas, anchos, cabecera=True):
    datos = [[Paragraph(str(c), st["tab"]) for c in f] for f in filas]
    t = Table(datos, colWidths=[a * cm for a in anchos])
    estilo = [("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbbb")),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]
    if cabecera:
        estilo += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6efe9"))]
    t.setStyle(TableStyle(estilo))
    return t


E = []
E += [Paragraph("Centinela del Café · Fase 1: línea base con MLP para detectar hojas de café afectadas", st["titulo"]),
      Paragraph("Briyith Lisdey Herrera Cruz · Juan Pablo Becerra Tirano · Johnatan Vélez Martínez — Deep Learning, "
                "Maestría en Ciencia de Datos, Universidad Santo Tomás · " + R["fecha_ejecucion"], st["sub"]),
      Spacer(1, 4)]

# 1. Problema y cliente
E += [Paragraph("1. Problema y cliente", st["h"]),
      P("Las <b>organizaciones de monitoreo fitosanitario</b> envían técnicos de sanidad vegetal a revisar lotes de café. "
        "No pueden inspeccionar cada hoja, y una hoja con <b>roya</b> (<i>Hemileia vastatrix</i>) o <b>ácaro rojo</b> que pasa "
        "inadvertida sigue esporulando o reproduciéndose y contagia el lote. El objetivo es binario: <b>¿la hoja está afectada "
        "(ácaro o roya de cualquier nivel = 1) o sana (= 0)?</b> Se resuelve a partir de una foto de celular. El error más "
        "costoso es el <b>falso negativo</b> (FN). Un falso positivo (FP) cuesta una verificación en campo; se asume FN:FP = 5:1, "
        "dentro del rango de 3 a 8 veces que cuesta dejar pasar un defecto en un control de calidad. La meta operativa es un "
        "<i>recall</i> de la clase afectada ≥ 0,90. Esta Fase 1 construye la línea base con un perceptrón multicapa (MLP). "
        "La Fase 2 incorporará la serie climática.")]

# 2. Datos
E += [Paragraph("2. Datos", st["h"]),
      P(f"<b>Fuente.</b> RoCoLe v2 (Parraga-Alava et al., 2019a, 2019b; CC BY 4.0), descargado de Mendeley Data. Son "
        f"{h['imagenes']} fotos de {h['plantas']} plantas de café robusta, en {h['cultivos']} cultivos, tomadas en CIIDEA, "
        f"Manabí, Ecuador. Cada planta tiene 4 fotos: 2 del haz y 2 del envés. Por cómo coinciden sus etiquetas, se infiere "
        f"que corresponden a 2 hojas fotografiadas por ambas caras, unas {h['hojas_inferidas']} hojas en total, aunque la "
        f"fuente no lo documenta. Hay {h['clases_multiclase']['sana']} hojas sanas, {h['clases_multiclase']['ácaro rojo']} con ácaro rojo "
        f"y {sum(v for k, v in h['clases_multiclase'].items() if k.startswith('roya'))} con roya: el balance es "
        f"{h['balance_afectada']['1']} afectadas frente a {h['balance_afectada']['0']} sanas. Este dataset reemplaza al de "
        "cacao de la propuesta v1. Sus autores confirmaron que las fotos se tomaron en Tocache, Huallaga y Rioja, pero "
        "ninguna imagen registra dónde, lo que impedía alinear cada foto con el clima. En RoCoLe, el sitio es único y "
        "georreferenciado, y la fecha de cada foto está en el EXIF."),
      P(f"<b>Huella de crudeza.</b> El CSV de anotaciones llega con {h['anotaciones_csv_filas_x_columnas_crudo']} celdas y "
        f"{n(h['pct_faltantes_csv_global'], 1)} % de faltantes. Las imágenes vienen de {len(h['dispositivos'])} "
        f"celulares, en {len(h['resoluciones'])} resoluciones y {len(h['fechas_captura'])} fechas. Hay "
        f"<b>{h['duplicados_exactos_grupos']} grupos de imágenes idénticas byte a byte</b> ({h['duplicados_exactos_imagenes']} "
        f"imágenes) entre plantas distintas. En {h['duplicados_exactos_grupos'] - h['duplicados_misma_clase_multi']} de ellos "
        "las copias tienen clase multiclase distinta, es decir, hay ruido de etiqueta en la fuente. Por decisión del equipo "
        "<b>no se eliminan</b>: se conservan con su etiqueta original y se agrupan para que nunca queden repartidos entre "
        "entrenamiento y prueba. El dato del anotador (<i>Created By</i>) se eliminó al cargar los datos."),
      P("<b>De imagen a tabla.</b> La modalidad que se aplana en esta fase es la imagen. Sobre los píxeles del polígono "
        "anotado de la hoja, redimensionada a 256 px, se calculan 28 rasgos: color RGB, HSV y CIELAB; proporciones de píxeles "
        "anaranjados, amarillos y oscuros; los índices ExG, VARI y R/G; textura GLCM, y la fracción que ocupa la hoja. Al "
        "modelo entran 27, porque <i>pct_verde</i> es igual a 1 − <i>pct_lesion</i>."),
      P(f"<b>Hallazgos del EDA → decisiones.</b> No hay NaN ({h['nan_en_rasgos']}). Los ceros de <i>pct_naranja</i> se "
        "concentran en hojas sanas: son biológicos. Los atípicos por IQR son la propia señal de la enfermedad: en "
        f"<i>pct_amarillo</i>, el {n(float(am['pct_atip_roya3_4']), 1)} % de las hojas con roya 3–4 son atípicas, frente al "
        f"{n(float(am['pct_atip_sanas']), 1)} % de las sanas. Por eso <b>no se eliminan atípicos</b>. Hay "
        f"{R['eda_multicolinealidad']['pares_spearman_mayor_0_9']} pares de rasgos con |ρ| > 0,9; se conservan, porque elegir "
        "variables con todo el conjunto filtraría información. La clase casi no depende del dispositivo (V de Cramér = "
        f"{n(R['eda_v_cramer']['dispositivo'])}) ni de la fecha ({n(R['eda_v_cramer']['fecha_txt'])}), pero dispositivo y fecha "
        "están confundidos entre sí."),
      P(f"<b>Partición.</b> La partición es estratificada y <b>agrupada</b>: las 390 plantas, unidas por sus duplicados "
        f"(SHA-256 y pHash), forman {R['grupos']['grupos']} grupos. Quedan {part['entrenamiento']['imagenes']} imágenes de "
        f"entrenamiento, {part['validacion']['imagenes']} de validación y {part['prueba']['imagenes']} de prueba "
        f"({pct(part['entrenamiento']['pct_imagenes'])} / {pct(part['validacion']['pct_imagenes'])} / "
        f"{pct(part['prueba']['pct_imagenes'])}), con semilla 42. El <i>StandardScaler</i> se ajusta solo con entrenamiento."),
      P(f"<b>Acoplamiento con el clima (para la Fase 2).</b> La clave es (CIIDEA, fecha EXIF), con una ventana de 60 días de "
        f"NASA POWER. Las 5 ventanas resultan casi idénticas: temperatura de {n(min(c['T2M_media_60d'] for c in clima), 2)} a "
        f"{n(max(c['T2M_media_60d'] for c in clima), 2)} °C y humedad relativa de {n(min(c['RH2M_media_60d'] for c in clima), 1)} "
        f"a {n(max(c['RH2M_media_60d'] for c in clima), 1)} %. El clima aportará contexto de riesgo, no señal por hoja."),
      figura("eda_atipicos_iqr.png", 9.5, "Figura 1. Porcentaje de hojas atípicas (regla IQR) por rasgo: sanas frente a roya 3–4. "
             "Los atípicos de los rasgos de lesión corresponden a enfermedad severa y se conservan.")]

# 3. Modelo y entrenamiento
c1, cE, c2, c3a, c3b, c4 = (cor[k] for k in ("R1", "R1-ES", "R2", "R3a", "R3b", "R4"))
E += [Paragraph("3. Modelo y entrenamiento", st["h"]),
      P("<b>Arquitectura.</b> MLP en PyTorch con dos capas ocultas (Linear → ReLU → Dropout) y una salida Linear(k, 1) que "
        "devuelve un <b>logit</b>. Se entrena con <i>BCEWithLogitsLoss</i>, la etiqueta tiene forma (N, 1) en float y la "
        "sigmoide se aplica solo al evaluar, para evitar el doble sigmoide. ReLU es necesaria porque las señales interactúan: "
        "un tono anaranjado solo indica roya si va acompañado de textura punteada y pérdida de verdor, y ese tipo de interacción "
        "no lo representa una frontera lineal. Sin activación no lineal, varias capas lineales se reducen a una sola; con "
        "ReLU, el MLP aproxima esas interacciones por tramos (Teorema de Aproximación Universal; Goodfellow et al., 2016). "
        "El bucle es explícito (forward → pérdida → zero_grad → backward → step), con "
        "Adam, lr = 10<super>−2</super> y lote completo; se guarda un <i>checkpoint</i> cada 10 épocas."),
      P(f"<b>Experimentos.</b> La corrida R1 (256 → 128, sin Dropout, 1.500 épocas) se <b>sobreajusta</b>: la pérdida de "
        f"validación toca su mínimo ({n(c1['perdida_min_val'])}) en la época {c1['epoca_min_val']} y luego sube, y la brecha "
        f"validación − entrenamiento pasa de {n(c1['brecha_en_min'])} a {n(c1['brecha_final'], 2)}. La parada temprana usa "
        "paciencia de 25 épocas, porque con lote completo una época es un solo paso de gradiente. Con esa paciencia y Dropout "
        f"0,3, la pérdida mínima de validación baja a {n(c2['perdida_min_val'])} (R2, 16 → 8) y a {n(c3a['perdida_min_val'])} "
        f"(R3a, 8 → 4). La comparación de capacidad muestra que la red grande R3b (64 → 32) casi no mejora la pérdida "
        f"({n(c3b['perdida_min_val'])}) y multiplica la brecha ({n(c3b['brecha_en_min'])} frente a {n(c3a['brecha_en_min'])}). "
        f"Por eso se elige <b>{fin}</b> (8 → 4, Dropout 0,3, parada temprana), con el estado del mínimo de validación restaurado."),
      tabla([["Corrida", "Ocultas", "Regularización", "Época mín.", "Pérdida val. mín.", "Brecha en mín.", "AUC val."]] +
            [[k, cor[k]["ocultas"], ("Dropout " + n(cor[k]["dropout"], 1) if cor[k]["dropout"] else "—") +
              (" + L2" if cor[k]["weight_decay"] else "") + (" + PT" if cor[k]["parada_temprana"] else ""),
              cor[k]["epoca_min_val"], n(cor[k]["perdida_min_val"]), n(cor[k]["brecha_en_min"]), n(cor[k]["auc_val_modelo_usado"])]
             for k in ("R0", "R1", "R1-ES", "R2", "R3a", "R3b", "R4")],
            [1.4, 1.8, 3.6, 1.7, 2.6, 2.3, 1.7]),
      Paragraph("Tabla 1. Corridas comparables (misma partición, semilla y lr). PT = parada temprana. Brecha = pérdida de "
                "validación − pérdida de entrenamiento en la época del mínimo.", st["pie"]),
      figura("curvas_R1_vs_R2.png", 13, "Figura 2. Pérdida por época en entrenamiento (punteada) y validación (continua) de R1 "
             "(sobreajuste) y R2 (regularizada). La línea discontinua vertical marca el mínimo de validación.")]

# 4. Resultados y errores
E += [Paragraph("4. Resultados y errores", st["h"]),
      P(f"El umbral se fijó en <b>validación</b> como el de menor costo 5·FN + FP con <i>recall</i> ≥ 0,90: "
        f"<b>{n(pr['umbral'], 2)}</b>. Con él, el conjunto de prueba se evaluó <b>una sola vez</b> (n = {pr['n']})."),
      tabla([["Modelo", "Recall afectada", "Precisión afectada", "F1 afectada", "Recall sana", "AUC", "FN", "FP", "Costo"]] +
            [[nom, n(m["recall_afectada"]), n(m["precision_afectada"]), n(m["f1_afectada"]), n(m["recall_sana"]),
              n(m["auc"]), int(m["FN"]), int(m["FP"]), int(m["costo"])]
             for nom, m in ((f"MLP {fin}", mlp), ("Escalar crudo pct_lesion", esc), ("Clase mayoritaria (sana)", may))],
            [3.6, 1.7, 1.8, 1.5, 1.5, 1.2, 0.9, 0.9, 1.2]),
      Paragraph("Tabla 2. Desempeño en prueba frente a las dos líneas base comprometidas.", st["pie"]),
      P(f"El MLP detecta {int(mlp['VP'])} de {int(mlp['VP'] + mlp['FN'])} hojas afectadas (<i>recall</i> {n(mlp['recall_afectada'])}) "
        f"con AUC = {n(mlp['auc'])}. Frente al escalar crudo, reduce el costo de {int(esc['costo'])} a {int(mlp['costo'])} y los "
        f"falsos positivos de {int(esc['FP'])} a {int(mlp['FP'])}. La clase mayoritaria no detecta ninguna hoja (costo "
        f"{int(may['costo'])}). <b>Análisis de errores:</b> los {int(mlp['FN'])} FN son lesiones incipientes (detección de "
        f"{n(sub['por_clase']['roya 1'])} en roya 1 y {n(sub['por_clase']['ácaro rojo'])} en ácaro rojo, frente a ≥ {n(roya24, 2)} en roya 2–4). "
        f"Es el caso que más le importa a una alerta temprana. Los FP de mayor probabilidad que se revisaron en la galería "
        f"del notebook son hojas sanas con brillos o tonos amarillentos. Es coherente con que el modelo dependa sobre todo "
        f"del color de la lesión (importancia por "
        f"permutación: <i>pct_naranja</i> {n(imp['pct_naranja'])}, <i>pct_amarillo</i> {n(imp['pct_amarillo'])}). "
        f"<b>Por subgrupo:</b> el <i>recall</i> es estable entre celulares, pero la tasa de falsa alarma en hojas sanas va de "
        f"{n(min(disp_fp.values()), 2)} a {n(max(disp_fp.values()), 2)} según la cámara."),
      figura("matriz_confusion_prueba.png", 11.5, "Figura 3. Matriz de confusión en prueba del MLP y del escalar crudo, cada uno "
             "con el umbral elegido en validación.")]

# 5. Decisión y ética
E += [Paragraph("5. Decisión recomendada y riesgos éticos", st["h"]),
      P(f"<b>Decisión.</b> Adoptar el MLP {fin} con umbral {n(pr['umbral'], 2)} como <b>filtro de priorización de inspección</b>, "
        "no como diagnóstico. Toda alerta la confirma el técnico en campo antes de cualquier aplicación. Sin el modelo, el "
        f"técnico tendría que revisar las {pr['n']} hojas; con él revisa {int(mlp['VP'] + mlp['FP'])} y deja escapar "
        f"{int(mlp['FN'])}."),
      P("<b>Marco Ético para la IA en Colombia</b> (Guío Español et al., 2021). <b>Responsabilidad:</b> el umbral se fijó por "
        "el costo del error para el cliente, no en 0,5, y la decisión final queda en manos humanas. <b>Transparencia:</b> el "
        f"sistema declara su dominio de validez (robusta, un sitio, {len(h['fechas_captura'])} días de 2019, "
        f"{len(h['dispositivos'])} celulares Samsung), informa que \"sin "
        "alerta\" no equivale a \"sana\" y reporta la falsa alarma por dispositivo. <b>Equidad y beneficio social:</b> no debe "
        "extrapolarse a café arábica ni a fincas colombianas sin un piloto local; hacerlo trasladaría el riesgo de FN a "
        "productores que el modelo no vio."),
      P(f"<b>Riesgos y mitigaciones.</b> (1) Ruido de etiqueta en duplicados: se reporta y se agrupa. (2) La máscara de la "
        "hoja proviene de la anotación humana: en uso real hará falta segmentación automática (Fase 2). (3) El clima casi "
        "constante limita la rama temporal. (4) <b>Auditoría a la IA, caso real:</b> el asistente generó el bucle con una "
        "paciencia de 10 épocas. Con lote completo eso equivale a solo 10 pasos de gradiente, y R2 se detenía en una meseta. "
        f"Reproducido con la misma semilla, la paciencia 10 deja una AUC de validación de {n(ap10['auc_val'])} y un costo de "
        f"{int(ap10['costo_val'])}; la paciencia corregida (25) da {n(ap25['auc_val'])} y {int(ap25['costo_val'])}. "
        "<b>Modificada:</b> la sugerencia de partir por hoja se cambió a partir por planta. Partiendo por hoja, un "
        f"{pct(aud['pct_prueba_con_grupo_en_train_ingenua'])} de las fotos de prueba tendría una hermana en entrenamiento, y "
        f"{aud['duplicados_exactos_prueba_en_train_ingenua']} serían copias exactas. <b>Rechazada:</b> eliminar duplicados. "
        "Con datos tabulares la comparación de filas no reconoce el contexto ni las vecindades de la imagen, y se corre el "
        f"riesgo de borrar registros que no son duplicados; además, {h['duplicados_exactos_grupos'] - h['duplicados_misma_clase_multi']} "
        "grupos de copias exactas tienen clases distintas. Por eso se conservan y solo se agrupan. "
        "La partición, la semilla y las líneas base se conservan para la Fase 2 (CNN + LSTM/GRU con fusión).")]

# Referencias
E += [Paragraph("Referencias", st["h"])]
for ref in [
    "Goodfellow, I., Bengio, Y., & Courville, A. (2016). <i>Deep learning</i>. MIT Press. https://www.deeplearningbook.org/",
    "Guío Español, A., Tamayo Uribe, E., Gómez Ayerbe, P., & Mujica, M. P. (2021). <i>Marco ético para la inteligencia "
    "artificial en Colombia</i>. Consejería Presidencial para Asuntos Económicos y Transformación Digital.",
    "NASA Langley Research Center. (2026). <i>Prediction of Worldwide Energy Resources (POWER) Project: Daily agroclimatology "
    "data</i> [Data set]. https://power.larc.nasa.gov/",
    "Parraga-Alava, J., Cusme, K., Loor, A., & Santander, E. (2019a). <i>RoCoLe: A robusta coffee leaf images dataset</i> "
    "(Version 2) [Data set]. Mendeley Data. https://doi.org/10.17632/c5yvn32dzg.2",
    "Parraga-Alava, J., Cusme, K., Loor, A., & Santander, E. (2019b). RoCoLe: A robusta coffee leaf images dataset for "
    "evaluation of machine learning based methods in plant diseases recognition. <i>Data in Brief, 25</i>, 104414. "
    "https://doi.org/10.1016/j.dib.2019.104414",
    "Rengifo-Lozano, D., & Sánchez-Flores, J. (2026). <i>Image dataset of healthy and monilia-infected cocoa pods for disease "
    "classification</i> (Version 1) [Data set]. Mendeley Data. https://doi.org/10.17632/ykbtpsyfv9.1",
]:
    E.append(Paragraph(ref, st["ref"]))


def pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont(FUENTE, 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawRightString(A4[0] - 1.7 * cm, 1.0 * cm, f"Proyecto Centinela · Fase 1 · p. {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=1.7 * cm, rightMargin=1.7 * cm,
                        topMargin=1.4 * cm, bottomMargin=1.5 * cm, title="Centinela del Café · Fase 1",
                        author="Herrera Cruz, Becerra Tirano, Vélez Martínez")
doc.build(E, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("Informe:", SALIDA)
