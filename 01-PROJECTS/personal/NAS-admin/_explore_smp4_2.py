"""Analyse approfondie : structure L2, archives, et fichiers sans extension."""
import sqlite3
from datetime import datetime

DB = r'inventaires/inventaire_34-controle voussoirs SMP4.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

def ts(t):
    try: return datetime.fromtimestamp(float(t)).strftime('%Y-%m-%d')
    except: return '?'

# 1. Structure L2 de USINE-VOUSSOIRS-SMLP
print("=" * 100)
print("USINE-VOUSSOIRS-SMLP — Structure L2")
print("=" * 100)
prefix = BASE + 'USINE-VOUSSOIRS-SMLP\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY SUM(size) DESC LIMIT 25""",
    (prefix, prefix, prefix, prefix, prefix))
for r in c.fetchall():
    print(f"  {r[0]:<60} {r[1]:>6} {r[2]:>8} Go  {ts(r[3])} → {ts(r[4])}")

# 2. Structure L2 de _a_classer
print(f"\n{'=' * 100}")
print("_a_classer — Structure L2")
print("=" * 100)
prefix2 = BASE + '_a_classer\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY SUM(size) DESC LIMIT 25""",
    (prefix2, prefix2, prefix2, prefix2, prefix2))
for r in c.fetchall():
    print(f"  {r[0]:<60} {r[1]:>6} {r[2]:>8} Go  {ts(r[3])} → {ts(r[4])}")

# 3. Toutes les archives .7z, .zip, .rar, .gz (les gros)
print(f"\n{'=' * 100}")
print("ARCHIVES COMPRESSÉES (> 100 Mo)")
print("=" * 100)
c.execute("""SELECT path, filename, extension, size, modified_time 
FROM files WHERE extension IN ('7z', 'zip', 'rar', 'msi', 'pwzip') AND size > 104857600
ORDER BY size DESC""")
for path, fn, ext, sz, mt in c.fetchall():
    rel = path[len(BASE):]
    # Tronquer le chemin pour affichage
    if len(rel) > 80:
        rel = '...' + rel[-77:]
    print(f"  {rel:<85} {sz/1073741824:.2f} Go  {ts(mt)}")

# 4. Fichiers .gz — ce sont quoi ?
print(f"\n{'=' * 100}")
print("FICHIERS .gz — Échantillon")
print("=" * 100)
c.execute("""SELECT filename, size FROM files WHERE extension = 'gz' ORDER BY size DESC LIMIT 10""")
for fn, sz in c.fetchall():
    print(f"  {fn:<60} {sz/1048576:.1f} Mo")
c.execute("SELECT COUNT(*), ROUND(SUM(size)/1073741824.0, 2) FROM files WHERE extension = 'gz'")
cnt, go = c.fetchone()
print(f"  Total .gz: {cnt} fichiers, {go} Go")

# 5. Fichiers sans extension — ce sont quoi ? 
print(f"\n{'=' * 100}")
print("FICHIERS SANS EXTENSION — Échantillon")
print("=" * 100)
c.execute("""SELECT filename, size FROM files WHERE (extension IS NULL OR extension = '') ORDER BY size DESC LIMIT 15""")
for fn, sz in c.fetchall():
    print(f"  {fn:<60} {sz/1048576:.1f} Mo")

# Où sont-ils ?
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as folder,
    COUNT(*), ROUND(SUM(size)/1073741824.0, 2)
FROM files WHERE (extension IS NULL OR extension = '') AND path LIKE ? || '%'
GROUP BY folder ORDER BY SUM(size) DESC""", (BASE, BASE, BASE, BASE, BASE))
print(f"\n  Distribution par dossier L1:")
for folder, cnt, go in c.fetchall():
    print(f"    {folder:<55} {cnt:>6} fich  {go:>6} Go")

# 6. 06-smp — c'est quoi ?
print(f"\n{'=' * 100}")
print("06-smp — Contenu")
print("=" * 100)
prefix3 = BASE + '06-smp\\'
c.execute("SELECT extension, COUNT(*), ROUND(SUM(size)/1048576.0, 1) FROM files WHERE path LIKE ? GROUP BY extension ORDER BY SUM(size) DESC",
          (prefix3 + '%',))
for ext, cnt, mo in c.fetchall():
    print(f"  .{ext or '(sans)':<12} {cnt:>4} fich  {mo:>8} Mo")

conn.close()
