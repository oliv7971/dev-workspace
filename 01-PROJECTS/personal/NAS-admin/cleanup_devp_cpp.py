# cleanup_devp_cpp.py -- Fusion DEVP dans CPP, suppression doublon StaMPS
#
# Actions :
#   1. Verifie que les deux copies StaMPS sont identiques (nom+taille)
#   2. Supprime DEVP/CPP/wetransfer_stamps.../ et le .zip si identique
#   3. Deplace DEVP/CPP/test/ -> CPP/test/
#   4. Deplace DEVP/ASSEMBLER_TXT/ -> CPP/assembler-txt/
#   5. Deplace DEVP/VBA/ -> VBA/ (merge avec le dossier VBA existant)
#   6. Supprime DEVP/ (vide)
#
# Usage :
#   python cleanup_devp_cpp.py            # dry-run
#   python cleanup_devp_cpp.py --apply    # execution

import os
import shutil
import sys

APPLY = '--apply' in sys.argv
BASE  = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

moved  = 0
errors = 0

def j(*parts):
    return os.path.join(BASE, *parts)

mode = 'APPLY' if APPLY else 'DRY-RUN'
print('=' * 60)
print(f'MODE : {mode}')
print('=' * 60)

# ─── helpers ──────────────────────────────────────────────────
def move_item(src, dst_dir):
    global moved, errors
    name = os.path.basename(src)
    dst  = os.path.join(dst_dir, name)
    if os.path.exists(dst):
        print(f'  SKIP (existant) : {src[len(BASE)+1:]}')
        return
    print(f'  MOVE : {src[len(BASE)+1:]}  ->  {dst[len(BASE)+1:]}')
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

def rmtree(path):
    n = path[len(BASE)+1:]
    cnt = sum(len(fs) for _, _, fs in os.walk(path)) if os.path.exists(path) else 0
    print(f'  SUPPR : {n}  ({cnt} fichiers)')
    if APPLY:
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f'    ERREUR rmtree : {e}')

def rmdir_if_empty(path):
    n = path[len(BASE)+1:]
    if not os.path.exists(path):
        return
    items = list(os.scandir(path))
    if items:
        print(f'  [!] {n} non vide : {[e.name for e in items]}')
        return
    print(f'  RMDIR : {n}')
    if APPLY:
        try:
            os.rmdir(path)
        except Exception as e:
            print(f'    ERREUR rmdir : {e}')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Verifier que les deux StaMPS sont identiques
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[CHECK] Verification doublon StaMPS (nom+taille)')

stamps_name = 'wetransfer_stamps-4-1-beta_2022-08-18_1201'
A_dir = j('DEVP', 'CPP', stamps_name)
B_dir = j('CPP', stamps_name)
A_zip = j('DEVP', 'CPP', stamps_name + '.zip')
B_zip = j('CPP', stamps_name + '.zip')

def collect_ns(folder):
    d = {}
    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            rel = fp[len(folder)+1:].lower()
            try: sz = os.path.getsize(fp)
            except: sz = -1
            d[rel] = sz
    return d

ok_dir = False
if os.path.exists(A_dir) and os.path.exists(B_dir):
    a = collect_ns(A_dir)
    b = collect_ns(B_dir)
    diffs = [(k, a[k], b[k]) for k in a if k in b and a[k] != b[k]]
    only_a = [k for k in a if k not in b]
    only_b = [k for k in b if k not in a]
    if not diffs and not only_a and not only_b:
        print(f'  OK : {len(a)} fichiers identiques dans les deux copies')
        ok_dir = True
    else:
        print(f'  ATTENTION : {len(diffs)} tailles diff, {len(only_a)} uniq A, {len(only_b)} uniq B')

ok_zip = False
if os.path.exists(A_zip) and os.path.exists(B_zip):
    szA = os.path.getsize(A_zip)
    szB = os.path.getsize(B_zip)
    if szA == szB:
        print(f'  OK : zip identique ({szA:,} octets)')
        ok_zip = True
    else:
        print(f'  ATTENTION : zip tailles differentes A={szA} B={szB}')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Supprimer la copie dans DEVP/CPP/
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[SUPPR] Doublon StaMPS dans DEVP/CPP/')
if ok_dir:
    rmtree(A_dir)
else:
    print('  SKIP : copies non identiques, verification manuelle requise')

if ok_zip:
    print(f'  SUPPR : {A_zip[len(BASE)+1:]}')
    if APPLY:
        try:
            os.remove(A_zip)
        except Exception as e:
            print(f'    ERREUR : {e}')
else:
    print('  SKIP zip : verification manuelle requise')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Deplacer DEVP/CPP/test/ -> CPP/test/
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[MERGE] DEVP/CPP/test/  ->  CPP/test/')
src_test = j('DEVP', 'CPP', 'test')
if os.path.exists(src_test):
    for item in sorted(os.scandir(src_test), key=lambda e: e.name):
        move_item(item.path, j('CPP', 'test'))
    rmdir_if_empty(src_test)

rmdir_if_empty(j('DEVP', 'CPP'))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Deplacer DEVP/ASSEMBLER_TXT/ -> CPP/assembler-txt/
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[MERGE] DEVP/ASSEMBLER_TXT/  ->  CPP/assembler-txt/')
src_assm = j('DEVP', 'ASSEMBLER_TXT')
if os.path.exists(src_assm):
    for item in sorted(os.scandir(src_assm), key=lambda e: e.name):
        move_item(item.path, j('CPP', 'assembler-txt'))
    rmdir_if_empty(src_assm)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Deplacer DEVP/VBA/ -> VBA/ (merge)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[MERGE] DEVP/VBA/  ->  VBA/')
src_vba = j('DEVP', 'VBA')
if os.path.exists(src_vba):
    for item in sorted(os.scandir(src_vba), key=lambda e: e.name):
        move_item(item.path, j('VBA'))
    rmdir_if_empty(src_vba)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Supprimer DEVP/ si vide
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print('\n[CLEAN] Suppression DEVP/ si vide')
rmdir_if_empty(j('DEVP'))

print('\n' + '=' * 60)
print(f'Resume : {moved} deplaces, {errors} erreurs')
if not APPLY:
    print('-> Relancer avec --apply pour executer')
print('=' * 60)
