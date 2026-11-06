"""Genera informe/Informe_Fase1.pdf: informe técnico-ético para una audiencia no técnica (≤ 4 páginas + referencias).

Todas las cifras se leen de lo que exporta el notebook (resultados/*.json y *.csv): ninguna se escribe a mano.
Las figuras se redibujan aquí con letra grande para que sean legibles impresas.
Uso:  python informe/generar_informe.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"
FIG = ROOT / "informe" / "figuras"
FIG.mkdir(parents=True, exist_ok=True)
SALIDA = ROOT / "informe" / "Informe_Fase1.pdf"

R = json.loads((RES / "resultados.json").read_text(encoding="utf-8"))
HIST = json.loads((RES / "historias_entrenamiento.json").read_text(encoding="utf-8"))
CURVA = pd.read_csv(RES / "umbral_validacion.csv")
COR = {c["corrida"]: c for c in R["corridas"]}
h, pr, sub = R["huella_crudeza"], R["prueba"], R["subgrupos"]
mlp, esc, may = pr["mlp"], pr["escalar"], pr["mayoritaria"]
FIN, U = R["modelo_final"], pr["umbral"]
ap = {a["paciencia"]: a for a in R["auditoria_paciencia"]}
aud = R["auditoria"]


def n(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def entero(x):
    return f"{int(x):,}".replace(",", ".")


def pct(x, d=0):
    return f"{100 * x:.{d}f}".replace(".", ",") + " %"


# ----------------------------------------------------------------------------- figuras
AZUL, NARANJA, AQUA, GRIS, TINTA, TINTA2 = "#2a78d6", "#eb6834", "#1baf7a", "#898781", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "Arial", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": GRIS, "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2,
                     "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6, "axes.axisbelow": True})


def guardar(fig, nombre):
    fig.savefig(FIG / nombre, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return FIG / nombre


def fig_datos():
    clases = h["clases_multiclase"]
    nombres = list(clases)[::-1]
    valores = [clases[k] for k in nombres]
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    barras = ax.barh(nombres, valores, color=[AQUA if k == "sana" else NARANJA for k in nombres], height=0.62)
    for b, v in zip(barras, valores):
        ax.text(v + 12, b.get_y() + b.get_height() / 2, entero(v), va="center", fontsize=11, color=TINTA)
    ax.set_xlabel("número de fotos")
    ax.set_xlim(0, max(valores) * 1.15)
    ax.grid(axis="y", visible=False)
    ax.text(0.98, 0.30, f"Sanas: {entero(h['balance_afectada']['0'])}\nAfectadas: {entero(h['balance_afectada']['1'])}",
            transform=ax.transAxes, ha="right", fontsize=11, color=TINTA)
    return guardar(fig, "f1_datos.png")


def fig_flujo():
    pasos = ["Foto de\nla hoja", "Se recorta\nsolo la hoja", "27 medidas:\ncolor, manchas,\ntextura",
             "Red neuronal\n(MLP 8 → 4)", "Probabilidad\nde afección", f"¿Probabilidad\n≥ {n(U)}?\n→ alerta"]
    fig, ax = plt.subplots(figsize=(10, 1.9))
    ax.set_xlim(0, 6); ax.set_ylim(0, 1); ax.axis("off")
    for i, t in enumerate(pasos):
        color = AZUL if i in (3, 5) else "#f0efec"
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.12), 0.84, 0.76, boxstyle="round,pad=0.02,rounding_size=0.05",
                                    fc=color, ec=GRIS if color != AZUL else AZUL, lw=1))
        ax.text(i + 0.48, 0.5, t, ha="center", va="center", fontsize=10.5, color="white" if color == AZUL else TINTA)
        if i < len(pasos) - 1:
            ax.annotate("", xy=(i + 1.06, 0.5), xytext=(i + 0.92, 0.5), arrowprops=dict(arrowstyle="->", color=GRIS, lw=1.4))
    return guardar(fig, "f2_flujo.png")


def fig_curvas():
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    r1, fin = HIST["R1"], HIST[FIN]
    lim = 400
    ax.plot(range(1, lim + 1), r1["val"][:lim], color=NARANJA, lw=2)
    ax.plot(range(1, lim + 1), r1["train"][:lim], color=NARANJA, lw=1.4, ls=":")
    ax.plot(range(1, len(fin["val"]) + 1), fin["val"], color=AZUL, lw=2)
    ax.plot(range(1, len(fin["train"]) + 1), fin["train"], color=AZUL, lw=1.4, ls=":")
    ax.axvline(r1["mejor_epoca"], color=NARANJA, ls="--", lw=1)
    ax.axvline(fin["mejor_epoca"], color=AZUL, ls="--", lw=1)
    ax.text(lim, r1["val"][lim - 1], " red grande:\n memoriza", color=TINTA, fontsize=10, va="center")
    ax.text(len(fin["val"]) + 5, fin["val"][-1] + 0.12, "red final:\naprende", color=TINTA, fontsize=10)
    ax.text(r1["mejor_epoca"] + 4, 1.42, f"mejor época\nred grande: {r1['mejor_epoca']}", fontsize=9.5, color=TINTA2)
    ax.text(fin["mejor_epoca"] + 4, 1.42, f"mejor época\nred final: {fin['mejor_epoca']}", fontsize=9.5, color=TINTA2)
    ax.set_ylim(0, 1.65); ax.set_xlim(0, lim * 1.25)
    ax.set_xlabel("época (vueltas de entrenamiento)"); ax.set_ylabel("error (pérdida)")
    ax.plot([], [], color=GRIS, lw=2, label="hojas nuevas (validación)")
    ax.plot([], [], color=GRIS, lw=1.4, ls=":", label="hojas de práctica (entrenamiento)")
    ax.legend(frameon=False, fontsize=9.5, loc="center right", bbox_to_anchor=(1.0, 0.55))
    return guardar(fig, "f3_curvas.png")


def fig_umbral():
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.plot(CURVA["umbral"], CURVA["costo"], color=AZUL, lw=2)
    fila = CURVA.loc[CURVA["umbral"].round(2) == round(U, 2)].iloc[0]
    ax.plot([U], [fila["costo"]], "o", ms=8, color=AZUL, mec="white", mew=2)
    ax.axvline(U, color=GRIS, ls="--", lw=1)
    ax.annotate(f"umbral {n(U)}\ncosto mínimo: {int(fila['costo'])}", (U, fila["costo"]), xytext=(0.36, 0.86),
                textcoords="axes fraction", fontsize=10, arrowprops=dict(arrowstyle="-", color=GRIS, lw=0.8))
    ax.set_xlabel("umbral de alerta"); ax.set_ylabel("costo = 5 × FN + FP")
    ax.set_xlim(0, 1)
    return guardar(fig, "f4_umbral.png")


def fig_resultados():
    modelos = ["Red neuronal", "Un solo número\n(% no verde)", "No alertar\nnunca"]
    fn = [mlp["FN"], esc["FN"], may["FN"]]
    fp = [mlp["FP"], esc["FP"], may["FP"]]
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    y = range(len(modelos))
    b1 = ax.barh([i + 0.2 for i in y], fn, height=0.38, color=NARANJA, label="enfermas que se escapan (FN)")
    b2 = ax.barh([i - 0.2 for i in y], fp, height=0.38, color=AZUL, label="falsas alarmas (FP)")
    for barras in (b1, b2):
        for b in barras:
            ax.text(b.get_width() + 2, b.get_y() + b.get_height() / 2, int(b.get_width()), va="center", fontsize=10, color=TINTA)
    ax.set_yticks(list(y), modelos); ax.invert_yaxis()
    ax.set_xlabel(f"número de hojas (de {pr['n']} en prueba)")
    ax.grid(axis="y", visible=False); ax.set_xlim(0, max(fn + fp) * 1.18)
    ax.legend(frameon=False, fontsize=9.5, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=1)
    return guardar(fig, "f5_resultados.png")


F1, F2, F3, F4, F5 = fig_datos(), fig_flujo(), fig_curvas(), fig_umbral(), fig_resultados()

# ----------------------------------------------------------------------------- estilos
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
FUENTE, NEGRITA = "Helvetica", "Helvetica-Bold"
try:
    for nom, arch in [("Arial", "arial.ttf"), ("Arial-Bold", "arialbd.ttf"), ("Arial-Italic", "ariali.ttf"), ("Arial-BoldItalic", "arialbi.ttf")]:
        pdfmetrics.registerFont(TTFont(nom, str(Path("C:/Windows/Fonts") / arch)))
    addMapping("Arial", 0, 0, "Arial"); addMapping("Arial", 1, 0, "Arial-Bold")
    addMapping("Arial", 0, 1, "Arial-Italic"); addMapping("Arial", 1, 1, "Arial-BoldItalic")
    FUENTE, NEGRITA = "Arial", "Arial-Bold"
except Exception:
    pass

VERDE_OSC = colors.HexColor("#1f4e3d")
st = {
    "titulo": ParagraphStyle("t", fontName=NEGRITA, fontSize=15, leading=18, textColor=VERDE_OSC, spaceAfter=2),
    "sub": ParagraphStyle("s", fontName=FUENTE, fontSize=8.5, leading=10.5, textColor=colors.HexColor("#555555"), spaceAfter=6),
    "h": ParagraphStyle("h", fontName=NEGRITA, fontSize=11.5, leading=14, textColor=VERDE_OSC, spaceBefore=7, spaceAfter=3, keepWithNext=1),
    "p": ParagraphStyle("p", fontName=FUENTE, fontSize=9.4, leading=12.4, alignment=TA_JUSTIFY, spaceAfter=4),
    "b": ParagraphStyle("b", fontName=FUENTE, fontSize=9.4, leading=12.4, leftIndent=11, bulletIndent=2, spaceAfter=2),
    "pie": ParagraphStyle("pie", fontName=FUENTE, fontSize=8, leading=9.6, textColor=colors.HexColor("#444444"), spaceAfter=5),
    "caja": ParagraphStyle("c", fontName=FUENTE, fontSize=9.4, leading=12.6, leftIndent=10, bulletIndent=0, spaceAfter=1),
    "tab": ParagraphStyle("tb", fontName=FUENTE, fontSize=8.6, leading=10.4),
    "ref": ParagraphStyle("r", fontName=FUENTE, fontSize=8.4, leading=10.4, leftIndent=12, firstLineIndent=-12, spaceAfter=3),
}
P = lambda t: Paragraph(t, st["p"])
B = lambda t: Paragraph(t, st["b"], bulletText="•")


def img(ruta, ancho_cm):
    from PIL import Image as PILImage
    w, hh = PILImage.open(ruta).size
    return Image(str(ruta), width=ancho_cm * cm, height=ancho_cm * cm * hh / w)


def figura(ruta, ancho_cm, pie):
    return KeepTogether([img(ruta, ancho_cm), Paragraph(pie, st["pie"])])


def tabla(filas, anchos):
    t = Table([[Paragraph(str(c), st["tab"]) for c in f] for f in filas], colWidths=[a * cm for a in anchos])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#c8c8c8")),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6efe9")),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def caja(titulo, lineas):
    contenido = [Paragraph(f"<b>{titulo}</b>", st["caja"])] + [Paragraph(l, st["caja"], bulletText="•") for l in lineas]
    t = Table([[contenido]], colWidths=[17.6 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef5f1")),
                           ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#9cc5b0")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


# ----------------------------------------------------------------------------- contenido
detecta = int(mlp["VP"]); enfermas = int(mlp["VP"] + mlp["FN"]); sanas = int(mlp["FP"] + mlp["VN"])
ahorro = 1 - mlp["costo"] / esc["costo"]
fp_disp = {k.replace("samsung ", ""): v["tasa_FP_sanas"] for k, v in sub["por_dispositivo"].items()}
c10, c22, c50 = (CURVA.loc[CURVA["umbral"].round(2) == u].iloc[0] for u in (0.10, round(U, 2), 0.50))

E = [Paragraph("Centinela del Café: alerta temprana de hojas de café afectadas", st["titulo"]),
     Paragraph("Informe técnico-ético · Proyecto Centinela, Fase 1 · Briyith Lisdey Herrera Cruz, Juan Pablo Becerra Tirano "
               "y Johnatan Vélez Martínez · Deep Learning, Maestría en Ciencia de Datos, Universidad Santo Tomás · "
               + R["fecha_ejecucion"], st["sub"]),
     caja("En breve", [
         f"Construimos un modelo que mira la foto de una hoja de café y avisa si puede estar enferma (roya o ácaro rojo).",
         f"En {pr['n']} hojas que el modelo nunca había visto, detectó <b>{detecta} de {enfermas}</b> hojas enfermas "
         f"({pct(mlp['recall_afectada'], 1)}), a cambio de {int(mlp['FP'])} falsas alarmas entre {sanas} hojas sanas.",
         f"Comparado con mirar un solo indicador de color, reduce el costo de los errores en un <b>{pct(ahorro)}</b>.",
         "Recomendación: usarlo para decidir qué hojas revisar primero, nunca como diagnóstico final."]),
     ]

# 1. Problema
E += [Paragraph("1. El problema y para quién", st["h"]),
      P("Las <b>organizaciones de monitoreo fitosanitario</b> envían técnicos de sanidad a revisar cultivos de café, pero no "
        "pueden inspeccionar cada hoja. La <b>roya</b> (un hongo que deja manchas anaranjadas) y el <b>ácaro rojo</b> se "
        "propagan si no se detectan a tiempo. La pregunta del proyecto es simple: <b>a partir de una foto, ¿la hoja está "
        "afectada o sana?</b>"),
      P("Hay dos errores posibles. Un <b>falso negativo</b> es una hoja enferma que el sistema deja pasar: sigue "
        "contagiando el cultivo. Un <b>falso positivo</b> es una falsa alarma: el técnico revisa una hoja que estaba sana. "
        "Con el equipo acordamos que <b>dejar pasar una hoja enferma cuesta 5 veces más</b> que una falsa alarma, en línea con "
        "lo que cuesta dejar pasar un defecto en un control de calidad (de 3 a 8 veces). La meta fue detectar al menos el 90 % "
        "de las hojas enfermas.")]

# 2. Datos
E += [Paragraph("2. Los datos", st["h"]),
      P(f"Usamos <b>RoCoLe</b>, un conjunto público de fotos de hojas de café robusta tomadas en una finca experimental de "
        f"Manabí, Ecuador (Parraga-Alava et al., 2019a, 2019b). Son <b>{entero(h['imagenes'])} fotos de {h['plantas']} plantas</b> "
        f"en {h['cultivos']} lotes: 4 fotos por planta, que corresponden a unas {entero(h['hojas_inferidas'])} hojas "
        "fotografiadas por ambas caras. Cada foto trae la clase asignada por un experto y la fecha en que se tomó. Esa fecha "
        "permitirá en la Fase 2 unir cada hoja con el clima de los 60 días anteriores (NASA Langley Research Center, 2026). "
        "Este conjunto reemplazó a uno de mazorcas de cacao (Rengifo-Lozano y Sánchez-Flores, 2026): sus autores nos "
        "confirmaron que no registraron dónde se tomó cada foto, y sin ese dato no se puede cruzar la foto con el clima."),
      Table([[img(F1, 8.6), [P(f"<b>Calidad de los datos.</b> Encontramos {h['duplicados_exactos_grupos']} grupos de fotos "
                                f"repetidas idénticas, y en {h['duplicados_exactos_grupos'] - h['duplicados_misma_clase_multi']} de "
                                "ellos las copias tienen etiquetas distintas. Decidimos <b>no borrarlas</b>: borrar obligaría a "
                                "escoger una etiqueta sin criterio. Se mantienen juntas, para que una copia no aparezca a la vez "
                                "en las fotos de práctica y en las de prueba."),
                              P("<b>Privacidad.</b> Las fotos solo muestran hojas, no tienen ubicación GPS, y se eliminó el único "
                                "dato personal: el nombre de quien etiquetó cada foto.")]]],
            colWidths=[9 * cm, 8.6 * cm], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
      Paragraph("Figura 1. Fotos por clase. Las clases de roya van de 1 (leve) a 4 (severa). Las sanas y las afectadas están casi "
                "en igual proporción.", st["pie"])]

# 3. Modelo
c3a, c2, c3b, c1 = COR["R3a"], COR["R2"], COR["R3b"], COR["R1"]
E += [Paragraph("3. Cómo funciona el modelo", st["h"]),
      figura(F2, 17.6, "Figura 2. Recorrido de una foto por el sistema."),
      B("<b>De foto a números.</b> Se recorta solo la hoja y se resume en 27 medidas con sentido agronómico: qué tan verde "
        "es, qué parte tiene manchas anaranjadas, amarillas u oscuras, y qué tan lisa o punteada es su textura."),
      B("<b>La red neuronal (MLP).</b> Recibe las 27 medidas y las combina en dos capas de 8 y 4 \"neuronas\". Usa la "
        "función de activación <b>ReLU</b>, que le permite aprender combinaciones: una mancha anaranjada indica roya solo si "
        "va con textura punteada y pérdida de verde (Goodfellow et al., 2016)."),
      B("<b>Cómo aprende.</b> Compara su respuesta con la etiqueta del experto mediante la <b>entropía cruzada binaria</b>, "
        "una medida de error que castiga más los errores cometidos con seguridad. Corrige sus pesos con el método "
        "<b>Adam</b> (Kingma y Ba, 2015)."),
      B(f"<b>Práctica y examen separados por planta.</b> El modelo practica con el 70 % de las plantas, se ajusta con el 15 % "
        f"y se examina con el otro 15 %. Separar por planta, y no por foto, evita que una hoja \"vista\" en la práctica "
        f"reaparezca en el examen: si se separara por foto, el {pct(aud['pct_prueba_con_grupo_en_train_ingenua'])} de las "
        "fotos del examen tendría una hermana en la práctica."),
      Table([[img(F3, 9.8), [P(f"<b>Aprender sin memorizar.</b> Una red grande (256 y 128 neuronas) mejora hasta la época "
                                f"{c1['epoca_min_val']} y luego empieza a <b>memorizar</b>: su error con hojas nuevas se dispara. La "
                                f"red final es pequeña, apaga neuronas al azar durante la práctica (<i>dropout</i>) y se detiene "
                                f"sola cuando deja de mejorar (<b>parada temprana</b>). Su mejor punto fue la época "
                                f"{c3a['epoca_min_val']}."),
                               P(f"Comparamos tres tamaños con hojas nuevas. El error fue de {n(c3a['perdida_min_val'], 3)} para "
                                 f"8 → 4 neuronas, {n(c2['perdida_min_val'], 3)} para 16 → 8 y {n(c3b['perdida_min_val'], 3)} "
                                 "para 64 → 32. La red más pequeña generaliza igual o mejor.")]]],
            colWidths=[10.2 * cm, 7.4 * cm], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
      Paragraph("Figura 3. Error por época con hojas nuevas (línea continua) y con hojas de práctica (punteada). Cuando las dos "
                "líneas se separan, el modelo está memorizando.", st["pie"])]

# 4. Resultados
E += [Paragraph("4. Resultados y errores", st["h"]),
      P(f"El modelo no responde sí o no: da una <b>probabilidad</b> de que la hoja esté afectada. El <b>umbral</b> es el punto "
        f"de corte para dar la alerta. No usamos 0,5: probamos todos los cortes con hojas de ajuste y elegimos el de menor costo "
        f"(Figura 4). Con <b>{n(U)}</b> basta un {pct(U)} de probabilidad para alertar, porque dejar pasar una hoja enferma es "
        f"lo más caro. Un corte de 0,10 dejaría pasar {int(c10['FN'])} hojas enfermas pero daría {int(c10['FP'])} falsas "
        f"alarmas; uno de 0,50 daría {int(c50['FP'])} falsas alarmas pero dejaría pasar {int(c50['FN'])} hojas enfermas."),
      Table([[img(F4, 8.2), img(F5, 8.9)]], colWidths=[8.6 * cm, 9 * cm],
            style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
      Paragraph(f"Figura 4 (izq.). Costo de los errores según el umbral, en hojas de ajuste. Figura 5 (der.). Errores en el "
                f"examen final ({pr['n']} hojas nuevas, evaluadas una sola vez) frente a dos alternativas simples.", st["pie"]),
      tabla([["", "Red neuronal", "Un solo número (% no verde)", "No alertar nunca"],
             ["Hojas enfermas detectadas", f"{int(mlp['VP'])} de {enfermas} ({pct(mlp['recall_afectada'], 1)})",
              f"{int(esc['VP'])} de {enfermas} ({pct(esc['recall_afectada'], 1)})", f"0 de {enfermas}"],
             ["De cada 100 alertas, cuántas son reales", f"{round(100 * mlp['precision_afectada'])}",
              f"{round(100 * esc['precision_afectada'])}", "—"],
             ["Costo total (5 × FN + FP)", f"<b>{int(mlp['costo'])}</b>", f"{int(esc['costo'])}", f"{int(may['costo'])}"]],
            [5.2, 4.2, 4.6, 3.6]),
      Spacer(1, 4),
      P(f"<b>¿Qué se escapa?</b> Sobre todo las lesiones <b>incipientes</b>: roya leve (nivel 1) y ácaro rojo, con "
        f"{pct(sub['por_clase']['roya 1'], 0)} de detección cada una. Las de roya 2 a 4 se detectaron todas. <b>¿Dónde hay "
        f"más falsas alarmas?</b> Depende del celular que tomó la foto: entre {pct(min(fp_disp.values()))} y "
        f"{pct(max(fp_disp.values()))} de las hojas sanas, según el modelo de cámara. El modelo se guía sobre todo por el "
        "color de las manchas, y los brillos o tonos amarillentos de algunas fotos lo confunden.")]

# 5. Decisión y ética
E += [Paragraph("5. Decisión recomendada y riesgos éticos", st["h"]),
      P(f"<b>Recomendación.</b> Usar el modelo con umbral {n(U)} como <b>filtro para priorizar la inspección</b>. De "
        f"{pr['n']} hojas, el técnico revisaría {int(mlp['VP'] + mlp['FP'])} y solo se escaparían {int(mlp['FN'])}. Toda "
        "alerta se confirma en campo antes de aplicar cualquier producto."),
      P("<b>Principios del Marco Ético para la Inteligencia Artificial en Colombia</b> (Guío Español et al., 2021):"),
      B("<b>Responsabilidad:</b> el umbral se fijó según el daño que causa cada error al cliente, y la decisión final la "
        "toma una persona."),
      B(f"<b>Transparencia:</b> el sistema declara sus límites. Se entrenó con café robusta de una sola finca, con fotos de "
        f"{len(h['fechas_captura'])} días de 2019 y {len(h['dispositivos'])} celulares. \"Sin alerta\" no significa \"sana\", y "
        "las falsas alarmas se vigilan por celular."),
      B("<b>Equidad y beneficio social:</b> no debe usarse en café arábica ni en fincas colombianas sin una prueba piloto "
        "local, para no trasladar el riesgo de errores a productores que el modelo nunca vio."),
      P(f"<b>Uso responsable de la IA.</b> Revisamos las sugerencias del asistente de IA usado en el desarrollo. Rechazamos "
        f"una (borrar fotos duplicadas) y corregimos dos: separar los datos por planta y no por foto, y dar más tiempo a la "
        f"parada temprana. Esta última corrección mejoró la capacidad del modelo para distinguir hojas (AUC) de "
        f"{n(ap[10]['auc_val'], 3)} a {n(ap[25]['auc_val'], 3)}. <b>Próximo paso (Fase 2):</b> una red que lea la foto "
        "directamente y la combine con el clima de los 60 días previos."),
      ]

# Glosario
E += [Spacer(1, 6), caja("Glosario", [
    "<b>Falso negativo (FN):</b> hoja enferma que el sistema deja pasar sin alerta.",
    "<b>Falso positivo (FP):</b> falsa alarma: hoja sana marcada como afectada.",
    "<b>Detección (<i>recall</i>):</b> de todas las hojas enfermas, qué porcentaje detecta el sistema.",
    "<b>Umbral:</b> probabilidad mínima a partir de la cual el sistema da la alerta.",
    "<b>AUC:</b> capacidad del modelo para ordenar las hojas enfermas por encima de las sanas (0,5 = azar; 1 = perfecto).",
    "<b>Época:</b> una vuelta completa del modelo sobre las fotos de práctica.",
    "<b>Sobreajuste:</b> cuando el modelo memoriza las fotos de práctica y empeora con fotos nuevas.",
    "<b>Validación y prueba:</b> fotos apartadas para ajustar el modelo (validación) y para el examen final (prueba), "
    "que se usa una sola vez."])]

# Referencias
E += [Paragraph("Referencias", st["h"])]
for ref in [
    "Goodfellow, I., Bengio, Y., & Courville, A. (2016). <i>Deep learning</i>. MIT Press. https://www.deeplearningbook.org/",
    "Guío Español, A., Tamayo Uribe, E., Gómez Ayerbe, P., & Mujica, M. P. (2021). <i>Marco ético para la inteligencia "
    "artificial en Colombia</i>. Consejería Presidencial para Asuntos Económicos y Transformación Digital.",
    "Kingma, D. P., & Ba, J. (2015). Adam: A method for stochastic optimization. En <i>3rd International Conference on "
    "Learning Representations (ICLR)</i>. https://doi.org/10.48550/arXiv.1412.6980",
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
    canvas.drawRightString(A4[0] - 1.6 * cm, 0.9 * cm, f"Proyecto Centinela · Fase 1 · p. {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(str(SALIDA), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm, topMargin=1.3 * cm,
                        bottomMargin=1.4 * cm, title="Centinela del Café · Fase 1",
                        author="Herrera Cruz, Becerra Tirano, Vélez Martínez")
doc.build(E, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("Informe:", SALIDA)
