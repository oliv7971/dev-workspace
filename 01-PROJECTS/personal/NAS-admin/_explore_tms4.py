"""Vérifier la poupée russe 270616_CHAT/270616_CHAT/ et les overlaps internes."""
import sqlite3

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE_TMS = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\TMS\\'
BASE_CHAT = BASE_TMS + '270616_CHAT\\'
BASE_INNER = BASE_CHAT + '270616_CHAT\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Structure du sous-dossier interne 270616_CHAT/270616_CHAT/
print("=== Structure de 270616_CHAT/270616_CHAT/ (L4) ===")
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY SUM(size) DESC""", 
    (BASE_INNER, BASE_INNER, BASE_INNER, BASE_INNER, BASE_INNER))

for r in c.fetchall():
    print(f"  {r[0]:<55} {r[1]:>6} fich  {r[2]:>6} Go")

# Extensions dans le sous-dossier interne
print("\n=== Extensions dans 270616_CHAT/270616_CHAT/ ===")
c.execute("""SELECT extension, COUNT(*), ROUND(SUM(size)/1073741824.0, 2)
FROM files WHERE path LIKE ? || '%'
GROUP BY extension ORDER BY SUM(size) DESC""", (BASE_INNER,))
for ext, cnt, go in c.fetchall():
    print(f"  .{ext or '(sans)':<10} {cnt:>6} fich  {go:>6} Go")

# Overlap: 270616_CHAT/270616_CHAT/ vs 270616_CHAT/ (hors le sous-dossier lui-même)
print("\n=== Overlap: inner vs outer (hors inner) ===")

# Fichiers de inner
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (BASE_INNER + '%',))
inner = c.fetchall()
inner_h = {h for _, _, h in inner if h}
inner_ns = {(fn, sz) for fn, sz, _ in inner}

# Fichiers de outer HORS inner
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ? AND path NOT LIKE ?",
          (BASE_CHAT + '%', BASE_INNER + '%'))
outer = c.fetchall()
outer_h = {h for _, _, h in outer if h}
outer_ns = {(fn, sz) for fn, sz, _ in outer}

# inner ⊂ outer ?
m_in_out = sum(1 for fn, sz, h in inner if (h and h in outer_h) or (fn, sz) in outer_ns)
print(f"  Inner: {len(inner)} fich, {sum(s for _, s, _ in inner)/1073741824:.1f} Go")
print(f"  Outer (hors inner): {len(outer)} fich, {sum(s for _, s, _ in outer)/1073741824:.1f} Go")
print(f"  Inner → Outer: {m_in_out}/{len(inner)} ({m_in_out*100//len(inner) if inner else 0}%)")

# outer ⊂ inner ?
m_out_in = sum(1 for fn, sz, h in outer if (h and h in inner_h) or (fn, sz) in inner_ns)
print(f"  Outer → Inner: {m_out_in}/{len(outer)} ({m_out_in*100//len(outer) if outer else 0}%)")

# Aussi: overlap entre s01-scans et inner
print("\n=== s01-scans 280616 vs 270616_CHAT/270616_CHAT/ ===")
prefix_s01 = BASE_CHAT + 's01-scans 280616\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix_s01 + '%',))
s01 = c.fetchall()
s01_h = {h for _, _, h in s01 if h}
s01_ns = {(fn, sz) for fn, sz, _ in s01}

m_s01_inner = sum(1 for fn, sz, h in s01 if (h and h in inner_h) or (fn, sz) in inner_ns)
print(f"  s01-scans: {len(s01)} fich → inner: {m_s01_inner}/{len(s01)} ({m_s01_inner*100//len(s01) if s01 else 0}%)")

m_inner_s01 = sum(1 for fn, sz, h in inner if (h and h in s01_h) or (fn, sz) in s01_ns)
print(f"  inner → s01-scans: {m_inner_s01}/{len(inner)} ({m_inner_s01*100//len(inner) if inner else 0}%)")

conn.close()
