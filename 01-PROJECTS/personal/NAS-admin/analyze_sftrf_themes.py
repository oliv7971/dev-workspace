"""
Analyse croisée des données SFTRF : 
Où sont les scans/données par thème (galerie secu, tunnel routier, BP, abris, rameaux, ST) 
dans chaque dossier top-level (01-TUNNEL ROUTIER, 02-GALERIE SECU, 16-RAMEAUX, 51-TMS, 52-CYCLONE)
"""
import sqlite3
import re

DB = "./reports/inventory_sftrf.db"
BASE = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\01-SFTRF"

conn = sqlite3.connect(DB)
cur = conn.cursor()

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

# Thèmes à détecter dans les chemins
themes = {
    'GALERIE SECU / GSF': ['galerie secu', 'galerie_secu', 'gsf', 'gal secu', 'galsecu', 'galerie de sec'],
    'TUNNEL ROUTIER': ['tunnel routier', 'routier', 'tube routier'],
    'BYPASS / BP': ['bypass', '\\bp2', '\\bp3', '\\bp4', 'bp2\\', 'bp3\\', 'bp4\\', '_bp2', '_bp3', '_bp4', '-bp2', '-bp3', '-bp4', 'rameaux et bp'],
    'ABRIS': ['abri', 'abris'],
    'RAMEAUX': ['rameau', 'rameaux', 'ram1', 'ram2', 'ram3', 'ram4', 'ram5', 'ram6', 'ram7', 'ram8', 'ram9'],
    'STATIONS TECHNIQUES / ST': ['station technique', 'st-', 'st_', '\\st\\', '-st\\', 'stations tech'],
    'GAF / GAV': ['\\gaf', 'gaf\\', '-gaf', '_gaf', 'galerie air', 'gav\\', '\\gav', '-gav'],
    'SOCAMO': ['socamo'],
    'TUNNELIER / TBM': ['tunnelier', 'tbm', 'chambre de mont', 'chambre mont', 'lancmt'],
    'GEM / PUITS': ['gem', 'puits'],
    'ENTREE TUNNEL': ['entree', 'entrée'],
}

top_folders = [
    '01-TUNNEL ROUTIER FREJUS',
    '02-GALERIE SECU FREJUS', 
    '16-RAMEAUX ET BP',
    '51-TMS',
    '52-CYCLONE',
    '11-SOCAMO',
    '40-Photos',
    '_ACLASSER',
]

print("=" * 120)
print("CARTOGRAPHIE : OÙ SONT LES DONNÉES PAR THÈME ?")
print("(fichiers restants après suppression des doublons)")
print("=" * 120)

# For each theme, search across all top folders
for theme, keywords in themes.items():
    print(f"\n{'─' * 120}")
    print(f"🏷️  {theme}")
    print(f"{'─' * 120}")
    
    # Build SQL LIKE conditions
    conditions = " OR ".join([f"LOWER(path) LIKE '%{kw}%'" for kw in keywords])
    
    total_files = 0
    total_size = 0
    
    for top in top_folders:
        cur.execute(f"""SELECT COUNT(*), COALESCE(SUM(size),0) 
            FROM files 
            WHERE path LIKE ? AND ({conditions})""",
            (f'%\\{top}\\%',))
        cnt, sz = cur.fetchone()
        if cnt > 0:
            total_files += cnt
            total_size += sz
            print(f"  {top:45s}: {cnt:6d} fichiers, {format_size(sz):>10s}")
            
            # Show level-2 breakdown
            prefix = BASE + "\\" + top + "\\"
            cur.execute(f"""SELECT 
                CASE 
                    WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
                    THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
                    ELSE '(racine)'
                END as subfolder,
                COUNT(*), SUM(size)
            FROM files 
            WHERE path LIKE ? AND ({conditions})
            GROUP BY subfolder ORDER BY SUM(size) DESC
            LIMIT 5""", (prefix + '%',))
            for sub, scnt, ssz in cur.fetchall():
                if sub:
                    print(f"      └─ {sub:41s}: {scnt:6d} fich.  {format_size(ssz):>10s}")
    
    if total_files > 0:
        print(f"  {'TOTAL':45s}: {total_files:6d} fichiers, {format_size(total_size):>10s}")

# Analyse spécifique : données TMS vs dossiers projets
print("\n\n" + "=" * 120)
print("ANALYSE TMS : Contenu de 51-TMS détaillé par type de données")
print("=" * 120)

prefix = BASE + "\\51-TMS\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as subfolder,
    COUNT(*), SUM(size),
    GROUP_CONCAT(DISTINCT extension) as exts
FROM files WHERE path LIKE ?
GROUP BY subfolder ORDER BY SUM(size) DESC""", (prefix + '%',))
for sub, cnt, sz, exts in cur.fetchall():
    if sub:
        # Identify what type of data this is
        top_exts = ', '.join(sorted(set(exts.split(',') if exts else []))[:8])
        print(f"  {sub:50s}: {cnt:5d} fich. {format_size(sz):>10s}  [{top_exts}]")

# Analyse Cyclone
print("\n" + "=" * 120)
print("ANALYSE 52-CYCLONE : Détail")
print("=" * 120)

prefix = BASE + "\\52-CYCLONE\\"
cur.execute(f"""SELECT 
    CASE 
        WHEN INSTR(SUBSTR(path, {len(prefix)+1}), '\\') > 0 
        THEN SUBSTR(path, {len(prefix)+1}, INSTR(SUBSTR(path, {len(prefix)+1}), '\\')-1)
        ELSE filename
    END as subfolder,
    COUNT(*), SUM(size),
    GROUP_CONCAT(DISTINCT extension) as exts
FROM files WHERE path LIKE ?
GROUP BY subfolder ORDER BY SUM(size) DESC""", (prefix + '%',))
for sub, cnt, sz, exts in cur.fetchall():
    if sub:
        top_exts = ', '.join(sorted(set(exts.split(',') if exts else []))[:8])
        print(f"  {sub:50s}: {cnt:5d} fich. {format_size(sz):>10s}  [{top_exts}]")

# Extensions par dossier top (pour comprendre le type de données)
print("\n" + "=" * 120)
print("TYPE DE DONNÉES PAR DOSSIER (extensions scan 3D)")
print("=" * 120)

scan_exts = ['.zfs', '.pts', '.ptsx', '.pcs', '.ptx', '.rcs', '.rcc', '.e57', '.zfi', '.imp', '.rsh']
for top in top_folders:
    cur.execute(f"""SELECT extension, COUNT(*), SUM(size) 
        FROM files WHERE path LIKE ? AND extension IN ({','.join(['?']*len(scan_exts))})
        GROUP BY extension ORDER BY SUM(size) DESC""",
        (f'%\\{top}\\%', *scan_exts))
    rows = cur.fetchall()
    if rows:
        total = sum(r[2] for r in rows)
        print(f"\n  {top}: {format_size(total)} de scans 3D")
        for ext, cnt, sz in rows:
            print(f"      {ext:8s}: {cnt:5d} fich. {format_size(sz):>10s}")

# Fichiers à la racine de 01-SFTRF
print("\n" + "=" * 120)
print("FICHIERS À LA RACINE DE 01-SFTRF")
print("=" * 120)
cur.execute(f"""SELECT filename, size FROM files 
    WHERE path LIKE '{BASE}\\%' 
    AND INSTR(SUBSTR(path, {len(BASE)+2}), '\\') = 0""")
for row in cur.fetchall():
    print(f"  {row[0]:60s} {format_size(row[1])}")

conn.close()
