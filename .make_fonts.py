"""Réduit les polices aux caractères réellement utilisés par le site (FR, IT, EN).

Usage : python3 .make_fonts.py   (nécessite fontTools + brotli)
Entrées : fonts/*-latin.woff2 téléchargés depuis Google Fonts (licence OFL).
Sorties : les mêmes fichiers, sous-ensemblés — le texte du site reste identique.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
SOURCES = ["fraunces-latin.woff2", "fraunces-italic-latin.woff2", "manrope-latin.woff2"]

# Caractères présents dans la page (les trois langues sont dans le HTML généré), plus la ponctuation
# courante et les chiffres, pour les textes à venir.
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
text = re.sub(r"<[^>]+>", " ", html)
chars = set(text) | set("0123456789€$£%‰°«»“”‘’–—…·•→←↑↓×÷±≈≤≥")
chars |= set("ÀÁÂÄÃÅÇÈÉÊËÌÍÎÏÑÒÓÔÖÕÙÚÛÜÝàáâäãåçèéêëìíîïñòóôöõùúûüýÿŒœŸ")
chars = {c for c in chars if c.isprintable() and ord(c) > 31}
unicodes = ",".join(f"U+{ord(c):04X}" for c in sorted(chars))
print(f"{len(chars)} caractères conservés")

for name in SOURCES:
    path = os.path.join(FONTS, name)
    before = os.path.getsize(path)
    subprocess.run(
        [sys.executable, "-m", "fontTools.subset", path,
         f"--unicodes={unicodes}",
         "--layout-features=kern,liga,clig,ccmp,mark,mkmk,locl,onum,lnum,tnum,frac,case",
         "--flavor=woff2", "--output-file=" + path,
         "--name-IDs=0,1,2,3,4,5,6,13,14", "--drop-tables+=DSIG"],
        check=True,
    )
    after = os.path.getsize(path)
    print(f"{name} · {round(before/1024)} Ko → {round(after/1024)} Ko")
