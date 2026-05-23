# cleanup_lisp.py -- Nettoyage du dossier lisp/
#
# Actions :
#   1. Supprimer lisp/scripts lisp/ (doublon quasi-exact de lisp - copie/)
#   2. Supprimer lisp/lisp - copie/AutoCAD 2007 et Covadis 2007/ (installeur)
#   3. Renommer lisp/lisp - copie/ -> lisp/lisp-archives/
#   4. Supprimer lisp/process/ (80 .dxf + 46 .bak - donnees de travail)
#   5. Fusionner IMPORTXYZ/ -> lisp/  (3 fichiers)
#
# Usage :
#   python cleanup_lisp.py            # dry-run
#   python cleanup_lisp.py --apply    # execution

import os
import shutil
import sys

APPLY = '--apply' in sys.argv
BASE  = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

moved   = 0
deleted = 0
errors  = 0

def j(*parts):
    return os.path.join(BASE, *parts)

def short(p):
    return p[len(BASE)+1:] if p.startswith(BASE) else p

mode = 'APPLY' if APPLY else 'DRY-RUN'
print('=' * 65)
print(f'MODE : {mode}')
print('=' * 65)

def rmtree(path, reason=''):
    n = sum(len(fs) for _,_,fs in os.walk(path)) if os.path.exists(path) else 0
    r = f'  ({reason})' if reason else ''
    print(f'  RMTREE{r} : {short(path)}  ({n} fichiers)')
    if APPLY:
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f'    ERREUR : {e}')
    return n

def move_item(src, dst_dir):
    global moved, errors
    name = os.path.basename(src)
    dst  = os.path.join(dst_dir, name)
    if os.path.exists(dst):
        if os.path.isfile(src) and os.path.isfile(dst):
            if os.path.getsize(src) == os.path.getsize(dst):
                print(f'  DUP supprime src : {short(src)}')
                if APPLY:
                    try:
                        os.remove(src)
                    except Exception as e:
                        print(f'    ERREUR : {e}')
                        errors += 1
                return
        print(f'  SKIP conflit : {short(src)}')
        return
    print(f'  MOVE : {short(src)} -> {short(dst)}')
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

# ─────────────────────────────────────────────────────────────
# 1. Supprimer lisp/scripts lisp/ (doublon)
# ─────────────────────────────────────────────────────────────
print('\n[1] Suppression lisp/scripts lisp/ (doublon de lisp - copie)')
sl = j('lisp', 'scripts lisp')
if os.path.exists(sl):
    deleted += rmtree(sl, 'doublon')
else:
    print('  ABSENT : scripts lisp/')

# ─────────────────────────────────────────────────────────────
# 2. Supprimer AutoCAD 2007 installeur dans lisp - copie/
# ─────────────────────────────────────────────────────────────
print('\n[2] Suppression lisp/lisp - copie/AutoCAD 2007 et Covadis 2007/')
acad = j('lisp', 'lisp - copie', 'AutoCAD 2007 et Covadis 2007')
if os.path.exists(acad):
    deleted += rmtree(acad, 'installeur AutoCAD 2007')
else:
    print('  ABSENT')

# ─────────────────────────────────────────────────────────────
# 3. Renommer lisp/lisp - copie/ -> lisp/lisp-archives/
# ─────────────────────────────────────────────────────────────
print('\n[3] Renommer lisp/lisp - copie/ -> lisp/lisp-archives/')
lc = j('lisp', 'lisp - copie')
la = j('lisp', 'lisp-archives')
if os.path.exists(lc):
    if os.path.exists(la):
        print(f'  SKIP : lisp-archives/ existe deja')
    else:
        print(f'  RENAME : {short(lc)} -> {short(la)}')
        if APPLY:
            try:
                os.rename(lc, la)
                moved += 1
            except Exception as e:
                print(f'    ERREUR : {e}')
                errors += 1
        else:
            moved += 1
else:
    print('  ABSENT : lisp - copie/')

# ─────────────────────────────────────────────────────────────
# 4. Supprimer lisp/process/ (dxf/bak de travail)
# ─────────────────────────────────────────────────────────────
print('\n[4] lisp/process/ : recuperer .lsp/.scr/.bat puis supprimer .dxf/.bak')
proc = j('lisp', 'process')
if os.path.exists(proc):
    # D'abord sauvegarder les fichiers code
    KEEP_EXTS = {'.lsp', '.scr', '.bat'}
    for r, _, fs in os.walk(proc):
        for f in fs:
            if os.path.splitext(f)[1].lower() in KEEP_EXTS:
                move_item(os.path.join(r, f), j('lisp'))
    # Puis supprimer le reste
    exts = {}
    for _,_,fs in os.walk(proc):
        for f in fs:
            ext = os.path.splitext(f)[1].lower() or '(none)'
            exts[ext] = exts.get(ext,0)+1
    print(f'  Reste a supprimer : {dict(sorted(exts.items(), key=lambda x:-x[1]))}')
    deleted += rmtree(proc, 'donnees travail .dxf/.bak')
else:
    print('  ABSENT')

# ─────────────────────────────────────────────────────────────
# 5. IMPORTXYZ/ -> lisp/
# ─────────────────────────────────────────────────────────────
print('\n[5] IMPORTXYZ/ -> lisp/')
ix = j('IMPORTXYZ')
if os.path.exists(ix):
    for item in sorted(os.scandir(ix), key=lambda e: e.name):
        print(f'  {item.name}')
        move_item(item.path, j('lisp'))
    # Supprimer si vide
    if APPLY:
        remaining = list(os.scandir(ix)) if os.path.exists(ix) else []
        if not remaining:
            os.rmdir(ix)
            print(f'  RMDIR : {short(ix)}')
        else:
            print(f'  [reste] {[e.name for e in remaining]}')
    else:
        print(f'  RMDIR (si vide) : {short(ix)}')
else:
    print('  ABSENT')

# ─────────────────────────────────────────────────────────────
# Resume
# ─────────────────────────────────────────────────────────────
print('\n' + '=' * 65)
print(f'Resume : {moved} deplaces/renommes, {deleted} supprimes, {errors} erreurs')
if not APPLY:
    print('-> Relancer avec --apply pour executer')
print('=' * 65)
