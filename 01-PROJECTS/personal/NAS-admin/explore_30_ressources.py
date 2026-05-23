#!/usr/bin/env python3
"""
explore_30_ressources.py
Analyse la structure de 30-RESSOURCES
"""
import os, sys, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\30-RESSOURCES")

def fmt(n):
    for u in ('o','Ko','Mo','Go','To'):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Po"

def scan(path):
    total, nb = 0, 0
    ext_c = defaultdict(int)
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = Path(root) / f
            try: sz = fp.stat().st_size
            except: sz = 0
            total += sz; nb += 1
            ext_c[fp.suffix.lower()] += 1
    return total, nb, ext_c

print(f"\nAnalyse de : {BASE}\n")
print(f"{'Dossier':<55} {'Ss-doss':>8}  {'Fich.direct':>12}")
print("-" * 80)

try:
    entries = sorted(BASE.iterdir())
except Exception as e:
    print(f"ERREUR : {e}"); exit(1)

root_files = [e for e in entries if e.is_file()]
root_dirs  = [e for e in entries if e.is_dir()]

for f in root_files:
    try: sz = f.stat().st_size
    except: sz = 0
    print(f"  [F] {f.name:<50} {fmt(sz):>10}")

print(f"\nSous-dossiers de premier niveau : {len(root_dirs)}\n")

# Listing non-récursif : juste niveau 1 + contenu direct
for d in root_dirs:
    try:
        items   = sorted(d.iterdir())
        subdirs = [i for i in items if i.is_dir()]
        files   = [i for i in items if i.is_file()]
    except:
        print(f"  {d.name:<53}  (erreur accès)")
        continue
    print(f"  {d.name:<53}  {len(subdirs):>3} ss-doss  {len(files):>4} fich")
    for s in subdirs[:20]:
        try:
            sub_items = list(s.iterdir())
            sub_dirs2 = sum(1 for x in sub_items if x.is_dir())
            sub_files2 = sum(1 for x in sub_items if x.is_file())
        except:
            sub_dirs2 = sub_files2 = 0
        print(f"    {s.name:<51}  {sub_dirs2:>3} ss-doss  {sub_files2:>4} fich")
    if len(subdirs) > 20:
        print(f"    ... et {len(subdirs)-20} autres sous-dossiers")
    print()

print("\n=== FIN ===")
