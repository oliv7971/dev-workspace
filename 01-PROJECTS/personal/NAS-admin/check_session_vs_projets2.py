import sqlite3, os
DB = os.path.abspath('inventaires/inventaire_46-BPNL.db')
conn = sqlite3.connect(DB)

# Compter fichiers SESSION et PROJETS
session_count = conn.execute("SELECT COUNT(*) FROM files WHERE path LIKE '%SESSION%'").fetchone()[0]
projets_count = conn.execute("SELECT COUNT(*) FROM files WHERE path LIKE '%PROJETS%'").fetchone()[0]
print(f"Fichiers avec SESSION dans le chemin : {session_count:,}")
print(f"Fichiers avec PROJETS dans le chemin : {projets_count:,}")

# Hashes SESSION
session_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE '%SESSION%' AND hash_md5 IS NOT NULL"
).fetchall())

# Hashes PROJETS
projets_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE '%PROJETS%' AND hash_md5 IS NOT NULL"
).fetchall())

# Fichiers SESSION dont le hash n'est pas dans PROJETS
uniques_in_session = session_hashes - projets_hashes
print(f"\nHash uniques dans SESSION (absents de PROJETS) : {len(uniques_in_session):,}")

if uniques_in_session:
    print("\n=== FICHIERS SESSION UNIQUES ===")
    rows = conn.execute(
        "SELECT path, size FROM files WHERE hash_md5 IS NOT NULL AND path LIKE '%SESSION%'"
    ).fetchall()
    unique_rows = [(p, s) for p, s in rows if conn.execute(
        "SELECT hash_md5 FROM files WHERE path=?", (p,)).fetchone()[0] in uniques_in_session]
    for p, s in sorted(unique_rows, key=lambda x: -x[1])[:50]:
        print(f"  {s/1024**2:8.1f} Mo  {p}")
else:
    print("\n=> SESSION ne contient aucun fichier unique absent de PROJETS.")
    print("=> Vous pouvez supprimer SESSION en toute securite.")

conn.close()
