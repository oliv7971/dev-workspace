import sqlite3, os

DB = os.path.abspath('inventaires/inventaire_60-CERN.db')
conn = sqlite3.connect(DB)

travail_rows = conn.execute(
    "SELECT path, size, hash_md5 FROM files WHERE path LIKE '%11-scans CERN%3dreshaper%' AND hash_md5 IS NOT NULL"
).fetchall()

livraison_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE '%CERN-FR-PT5%3dreshaper%' AND hash_md5 IS NOT NULL"
).fetchall())

uniques = [(p, s) for p, s, h in travail_rows if h not in livraison_hashes]
total = sum(s for _, s in uniques)

out = os.path.abspath('reports/cern_uniques_complet.txt')
with open(out, 'w', encoding='utf-8') as f:
    f.write(f"Total : {len(uniques)} fichiers uniques dans TRAVAIL - {total/1024**3:.2f} Go\n")
    f.write("="*100 + "\n\n")
    for p, s in sorted(uniques, key=lambda x: x[0]):
        f.write(f"{s/1024**2:10.1f} Mo  {p}\n")

print(f"Rapport ecrit : {out}")
print(f"Total : {len(uniques)} fichiers - {total/1024**3:.2f} Go")
conn.close()
