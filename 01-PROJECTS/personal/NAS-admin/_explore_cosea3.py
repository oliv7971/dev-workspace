import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_12-COSEA.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\12-COSEA'
SAUV = BASE + r'\sauvegardes'

conn = sqlite3.connect(DB)
c = conn.cursor()

# ── 1) Sous-dossiers de sauvegardes/ ────────────────────────────────────
c.execute("SELECT path, size FROM files WHERE path LIKE ?", (SAUV + r'\%',))
sub = defaultdict(lambda: [0, 0])
for path, size in c.fetchall():
    rel = path.replace(SAUV, '').lstrip('\\')
    top = rel.split('\\')[0] if '\\' in rel else '(racine sauv)'
    sub[top][0] += 1
    sub[top][1] += (size or 0)

print(f"{'Sous-dossier de sauvegardes/':<60} {'Fich':>7} {'Go':>7}")
print('=' * 78)
for d in sorted(sub.keys()):
    cnt, sz = sub[d]
    print(f"  {d:<58} {cnt:>7} {sz/1024**3:>6.1f}")

# ── 2) Hash MD5 dans sauvegardes vs reste ────────────────────────────────
c.execute("""
    SELECT COUNT(*), COALESCE(SUM(size),0)
    FROM files WHERE path LIKE ? AND hash_md5 IS NOT NULL AND hash_md5 != ''
""", (SAUV + r'\%',))
n_hash_sauv, _ = c.fetchone()

c.execute("SELECT COUNT(*) FROM files WHERE path LIKE ?", (SAUV + r'\%',))
n_sauv = c.fetchone()[0]

print(f"\n  Hash dans sauvegardes/ : {n_hash_sauv}/{n_sauv}")

# ── 3) Doublons MD5 : fichiers de sauvegardes identiques à un fichier hors sauvegardes
c.execute("""
    SELECT s.hash_md5, COUNT(*) as cnt, SUM(s.size) as sz
    FROM files s
    WHERE s.path LIKE ?
      AND s.hash_md5 IS NOT NULL AND s.hash_md5 != ''
      AND EXISTS (
          SELECT 1 FROM files o
          WHERE o.hash_md5 = s.hash_md5
            AND o.path NOT LIKE ?
      )
    GROUP BY s.hash_md5
""", (SAUV + r'\%', SAUV + r'\%'))

dupes = c.fetchall()
total_dupe_files = sum(cnt for _, cnt, _ in dupes)
total_dupe_size  = sum(sz for _, _, sz in dupes)
total_dupe_hashes = len(dupes)

print(f"\n  Fichiers sauvegardes identiques (MD5) à un fichier hors sauvegardes :")
print(f"    {total_dupe_files} fichiers ({total_dupe_size/1024**3:.1f} Go)")
print(f"    {total_dupe_hashes} hashes distincts")

# ── 4) Fichiers de sauvegardes UNIQUES (aucun doublon hors sauvegardes)
c.execute("""
    SELECT COUNT(*), COALESCE(SUM(size),0)
    FROM files s
    WHERE s.path LIKE ?
      AND s.hash_md5 IS NOT NULL AND s.hash_md5 != ''
      AND NOT EXISTS (
          SELECT 1 FROM files o
          WHERE o.hash_md5 = s.hash_md5
            AND o.path NOT LIKE ?
      )
""", (SAUV + r'\%', SAUV + r'\%'))
n_unique, sz_unique = c.fetchone()
print(f"\n  Fichiers sauvegardes UNIQUES (pas de copie ailleurs) :")
print(f"    {n_unique} fichiers ({sz_unique/1024**3:.1f} Go)")

# ── 5) Fichiers sans hash dans sauvegardes
c.execute("""
    SELECT COUNT(*), COALESCE(SUM(size),0)
    FROM files WHERE path LIKE ?
    AND (hash_md5 IS NULL OR hash_md5 = '')
""", (SAUV + r'\%',))
n_noh, sz_noh = c.fetchone()
print(f"\n  Fichiers sauvegardes SANS hash (non comparables) :")
print(f"    {n_noh} fichiers ({sz_noh/1024**3:.1f} Go)")

# ── 6) Gros dossiers redondants dans les dossiers principaux (pas seulement sauvegardes)
print(f"\n\n=== Autres dossiers 'sauvegarde' intégrés dans les dossiers principaux ===")
SAUV_KW = ['sauvegarde', 'backup', 'save']
c.execute("SELECT DISTINCT path FROM files WHERE path NOT LIKE ?", (SAUV + r'\%',))
found = set()
for (p,) in c.fetchall():
    rel = p.replace(BASE + '\\', '').lower()
    parts = rel.split('\\')
    for i, part in enumerate(parts):
        if any(kw in part for kw in SAUV_KW):
            found.add(BASE + '\\' + p.replace(BASE + '\\', '').split('\\')[0] + '\\' + '\\'.join(p.replace(BASE + '\\', '').split('\\')[1:i+1]))
            break

# Filtrer racines uniquement
roots = sorted(found)
filtered = [p for p in roots if not any(p.startswith(o + '\\') for o in roots if o != p)]
for p in sorted(filtered):
    c.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?", (p + '%',))
    cnt, sz = c.fetchone()
    if cnt > 50:
        rel = p.replace(BASE + '\\', '')
        print(f"  {rel:<70} {cnt:>7} fich  {sz/1024**3:.1f} Go")

conn.close()
