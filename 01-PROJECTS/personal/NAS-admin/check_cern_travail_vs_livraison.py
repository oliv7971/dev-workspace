"""
Compare les fichiers entre :
  - 11-scans CERN\3dreshaper\ (dossier de travail)
  - 11-scans CERN\CERN-FR-PT5-21-09-03\zf\CERN-FR-PT5-21-09-03\3dreshaper\ (livraison)
Pour savoir lequel contient des fichiers uniques avant suppression.
"""
import sqlite3, os

DB = os.path.abspath('inventaires/inventaire_60-CERN.db')
conn = sqlite3.connect(DB)

TRAVAIL   = '%11-scans CERN\\3dreshaper%'
LIVRAISON = '%CERN-FR-PT5-21-09-03\\\\zf\\\\CERN-FR-PT5-21-09-03\\\\3dreshaper%'

# Compter
t_count = conn.execute("SELECT COUNT(*) FROM files WHERE path LIKE ?", (TRAVAIL,)).fetchone()[0]
l_count = conn.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE '%CERN-FR-PT5%3dreshaper%'").fetchone()

print(f"Fichiers dans TRAVAIL (3dreshaper)   : {t_count:,}")
print(f"Fichiers dans LIVRAISON (CERN-FR-PT5 3dreshaper) : {l_count[0]:,}  ({l_count[1]/1024**3:.1f} Go)")

# Hashes TRAVAIL
travail_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE ? AND hash_md5 IS NOT NULL", (TRAVAIL,)
).fetchall())

# Hashes LIVRAISON
livraison_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE '%CERN-FR-PT5%3dreshaper%' AND hash_md5 IS NOT NULL"
).fetchall())

uniques_travail   = travail_hashes - livraison_hashes
uniques_livraison = livraison_hashes - travail_hashes

print(f"\nUniques dans TRAVAIL (absents de LIVRAISON)   : {len(uniques_travail):,}")
print(f"Uniques dans LIVRAISON (absents de TRAVAIL)   : {len(uniques_livraison):,}")

# Taille des uniques TRAVAIL
if uniques_travail:
    rows = conn.execute("SELECT path, size, hash_md5 FROM files WHERE path LIKE ? AND hash_md5 IS NOT NULL", (TRAVAIL,)).fetchall()
    u_rows = [(p, s) for p, s, h in rows if h in uniques_travail]
    total_u = sum(s for _, s in u_rows)
    print(f"\n=== UNIQUES dans TRAVAIL ({len(u_rows)} fichiers - {total_u/1024**3:.2f} Go) ===")
    for p, s in sorted(u_rows, key=lambda x: -x[1])[:20]:
        print(f"  {s/1024**2:8.1f} Mo  {p}")

# Taille des uniques LIVRAISON
if uniques_livraison:
    rows = conn.execute("SELECT path, size, hash_md5 FROM files WHERE path LIKE '%CERN-FR-PT5%3dreshaper%' AND hash_md5 IS NOT NULL").fetchall()
    u_rows = [(p, s) for p, s, h in rows if h in uniques_livraison]
    total_u = sum(s for _, s in u_rows)
    print(f"\n=== UNIQUES dans LIVRAISON ({len(u_rows)} fichiers - {total_u/1024**3:.2f} Go) ===")
    for p, s in sorted(u_rows, key=lambda x: -x[1])[:20]:
        print(f"  {s/1024**2:8.1f} Mo  {p}")

conn.close()
