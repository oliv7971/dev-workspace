#!/usr/bin/env python3
"""
analyze_42_photos_dupes.py
Compare les dossiers 31-PHOTOS et PHOTOS dans 42-PHOTOS pour identifier les doublons.
Utilise les hash MD5 pour une comparaison fiable.
"""
import os
import hashlib
import sys
from pathlib import Path

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\42-PHOTOS")
DIR_A = BASE / "31-PHOTOS"
DIR_B = BASE / "PHOTOS"

REPORT = Path("reports/analyze_31photos_vs_photos.txt")
REPORT.parent.mkdir(exist_ok=True)

SKIP = {'@eaDir', '#recycle', 'Thumbs.db', 'desktop.ini'}


def hash_file(p: Path) -> str | None:
    try:
        h = hashlib.md5()
        with open(p, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def scan_dir(base: Path) -> dict:
    """Retourne {hash: [chemin_relatif, ...]}"""
    result = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            if f in SKIP:
                continue
            fp = Path(root) / f
            rel = fp.relative_to(base)
            print(f"  hash: {rel}", end='\r')
            h = hash_file(fp)
            if h:
                result.setdefault(h, []).append(str(rel))
    print()
    return result


print(f"Scan de {DIR_A.name} ...")
hashes_a = scan_dir(DIR_A)
print(f"  {len(hashes_a)} hashes uniques")

print(f"Scan de {DIR_B.name} ...")
hashes_b = scan_dir(DIR_B)
print(f"  {len(hashes_b)} hashes uniques")

set_a = set(hashes_a)
set_b = set(hashes_b)

common   = set_a & set_b
only_a   = set_a - set_b
only_b   = set_b - set_a

lines = []
lines.append(f"Comparaison : {DIR_A.name}  vs  {DIR_B.name}")
lines.append("=" * 70)
lines.append(f"  Fichiers dans {DIR_A.name}  : {sum(len(v) for v in hashes_a.values())}")
lines.append(f"  Fichiers dans {DIR_B.name}   : {sum(len(v) for v in hashes_b.values())}")
lines.append(f"  Hashes uniques A : {len(set_a)}")
lines.append(f"  Hashes uniques B : {len(set_b)}")
lines.append(f"  Communs (doublons) : {len(common)}")
lines.append(f"  Uniques à {DIR_A.name}  : {len(only_a)}")
lines.append(f"  Uniques à {DIR_B.name}   : {len(only_b)}")

lines.append(f"\n{'=' * 70}")
lines.append(f"FICHIERS UNIQUES DANS {DIR_A.name} (absents de PHOTOS) — à conserver/migrer")
lines.append("=" * 70)
for h in sorted(only_a):
    for p in hashes_a[h]:
        lines.append(f"  {p}")

lines.append(f"\n{'=' * 70}")
lines.append(f"FICHIERS EN DOUBLE (présents dans les 2)")
lines.append("=" * 70)
for h in sorted(common):
    pa = hashes_a[h]
    pb = hashes_b[h]
    lines.append(f"  A: {pa[0]}")
    lines.append(f"  B: {pb[0]}")
    lines.append("")

REPORT.write_text('\n'.join(lines), encoding='utf-8')
print(f"\nRapport: {REPORT}")
for l in lines[:12]:
    print(l)
