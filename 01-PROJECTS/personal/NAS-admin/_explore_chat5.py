"""Vérification des inclusions pour phase 2."""
import sqlite3
from collections import defaultdict

DB = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'

DELETED_P1 = {
    'TUNNEL DU CHAT - 2017', 'rep pytha scooter ordi chat',
    '10-Tunnel du Chat', '01-donnees avant projet 2017- PAUL & LUDO & TMS',
    '21-travaux-bureau-proj', '70-sauvegardes cartes TPS1200',
    'Migration TMS Amberg chat', 'LUDO',
}

conn = sqlite3.connect(DB)
c = conn.cursor()

def get_dir_data(dir_name):
    prefix = BASE + '\\' + dir_name + '\\'
    c.execute("SELECT filename, size, hash_md5, modified_time FROM files WHERE path LIKE ?",
              (prefix + '%',))
    return c.fetchall()

def check_inclusion(a_name, b_name):
    """Vérifie si tous les fichiers de A ont un équivalent dans B."""
    files_a = get_dir_data(a_name)
    files_b = get_dir_data(b_name)
    hashes_b = {h for _, _, h, _ in files_b if h}
    ns_b = {(fn, sz) for fn, sz, _, _ in files_b}
    
    matched = missing = 0
    miss_list = []
    for fn, sz, h, mt in files_a:
        if h and h in hashes_b:
            matched += 1
        elif (fn, sz) in ns_b:
            matched += 1
        else:
            missing += 1
            miss_list.append((fn, sz, h))
    return len(files_a), matched, missing, miss_list

# Paires à vérifier
pairs = [
    ('Etude BG',              '99-olivier'),
    ('PAUL',                   'TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('Pour Eiffage',           '20150904-CHAT'),
    ('TUNNEL CHAT',            '20150904-CHAT'),
    ('TUNNEL CHAT',            '99-olivier'),
    ('documents-tunnel-du-chat', '99-olivier'),
    ('documents-tunnel-du-chat', '20150904-CHAT'),
    ('03-POLYGONALE',          'TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('89-PLANS EXE',           'TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('14 tunnel chat',         '20150904-CHAT'),
    ('14 tunnel chat',         '99-olivier'),
    ('leve-tetes-dec2014',     '20150904-CHAT'),
    ('scan chat rescindement', '20150904-CHAT'),
    ('scan chat rescindement', '03-tunnel chat'),
    ('Polygo chat lucas',      '20150904-CHAT'),
    ('voute parapluie',        '20150904-CHAT'),
    ('71-envoi FC scans mai2017', '03-tunnel chat'),
    ('11-TUNNEL DU CHAT',      '03-tunnel chat'),
    ('CHAT',                   '03-tunnel chat'),
    ('TMS Office',             'TMS'),
]

# Vérifier aussi : 2017/ est-il inclus dans la combinaison des autres ?
# Et 20150904-CHAT\99-olivier ⊂ 99-olivier ?

print(f"{'A (contenu dans B?)':<45} {'B':<45} {'Tot':>5} {'OK':>5} {'Miss':>5} {'Verdict'}")
print('=' * 120)
for a, b in pairs:
    tot, ok, miss, ml = check_inclusion(a, b)
    if tot == 0:
        verdict = 'VIDE'
    elif miss == 0:
        verdict = 'OK 100%'
    elif miss <= 3:
        verdict = f'QUASI ({miss})'
    else:
        verdict = f'{miss} manquants'
    print(f"  {a:<43} {b:<43} {tot:>5} {ok:>5} {miss:>5} {verdict}")
    if miss > 0 and miss <= 5:
        for fn, sz, h in ml:
            print(f"    → {fn} ({sz//1024 if sz else 0} Ko)")

# Check spécial: 20150904-CHAT\99-olivier vs 99-olivier
print("\n=== Cas spécial : 20150904-CHAT contient un sous-dossier 99-olivier ===")
prefix_sub = BASE + r'\20150904-CHAT\99-olivier\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix_sub + '%',))
sub_files = c.fetchall()
prefix_main = BASE + r'\99-olivier\\'
c.execute("SELECT filename, size, hash_md5 FROM files WHERE path LIKE ?", (prefix_main + '%',))
main_files = c.fetchall()
h_main = {h for _, _, h in main_files if h}
ns_main = {(fn, sz) for fn, sz, _ in main_files}
matched = sum(1 for fn, sz, h in sub_files if (h and h in h_main) or (fn, sz) in ns_main)
missing = len(sub_files) - matched
print(f"  20150904-CHAT\\99-olivier: {len(sub_files)} fichiers, {matched} trouvés dans 99-olivier/, {missing} manquants")

# Inverse: 99-olivier ⊂ 20150904-CHAT\99-olivier ?
h_sub = {h for _, _, h in sub_files if h}
ns_sub = {(fn, sz) for fn, sz, _ in sub_files}
matched2 = sum(1 for fn, sz, h in main_files if (h and h in h_sub) or (fn, sz) in ns_sub)
missing2 = len(main_files) - matched2
print(f"  99-olivier/: {len(main_files)} fichiers, {matched2} trouvés dans 20150904\\99-olivier, {missing2} manquants")

conn.close()
