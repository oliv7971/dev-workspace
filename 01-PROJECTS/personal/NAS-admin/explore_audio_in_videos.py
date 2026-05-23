#!/usr/bin/env python3
"""
explore_audio_in_videos.py
Identifie les fichiers audio dans 40-VIDEOS et explique leur origine probable.
"""
import os, sys, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\40-VIDEOS")
AUDIO_EXT = {'.m4a', '.ogg', '.flac', '.mp3', '.opus'}

by_top = defaultdict(lambda: defaultdict(list))  # top_dir -> ext -> [paths]
sizes  = defaultdict(int)

for root, dirs, files in os.walk(BASE):
    rp = Path(root)
    parts = rp.relative_to(BASE).parts if rp != BASE else ()
    top = parts[0] if parts else "(racine)"
    for f in files:
        fp = rp / f
        ext = fp.suffix.lower()
        if ext in AUDIO_EXT:
            try:
                sz = fp.stat().st_size
            except Exception:
                sz = 0
            sizes[top] += sz
            by_top[top][ext].append((fp.relative_to(BASE), sz))

def fmt(n):
    for u in ('o','Ko','Mo','Go'):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"

total_files = sum(len(v) for d in by_top.values() for v in d.values())
total_sz    = sum(sizes.values())
print(f"\n{'='*70}")
print(f"FICHIERS AUDIO dans 40-VIDEOS  —  {total_files} fichiers, {fmt(total_sz)} total")
print(f"{'='*70}\n")

for top in sorted(by_top.keys()):
    exts = by_top[top]
    nb   = sum(len(v) for v in exts.values())
    sz   = sizes[top]
    print(f"  {top}  ({nb} fichiers, {fmt(sz)})")
    for ext in sorted(exts.keys()):
        items = exts[ext]
        print(f"    {ext}: {len(items)} fichiers")
        for rel, s in sorted(items, key=lambda x:-x[1])[:4]:
            print(f"      {rel}  ({fmt(s)})")
        if len(items) > 4:
            print(f"      ... et {len(items)-4} autres")
    print()

# Vérifier si des .m4a ont un .mp4 du même nom dans le même dossier (=doublon yt-dlp)
print(f"\n{'='*70}")
print("DIAGNOSTIC : .m4a sans .mp4 correspondant (=audio seul intentionnel)")
print("             .m4a AVEC .mp4 correspondant (=résidu yt-dlp, supprimer)")
print(f"{'='*70}\n")

paired = 0; orphan = 0
for root, dirs, files in os.walk(BASE):
    rp   = Path(root)
    fset = {f.lower() for f in files}
    for f in files:
        if f.lower().endswith('.m4a'):
            stem = Path(f).stem
            has_mp4 = any((stem + ext) in fset for ext in ('.mp4','.mkv','.avi','.webm'))
            rel = (rp / f).relative_to(BASE)
            if has_mp4:
                paired += 1
            else:
                orphan += 1

print(f"  .m4a avec vidéo du même nom (résidus yt-dlp) : {paired}")
print(f"  .m4a sans vidéo correspondante (audio seul)   : {orphan}")

# Lister les .ogg dans le dossier 'videos'
print(f"\n{'='*70}")
print("Exemples de .ogg (probablement téléchargements YouTube yt-dlp)")
print(f"{'='*70}\n")
count = 0
for root, dirs, files in os.walk(BASE):
    for f in files:
        if f.lower().endswith('.ogg') and count < 15:
            rel = (Path(root) / f).relative_to(BASE)
            sz  = (Path(root)/f).stat().st_size
            print(f"  {rel}  ({fmt(sz)})")
            count += 1
if count == 0:
    print("  (aucun)")

print("\n=== FIN ===\n")
