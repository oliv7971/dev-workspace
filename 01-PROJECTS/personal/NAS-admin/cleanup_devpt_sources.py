# cleanup_devpt_sources.py -- Nettoyage developpement/ et sources/
#
# Actions dans developpement/ :
#   1. .lsp a la racine -> lisp/
#   2. NetBeansProjects/ -> java/NetBeansProjects-devpt/
#   3. macros & divers/ -> excel-vba/macros-divers/
#   4. vba tools/ -> excel-vba/macros-divers/vba-tools/
#   5. .xlsm/.xls a la racine -> excel-vba/excel/  (avec dedup)
#   6. Renommer developpement/ -> php-web/
#      (topo residuels laisses pour l'utilisateur)
#
# Actions dans sources/ :
#   7. autolisp/ -> lisp/autolisp-sources/
#   8. java/ -> java/sources/
#   9. mesprogs/lisp/ -> lisp/
#  10. mesprogs/vba-excel/ -> excel-vba/
#  11. calcul_pente.xls -> excel-vba/excel/
#  12. Supprimer ~$argets.doc (fichier temporaire Word)
#  13. sources/ devient vide -> supprimer si vide
#
# Usage :
#   python cleanup_devpt_sources.py            # dry-run
#   python cleanup_devpt_sources.py --apply    # execution

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

def delete_file(path, reason=''):
    global deleted
    r = f'  ({reason})' if reason else ''
    print(f'  DELETE{r} : {short(path)}')
    if APPLY:
        try:
            os.remove(path)
            deleted += 1
        except Exception as e:
            print(f'    ERREUR : {e}')
    else:
        deleted += 1

def rmdir_if_empty(path):
    if not os.path.exists(path):
        return
    items = list(os.scandir(path))
    if items:
        still = [e.name for e in items]
        print(f'  [reste] {short(path)} : {len(still)} item(s) = {still[:5]}')
        return
    print(f'  RMDIR : {short(path)}')
    if APPLY:
        try:
            os.rmdir(path)
        except Exception as e:
            print(f'    ERREUR rmdir : {e}')

# ─────────────────────────────────────────────────────────────
# Actions sur developpement/
# ─────────────────────────────────────────────────────────────
devp = j('developpement')

# 1. Fichiers .lsp a la racine -> lisp/
print('\n[1] developpement/*.lsp -> lisp/')
if os.path.exists(devp):
    for item in sorted(os.scandir(devp), key=lambda e: e.name):
        if item.is_file() and item.name.lower().endswith('.lsp'):
            move_item(item.path, j('lisp'))

# 2. NetBeansProjects/ -> java/NetBeansProjects/ (merge si conflit)
print('\n[2] developpement/NetBeansProjects/ -> java/NetBeansProjects/')
nbp = j('developpement', 'NetBeansProjects')
if os.path.exists(nbp):
    dst_nbp = j('java', 'NetBeansProjects')
    if os.path.exists(dst_nbp):
        # Merger le contenu
        for item in sorted(os.scandir(nbp), key=lambda e: e.name):
            move_item(item.path, dst_nbp)
        rmdir_if_empty(nbp)
    else:
        move_item(nbp, j('java'))
        rmdir_if_empty(nbp)

# 3. macros & divers/ -> excel-vba/macros-divers/
print('\n[3] developpement/macros & divers/ -> excel-vba/macros-divers/')
mad = j('developpement', 'macros & divers')
if os.path.exists(mad):
    for item in sorted(os.scandir(mad), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'macros-divers'))
    rmdir_if_empty(mad)

# 4. vba tools/ -> excel-vba/macros-divers/
print('\n[4] developpement/vba tools/ -> excel-vba/macros-divers/')
vt = j('developpement', 'vba tools')
if os.path.exists(vt):
    for item in sorted(os.scandir(vt), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'macros-divers'))
    rmdir_if_empty(vt)

# 5. Fichiers .xls/.xlsm/.xlsx a la racine -> excel-vba/excel/
print('\n[5] developpement/*.xls/.xlsm/.xlsx -> excel-vba/excel/')
XLS_EXTS = {'.xls', '.xlsx', '.xlsm'}
if os.path.exists(devp):
    for item in sorted(os.scandir(devp), key=lambda e: e.name):
        if item.is_file() and os.path.splitext(item.name)[1].lower() in XLS_EXTS:
            move_item(item.path, j('excel-vba', 'excel'))

# 6. Renommer developpement/ -> php-web/
print('\n[6] Renommer developpement/ -> php-web/')
phpweb = j('php-web')
if os.path.exists(devp):
    if os.path.exists(phpweb):
        print(f'  SKIP : php-web/ existe deja')
    else:
        print(f'  RENAME : {short(devp)} -> {short(phpweb)}')
        if APPLY:
            try:
                os.rename(devp, phpweb)
                moved += 1
            except Exception as e:
                print(f'    ERREUR : {e}')
                errors += 1
        else:
            moved += 1
    # Indiquer ce qui reste (topo residuels)
    target = phpweb if (APPLY and os.path.exists(phpweb)) else devp
    if os.path.exists(target):
        topo_remain = []
        for item in sorted(os.scandir(target), key=lambda e: e.name):
            if item.is_dir():
                topo_remain.append(f'  [USER-TOPO] {item.name}/')
        if topo_remain:
            print('  Sous-dossiers residuels (topo - laisser a l\'utilisateur) :')
            for t in topo_remain:
                print(t)

# ─────────────────────────────────────────────────────────────
# Actions sur sources/
# ─────────────────────────────────────────────────────────────
srcs = j('sources')

# 7. sources/autolisp/ -> lisp/autolisp/ (merge si conflit)
print('\n[7] sources/autolisp/ -> lisp/autolisp/')
al = j('sources', 'autolisp')
if os.path.exists(al):
    dst_al = j('lisp', 'autolisp')
    if os.path.exists(dst_al):
        # Merger le contenu
        for item in sorted(os.scandir(al), key=lambda e: e.name):
            move_item(item.path, dst_al)
        rmdir_if_empty(al)
    else:
        move_item(al, j('lisp'))
        rmdir_if_empty(al)

# 8. sources/java/ -> java/sources/ (nom explicite)
print('\n[8] sources/java/ -> java/sources/')
sj = j('sources', 'java')
if os.path.exists(sj):
    dst_sj = j('java', 'sources')
    if os.path.exists(dst_sj):
        for item in sorted(os.scandir(sj), key=lambda e: e.name):
            move_item(item.path, dst_sj)
        rmdir_if_empty(sj)
    else:
        print(f'  RENAME : {short(sj)} -> {short(dst_sj)}')
        if APPLY:
            try:
                os.rename(sj, dst_sj)
                moved += 1
            except Exception as e:
                print(f'    ERREUR : {e}')
                errors += 1
        else:
            moved += 1
        rmdir_if_empty(sj)

# 9. sources/mesprogs/lisp/ -> lisp/
print('\n[9] sources/mesprogs/lisp/ -> lisp/')
mpl = j('sources', 'mesprogs', 'lisp')
if os.path.exists(mpl):
    for item in sorted(os.scandir(mpl), key=lambda e: e.name):
        move_item(item.path, j('lisp'))
    rmdir_if_empty(mpl)

# 10. sources/mesprogs/vba-excel/ -> excel-vba/
print('\n[10] sources/mesprogs/vba-excel/ -> excel-vba/')
mpv = j('sources', 'mesprogs', 'vba-excel')
if os.path.exists(mpv):
    for item in sorted(os.scandir(mpv), key=lambda e: e.name):
        move_item(item.path, j('excel-vba', 'excel'))
    rmdir_if_empty(mpv)

# Nettoyer mesprogs/ si vide
rmdir_if_empty(j('sources', 'mesprogs'))

# 11. sources/calcul_pente.xls -> excel-vba/excel/
print('\n[11] sources/calcul_pente.xls -> excel-vba/excel/')
cp = j('sources', 'calcul_pente.xls')
if os.path.exists(cp):
    move_item(cp, j('excel-vba', 'excel'))

# 12. Supprimer ~$argets.doc (verrou Word)
print('\n[12] sources/~$argets.doc -> DELETE')
lock = j('sources', '~$argets.doc')
if os.path.exists(lock):
    delete_file(lock, 'verrou Word')

# 13. sources/ -> garder Targets.doc + java/ si vide
print('\n[13] Etat final sources/')
if os.path.exists(srcs):
    for item in sorted(os.scandir(srcs), key=lambda e: e.name):
        n = sum(len(fs) for _,_,fs in os.walk(item.path)) if item.is_dir() else 1
        print(f'  {item.name}{"/" if item.is_dir() else ""}  ({n})')

# ─────────────────────────────────────────────────────────────
print('\n' + '=' * 65)
print(f'Resume : {moved} deplaces, {skipped} suppr-dupes, {deleted} supprimes, {errors} erreurs')
if not APPLY:
    print('-> Relancer avec --apply pour executer')
print('=' * 65)
