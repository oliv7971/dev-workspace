"""Audit de classement du dossier 34-controle voussoirs SMP4."""
import sqlite3
from collections import defaultdict

DB = "reports/inventory_voussoirs_smp4.db"
ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4\\"

def human_size(n):
    for u in ["o", "Ko", "Mo", "Go", "To"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"

c = sqlite3.connect(DB)

# --- 1. Sous-dossiers de 1er niveau ---
print("\n" + "="*70)
print("ARBORESCENCE 1er NIVEAU (sous-dossiers directs)")
print("="*70)
rows = c.execute("SELECT path, size FROM files").fetchall()

level1 = defaultdict(lambda: [0, 0])  # {dossier: [nb, taille]}
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl1 = parts[0] if len(parts) > 1 else "(racine)"
    level1[lvl1][0] += 1
    level1[lvl1][1] += size or 0

sorted_l1 = sorted(level1.items(), key=lambda x: -x[1][1])
for folder, (nb, sz) in sorted_l1:
    print(f"  {folder:<45} {nb:>7} fichiers   {human_size(sz):>10}")

# --- 2. Sous-dossiers de 2e niveau ---
print("\n" + "="*70)
print("ARBORESCENCE 2e NIVEAU (top 30 par taille)")
print("="*70)
level2 = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl = "\\".join(parts[:2]) if len(parts) > 2 else ("\\".join(parts[:1]) if parts else "(racine)")
    level2[lvl][0] += 1
    level2[lvl][1] += size or 0

sorted_l2 = sorted(level2.items(), key=lambda x: -x[1][1])[:30]
for folder, (nb, sz) in sorted_l2:
    print(f"  {folder:<55} {nb:>7} fichiers   {human_size(sz):>10}")

# --- 3. Fichiers sans extension ---
print("\n" + "="*70)
print("FICHIERS SANS EXTENSION")
print("="*70)
no_ext = c.execute(
    "SELECT COUNT(*), SUM(size) FROM files WHERE extension IS NULL OR extension = ''"
).fetchone()
print(f"  Nombre : {no_ext[0]:,}   Taille : {human_size(no_ext[1] or 0)}")

# Echantillon de chemins pour comprendre leur nature
samples = c.execute(
    "SELECT path FROM files WHERE (extension IS NULL OR extension = '') LIMIT 10"
).fetchall()
print("  Exemples de chemins :")
for s in samples:
    print(f"    {s[0]}")

# --- 4. Archives (gz, zip, 7z, rar) ---
print("\n" + "="*70)
print("ARCHIVES (gz / zip / 7z / rar / pwzip)")
print("="*70)
archives = c.execute(
    "SELECT extension, COUNT(*), SUM(size) FROM files "
    "WHERE extension IN ('.gz','.zip','.7z','.rar','.pwzip') "
    "GROUP BY extension ORDER BY SUM(size) DESC"
).fetchall()
for ext, nb, sz in archives:
    print(f"  {ext:<12} {nb:>7} fichiers   {human_size(sz or 0):>10}")

# --- 5. Fichiers PDF ---
print("\n" + "="*70)
print("FICHIERS PDF (documents)")
print("="*70)
pdfs = c.execute(
    "SELECT path, size FROM files WHERE extension = '.pdf' ORDER BY size DESC LIMIT 20"
).fetchall()
for path, size in pdfs:
    rel = path[len(ROOT):]
    print(f"  {human_size(size or 0):>10}   {rel}")

# --- 6. Gros fichiers uniques ---
print("\n" + "="*70)
print("TOP 20 PLUS GROS FICHIERS")
print("="*70)
big = c.execute(
    "SELECT path, size FROM files ORDER BY size DESC LIMIT 20"
).fetchall()
for path, size in big:
    rel = path[len(ROOT):]
    print(f"  {human_size(size or 0):>10}   {rel}")

# --- 7. Extensions inconnues/métier ---
print("\n" + "="*70)
print("TOUTES LES EXTENSIONS (triées par taille)")
print("="*70)
exts = c.execute(
    "SELECT extension, COUNT(*), SUM(size) FROM files "
    "GROUP BY extension ORDER BY SUM(size) DESC"
).fetchall()
for ext, nb, sz in exts:
    print(f"  {(ext or '(aucune)'):<15} {nb:>7} fichiers   {human_size(sz or 0):>10}")

c.close()
print("\nAudit terminé.")
