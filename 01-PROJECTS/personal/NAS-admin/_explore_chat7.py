"""Analyse temporelle et par contributeur des dossiers 33-TUNNEL DU CHAT.
On regarde les plages de dates par dossier L1 pour identifier les phases."""
import sqlite3
from datetime import datetime

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'

conn = sqlite3.connect(DB)
c = conn.cursor()

# Dossiers supprimés en P1
DELETED = {
    'TUNNEL DU CHAT - 2017', 'rep pytha scooter ordi chat',
    '10-Tunnel du Chat', '01-donnees avant projet 2017- PAUL & LUDO & TMS',
    '21-travaux-bureau-proj', '70-sauvegardes cartes TPS1200',
    'Migration TMS Amberg chat', 'LUDO',
}

c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1) as folder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time) as date_min,
    MAX(modified_time) as date_max,
    MIN(created_time) as crea_min,
    MAX(created_time) as crea_max
FROM files WHERE path LIKE ? || '%'
GROUP BY folder ORDER BY date_min""", (BASE, BASE, BASE))

print(f"{'Dossier':<50} {'Fich':>5} {'Go':>6}  {'Modif min':>19}  {'Modif max':>19}  {'Créa min':>19}  {'Créa max':>19}")
print('=' * 170)
for r in c.fetchall():
    folder = r[0]
    if folder in DELETED or folder == '\\':
        continue
    # Format dates
    def fmt(d):
        if not d: return '?'
        try:
            return datetime.fromisoformat(d).strftime('%Y-%m-%d')
        except:
            return str(d)[:10]
    print(f"  {folder:<48} {r[1]:>5} {r[2]:>6}  {fmt(r[3]):>19}  {fmt(r[4]):>19}  {fmt(r[5]):>19}  {fmt(r[6]):>19}")

# Détail: sous-structure de 20150904-CHAT (le gros dump)
print("\n=== Structure de 20150904-CHAT (L2) avec dates ===")
prefix_20150904 = BASE + '20150904-CHAT\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time),
    MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY cnt DESC""", 
    (prefix_20150904, prefix_20150904, prefix_20150904, prefix_20150904, prefix_20150904))

for r in c.fetchall():
    def fmt(d):
        if not d: return '?'
        try: return datetime.fromisoformat(d).strftime('%Y-%m-%d')
        except: return str(d)[:10]
    print(f"  {r[0]:<50} {r[1]:>5} {r[2]:>6} Go  {fmt(r[3])} → {fmt(r[4])}")

# Dossier 99-olivier L1 sous-structure
print("\n=== Structure de 99-olivier L1 (L2) avec dates ===")
prefix_ol = BASE + '99-olivier\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time),
    MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY cnt DESC""", 
    (prefix_ol, prefix_ol, prefix_ol, prefix_ol, prefix_ol))

for r in c.fetchall():
    def fmt(d):
        if not d: return '?'
        try: return datetime.fromisoformat(d).strftime('%Y-%m-%d')
        except: return str(d)[:10]
    print(f"  {r[0]:<50} {r[1]:>5} {r[2]:>6} Go  {fmt(r[3])} → {fmt(r[4])}")

# TUNNEL DU CHAT - 2017 - 19mai2017 sous-structure
print("\n=== Structure de TUNNEL DU CHAT - 2017 - 19mai2017 (L2) ===")
prefix_19mai = BASE + 'TUNNEL DU CHAT - 2017 - 19mai2017\\'
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
        THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
        ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time),
    MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY subfolder ORDER BY cnt DESC""", 
    (prefix_19mai, prefix_19mai, prefix_19mai, prefix_19mai, prefix_19mai))

for r in c.fetchall():
    def fmt(d):
        if not d: return '?'
        try: return datetime.fromisoformat(d).strftime('%Y-%m-%d')
        except: return str(d)[:10]
    print(f"  {r[0]:<50} {r[1]:>5} {r[2]:>6} Go  {fmt(r[3])} → {fmt(r[4])}")

conn.close()
