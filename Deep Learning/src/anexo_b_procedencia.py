"""Anexo B · Cadena de procedencia: huella SHA-256 de cada archivo descargado.

Uso:  python src/anexo_b_procedencia.py data/raw/Monilia.rar data/raw/Sanos.rar data/raw/power_daily.csv
Lee por bloques: los .rar pesan varios GB y no caben de una vez en la RAM de Colab.
"""
import hashlib
import sys
from datetime import date
from pathlib import Path

FUENTES = {
    "Monilia.rar": "https://doi.org/10.17632/ykbtpsyfv9.1",
    "Sanos.rar": "https://doi.org/10.17632/ykbtpsyfv9.1",
    "power_daily.csv": "https://power.larc.nasa.gov/api/temporal/daily/point",
}


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


print("| Archivo (nombre exacto) | URL o DOI del productor primario | Fecha de descarga | Huella SHA-256 |")
print("| --- | --- | --- | --- |")
for ruta in map(Path, sys.argv[1:]):
    descarga = date.fromtimestamp(ruta.stat().st_mtime).isoformat()
    print(f"| `{ruta.name}` | {FUENTES.get(ruta.name, '?')} | {descarga} | `{sha256(ruta)}` |")
