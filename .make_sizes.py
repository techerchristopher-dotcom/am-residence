"""Versions allégées de toutes les photos du site (960 px et 1440 px à côté des 1800 px d'origine).

Usage : python3 .make_sizes.py
Le HTML les propose en `srcset` : un téléphone télécharge la 960, un grand écran la 1800.
Les logos, favicons et vignettes Taxi Food sont ignorés (déjà petits).
"""
import os
import subprocess

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
SKIP = ("logo-", "favicon", "og.jpg", "tf-", "rentanoo-logo", "taxifood-logo")
WIDTHS = (960, 1440)

sources = sorted(
    f for f in os.listdir(IMG)
    if f.endswith(".webp") and not any(f.startswith(s) or s in f for s in SKIP)
    and not any(f.endswith(f"-{w}.webp") for w in WIDTHS)
)

total_before = total_after = 0
for name in sources:
    source = os.path.join(IMG, name)
    base = name[: -len(".webp")]
    for width in WIDTHS:
        target = os.path.join(IMG, f"{base}-{width}.webp")
        if os.path.exists(target) and os.path.getmtime(target) > os.path.getmtime(source):
            continue
        subprocess.run(["cwebp", "-quiet", "-q", "78", "-resize", str(width), "0", source, "-o", target], check=True)
    total_before += os.path.getsize(source)
    total_after += os.path.getsize(os.path.join(IMG, f"{base}-960.webp"))

print(f"{len(sources)} photos · 1800 px : {round(total_before/1024/1024, 1)} Mo · 960 px : {round(total_after/1024/1024, 1)} Mo")
