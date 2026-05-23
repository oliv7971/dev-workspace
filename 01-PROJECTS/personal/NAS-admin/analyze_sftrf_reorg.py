"""Analyse détaillée de la structure de 01-SFTRF pour réorganisation."""
import sqlite3

DB = "./reports/inventory_sftrf.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\01-SFTRF"

conn = sqlite3.connect(DB)
cur = conn.cursor()

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

# Exclure les fichiers déjà supprimés (doublons + junk)
# On vérifie quels fichiers restent réellement
# Utilisons les fichiers non-supprimés : ceux qui ne sont pas dans duplicate_groups en tant que copies,
# ni Thumbs.db, .bak, ~$, .log
# Plus simple : analysons la base telle quelle et identifions les problèmes de structure

print("=" * 80)
print("STRUCTURE COMPLÈTE DE 01-SFTRF (2 premiers niveaux)")
print("=" * 80)

# Get top-level folders
cur.execute(f"""SELECT 
    SUBSTR(path, {len(BASE)+2}, INSTR(SUBSTR(path, {len(BASE)+2}), '\\')-1) as top_folder,
    COUNT(*), SUM(size)
FROM files 
WHERE INSTR(SUBSTR(path, {len(BASE)+2}), '\\') > 0
GROUP BY top_folder ORDER BY top_folder""")
top_folders = cur.fetchall()

for top, cnt, sz in top_folders:
    if not top:
        continue
    print(f"\n📁 {top}  ({cnt} fichiers, {format_size(sz)})")
    
    # Get level-2 subfolders
    prefix = BASE + "\\" + top + "\\"
    cur.execute(f"""SELECT 
        CASE 
            WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
            THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
            ELSE '(fichiers racine)'
        END as subfolder,
        COUNT(*), SUM(size)
    FROM files 
    WHERE path LIKE ? AND LENGTH(path) > {len(prefix)}
    GROUP BY subfolder ORDER BY SUM(size) DESC
    LIMIT 15""", (prefix + '%',))
    subs = cur.fetchall()
    for sub, scnt, ssz in subs:
        if sub:
            print(f"    ├── {sub:55s} {scnt:5d} fich.  {format_size(ssz):>10s}")

# Analyse spécifique des problèmes
print("\n" + "=" * 80)
print("ANALYSES DE RÉORGANISATION")
print("=" * 80)

# 1. _ACLASSER
print("\n--- _ACLASSER (à trier) ---")
prefix = BASE + "\\_ACLASSER\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as item,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE ?
GROUP BY item ORDER BY SUM(size) DESC""", (prefix + '%',))
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:55s} {row[1]:5d} fich.  {format_size(row[2]):>10s}")

# 2. 50-DIVERS
print("\n--- 50-DIVERS (contenu ?) ---")
prefix = BASE + "\\50-DIVERS\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as item,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE ?
GROUP BY item ORDER BY SUM(size) DESC""", (prefix + '%',))
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:55s} {row[1]:5d} fich.  {format_size(row[2]):>10s}")

# 3. 52-CYCLONE (67.9 Go !)
print("\n--- 52-CYCLONE (contenu ?) ---")
prefix = BASE + "\\52-CYCLONE\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as item,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE ?
GROUP BY item ORDER BY SUM(size) DESC""", (prefix + '%',))
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:55s} {row[1]:5d} fich.  {format_size(row[2]):>10s}")

# 4. 51-TMS (136 Go)
print("\n--- 51-TMS (contenu ?) ---")
prefix = BASE + "\\51-TMS\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as item,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE ?
GROUP BY item ORDER BY SUM(size) DESC""", (prefix + '%',))
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:55s} {row[1]:5d} fich.  {format_size(row[2]):>10s}")

# 5. 40-Photos
print("\n--- 40-Photos (contenu ?) ---")
prefix = BASE + "\\40-Photos\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as item,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE ?
GROUP BY item ORDER BY SUM(size) DESC
LIMIT 20""", (prefix + '%',))
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:55s} {row[1]:5d} fich.  {format_size(row[2]):>10s}")

# 6. Chevauchements : fichiers FREJUS répartis dans combien de dossiers ?
print("\n" + "=" * 80)
print("CHEVAUCHEMENTS : Données FREJUS réparties dans plusieurs dossiers")
print("=" * 80)
frejus_folders = [
    '01-TUNNEL ROUTIER FREJUS',
    '02-GALERIE SECU FREJUS',
    '16-RAMEAUX ET BP',
    '51-TMS',
    '52-CYCLONE',
    '15-GAF GAV',
]
for f in frejus_folders:
    cur.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files WHERE path LIKE ?",
                (f'%\\{f}\\%',))
    cnt, sz = cur.fetchone()
    print(f"  {f:40s}: {cnt:6d} fichiers, {format_size(sz)}")

# 7. Dossiers "Nouveau dossier"
print("\n--- Dossiers 'Nouveau dossier' ---")
cur.execute("""SELECT path FROM files WHERE path LIKE '%\\Nouveau dossier%' LIMIT 20""")
for row in cur.fetchall():
    print(f"    {row[0].replace(BASE + chr(92), '')[:90]}")

# 8. DLL dans 16-RAMEAUX ET BP
print("\n--- DLL dans 16-RAMEAUX ET BP ---")
prefix = BASE + "\\16-RAMEAUX ET BP\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as item,
    COUNT(*), SUM(size)
FROM files WHERE path LIKE ? AND extension = '.dll'
GROUP BY item ORDER BY SUM(size) DESC""", (prefix + '%',))
for row in cur.fetchall():
    if row[0]:
        print(f"    {row[0]:55s} {row[1]:5d} fich.  {format_size(row[2]):>10s}")

conn.close()
