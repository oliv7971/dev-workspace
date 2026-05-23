"""Audit de classement du dossier 37-TUNNEL GRAND CHAMBON."""
import sqlite3
from collections import defaultdict

DB   = "reports/inventory_chambon37.db"
ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\37-TUNNEL GRAND CHAMBON\\"

def human_size(n):
    if n is None: n = 0
    for u in ["o", "Ko", "Mo", "Go", "To"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} To"

c = sqlite3.connect(DB)

total = c.execute("SELECT COUNT(*), SUM(size) FROM files").fetchone()
print(f"\n{'='*72}")
print(f"AUDIT — 37-TUNNEL GRAND CHAMBON")
print(f"{'='*72}")
print(f"  Total : {total[0]:,} fichiers   {human_size(total[1])}\n")

rows = c.execute("SELECT path, size FROM files").fetchall()

# --- 1er niveau ---
print(f"{'='*72}")
print("ARBORESCENCE 1er NIVEAU")
print(f"{'='*72}")
level1 = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl1 = parts[0] if parts else "(racine)"
    level1[lvl1][0] += 1
    level1[lvl1][1] += size or 0

for folder, (nb, sz) in sorted(level1.items(), key=lambda x: -x[1][1]):
    print(f"  {folder:<50} {nb:>7} fich.  {human_size(sz):>10}")

# --- 2e niveau ---
print(f"\n{'='*72}")
print("ARBORESCENCE 2e NIVEAU (top 40 par taille)")
print(f"{'='*72}")
level2 = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl = "\\".join(parts[:2]) if len(parts) > 2 else ("\\".join(parts[:1]) if parts else "(racine)")
    level2[lvl][0] += 1
    level2[lvl][1] += size or 0

for folder, (nb, sz) in sorted(level2.items(), key=lambda x: -x[1][1])[:40]:
    print(f"  {folder:<60} {nb:>7} fich.  {human_size(sz):>10}")

# --- 3e niveau (top 30) ---
print(f"\n{'='*72}")
print("ARBORESCENCE 3e NIVEAU (top 30 par taille)")
print(f"{'='*72}")
level3 = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl = "\\".join(parts[:3]) if len(parts) > 3 else ("\\".join(parts) if parts else "(racine)")
    level3[lvl][0] += 1
    level3[lvl][1] += size or 0

for folder, (nb, sz) in sorted(level3.items(), key=lambda x: -x[1][1])[:30]:
    print(f"  {folder:<70} {nb:>6} fich.  {human_size(sz):>10}")

# --- Extensions ---
print(f"\n{'='*72}")
print("TOP 20 EXTENSIONS (par volume)")
print(f"{'='*72}")
exts = c.execute("""
    SELECT COALESCE(LOWER(extension), '(aucune)'), COUNT(*), SUM(size)
    FROM files
    GROUP BY LOWER(extension)
    ORDER BY SUM(size) DESC
    LIMIT 20
""").fetchall()
for ext, nb, sz in exts:
    print(f"  {ext:<20} {nb:>8} fich.  {human_size(sz):>10}")

# --- Top fichiers volumineux ---
print(f"\n{'='*72}")
print("TOP 20 FICHIERS LES PLUS VOLUMINEUX")
print(f"{'='*72}")
tops = c.execute("SELECT path, size FROM files ORDER BY size DESC LIMIT 20").fetchall()
for path, sz in tops:
    short = path[len(ROOT):]
    if len(short) > 75: short = "..." + short[-72:]
    print(f"  {human_size(sz):>10}  {short}")

# --- Fichiers sans extension ---
print(f"\n{'='*72}")
print("FICHIERS SANS EXTENSION")
print(f"{'='*72}")
no_ext = c.execute(
    "SELECT COUNT(*), SUM(size) FROM files WHERE extension IS NULL OR extension = ''"
).fetchone()
print(f"  Nombre : {no_ext[0]:,}   Taille : {human_size(no_ext[1] or 0)}")
sample = c.execute(
    "SELECT path FROM files WHERE extension IS NULL OR extension = '' LIMIT 10"
).fetchall()
for (p,) in sample:
    print(f"    {p[len(ROOT):]}")

# --- Doublons potentiels (nom + taille) ---
print(f"\n{'='*72}")
print("DOUBLONS POTENTIELS (même nom + même taille — top 15 groupes)")
print(f"{'='*72}")
dupes = c.execute("""
    SELECT filename, size, COUNT(*) as n
    FROM files
    WHERE size > 102400
    GROUP BY filename, size
    HAVING n > 1
    ORDER BY n * size DESC
    LIMIT 15
""").fetchall()
if dupes:
    total_dupe_size = 0
    for nm, sz, cnt in dupes:  # nm = filename
        wasted = sz * (cnt - 1)
        total_dupe_size += wasted
        print(f"  {nm:<45} {cnt}x  {human_size(sz):>8}  perdu: {human_size(wasted)}")
    print(f"\n  Volume potentiellement dupliqué (excédent) : {human_size(total_dupe_size)}")

    # Compte global doublons candidats
    cand = c.execute("""
        SELECT COUNT(*), SUM(size) FROM (
            SELECT path, size FROM files WHERE size > 102400 AND (filename, size) IN (
                SELECT filename, size FROM files WHERE size > 102400 GROUP BY filename, size HAVING COUNT(*) > 1
            )
        )
    """).fetchone()
    print(f"  Total candidats doublons (nom+taille) : {cand[0]:,} fichiers  {human_size(cand[1])}")
else:
    print("  Aucun doublon potentiel trouvé.")

print(f"\n{'='*72}")
print("FIN DE L'AUDIT")
print(f"{'='*72}")

c.close()
