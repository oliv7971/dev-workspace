"""Audit de classement du dossier 38-TUNNEL DE SIAIX."""
import sqlite3
from collections import defaultdict

DB   = "reports/inventory_siaix38.db"
ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\38-TUNNEL DE SIAIX\\"

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
print(f"AUDIT — 38-TUNNEL DE SIAIX")
print(f"{'='*72}")
print(f"  Total : {total[0]:,} fichiers   {human_size(total[1])}\n")

rows = c.execute("SELECT path, size FROM files").fetchall()

# --- Top extensions ---
print(f"{'='*72}")
print("TOP EXTENSIONS (par taille)")
print(f"{'='*72}")
ext_stats = defaultdict(lambda: [0, 0])
for path, size in rows:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path.split("\\")[-1] else "(sans ext)"
    ext_stats[ext][0] += 1
    ext_stats[ext][1] += size or 0
for ext, (nb, sz) in sorted(ext_stats.items(), key=lambda x: -x[1][1])[:20]:
    print(f"  .{ext:<15} {nb:>7} fich.  {human_size(sz):>10}")

# --- 1er niveau ---
print(f"\n{'='*72}")
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
    print(f"  {folder:<55} {nb:>7} fich.  {human_size(sz):>10}")

# --- 2e niveau ---
print(f"\n{'='*72}")
print("ARBORESCENCE 2e NIVEAU (top 50 par taille)")
print(f"{'='*72}")
level2 = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl = "\\".join(parts[:2]) if len(parts) > 2 else ("\\".join(parts[:1]) if parts else "(racine)")
    level2[lvl][0] += 1
    level2[lvl][1] += size or 0

for folder, (nb, sz) in sorted(level2.items(), key=lambda x: -x[1][1])[:50]:
    print(f"  {folder:<65} {nb:>7} fich.  {human_size(sz):>10}")

# --- 3e niveau (top 30) ---
print(f"\n{'='*72}")
print("ARBORESCENCE 3e NIVEAU (top 30 par taille)")
print(f"{'='*72}")
level3 = defaultdict(lambda: [0, 0])
for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    lvl = "\\".join(parts[:3]) if len(parts) > 3 else ("\\".join(parts[:2]) if len(parts) > 2 else "\\".join(parts[:1]))
    level3[lvl][0] += 1
    level3[lvl][1] += size or 0

for folder, (nb, sz) in sorted(level3.items(), key=lambda x: -x[1][1])[:30]:
    print(f"  {folder:<70} {nb:>7} fich.  {human_size(sz):>10}")

# --- Fichiers volumineux ---
print(f"\n{'='*72}")
print("TOP 30 FICHIERS LES PLUS LOURDS")
print(f"{'='*72}")
big = c.execute("SELECT path, size FROM files ORDER BY size DESC LIMIT 30").fetchall()
for path, size in big:
    short = path[len(ROOT):]
    print(f"  {human_size(size):>10}  {short}")

# --- Doublons potentiels (même nom + même taille) ---
print(f"\n{'='*72}")
print("DOUBLONS POTENTIELS (même nom + même taille, top 20 groupes)")
print(f"{'='*72}")
dupes = c.execute("""
    SELECT filename, size, COUNT(*) as nb
    FROM files
    WHERE size > 1024
    GROUP BY filename, size
    HAVING nb > 1
    ORDER BY (nb * size) DESC
    LIMIT 20
""").fetchall()
if dupes:
    print(f"  {'Fichier':<50} {'Taille':>10}  {'Copies':>6}  {'Gaspillage':>10}")
    print(f"  {'-'*80}")
    for fname, sz, nb in dupes:
        print(f"  {fname:<50} {human_size(sz):>10}  {nb:>6}  {human_size(sz*(nb-1)):>10}")
else:
    print("  Aucun doublon détecté.")

total_waste = c.execute("""
    SELECT SUM(size * (cnt - 1)) FROM (
        SELECT size, COUNT(*) as cnt FROM files
        WHERE size > 1024
        GROUP BY filename, size
        HAVING cnt > 1
    )
""").fetchone()[0] or 0
print(f"\n  Gaspillage total estimé (doublons) : {human_size(total_waste)}")

c.close()
