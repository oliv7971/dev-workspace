"""
Cleanup 36-TUNNEL GRAND CHAMBON dans 37:
1. Fusionner les fichiers uniques de CHAMBON 2017/SESSION JANVIER 2017 -> 03-PHASE 03/SESSION JANVIER 2017
2. Supprimer tout 36-TUNNEL GRAND CHAMBON

Usage:
    python cleanup_36_chambon.py          # dry-run
    python cleanup_36_chambon.py --apply  # execution
"""
import os
import sys
import shutil
import sqlite3
import hashlib
from collections import defaultdict

DRY_RUN = '--apply' not in sys.argv

BASE37 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'
PATH36 = os.path.join(BASE37, '36-TUNNEL GRAND CHAMBON')
SRC_CHAMBON2017 = os.path.join(PATH36, 'CHAMBON 2017', 'SESSION JANVIER 2017')
DST_PHASE03 = os.path.join(BASE37, '03-PHASE 03 - interchantier 2017', 'SESSION JANVIER 2017')

DB_PATH = 'inventaires/inventaire_37-TUNNEL GRAND CHAMBON.db'

def quick_hash(filepath, chunk=65536):
    try:
        h = hashlib.md5()
        h.update(str(os.path.getsize(filepath)).encode())
        with open(filepath, 'rb') as f:
            h.update(f.read(chunk))
        return h.hexdigest()
    except:
        return None

def format_size(size):
    if size > 1073741824: return f'{size/1073741824:.2f} Go'
    if size > 1048576: return f'{size/1048576:.0f} Mo'
    if size > 1024: return f'{size/1024:.0f} Ko'
    return f'{size} o'

print('=' * 80)
print(f'CLEANUP 36-TUNNEL GRAND CHAMBON')
print(f'Mode: {"DRY-RUN" if DRY_RUN else "APPLY"}')
print('=' * 80)

# Verifications
if not os.path.exists(PATH36):
    print('ERREUR: 36-TUNNEL GRAND CHAMBON introuvable!')
    sys.exit(1)

if not os.path.exists(DST_PHASE03):
    print(f'Le dossier destination n\'existe pas, il sera cree: {DST_PHASE03}')

# Phase 1: Construire index des fichiers deja presents dans Phase 03
print('\n--- Phase 1: Index de 03-PHASE 03 ---')
base_ph3 = os.path.join(BASE37, '03-PHASE 03 - interchantier 2017')
existing_hashes = set()
existing_name_size = set()

if os.path.exists(base_ph3):
    for dirpath, dirs, files in os.walk(base_ph3):
        for f in files:
            full = os.path.join(dirpath, f)
            try:
                size = os.path.getsize(full)
                h = quick_hash(full)
                if h:
                    existing_hashes.add(h)
                existing_name_size.add((f.lower(), size))
            except:
                pass
    print(f'  {len(existing_hashes)} hashes, {len(existing_name_size)} fichiers indexes')
else:
    print('  Phase 03 vide ou inexistante')

# Phase 2: Scanner CHAMBON 2017/SESSION JANVIER 2017 et identifier les uniques
print('\n--- Phase 2: Identification des fichiers uniques dans CHAMBON 2017 ---')
to_copy = []  # (src, dst, size)
skipped = 0
skipped_size = 0

if os.path.exists(SRC_CHAMBON2017):
    for dirpath, dirs, files in os.walk(SRC_CHAMBON2017):
        for f in files:
            src = os.path.join(dirpath, f)
            rel = os.path.relpath(src, SRC_CHAMBON2017)
            dst = os.path.join(DST_PHASE03, rel)
            try:
                size = os.path.getsize(src)
                h = quick_hash(src)
                
                is_dup = False
                if h and h in existing_hashes:
                    is_dup = True
                elif (f.lower(), size) in existing_name_size:
                    is_dup = True
                
                if is_dup:
                    skipped += 1
                    skipped_size += size
                else:
                    to_copy.append((src, dst, size))
            except Exception as e:
                print(f'  ERREUR lecture: {src}: {e}')

    print(f'  A copier (uniques): {len(to_copy)} fichiers, {format_size(sum(s for _,_,s in to_copy))}')
    print(f'  Ignores (doublons): {skipped} fichiers, {format_size(skipped_size)}')
else:
    print(f'  CHAMBON 2017/SESSION JANVIER 2017 introuvable dans 36')

# Aussi verifier le sous-dossier "prepa intervention mars" 
src_prepa = os.path.join(PATH36, 'CHAMBON 2017', 'prepa intervention mars')
if os.path.exists(src_prepa):
    dst_prepa = os.path.join(base_ph3, 'prepa intervention mars')
    for dirpath, dirs, files in os.walk(src_prepa):
        for f in files:
            src = os.path.join(dirpath, f)
            rel = os.path.relpath(src, src_prepa)
            dst = os.path.join(dst_prepa, rel)
            try:
                size = os.path.getsize(src)
                h = quick_hash(src)
                is_dup = (h and h in existing_hashes) or (f.lower(), size) in existing_name_size
                if not is_dup:
                    to_copy.append((src, dst, size))
            except:
                pass

# Phase 3: Copier les fichiers uniques
print(f'\n--- Phase 3: Copie des {len(to_copy)} fichiers uniques vers Phase 03 ---')
copied = 0
copy_errors = 0
for src, dst, size in to_copy:
    rel_src = os.path.relpath(src, PATH36)
    rel_dst = os.path.relpath(dst, base_ph3)
    print(f'  COPY {rel_src}')
    print(f'    -> {rel_dst}')
    if not DRY_RUN:
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
            print(f'    OK')
        except Exception as e:
            print(f'    ERREUR: {e}')
            copy_errors += 1
    else:
        copied += 1

# Phase 4: Supprimer 36-TUNNEL GRAND CHAMBON
print(f'\n--- Phase 4: Suppression de 36-TUNNEL GRAND CHAMBON ---')
# Compter ce qu'on va supprimer
del_files = sum(len(files) for _, _, files in os.walk(PATH36))
del_size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(PATH36) for f in files)
print(f'  A supprimer: {del_files} fichiers, {format_size(del_size)}')
print(f'  DELETE {os.path.basename(PATH36)}/')

if not DRY_RUN:
    if copy_errors > 0:
        print(f'  ABANDON: {copy_errors} erreurs de copie, on ne supprime pas')
    else:
        try:
            shutil.rmtree(PATH36)
            print(f'    OK')
        except Exception as e:
            print(f'    ERREUR: {e}')
else:
    print(f'    (dry-run)')

# Resume
print(f'\n{"=" * 80}')
print(f'RESULTAT')
print(f'{"=" * 80}')
print(f'  Fichiers copies:    {copied}')
print(f'  Doublons ignores:   {skipped}')
if not DRY_RUN:
    print(f'  Erreurs copie:      {copy_errors}')
    if copy_errors == 0:
        print(f'  36-TUNNEL supprime: OUI')
    else:
        print(f'  36-TUNNEL supprime: NON (erreurs)')
else:
    print(f'  36-TUNNEL a supprimer: {del_files} fichiers, {format_size(del_size)}')
    print(f'\n  -> Relancer avec --apply pour executer')
