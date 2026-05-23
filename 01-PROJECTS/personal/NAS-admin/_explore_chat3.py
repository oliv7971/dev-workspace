"""
Vérification rigoureuse des inclusions entre dossiers.
Pour chaque relation A ⊂ B supposée, on vérifie :
  - Tous les fichiers hashés de A ont un hash identique dans B
  - Les fichiers sans hash de A ont un fichier de même nom+taille dans B
  - On compte les fichiers de A qui n'ont PAS de correspondance dans B
"""
import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'

conn = sqlite3.connect(DB)

# Paires à vérifier : (contenu_dans, contient)  — "A est contenu dans B"
pairs = [
    ('TUNNEL DU CHAT - 2017',                       '03-tunnel chat'),
    ('rep pytha scooter ordi chat',                  '99-olivier'),
    ('21-travaux-bureau-proj',                       '99-olivier'),
    ('10-Tunnel du Chat',                            '20150904-CHAT'),
    ('Migration TMS Amberg chat',                    'LUDO'),
    ('LUDO',                                         '01-donnees avant projet 2017- PAUL & LUDO & TMS'),
    ('01-donnees avant projet 2017- PAUL & LUDO & TMS', 'TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('70-sauvegardes cartes TPS1200',                'carte tps 170615'),
]

def get_files(dir_name):
    """Retourne tous les fichiers d'un dossier L1."""
    c = conn.cursor()
    prefix = BASE + '\\' + dir_name + '\\'
    c.execute("SELECT path, filename, size, hash_md5, modified_time FROM files WHERE path LIKE ?",
              (prefix + '%',))
    return c.fetchall()

def get_hashes(dir_name):
    """Retourne {hash: [(filename, size, mtime)]} pour un dossier."""
    files = get_files(dir_name)
    result = defaultdict(list)
    for p, fn, sz, h, mt in files:
        if h:
            result[h].append((fn, sz, mt))
    return result

def get_name_size(dir_name):
    """Retourne {(filename, size): [mtime]} pour les fichiers sans hash."""
    files = get_files(dir_name)
    result = defaultdict(list)
    for p, fn, sz, h, mt in files:
        if not h:
            result[(fn, sz)].append(mt)
    return result

print(f"{'A (contenu dans B)':<55} {'B (contient A)':<55} {'Total A':>8} {'OK':>6} {'Miss':>6} {'Verdict'}")
print('=' * 140)

for dir_a, dir_b in pairs:
    files_a = get_files(dir_a)
    hashes_b = get_hashes(dir_b)
    ns_b = get_name_size(dir_b)
    # Also get all hashes of B as a set
    all_h_b = set(hashes_b.keys())
    # And all (name,size) of B
    all_ns_b_hashed = set()
    for h, items in hashes_b.items():
        for fn, sz, mt in items:
            all_ns_b_hashed.add((fn, sz))

    total_a = len(files_a)
    matched = 0
    missing = []

    for p, fn, sz, h, mt in files_a:
        if h and h in all_h_b:
            matched += 1
        elif not h and (fn, sz) in ns_b:
            matched += 1
        elif not h and (fn, sz) in all_ns_b_hashed:
            matched += 1
        else:
            missing.append((fn, sz, h, mt))

    n_miss = len(missing)
    verdict = 'OK 100%' if n_miss == 0 else f'PARTIEL ({n_miss} manquants)'

    print(f"  {dir_a:<53} {dir_b:<53} {total_a:>8} {matched:>6} {n_miss:>6} {verdict}")

    if missing and len(missing) <= 10:
        for fn, sz, h, mt in missing:
            print(f"    MANQUANT: {fn}  ({sz//1024} Ko)  hash={h or 'N/A'}")
    elif missing:
        print(f"    (premiers manquants:)")
        for fn, sz, h, mt in missing[:5]:
            print(f"    MANQUANT: {fn}  ({sz//1024} Ko)  hash={h or 'N/A'}")

conn.close()
