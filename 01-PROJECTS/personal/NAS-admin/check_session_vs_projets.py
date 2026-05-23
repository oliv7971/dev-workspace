import sqlite3, os

DB = os.path.abspath('inventaires/inventaire_46-BPNL.db')
conn = sqlite3.connect(DB)

SESSION = '\\\\\\\\Nas_travail\\\\01-ds414-data\\\\31-GGC-DOSSIERS\\\\46-BPNL\\\\01-scans BPNL\\\\01-SESSION SCAN NOV2015\\\\'
PROJETS = '\\\\\\\\Nas_travail\\\\01-ds414-data\\\\31-GGC-DOSSIERS\\\\46-BPNL\\\\01-scans BPNL\\\\01-PROJETS SCANS BPNL SUD NOV2015\\\\'

# Tous les fichiers de SESSION avec leur hash
session_files = conn.execute(
    "SELECT path, hash_md5, size FROM files WHERE path LIKE ?", (SESSION + '%',)
).fetchall()

# Tous les hash présents dans PROJETS
projets_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE ? AND hash_md5 IS NOT NULL", (PROJETS + '%',)
).fetchall())

# Fichiers SESSION sans équivalent dans PROJETS
uniques_session = [(p, h, s) for p, h, s in session_files if h not in projets_hashes]
uniques_no_hash  = [(p, h, s) for p, h, s in session_files if h is None]

print(f"Fichiers dans SESSION     : {len(session_files):,}")
print(f"Hash PROJETS              : {len(projets_hashes):,}")
print(f"Fichiers SESSION sans hash: {len(uniques_no_hash):,}")
print(f"Fichiers SESSION UNIQUES  : {len(uniques_session):,}  (pas dans PROJETS)")
print()

if uniques_session:
    total_size = sum(s for _, _, s in uniques_session)
    print(f"Taille totale des uniques : {total_size/1024**3:.2f} Go")
    print()
    print("=== FICHIERS UNIQUES DANS SESSION (pas dans PROJETS) ===")
    for p, h, s in sorted(uniques_session, key=lambda x: -x[2]):
        print(f"  {s/1024**2:8.1f} Mo  {p}")
else:
    print("SESSION ne contient aucun fichier unique absent de PROJETS.")
    print("=> Vous pouvez supprimer SESSION en toute securite.")

conn.close()
