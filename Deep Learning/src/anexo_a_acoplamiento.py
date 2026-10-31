"""Anexo A · Prueba de acoplamiento (Propuesta de Datos, sección 5).

Lee el EXIF de las fotos (fecha y GPS), arma la clave (región, mes) y le une
el clima de los 60 días previos desde NASA POWER. Escribe:
  - data/interim/exif_inventario.csv  (huella de crudeza: fecha/GPS presentes o no)
  - anexo_a.csv                       (diez filas reales para el anexo A)

Uso:
  python src/anexo_a_acoplamiento.py --fotos data/raw --lat <LAT> --lon <LON>
Si el EXIF trae GPS, --lat/--lon se pueden omitir: se usa la mediana del GPS
redondeada a 0,1° (~11 km, nivel municipio; nunca la coordenada de la finca).
"""
import argparse
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
from PIL import Image, ExifTags

API = "https://power.larc.nasa.gov/api/temporal/daily/point"
VARS = "T2M,RH2M,PRECTOTCORR,WS2M"
GPS_TAG = next(k for k, v in ExifTags.TAGS.items() if v == "GPSInfo")


def _dms_a_grados(dms, ref):
    g = float(dms[0]) + float(dms[1]) / 60 + float(dms[2]) / 3600
    return -g if ref in ("S", "W") else g


def leer_exif(ruta):
    fila = {"archivo": ruta.name, "clase": ruta.parent.name, "fecha": None, "lat": None, "lon": None}
    try:
        with Image.open(ruta) as im:
            fila["ancho"], fila["alto"] = im.size
            exif = im.getexif()
            fecha = exif.get_ifd(0x8769).get(36867) or exif.get(306)  # DateTimeOriginal o DateTime
            if fecha:
                fila["fecha"] = datetime.strptime(fecha.strip(), "%Y:%m:%d %H:%M:%S")
            gps = exif.get_ifd(GPS_TAG)
            if gps and 2 in gps and 4 in gps:
                fila["lat"] = round(_dms_a_grados(gps[2], gps.get(1, "N")), 1)
                fila["lon"] = round(_dms_a_grados(gps[4], gps.get(3, "E")), 1)
    except Exception as e:  # archivo corrupto: se cuenta en la huella de crudeza
        fila["error"] = str(e)
    return fila


def clima_power(lat, lon, inicio, fin):
    params = {"parameters": VARS, "community": "AG", "latitude": lat, "longitude": lon,
              "start": inicio.strftime("%Y%m%d"), "end": fin.strftime("%Y%m%d"), "format": "JSON"}
    r = requests.get(API, params=params, timeout=120)
    r.raise_for_status()
    datos = r.json()["properties"]["parameter"]
    df = pd.DataFrame(datos)
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    return df.replace(-999, pd.NA)  # -999 = faltante en POWER


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fotos", type=Path, required=True)
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--region", default="origen_fotos")
    args = ap.parse_args()

    rutas = [p for p in args.fotos.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
    inv = pd.DataFrame([leer_exif(p) for p in rutas])
    Path("data/interim").mkdir(parents=True, exist_ok=True)
    inv.to_csv("data/interim/exif_inventario.csv", index=False)
    print(f"Fotos: {len(inv)} · con fecha EXIF: {inv['fecha'].notna().mean():.1%} · "
          f"con GPS: {inv['lat'].notna().mean():.1%}")

    con_fecha = inv.dropna(subset=["fecha"]).copy()
    if con_fecha.empty:
        raise SystemExit("Sin fecha EXIF: usar la clave de respaldo de la sección 5 y escribir a los autores.")

    lat = args.lat if args.lat is not None else con_fecha["lat"].median()
    lon = args.lon if args.lon is not None else con_fecha["lon"].median()
    if pd.isna(lat) or pd.isna(lon):
        raise SystemExit("Sin GPS: pasar --lat/--lon de la región declarada por los autores.")

    con_fecha["mes"] = con_fecha["fecha"].dt.to_period("M")
    clima = clima_power(lat, lon, con_fecha["fecha"].min() - timedelta(days=60), con_fecha["fecha"].max())

    filas = []
    for mes, grupo in con_fecha.groupby("mes"):
        inicio_mes = mes.to_timestamp()
        ventana = clima.loc[inicio_mes - timedelta(days=60): inicio_mes - timedelta(days=1)]
        for _, foto in grupo.iterrows():
            filas.append({"clave": f"({args.region}, {mes})", "archivo": foto["archivo"],
                          "clase": foto["clase"],
                          "RH2M_media_60d": round(float(ventana["RH2M"].mean()), 1),
                          "PRECTOTCORR_suma_60d": round(float(ventana["PRECTOTCORR"].sum()), 1)})
    acople = pd.DataFrame(filas)
    # diez filas repartidas entre meses y clases, no las diez primeras
    muestra = acople.groupby(["clave", "clase"]).head(1).head(10)
    if len(muestra) < 10:
        muestra = pd.concat([muestra, acople.drop(muestra.index).head(10 - len(muestra))])
    muestra.to_csv("anexo_a.csv", index=False)
    print(muestra.to_string(index=False))


if __name__ == "__main__":
    main()
