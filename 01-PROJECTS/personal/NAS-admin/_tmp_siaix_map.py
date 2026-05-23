"""
Cartographie détaillée de 38-TUNNEL DE SIAIX pour proposer un plan de regroupement.
Affiche tous les dossiers niveaux 1 et 2 avec taille et nombre de fichiers.
"""
import sqlite3
from collections import defaultdict

DB_PATH = "./reports/inventory_siaix38.db"
ROOT    = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\38-TUNNEL DE SIAIX\\"

def fmt(n):
    if n is None: n = 0
    if n >= 1_073_741_824: return f"{n/1_073_741_824:.1f} Go"
    if n >= 1_048_576:     return f"{n/1_048_576:.0f} Mo"
    return f"{n/1024:.0f} Ko"

conn = sqlite3.connect(DB_PATH)
rows = conn.execute("SELECT path, size FROM files").fetchall()
conn.close()

level1 = defaultdict(lambda: [0, 0])
level2 = defaultdict(lambda: [0, 0])

for path, size in rows:
    rel = path[len(ROOT):]
    parts = rel.split("\\")
    l1 = parts[0] if parts else "(racine)"
    level1[l1][0] += 1
    level1[l1][1] += size or 0
    l2 = "\\".join(parts[:2]) if len(parts) >= 2 else l1
    level2[l2][0] += 1
    level2[l2][1] += size or 0

print("NIVEAU 1 — tous les dossiers :")
print(f"{'Dossier':<55} {'Fich':>6}  {'Taille':>9}")
print("-"*75)
for d, (nb, sz) in sorted(level1.items(), key=lambda x: x[0]):
    print(f"  {d:<53} {nb:>6}  {fmt(sz):>9}")

print("\n\nNIVEAU 2 — tous les sous-dossiers :")
print(f"{'Dossier':<70} {'Fich':>6}  {'Taille':>9}")
print("-"*90)
for d, (nb, sz) in sorted(level2.items(), key=lambda x: x[0]):
    print(f"  {d:<68} {nb:>6}  {fmt(sz):>9}")
