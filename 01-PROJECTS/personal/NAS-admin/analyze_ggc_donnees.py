"""Analyse de la structure de 33-GGC-DONNEES pour identifier le junk."""
import sqlite3
from pathlib import PureWindowsPath

DB = "./reports/inventory_ggc_donnees.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\33-GGC-DONNEES"

conn = sqlite3.connect(DB)
cur = conn.cursor()

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

# 1. Fichiers système Mac (.Spotlight-V100, .Trashes, .fseventsd, .DS_Store)
print("=" * 70)
print("1. FICHIERS SYSTÈME MAC")
print("=" * 70)
mac_patterns = ['.Spotlight-V100', '.Trashes', '.fseventsd', '.DS_Store', '.TemporaryItems']
for pat in mac_patterns:
    cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?", (f'%{pat}%',))
    cnt, sz = cur.fetchone()
    if cnt > 0:
        print(f"  {pat}: {cnt} fichiers, {format_size(sz)}")

# Total Mac
cur.execute("""SELECT COUNT(*), COALESCE(SUM(size),0) FROM files 
    WHERE path LIKE '%.Spotlight-V100%' OR path LIKE '%.Trashes%' 
    OR path LIKE '%.fseventsd%' OR filename = '.DS_Store' OR path LIKE '%.TemporaryItems%'""")
cnt, sz = cur.fetchone()
print(f"  TOTAL MAC: {cnt} fichiers, {format_size(sz)}")

# 2. Cyberducksegment (incomplete uploads)
print("\n" + "=" * 70)
print("2. FICHIERS CYBERDUCKSEGMENT (uploads incomplets)")
print("=" * 70)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.cyberducksegment'")
cnt, sz = cur.fetchone()
print(f"  .cyberducksegment: {cnt} fichiers, {format_size(sz)}")
cur.execute("SELECT path, size FROM files WHERE extension = '.cyberducksegment' ORDER BY size DESC LIMIT 10")
for row in cur.fetchall():
    p = row[0].replace(BASE + "\\", "")
    print(f"    {format_size(row[1]):>12s}  {p[:90]}")

# 3. .bak files
print("\n" + "=" * 70)
print("3. FICHIERS .BAK")
print("=" * 70)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE extension = '.bak'")
cnt, sz = cur.fetchone()
print(f"  .bak: {cnt} fichiers, {format_size(sz)}")
# Where are they?
cur.execute("""SELECT 
    CASE 
        WHEN path LIKE '%\\04-DONNEES\\%' THEN '04-DONNEES'
        WHEN path LIKE '%\\01-SCANS BRUT\\%' THEN '01-SCANS BRUT'
        WHEN path LIKE '%\\23-GGC_Adr%' THEN '23-GGC_Adr'
        WHEN path LIKE '%--- a classer ---%' THEN '--- a classer ---'
        ELSE 'autre'
    END as folder,
    COUNT(*), SUM(size)
FROM files WHERE extension = '.bak' GROUP BY folder ORDER BY SUM(size) DESC""")
for row in cur.fetchall():
    print(f"    {row[0]:25s}: {row[1]:5d} fichiers, {format_size(row[2])}")

# 4. Thumbs.db
print("\n" + "=" * 70)
print("4. THUMBS.DB")
print("=" * 70)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE LOWER(filename) = 'thumbs.db'")
cnt, sz = cur.fetchone()
print(f"  Thumbs.db: {cnt} fichiers, {format_size(sz)}")

# 5. --- a classer --- contents
print("\n" + "=" * 70)
print("5. CONTENU DE '--- a classer ---'")
print("=" * 70)
cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE '%--- a classer ---%'")
cnt, sz = cur.fetchone()
print(f"  Total: {cnt} fichiers, {format_size(sz)}")
# Sub-folders
cur.execute("""SELECT 
    REPLACE(SUBSTR(path, INSTR(path, '--- a classer ---') + 19), 
        SUBSTR(path, INSTR(path, '--- a classer ---') + 19, 
            INSTR(SUBSTR(path, INSTR(path, '--- a classer ---') + 19)||'\\', '\\')
        ), '') as subfolder_raw,
    SUBSTR(path, INSTR(path, '--- a classer ---') + 19, 
        INSTR(SUBSTR(path, INSTR(path, '--- a classer ---') + 19)||'\\', '\\')-1
    ) as subfolder,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE '%--- a classer ---%'
GROUP BY subfolder ORDER BY SUM(size) DESC""")
for row in cur.fetchall():
    if row[1]:
        print(f"    {row[1]:35s}: {row[2]:5d} fichiers, {format_size(row[3])}")

# 6. Dossiers suspects (tmp, old, backup, Nouveau dossier)
print("\n" + "=" * 70)
print("6. DOSSIERS SUSPECTS")
print("=" * 70)
suspects = ['\\tmp\\', '\\old\\', '\\backup\\', '\\Nouveau dossier', '\\Copie de ', '\\Copy of ']
for pat in suspects:
    cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?", (f'%{pat}%',))
    cnt, sz = cur.fetchone()
    if cnt > 0:
        print(f"  '{pat.strip(chr(92))}': {cnt} fichiers, {format_size(sz)}")

# 7. Extensions lourdes suspectes
print("\n" + "=" * 70)
print("7. ARCHIVES (.zip, .7z, .rar)")
print("=" * 70)
cur.execute("""SELECT extension, COUNT(*), SUM(size) FROM files 
    WHERE extension IN ('.zip', '.7z', '.rar', '.tar', '.gz')
    GROUP BY extension ORDER BY SUM(size) DESC""")
for row in cur.fetchall():
    print(f"  {row[0]:6s}: {row[1]:5d} fichiers, {format_size(row[2])}")

# 8. .htm files (6.1 Go - suspicious for data folder)
print("\n" + "=" * 70)
print("8. FICHIERS .HTM (6.1 Go)")
print("=" * 70)
cur.execute("SELECT path, size FROM files WHERE extension = '.htm' ORDER BY size DESC LIMIT 10")
for row in cur.fetchall():
    p = row[0].replace(BASE + "\\", "")
    print(f"  {format_size(row[1]):>12s}  {p[:90]}")

# 9. Top-level folder structure
print("\n" + "=" * 70)
print("9. STRUCTURE TOP-LEVEL")
print("=" * 70)
cur.execute(f"""SELECT 
    SUBSTR(path, {len(BASE)+2}, INSTR(SUBSTR(path, {len(BASE)+2}), '\\')-1) as top_folder,
    COUNT(*), SUM(size)
FROM files 
GROUP BY top_folder ORDER BY SUM(size) DESC""")
for row in cur.fetchall():
    if row[0]:
        print(f"  {row[0]:40s}: {row[1]:6d} fichiers, {format_size(row[2])}")

conn.close()
