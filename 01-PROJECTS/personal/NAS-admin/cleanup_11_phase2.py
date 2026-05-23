# cleanup_11_phase2.py -- Nettoyage 11-DEVELOPPEMENT Phase 2
# Actions :
#   1. Supprime les dossiers d'installation/binaires :
#      - sqlitestudio-3.3.3  (DLL + EXE)
#      - DVP                 (netbeans .dmg + vbsetup.exe)
#      - wscite225           (config editeur SciTE)
#   2. Fusionne Visual Studio 2010 -> CPP/vs2010-projects
#   3. Fusionne exs java -> java/exs-java
#      Fusionne NetBeansProjects -> java/NetBeansProjects
#   4. Fusionne divers/ (xlsx/xlsm) -> excel/divers-topo
#      Fusionne calculs_topometriques_XLS(1)/ -> excel/
#
# Usage :
#   python cleanup_11_phase2.py            # dry-run
#   python cleanup_11_phase2.py --apply    # execution reelle
import os
import sys
import shutil

APPLY = '--apply' in sys.argv
BASE  = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

moved  = 0
errors = 0
deleted_dirs = []

def p(folder):
    return os.path.join(BASE, folder)

mode = 'APPLY' if APPLY else 'DRY-RUN'
print('=' * 60)
print(f'MODE : {mode}')
print('=' * 60)

# ─── Helper : move item (file or dir) ─────────────────────────────────────────
def move_item(src, dst_dir, label=''):
    global moved, errors
    name = os.path.basename(src)
    dst  = os.path.join(dst_dir, name)
    tag  = f'[{label}] ' if label else ''
    if os.path.exists(dst):
        print(f'  SKIP (existant) : {tag}{name}')
        return
    print(f'  MOVE : {tag}{src[len(BASE)+1:]}  →  {dst[len(BASE)+1:]}')
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

# ─── Helper : delete folder (must be empty in dry-run) ────────────────────────
def rmdir_if_empty(path, label=''):
    name = path[len(BASE)+1:]
    if not os.path.exists(path):
        return
    remaining = list(os.scandir(path))
    if remaining:
        items = [e.name for e in remaining]
        print(f'  [!] {name} non vide ({len(items)} éléments) : {items[:5]}')
        return
    print(f'  RMDIR : {name}')
    if APPLY:
        try:
            os.rmdir(path)
            deleted_dirs.append(name)
        except Exception as e:
            print(f'    ERREUR rmdir : {e}')

def rmtree(path, label=''):
    name = path[len(BASE)+1:]
    count = sum(len(fs) for _, _, fs in os.walk(path)) if os.path.exists(path) else 0
    print(f'  DELETE : {name}  ({count} fichiers)')
    if APPLY:
        try:
            shutil.rmtree(path)
            deleted_dirs.append(name)
        except Exception as e:
            print(f'    ERREUR rmtree : {e}')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Suppression des dossiers d'installation / binaires
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[SUPPR] sqlitestudio-3.3.3  (appli SQLiteStudio - DLL/EXE)')
rmtree(p('sqlitestudio-3.3.3'))

print('\n[SUPPR] DVP  (netbeans .dmg + vbsetup.exe = installeurs)')
rmtree(p('DVP'))

print('\n[SUPPR] wscite225  (config éditeur SciTE - pas du code perso)')
rmtree(p('wscite225'))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Visual Studio 2010  →  CPP\vs2010-projects
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[MERGE] Visual Studio 2010  →  CPP\\vs2010-projects')
src_vs = p('Visual Studio 2010')
if os.path.exists(src_vs):
    dst_vs = p(r'CPP\vs2010-projects')
    for item in sorted(os.scandir(src_vs), key=lambda e: e.name):
        move_item(item.path, dst_vs)
    rmdir_if_empty(src_vs)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Java : consolider exs java + NetBeansProjects
#    La racine java\ (sans .java) → java\web-resources
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[MERGE] exs java  →  java\\exs-java')
src_exs = p('exs java')
if os.path.exists(src_exs):
    dst_exs = p(r'java\exs-java')
    for item in sorted(os.scandir(src_exs), key=lambda e: e.name):
        move_item(item.path, dst_exs)
    rmdir_if_empty(src_exs)

print('\n[MERGE] NetBeansProjects  →  java\\NetBeansProjects')
src_nb = p('NetBeansProjects')
if os.path.exists(src_nb):
    dst_nb = p(r'java\NetBeansProjects')
    for item in sorted(os.scandir(src_nb), key=lambda e: e.name):
        move_item(item.path, dst_nb)
    rmdir_if_empty(src_nb)

# Racine java\ : déplacer le contenu web dans un sous-dossier propre
print('\n[REORG] java\\ (racine) : sous-dossiers déjà structurés (01-, 02-)')
print('  (Pas de déplacement automatique - structure déjà lisible)')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. divers + calculs_topometriques_XLS(1)  →  excel\
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[MERGE] divers  →  excel\\divers-topo')
src_div = p('divers')
if os.path.exists(src_div):
    dst_div = p(r'excel\divers-topo')
    for item in sorted(os.scandir(src_div), key=lambda e: e.name):
        move_item(item.path, dst_div)
    rmdir_if_empty(src_div)

print('\n[MERGE] calculs_topometriques_XLS(1)  →  excel\\')
src_xls = p('calculs_topometriques_XLS(1)')
if os.path.exists(src_xls):
    dst_xls = p('excel')
    for item in sorted(os.scandir(src_xls), key=lambda e: e.name):
        move_item(item.path, dst_xls)
    rmdir_if_empty(src_xls)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n' + '=' * 60)
print(f'Résumé : {moved} déplacés, {errors} erreurs, {len(deleted_dirs)} dossiers supprimés')
if not APPLY:
    print('→ Relancer avec --apply pour exécuter')
print('=' * 60)
