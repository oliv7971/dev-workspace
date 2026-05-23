# cleanup_excel_vba.py -- Consolidation Excel/VBA
#
# Actions :
#   1. Supprime CALCUL/ (1 unique = Thumbs.db, tout le reste = doublons
#      deja presents dans 11-CODES EXEMPLES et 00.Utilitaire de travail)
#   2. Fusionne VBA/ + VisualBasic/ -> excel-vba/
#      en dedupliquant (si meme nom+taille dans les deux, garde un seul)
#   3. Deplace excel/ -> excel-vba/excel/ (contenu intact, pas de dedup interne)
#   4. Deplace Olivier BURE/ -> excel-vba/olivier-bure/
#   5. Deplace BURE8OLIVIER/ -> excel-vba/bure8olivier/
#   6. Deplace petits dossiers projets ->
#      boulons radio/  -> excel-vba/projets/
#      17-PL TMS/      -> excel-vba/projets/
#      CircleBestFitting/ -> excel-vba/projets/
#   7. Scinde developpement/ :
#      - sous-dossier convergences/ (.xls tunnels) -> excel-vba/convergences/
#      - reste (PHP, Java, etc.) -> reste dans developpement/
#
# Usage :
#   python cleanup_excel_vba.py            # dry-run
#   python cleanup_excel_vba.py --apply    # execution

import os
import shutil
import sys
from collections import defaultdict

APPLY = '--apply' in sys.argv
BASE  = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

moved   = 0
deleted = 0
skipped = 0
errors  = 0

def j(*parts):
    return os.path.join(BASE, *parts)

def short(p):
    return p[len(BASE)+1:] if p.startswith(BASE) else p

mode = 'APPLY' if APPLY else 'DRY-RUN'
print('=' * 65)
print(f'MODE : {mode}')
print('=' * 65)

def move_item(src, dst_dir, label=''):
    global moved, skipped, errors
    name = os.path.basename(src)
    dst  = os.path.join(dst_dir, name)
    tag  = f'[{label}] ' if label else ''
    if os.path.exists(dst):
        # Verifier si doublon exact (meme taille)
        if os.path.isfile(src) and os.path.isfile(dst):
            if os.path.getsize(src) == os.path.getsize(dst):
                print(f'  DUP (supprime src) : {tag}{short(src)}')
                if APPLY:
                    try:
                        os.remove(src)
                        skipped += 1
                    except Exception as e:
                        print(f'    ERREUR suppr dup : {e}')
                        errors += 1
                else:
                    skipped += 1
                return
        print(f'  SKIP (conflit) : {tag}{short(src)}  ->  {short(dst)}')
        skipped += 1
        return
    print(f'  MOVE : {tag}{short(src)}  ->  {short(dst)}')
    if APPLY:
        try:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.move(src, dst)
            moved += 1
        except Exception as e:
            print(f'    ERREUR : {e}')
            errors += 1
    else:
        moved += 1

def move_dir_contents(src_dir, dst_dir, label=''):
    if not os.path.exists(src_dir):
        print(f'  ABSENT : {short(src_dir)}')
        return
    items = sorted(os.scandir(src_dir), key=lambda e: e.name)
    for item in items:
        move_item(item.path, dst_dir, label)
    rmdir_if_empty(src_dir)

def move_dir(src_dir, dst_parent, label=''):
    if not os.path.exists(src_dir):
        print(f'  ABSENT : {short(src_dir)}')
        return
    move_item(src_dir, dst_parent, label)

def rmdir_if_empty(path):
    if not os.path.exists(path):
        return
    items = list(os.scandir(path))
    if items:
        still = [e.name for e in items]
        print(f'  [reste] {short(path)} : {len(still)} elements -> {still[:5]}')
        return
    print(f'  RMDIR : {short(path)}')
    if APPLY:
        try:
            os.rmdir(path)
        except Exception as e:
            print(f'    ERREUR rmdir : {e}')

def delete_file(path):
    global deleted
    print(f'  DELETE : {short(path)}')
    if APPLY:
        try:
            os.remove(path)
            deleted += 1
        except Exception as e:
            print(f'    ERREUR delete : {e}')
    else:
        deleted += 1

def rmtree(path):
    global deleted
    n = sum(len(fs) for _, _, fs in os.walk(path)) if os.path.exists(path) else 0
    print(f'  RMTREE : {short(path)}  ({n} fichiers)')
    if APPLY:
        try:
            shutil.rmtree(path)
            deleted += n
        except Exception as e:
            print(f'    ERREUR rmtree : {e}')
    else:
        deleted += n

# ─────────────────────────────────────────────────────────────
# 1. Supprimer CALCUL/ (doublons confirmes + Thumbs.db)
# ─────────────────────────────────────────────────────────────
print('\n[1] SUPPRESSION CALCUL/ (doublons + Thumbs.db)')
calcul = j('CALCUL')
if os.path.exists(calcul):
    # Verifier que le seul fichier unique est bien Thumbs.db
    all_files = [(os.path.join(r, f), f.lower())
                 for r, dirs, files in os.walk(calcul)
                 for f in files]
    thumbs = [fp for fp, fn in all_files if fn == 'thumbs.db']
    others = [fp for fp, fn in all_files if fn != 'thumbs.db']
    print(f'  Total : {len(all_files)} fichiers, dont {len(thumbs)} Thumbs.db')
    rmtree(calcul)

# ─────────────────────────────────────────────────────────────
# 2. Fusionner VBA/ + VisualBasic/ -> excel-vba/
#    (dedup integre dans move_item : si meme taille -> supprime src)
# ─────────────────────────────────────────────────────────────
print('\n[2] FUSION VBA/ + VisualBasic/ -> excel-vba/')

# D'abord VBA/ -> excel-vba/vba/
print('\n  VBA/ -> excel-vba/vba/')
vba_src = j('VBA')
if os.path.exists(vba_src):
    for item in sorted(os.scandir(vba_src), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'vba'))
    rmdir_if_empty(vba_src)

# Puis VisualBasic/ -> excel-vba/visual-basic/
print('\n  VisualBasic/ -> excel-vba/visual-basic/')
vb_src = j('VisualBasic')
if os.path.exists(vb_src):
    for item in sorted(os.scandir(vb_src), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'visual-basic'))
    rmdir_if_empty(vb_src)

# ─────────────────────────────────────────────────────────────
# 3. excel/ -> excel-vba/excel/
# ─────────────────────────────────────────────────────────────
print('\n[3] excel/ -> excel-vba/excel/')
excel_src = j('excel')
if os.path.exists(excel_src):
    for item in sorted(os.scandir(excel_src), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'excel'))
    rmdir_if_empty(excel_src)

# ─────────────────────────────────────────────────────────────
# 4. Olivier BURE/ -> excel-vba/olivier-bure/
# ─────────────────────────────────────────────────────────────
print('\n[4] Olivier BURE/ -> excel-vba/olivier-bure/')
ob_src = j('Olivier BURE')
if os.path.exists(ob_src):
    for item in sorted(os.scandir(ob_src), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'olivier-bure'))
    rmdir_if_empty(ob_src)

# ─────────────────────────────────────────────────────────────
# 5. BURE8OLIVIER/ -> excel-vba/bure8olivier/
# ─────────────────────────────────────────────────────────────
print('\n[5] BURE8OLIVIER/ -> excel-vba/bure8olivier/')
b8o_src = j('BURE8OLIVIER')
if os.path.exists(b8o_src):
    for item in sorted(os.scandir(b8o_src), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'bure8olivier'))
    rmdir_if_empty(b8o_src)

# ─────────────────────────────────────────────────────────────
# 6. Petits dossiers projets -> excel-vba/projets/
# ─────────────────────────────────────────────────────────────
print('\n[6] Petits dossiers -> excel-vba/projets/')
for folder in ['boulons radio', '17-PL TMS', 'CircleBestFitting']:
    src = j(folder)
    if os.path.exists(src):
        print(f'\n  {folder}/ -> excel-vba/projets/{folder}/')
        for item in sorted(os.scandir(src), key=lambda e: e.name):
            move_item(item.path, j('excel-vba', 'projets', folder))
        rmdir_if_empty(src)

# ─────────────────────────────────────────────────────────────
# 7. Scinder developpement/ : convergences/ -> excel-vba/convergences/
# ─────────────────────────────────────────────────────────────
print('\n[7] developpement/convergences/ -> excel-vba/convergences/')
conv_src = j('developpement', 'convergences')
if os.path.exists(conv_src):
    for item in sorted(os.scandir(conv_src), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'convergences'))
    rmdir_if_empty(conv_src)

# Autres sous-dossiers residuels dans developpement a verifier
print('\n  Reste dans developpement/ :')
devp = j('developpement')
if os.path.exists(devp):
    for item in sorted(os.scandir(devp), key=lambda e: e.name):
        if item.is_dir():
            cnt = sum(len(fs) for _, _, fs in os.walk(item.path))
            print(f'    {item.name}/  ({cnt} fichiers)')
        else:
            print(f'    {item.name}')

# ─────────────────────────────────────────────────────────────
print('\n' + '=' * 65)
print(f'Resume : {moved} deplaces, {skipped} suppr-dupes, {deleted} supprimes, {errors} erreurs')
if not APPLY:
    print('-> Relancer avec --apply pour executer')
print('=' * 65)
