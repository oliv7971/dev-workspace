"""Timeline lisible des dossiers 33-TUNNEL DU CHAT."""
import sqlite3
from datetime import datetime

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = '\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\33-TUNNEL DU CHAT\\'
DELETED = {
    'TUNNEL DU CHAT - 2017', 'rep pytha scooter ordi chat',
    '10-Tunnel du Chat', '01-donnees avant projet 2017- PAUL & LUDO & TMS',
    '21-travaux-bureau-proj', '70-sauvegardes cartes TPS1200',
    'Migration TMS Amberg chat', 'LUDO', '\\'
}

conn = sqlite3.connect(DB)
c = conn.cursor()

def ts_to_date(ts):
    if not ts: return '?'
    try:
        t = float(ts)
        if t < 946684800:  # avant 2000
            return '<2000'
        return datetime.fromtimestamp(t).strftime('%Y-%m-%d')
    except:
        return '?'

c.execute("""SELECT 
    SUBSTR(path, LENGTH(?)+1, INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1) as folder,
    COUNT(*) as cnt,
    ROUND(SUM(size)/1073741824.0, 2) as go,
    MIN(modified_time), MAX(modified_time)
FROM files WHERE path LIKE ? || '%'
GROUP BY folder ORDER BY MIN(modified_time)""", (BASE, BASE, BASE))

print("CHRONOLOGIE DES DOSSIERS - 33-TUNNEL DU CHAT")
print("=" * 100)
print(f"  {'Dossier':<50} {'Fich':>5} {'Go':>6}  {'Modif de':>10} → {'à':>10}")
print("-" * 100)

phase1 = []
phase2 = []
snapshots = []

for r in c.fetchall():
    folder = r[0]
    if folder in DELETED:
        continue
    d_min = ts_to_date(r[3])
    d_max = ts_to_date(r[4])
    print(f"  {folder:<50} {r[1]:>5} {r[2]:>6}  {d_min:>10} → {d_max:>10}")

# Détail des gros dossiers
for dname in ['20150904-CHAT', '99-olivier', 'TUNNEL DU CHAT - 2017 - 19mai2017', 'tunnel-chat', '03-tunnel chat', 'TMS', '2017']:
    prefix = BASE + dname + '\\'
    c.execute("""SELECT 
        SUBSTR(path, LENGTH(?)+1, CASE WHEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92)) > 0 
            THEN INSTR(SUBSTR(path, LENGTH(?)+1), CHAR(92))-1 
            ELSE LENGTH(SUBSTR(path, LENGTH(?)+1)) END) as subfolder,
        COUNT(*) as cnt,
        ROUND(SUM(size)/1073741824.0, 2) as go,
        MIN(modified_time), MAX(modified_time)
    FROM files WHERE path LIKE ? || '%'
    GROUP BY subfolder ORDER BY cnt DESC""", 
        (prefix, prefix, prefix, prefix, prefix))
    rows = c.fetchall()
    print(f"\n  ┌── {dname}/ ──")
    for r in rows:
        d_min = ts_to_date(r[3])
        d_max = ts_to_date(r[4])
        print(f"  │ {r[0]:<48} {r[1]:>5} {r[2]:>6} Go  {d_min} → {d_max}")

# Identification des phases
print("\n" + "=" * 100)
print("SYNTHÈSE PAR PHASE")
print("=" * 100)
print("""
PHASE 1 — Galerie de sécurité (2014-2015):
  Contributeurs: Olivier, Ludo, (Benoit?)
  Dossiers principaux:
  • 20150904-CHAT (6721 fich, 3.94 Go) — backup du 4 sept 2015, contient:
    - 99-olivier/ (5171 fich, 3.87 Go) — copie de travail d'Olivier
    - TMS/ (1034 fich) — données TMS de cette période
    - 10-Tunnel du Chat/ (516 fich) — données projet
  • 99-olivier L1 (3975 fich, 0.23 Go) — autre copie de travail d'Olivier
    (1314 fichiers uniques vs le 99-olivier dans 20150904-CHAT)
  • documents-tunnel-du-chat (43 fich)
  • 14 tunnel chat (34 fich)
  • leve-tetes-dec2014 (32 fich)
  • 01-reperage 23nov2014 (20 fich)
  • scan chat rescindement (15 fich)

PHASE 2 — Restauration tunnel existant (2016-2017):
  Contributeurs: Paul, Ludo, Olivier, (Benoit?)
  Dossiers principaux:
  • TMS (9791 fich, 106 Go) — données TMS complètes (actif jusqu'en 2026!)
  • 03-tunnel chat (157 fich, 32.15 Go) — scans/RSH lourds
  • tunnel-chat (1333 fich, 1.69 Go) — livraisons et scans
  • 02-ACTIVITES TOPO (957 fich)
  • PAUL (16 fich)

SNAPSHOTS / SAUVEGARDES:
  • TUNNEL DU CHAT - 2017 - 19mai2017 (3811 fich, 0.46 Go) — snapshot complet du 19 mai 2017
  • 2017/ (1477 fich, 0.08 Go) — snapshot partiel de 2017
  • carte tps 170615 (283 fich) — sauvegarde cartes du 15 juin 2017

PETITS DOSSIERS ORPHELINS:
  • Etude BG (10 fich) — 100% dans 99-olivier → À SUPPRIMER
  • PAUL (16 fich) — 100% dans TUNNEL DU CHAT-2017-19mai → À SUPPRIMER
  • Pour Eiffage (17 fich) — 100% dans 20150904-CHAT → À SUPPRIMER
  • 03-POLYGONALE (4 fich) — 100% dans TUNNEL DU CHAT-2017-19mai → À SUPPRIMER
  • voute parapluie (8 fich) — 100% dans 20150904-CHAT → À SUPPRIMER
  • Plans EIFFAGE (5 fich) — à vérifier
  • polygo 20150926 (1 fich)
  • Polygo chat lucas (2 fich)
  • temp (1 fich)  
  • CHAT (3 fich, 0.09 Go) — fichier .imp Amberg
  • 11-TUNNEL DU CHAT (3 fich) — config Amberg
  • 71-envoi FC scans mai2017 (4 fich) — DXF envoi FC
  • 98-LREF rameaux (1 fich)
  • 99-LREF carneaux (3 fich)
  • xxxxxxxx a classer xxxxxxxx (65 fich)
  • TUNNEL CHAT (49 fich)
  • TUNNEL DU CHAT (35 fich)
""")

conn.close()
