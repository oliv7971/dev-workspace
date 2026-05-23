"""Analyse de la structure de 01-SFTRF pour identifier junk et doublons."""
import sqlite3

DB = "./reports/inventory_sftrf.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\01-SFTRF"

conn = sqlite3.connect(DB)
cur = conn.cursor()

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

# 1. Top-level structure
print("=" * 70)
print("1. STRUCTURE TOP-LEVEL")
print("=" * 70)
cur.execute(f"""SELECT 
    SUBSTR(path, {len(BASE)+2}, INSTR(SUBSTR(path, {len(BASE)+2}), '\\')-1) as top_folder,
    COUNT(*), SUM(size)
FROM files 
GROUP BY top_folder ORDER BY SUM(size) DESC""")
for row in cur.fetchall():
    if row[0]:
        print(f"  {row[0]:50s}: {row[1]:6d} fichiers, {format_size(row[2])}")

# 2. Doublons : où sont les copies ?
print("\n" + "=" * 70)
print("2. ANALYSE DES DOUBLONS PAR DOSSIER TOP-LEVEL")
print("=" * 70)
cur.execute("SELECT hash_md5, size, file_count FROM duplicate_groups ORDER BY wasted_space DESC LIMIT 200")
groups = cur.fetchall()

from collections import Counter
folder_dup_size = Counter()
folder_dup_count = Counter()

for hash_md5, size, file_count in groups:
    cur.execute("SELECT path FROM files WHERE hash_md5 = ? AND size = ?", (hash_md5, size))
    paths = [r[0] for r in cur.fetchall()]
    if len(paths) < 2:
        continue
    
    # Score each path
    def score(p):
        s = len(p)
        lp = p.lower()
        if 'copie' in lp or 'copy' in lp or 'backup' in lp: s += 1000
        if 'old' in lp or 'ancien' in lp: s += 500
        if '60-projets recap' in lp: s += 200  # recap = copies
        return s
    
    paths.sort(key=score)
    keep = paths[0]
    for p in paths[1:]:
        # Get top folder of the duplicate
        rel = p[len(BASE)+1:]
        top = rel.split("\\")[0] if "\\" in rel else rel
        folder_dup_size[top] += size
        folder_dup_count[top] += 1

print("  Dossier contenant le plus de doublons (copies supprimables) :")
for folder, sz in folder_dup_size.most_common(20):
    print(f"    {folder:50s}: {folder_dup_count[folder]:5d} fichiers, {format_size(sz)}")

# 3. Junk files
print("\n" + "=" * 70)
print("3. FICHIERS JUNK")
print("=" * 70)

# Thumbs.db
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE LOWER(filename) = 'thumbs.db'")
cnt, sz = cur.fetchone()
print(f"  Thumbs.db       : {cnt:5d} fichiers, {format_size(sz)}")

# .bak
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.bak'")
cnt, sz = cur.fetchone()
print(f"  .bak             : {cnt:5d} fichiers, {format_size(sz)}")

# .db (Thumbs databases?)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.db' AND LOWER(filename) != 'thumbs.db'")
cnt, sz = cur.fetchone()
print(f"  .db (hors thumbs): {cnt:5d} fichiers, {format_size(sz)}")
# Sample .db files
cur.execute("SELECT filename, path FROM files WHERE extension = '.db' AND LOWER(filename) != 'thumbs.db' LIMIT 5")
for row in cur.fetchall():
    print(f"      ex: {row[0]}")

# .DS_Store
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE filename = '.DS_Store'")
cnt, sz = cur.fetchone()
print(f"  .DS_Store        : {cnt:5d} fichiers, {format_size(sz)}")

# Mac system files
cur.execute("""SELECT COUNT(*), COALESCE(SUM(size),0) FROM files 
    WHERE path LIKE '%.Spotlight-V100%' OR path LIKE '%.Trashes%' 
    OR path LIKE '%.fseventsd%' OR path LIKE '%.TemporaryItems%'""")
cnt, sz = cur.fetchone()
print(f"  Mac système      : {cnt:5d} fichiers, {format_size(sz)}")

# .tmp files
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.tmp'")
cnt, sz = cur.fetchone()
print(f"  .tmp             : {cnt:5d} fichiers, {format_size(sz)}")

# ~$ files (office temp)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE filename LIKE '~$%'")
cnt, sz = cur.fetchone()
print(f"  ~$ (Office temp) : {cnt:5d} fichiers, {format_size(sz)}")

# .log files
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.log'")
cnt, sz = cur.fetchone()
print(f"  .log             : {cnt:5d} fichiers, {format_size(sz)}")

# 4. Dossiers suspects
print("\n" + "=" * 70)
print("4. DOSSIERS SUSPECTS")
print("=" * 70)
suspects = ['\\Nouveau dossier', '\\Copie de ', '\\Copy of ', '\\tmp\\', '\\old\\', '\\backup\\', '\\RECAP\\']
for pat in suspects:
    cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?", (f'%{pat}%',))
    cnt, sz = cur.fetchone()
    if cnt > 0:
        print(f"  '{pat.strip(chr(92))}': {cnt:5d} fichiers, {format_size(sz)}")

# 5. DLL files (software residue?)
print("\n" + "=" * 70)
print("5. FICHIERS DLL (résidus logiciels)")
print("=" * 70)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.dll'")
cnt, sz = cur.fetchone()
print(f"  .dll: {cnt} fichiers, {format_size(sz)}")
cur.execute(f"""SELECT 
    SUBSTR(path, {len(BASE)+2}, INSTR(SUBSTR(path, {len(BASE)+2}), '\\')-1) as top_folder,
    COUNT(*), SUM(size)
FROM files WHERE extension = '.dll'
GROUP BY top_folder ORDER BY SUM(size) DESC""")
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:40s}: {row[1]:5d} fichiers, {format_size(row[2])}")

conn.close()
