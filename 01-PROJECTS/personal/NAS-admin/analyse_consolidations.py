# analyse_consolidations.py -- Analyse detaillee des groupes a consolider
# Groupes : Excel/VBA, dev-mixte (developpement/sources/progs)

import os
from collections import defaultdict

BASE = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

# Groupes a analyser (hors topo pris en charge separement)
EXCEL_VBA = ['VBA', 'VisualBasic', 'excel', '00.Utilitaire de travail',
             '11-CODES EXEMPLES', 'Olivier BURE', 'BURE8OLIVIER',
             'boulons radio', '17-PL TMS', 'CircleBestFitting', 'CALCUL',
             'developpement']
DEV_MIXTE = ['developpement', 'sources', 'progs']
AUTRES    = ['admin', 'info', '04-LASERSCAN', 'demo_scan',
             '13-FRENEY', '00.Utilitaire de travail',
             '11-CODES EXEMPLES', 'BATCH', 'BIBLIOTHEQUE AUTOCAD']

def collect_group(folders):
    all_files = []  # (folder, relpath, size, basename)
    for folder in folders:
        p = os.path.join(BASE, folder)
        if not os.path.exists(p):
            continue
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                rel = fp[len(p)+1:]
                try:
                    sz = os.path.getsize(fp)
                except OSError:
                    sz = -1
                all_files.append((folder, rel, sz, f.lower()))
    return all_files

def find_exact_dups(files):
    by_key = defaultdict(list)
    for folder, rel, sz, bn in files:
        by_key[(bn, sz)].append((folder, rel))
    return {k: v for k, v in by_key.items()
            if len(set(x[0] for x in v)) > 1}

def top_subdirs(folder, n=8):
    p = os.path.join(BASE, folder)
    if not os.path.exists(p):
        return []
    items = []
    for e in os.scandir(p):
        if e.is_dir():
            cnt = sum(len(fs) for _, _, fs in os.walk(e.path))
            items.append((e.name, cnt))
        else:
            items.append((e.name, 0))
    return sorted(items, key=lambda x: -x[1])[:n]

# ══════════════════════════════════════════════════════════════
print('=' * 65)
print('GROUPE EXCEL / VBA')
print('=' * 65)

ev_files = collect_group(EXCEL_VBA)
ev_dups  = find_exact_dups(ev_files)

for folder in EXCEL_VBA:
    p = os.path.join(BASE, folder)
    if not os.path.exists(p):
        print(f'  {folder:<35} ABSENT')
        continue
    ffiles = [(rel, sz, bn) for f, rel, sz, bn in ev_files if f == folder]
    ext_cnt = defaultdict(int)
    for _, sz, bn in ffiles:
        ext_cnt[os.path.splitext(bn)[1] or '(none)'] += 1
    top_ext = sorted(ext_cnt.items(), key=lambda x: -x[1])[:5]
    print(f'  {folder:<35} {len(ffiles):>4} fichiers  |  {dict(top_ext)}')

print(f'\nDoublons exacts (nom+taille) entre dossiers : {len(ev_dups)}')
print('Top 20 doublons les plus lourds :')
for (bn, sz), locs in sorted(ev_dups.items(), key=lambda x: -x[0][1])[:20]:
    folders = sorted(set(l[0] for l in locs))
    sz_str = f'{sz//1024} Ko' if sz >= 1024 else f'{sz} o'
    print(f'  {bn:<45} ({sz_str})  {folders}')

# Identifier les uniques par dossier
print('\nFichiers UNIQUES par dossier (absents partout ailleurs) :')
dup_keys = set(ev_dups.keys())
for folder in EXCEL_VBA:
    ffiles = [(rel, sz, bn) for f, rel, sz, bn in ev_files if f == folder]
    uniques = [(rel, sz) for rel, sz, bn in ffiles if (bn, sz) not in dup_keys]
    if uniques:
        print(f'  {folder} : {len(uniques)} uniques / {len(ffiles)} total')
        for rel, sz in sorted(uniques)[:5]:
            print(f'    {rel}')
        if len(uniques) > 5:
            print(f'    ... et {len(uniques)-5} autres')

# ══════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('GROUPE DEV-MIXTE (developpement / sources / progs)')
print('=' * 65)

dm_files = collect_group(DEV_MIXTE)
dm_dups  = find_exact_dups(dm_files)

for folder in DEV_MIXTE:
    p = os.path.join(BASE, folder)
    if not os.path.exists(p):
        print(f'  {folder:<35} ABSENT')
        continue
    ffiles = [(rel, sz, bn) for f, rel, sz, bn in dm_files if f == folder]
    ext_cnt = defaultdict(int)
    for _, sz, bn in ffiles:
        ext_cnt[os.path.splitext(bn)[1] or '(none)'] += 1
    top_ext = sorted(ext_cnt.items(), key=lambda x: -x[1])[:6]
    print(f'\n  [{folder}] {len(ffiles)} fichiers  |  top exts: {dict(top_ext)}')
    print('  Sous-dossiers :')
    for name, cnt in top_subdirs(folder):
        print(f'    {name}  ({cnt})')

print(f'\nDoublons exacts entre les 3 dossiers : {len(dm_dups)}')
for (bn, sz), locs in sorted(dm_dups.items(), key=lambda x: -x[0][1])[:15]:
    folders = sorted(set(l[0] for l in locs))
    sz_str = f'{sz//1024} Ko' if sz >= 1024 else f'{sz} o'
    print(f'  {bn:<40} ({sz_str})  {folders}')

# ══════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('PETITS DOSSIERS A TRIER (admin/info/13-FRENEY/etc.)')
print('=' * 65)
for folder in AUTRES:
    p = os.path.join(BASE, folder)
    if not os.path.exists(p):
        continue
    ffiles = collect_group([folder])
    ext_cnt = defaultdict(int)
    for _, rel, sz, bn in ffiles:
        ext_cnt[os.path.splitext(bn)[1] or '(none)'] += 1
    top_ext = sorted(ext_cnt.items(), key=lambda x: -x[1])[:4]
    print(f'  {folder:<35} {len(ffiles):>4} fichiers  |  {dict(top_ext)}')
    for name, cnt in top_subdirs(folder, 4):
        print(f'    {name}  ({cnt})')
