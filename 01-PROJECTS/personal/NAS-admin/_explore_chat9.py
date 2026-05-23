"""État actuel des dossiers L1 (depuis la DB, rapide)."""
import sqlite3
import os

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'
NAS = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'

# Dossiers supprimés en P1 et P2a
DELETED = {
    'TUNNEL DU CHAT - 2017', 'rep pytha scooter ordi chat',
    '10-Tunnel du Chat', '01-donnees avant projet 2017- PAUL & LUDO & TMS',
    '21-travaux-bureau-proj', '70-sauvegardes cartes TPS1200',
    'Migration TMS Amberg chat', 'LUDO',
    'Etude BG', 'PAUL', 'Pour Eiffage', '03-POLYGONALE', 'voute parapluie',
}

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1) as folder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go
FROM files WHERE path LIKE ? || '%'
GROUP BY folder ORDER BY SUM(size) DESC""", (BASE, BASE, BASE))

print(f"  {'Dossier':<55} {'Fich':>6} {'Taille':>8}")
print('=' * 75)
total_f = total_s = 0
remaining = []
for folder, cnt, go in c.fetchall():
    if folder in DELETED or folder == '\\':
        continue
    # Vérifier si existe encore
    if not os.path.exists(os.path.join(NAS, folder)):
        continue
    if go >= 1:
        sz = f"{go:.1f} Go"
    elif go >= 0.001:
        sz = f"{go*1024:.0f} Mo"
    else:
        sz = f"{cnt} fich"
    print(f"  {folder:<55} {cnt:>6} {sz:>8}")
    total_f += cnt
    total_s += go
    remaining.append(folder)

print(f"\nRestant: {len(remaining)} dossiers, {total_f} fichiers, {total_s:.1f} Go")

# Vérifier aussi s'il y a des fichiers orphelins en racine
root_files = [f for f in os.listdir(NAS) if os.path.isfile(os.path.join(NAS, f))]
if root_files:
    print(f"\nFichiers en racine: {len(root_files)}")
    for f in root_files:
        print(f"  {f}")

conn.close()
