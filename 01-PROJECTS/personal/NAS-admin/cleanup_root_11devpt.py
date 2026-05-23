# cleanup_root_11devpt.py -- Nettoyage fichiers a la racine de 11-DEVELOPPEMENT
#
# Actions :
#   1. Supprimer 11-DEVELOPPEMENT/ recursif (uniquement .DS_Store macOS)
#   2. Supprimer Thumbs.db, .lnk, fichiers test vides
#   3. Deplacer .xls/.xlsx/.xlsm -> excel-vba/racine-devpt/
#   4. Deplacer .bas/.vba/.txt code-VBA -> excel-vba/racine-devpt/
#   5. Deplacer .lsp -> lisp/
#   6. Deplacer .pdf -> admin/ (ou reclasser)
#   7. Garder en place : installers .exe, archives .zip, .csv utiles, etc.
#
# Usage :
#   python cleanup_root_11devpt.py            # dry-run
#   python cleanup_root_11devpt.py --apply    # execution

import os
import shutil
import sys

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
        if os.path.isfile(src) and os.path.isfile(dst):
            if os.path.getsize(src) == os.path.getsize(dst):
                print(f'  DUP -> supprime src : {tag}{short(src)}')
                if APPLY:
                    try:
                        os.remove(src)
                        skipped += 1
                    except Exception as e:
                        print(f'    ERREUR : {e}')
                        errors += 1
                else:
                    skipped += 1
                return
        print(f'  SKIP conflit : {tag}{short(src)}')
        skipped += 1
        return
    print(f'  MOVE : {tag}{short(src)} -> {short(dst)}')
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

def delete_item(path, reason=''):
    global deleted
    r = f'  ({reason})' if reason else ''
    is_dir = os.path.isdir(path)
    n = sum(len(fs) for _,_,fs in os.walk(path)) if is_dir else 1
    print(f'  DELETE{r} : {short(path)}  ({n} fichier(s))')
    if APPLY:
        try:
            if is_dir:
                shutil.rmtree(path)
            else:
                os.remove(path)
            deleted += n
        except Exception as e:
            print(f'    ERREUR : {e}')
    else:
        deleted += n

# ─────────────────────────────────────────────────────────────
# 1. Supprimer 11-DEVELOPPEMENT/ recursif (uniquement .DS_Store)
# ─────────────────────────────────────────────────────────────
print('\n[1] Suppression 11-DEVELOPPEMENT/ recursif (DS_Store macOS)')
sub11 = j('11-DEVELOPPEMENT')
if os.path.exists(sub11):
    # Verifier que c'est bien que du .DS_Store / ._ files
    all_files = [(os.path.join(r,f), f) for r,_,fs in os.walk(sub11) for f in fs]
    non_ds = [(p,f) for p,f in all_files if not f.startswith('.')]
    print(f'  {len(all_files)} fichiers dont {len(non_ds)} non-.DS_Store')
    if non_ds:
        print(f'  Attention fichiers non-junk : {non_ds[:3]}')
    else:
        delete_item(sub11, 'uniquement .DS_Store macOS')

# ─────────────────────────────────────────────────────────────
# 2. Supprimer fichiers junk a la racine
# ─────────────────────────────────────────────────────────────
JUNK_NAMES = {'Thumbs.db', 'CursorUserSetup-x64-1.2.2.exe'}
JUNK_EXTS  = {'.lnk'}
TEST_NAMES = {'essai.txt', 'essai2.txt', 'distances50.txt',
              'fichiertest.csv', 'fichiertest2.csv', 'fichiertest3.csv',
              'fichiertest10.csv'}

print('\n[2] Suppression junk a la racine')
for item in sorted(os.scandir(BASE), key=lambda e: e.name):
    if not item.is_file():
        continue
    nm = item.name
    ext = os.path.splitext(nm)[1].lower()
    if nm in JUNK_NAMES or ext in JUNK_EXTS or nm in TEST_NAMES:
        delete_item(item.path, 'junk')

# ─────────────────────────────────────────────────────────────
# 3. Deplacer .xls/.xlsx/.xlsm a la racine -> excel-vba/racine-devpt/
# ─────────────────────────────────────────────────────────────
XLS_EXTS = {'.xls', '.xlsx', '.xlsm', '.xla', '.xlt'}
print('\n[3] Fichiers Excel a la racine -> excel-vba/racine-devpt/')
for item in sorted(os.scandir(BASE), key=lambda e: e.name):
    if item.is_file() and os.path.splitext(item.name)[1].lower() in XLS_EXTS:
        move_item(item.path, j('excel-vba', 'racine-devpt'))

# ─────────────────────────────────────────────────────────────
# 4. Deplacer code VBA (.bas, .vba) + dossier code-vba-excel-monito-lyon
# ─────────────────────────────────────────────────────────────
VBA_EXTS = {'.bas', '.vba'}
VBA_TXT  = {'polyline2pointcloud.vba', 'vba-regex-Linder.txt',
            'SAUVEGARDE PROG CODE GGC OBSERVER.txt', 'macros_carnetGIF2.txt'}
print('\n[4] Code VBA -> excel-vba/racine-devpt/')
for item in sorted(os.scandir(BASE), key=lambda e: e.name):
    if not item.is_file():
        continue
    nm = item.name
    ext = os.path.splitext(nm)[1].lower()
    if ext in VBA_EXTS or nm in VBA_TXT:
        move_item(item.path, j('excel-vba', 'racine-devpt'))

# Dossier code-vba-excel-monito-lyon
cvba = j('code-vba-excel-monito-lyon')
if os.path.exists(cvba):
    move_item(cvba, j('excel-vba'))

# ─────────────────────────────────────────────────────────────
# 5. Deplacer .lsp a la racine -> lisp/
# ─────────────────────────────────────────────────────────────
# (deja fait via cleanup_devpt_sources mais verifier s'il en reste)
print('\n[5] Fichiers .lsp a la racine -> lisp/')
for item in sorted(os.scandir(BASE), key=lambda e: e.name):
    if item.is_file() and item.name.lower().endswith('.lsp'):
        move_item(item.path, j('lisp'))

# ─────────────────────────────────────────────────────────────
# 6. Deplacer .pdf -> admin/
#    (ci_olivier = CV; obformationVBA = formation; Shinken = doc IT)
# ─────────────────────────────────────────────────────────────
print('\n[6] Fichiers .pdf -> admin/')
for item in sorted(os.scandir(BASE), key=lambda e: e.name):
    if item.is_file() and item.name.lower().endswith('.pdf'):
        move_item(item.path, j('admin'))

# CMakeLists.txt -> CPP/
print('\n[6b] CMakeLists.txt -> CPP/')
cm = j('CMakeLists.txt')
if os.path.exists(cm):
    move_item(cm, j('CPP'))

# modules-pytha.txt -> 11-CODES EXEMPLES/
print('\n[6c] modules-pytha.txt -> 11-CODES EXEMPLES/')
mpt = j('modules-pytha.txt')
if os.path.exists(mpt):
    move_item(mpt, j('11-CODES EXEMPLES'))

# ─────────────────────────────────────────────────────────────
# 7. Lister ce qui reste (pour information)
# ─────────────────────────────────────────────────────────────
print('\n[7] Reste a la racine (non traite) :')
HANDLED_DIRS = {'excel-vba','lisp','java','CPP','php-web','progs','sources',
                'admin','rubyLibraryDepot','00.Utilitaire de travail',
                '11-CODES EXEMPLES','04-LASERSCAN','demo_scan',
                'BIBLIOTHEQUE AUTOCAD','BATCH','info','13-FRENEY',
                'AXE','Gisement et distance','IMPORTXYZ','menutopo',
                'outils topo','polyroute','Topo'}
for item in sorted(os.scandir(BASE), key=lambda e: (not e.is_dir(), e.name)):
    if item.name in HANDLED_DIRS:
        continue
    if item.is_dir():
        n = sum(len(fs) for _,_,fs in os.walk(item.path))
        print(f'  DIR  {item.name}/  ({n})')
    else:
        print(f'  FILE {item.name}')

# ─────────────────────────────────────────────────────────────
print('\n' + '=' * 65)
print(f'Resume : {moved} deplaces, {skipped} suppr-dupes, {deleted} supprimes, {errors} erreurs')
if not APPLY:
    print('-> Relancer avec --apply pour executer')
print('=' * 65)
