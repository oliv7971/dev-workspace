#!/usr/bin/env python3
"""
explore_40_videos.py
Analyse la structure de 40-VIDEOS :
- Liste les sous-dossiers de premier niveau avec tailles et nombre de fichiers
- Détecte les extensions présentes
- Repère les fichiers potentiellement inutiles (nfo, jpg isolés, txt, srt, sub, idx, etc.)
- Repère les petits fichiers suspects (< 1 Mo)
"""

import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from collections import defaultdict

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\40-VIDEOS")

# Extensions vidéo reconnues
VIDEO_EXT = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.m4v', '.mpg', '.mpeg',
             '.ts', '.m2ts', '.vob', '.divx', '.xvid', '.webm', '.ogv', '.rmvb', '.rm'}

# Extensions jugées "junk" ou secondaires
JUNK_EXT = {'.nfo', '.url', '.lnk', '.db', '.ini', '.log', '.bak', '.tmp'}
SUB_EXT  = {'.srt', '.sub', '.idx', '.ass', '.ssa', '.vtt', '.sup'}
IMG_EXT  = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tbn', '.webp'}
TXT_EXT  = {'.txt', '.nfo', '.url', '.htm', '.html'}


def fmt_size(n):
    for unit in ('o', 'Ko', 'Mo', 'Go', 'To'):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} Po"


def scan_dir(path: Path):
    """Retourne (total_size, nb_files, ext_counts, junk_files, small_videos)"""
    total = 0
    nb = 0
    ext_counts = defaultdict(int)
    junk_files = []
    small_videos = []

    for root, dirs, files in os.walk(path):
        for f in files:
            fp = Path(root) / f
            try:
                sz = fp.stat().st_size
            except Exception:
                sz = 0
            total += sz
            nb += 1
            ext = fp.suffix.lower()
            ext_counts[ext] += 1

            if ext in JUNK_EXT:
                junk_files.append((fp, sz))
            if ext in IMG_EXT and sz < 500_000:
                junk_files.append((fp, sz))
            if ext in TXT_EXT and sz < 100_000:
                junk_files.append((fp, sz))
            if ext in VIDEO_EXT and sz < 1_000_000:
                small_videos.append((fp, sz))

    return total, nb, ext_counts, junk_files, small_videos


print(f"\nAnalyse de : {BASE}\n")
print("=" * 80)

# Scan global
total_size = 0
total_files = 0
all_ext = defaultdict(int)
all_junk = []
all_small_videos = []
top_dirs = []

try:
    entries = sorted(BASE.iterdir())
except Exception as e:
    print(f"ERREUR accès racine: {e}")
    exit(1)

# Fichiers à la racine (hors sous-dossiers)
root_files = [e for e in entries if e.is_file()]
root_dirs  = [e for e in entries if e.is_dir()]

print(f"Fichiers à la racine : {len(root_files)}")
for f in root_files:
    try:
        sz = f.stat().st_size
    except Exception:
        sz = 0
    print(f"  {f.name}  ({fmt_size(sz)})")

print(f"\nSous-dossiers de premier niveau : {len(root_dirs)}\n")
print(f"{'Dossier':<50} {'Taille':>10}  {'Fichiers':>8}  {'Vidéos':>7}  {'Junk':>6}")
print("-" * 90)

for d in sorted(root_dirs):
    sz, nb, ext_c, junk, small_v = scan_dir(d)
    total_size += sz
    total_files += nb
    for k, v in ext_c.items():
        all_ext[k] += v
    all_junk.extend(junk)
    all_small_videos.extend(small_v)
    nb_video = sum(v for k, v in ext_c.items() if k in VIDEO_EXT)
    nb_junk  = len(junk)
    print(f"  {d.name:<48} {fmt_size(sz):>10}  {nb:>8}  {nb_video:>7}  {nb_junk:>6}")
    top_dirs.append((d.name, sz, nb, nb_video, nb_junk))

print("-" * 90)
print(f"  {'TOTAL':<48} {fmt_size(total_size):>10}  {total_files:>8}")

# Extensions présentes
print("\n\n=== EXTENSIONS PRÉSENTES ===")
for ext, cnt in sorted(all_ext.items(), key=lambda x: -x[1]):
    category = ""
    if ext in VIDEO_EXT: category = "[VIDEO]"
    elif ext in SUB_EXT:  category = "[SOUS-TITRES]"
    elif ext in IMG_EXT:  category = "[IMAGE]"
    elif ext in JUNK_EXT: category = "[JUNK]"
    elif ext in TXT_EXT:  category = "[TEXTE]"
    print(f"  {ext:<12} {cnt:>6}  {category}")

# Fichiers junk
print(f"\n\n=== FICHIERS POTENTIELLEMENT INUTILES ({len(all_junk)}) ===")
print("(nfo, url, ini, db, images isolées < 500Ko, txt...)\n")
# Grouper par extension
by_ext = defaultdict(list)
for fp, sz in all_junk:
    by_ext[fp.suffix.lower()].append((fp, sz))
for ext in sorted(by_ext.keys()):
    items = by_ext[ext]
    total_junk_sz = sum(s for _, s in items)
    print(f"  {ext}  — {len(items)} fichier(s), {fmt_size(total_junk_sz)} total")
    for fp, sz in sorted(items, key=lambda x: -x[1])[:5]:  # top 5
        try:
            rel = fp.relative_to(BASE)
        except Exception:
            rel = fp
        print(f"      {rel}  ({fmt_size(sz)})")
    if len(items) > 5:
        print(f"      ... et {len(items)-5} autres")

# Petites vidéos suspectes
print(f"\n\n=== PETITES VIDÉOS SUSPECTES (< 1 Mo, {len(all_small_videos)}) ===")
for fp, sz in sorted(all_small_videos, key=lambda x: x[1])[:30]:
    try:
        rel = fp.relative_to(BASE)
    except Exception:
        rel = fp
    print(f"  {fmt_size(sz):>10}  {rel}")

print("\n=== FIN ANALYSE ===\n")
