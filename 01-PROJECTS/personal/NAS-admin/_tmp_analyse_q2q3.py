"""
Q2 : Compare les .zfs de TMS CHAMBON vs ceux de 02-PHASE 02 (taille + nom)
Q3 : Identifie le .dwg répété 32 fois
"""
import sqlite3
import os
from collections import defaultdict

DB_PATH = "./reports/inventory_chambon37.db"
BASE = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── Q2 : .zfs dans TMS CHAMBON vs 02-PHASE 02 ──────────────────────────────
print("=" * 70)
print("Q2 — Comparaison .zfs : TMS CHAMBON vs 02-PHASE 02")
print("=" * 70)

cur.execute("""
    SELECT filename, size, path
    FROM files
    WHERE UPPER(filename) LIKE '%.ZFS'
      AND path LIKE '%TMS CHAMBON%'
    ORDER BY filename
""")
tms = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
print(f"\nTMS CHAMBON : {len(tms)} fichiers .zfs\n")

cur.execute("""
    SELECT filename, size, path
    FROM files
    WHERE UPPER(filename) LIKE '%.ZFS'
      AND path LIKE '%02-PHASE 02%'
    ORDER BY filename
""")
phase02_rows = cur.fetchall()
# Regroupe par nom (il peut y en avoir plusieurs copies dans 02-PHASE 02)
phase02 = defaultdict(list)
for fname, size, path in phase02_rows:
    phase02[fname].append((size, path))

print(f"02-PHASE 02 : {len(phase02_rows)} fichiers .zfs ({len(phase02)} noms distincts)\n")

print(f"{'Fichier':<55} {'TMS Mo':>8} {'P02 Mo':>8} {'Taille?':>8}")
print("-" * 82)

tms_only = []
size_mismatch = []
match = []

for fname, (tms_size, tms_path) in sorted(tms.items()):
    if fname not in phase02:
        tms_only.append(fname)
        print(f"  TMS SEUL  {fname:<53} {tms_size/1e6:>8.1f}")
    else:
        # Vérifier si au moins une copie dans 02-PHASE 02 a la même taille
        p02_sizes = [s for s, _ in phase02[fname]]
        if tms_size in p02_sizes:
            match.append(fname)
            print(f"  OK        {fname:<53} {tms_size/1e6:>8.1f}  {tms_size/1e6:>8.1f}  IDENTIQUE")
        else:
            size_mismatch.append((fname, tms_size, p02_sizes))
            p02_str = "/".join(f"{s/1e6:.1f}" for s in p02_sizes)
            print(f"  DIFF TAILLE {fname:<51} {tms_size/1e6:>8.1f}  {p02_str:>8}  !!!")

print()
print(f"  Identiques (nom+taille) : {len(match)}")
print(f"  Taille différente       : {len(size_mismatch)}")
print(f"  Uniquement dans TMS     : {len(tms_only)}")

if size_mismatch:
    print("\n  Détail tailles différentes :")
    for fname, tms_sz, p02_szs in size_mismatch:
        print(f"    {fname}")
        print(f"      TMS       : {tms_sz:,} octets")
        for sz in p02_szs:
            print(f"      02-PHASE  : {sz:,} octets  (diff={tms_sz-sz:+,})")

# ── Q3 : .dwg répété 32 fois ────────────────────────────────────────────────
print()
print("=" * 70)
print("Q3 — Fichier .dwg répété 32 fois")
print("=" * 70)

cur.execute("""
    SELECT filename, COUNT(*) as n, SUM(size) as total_size, MIN(size), MAX(size)
    FROM files
    WHERE UPPER(filename) LIKE '%.DWG'
    GROUP BY filename
    HAVING COUNT(*) > 5
    ORDER BY n DESC
    LIMIT 10
""")
rows = cur.fetchall()
for fname, n, total, minsize, maxsize in rows:
    print(f"\n  {fname}")
    print(f"  {n} copies  |  total : {total/1e6:.1f} Mo  |  taille unitaire : {minsize/1e6:.1f}–{maxsize/1e6:.1f} Mo")
    # Lister les chemins
    cur.execute("""
        SELECT path FROM files WHERE filename = ? ORDER BY path
    """, (fname,))
    paths = cur.fetchall()
    for (p,) in paths:
        rel = os.path.relpath(p, BASE)
        print(f"    {rel}")

conn.close()
