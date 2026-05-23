"""
cleanup_reorg_11devpt.py  — Réorganisation finale de 11-DEVELOPPEMENT par langage/domaine

Actions :
  [1] Supprimer lisp/lisp-copie/  en récupérant les 8 fichiers extras vers lisp/lisp-archives/12-OUTILS/
  [2] Renommer BIBLIOTHEQUE AUTOCAD/ → autocad-dwg/
  [3] Renommer rubyLibraryDepot/ → ruby/
  [4] Renommer CPP/ → cpp/
  [5] Renommer 11-CODES EXEMPLES/ → pytha-cao/
  [6] Créer topo/ et y déplacer AXE, Gisement et distance, menutopo, outils topo, polyroute
  [7] Déplacer progs/macros acad/*.lsp/.dcl/.dwg → lisp/
  [8] Renommer progs/fileconverterjava_5_03/ : supprimer les doublons "(2)" et déplacer sous logiciels-topo/
  [9] Déplacer lisp/ → autocad-lisp/   (renommer le dossier racine)
  [10] Supprimer sources/ (1 fichier Targets.doc → signaler)
  [11] info/ → docs/  (1 docx)

Usage :
  python -X utf8 cleanup_reorg_11devpt.py           (dry-run)
  python -X utf8 cleanup_reorg_11devpt.py --apply
"""

import os, sys, shutil

APPLY = '--apply' in sys.argv
BASE  = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'

moved = 0
deleted = 0
errors = 0

def j(*parts):
    return os.path.join(BASE, *parts)

def say(msg):
    print(msg)

def move_item(src, dst_dir):
    global moved, errors
    os.makedirs(dst_dir, exist_ok=True) if APPLY else None
    dst = os.path.join(dst_dir, os.path.basename(src))
    if os.path.exists(dst):
        say(f'  SKIP (existe deja) : {os.path.relpath(dst, BASE)}')
        return
    say(f'  MOVE : {os.path.relpath(src, BASE)} -> {os.path.relpath(dst, BASE)}')
    if APPLY:
        try:
            shutil.move(src, dst)
            moved += 1
        except Exception as e:
            say(f'  ERREUR MOVE : {e}')
            errors += 1
    else:
        moved += 1

def rename_folder(src, dst):
    global moved, errors
    say(f'  RENAME : {os.path.relpath(src, BASE)} -> {os.path.relpath(dst, BASE)}')
    if APPLY:
        try:
            os.rename(src, dst)
            moved += 1
        except Exception as e:
            say(f'  ERREUR RENAME : {e}')
            errors += 1
    else:
        moved += 1

def rmtree(path, reason):
    global deleted, errors
    n = sum(len(fs) for _,_,fs in os.walk(path))
    say(f'  RMTREE  ({reason}) : {os.path.relpath(path, BASE)}  ({n} fichiers)')
    if APPLY:
        try:
            shutil.rmtree(path)
            deleted += n
        except Exception as e:
            say(f'  ERREUR RMTREE : {e}')
            errors += 1
    else:
        deleted += n
    return n

def rmfile(path, reason=''):
    global deleted, errors
    say(f'  DELETE  ({reason}) : {os.path.relpath(path, BASE)}')
    if APPLY:
        try:
            os.remove(path)
            deleted += 1
        except Exception as e:
            say(f'  ERREUR DELETE : {e}')
            errors += 1
    else:
        deleted += 1


print(f"{'=== APPLY ===' if APPLY else '=== DRY-RUN ==='}\n")

# ------------------------------------------------------------------
# [1] lisp/lisp-copie/ : récupérer les 8 extras → lisp-archives/12-OUTILS/ puis supprimer
# ------------------------------------------------------------------
print('\n[1] lisp/lisp-copie/ : récupérer extras puis supprimer doublon')
lisp_copie   = j('lisp', 'lisp-copie')
lisp_archives = j('lisp', 'lisp-archives')
if os.path.exists(lisp_copie):
    # Fichiers présents dans lisp-copie mais pas dans lisp-archives
    fa = {os.path.relpath(os.path.join(r,f), lisp_archives)
          for r,_,fs in os.walk(lisp_archives) for f in fs} if os.path.exists(lisp_archives) else set()
    for r,_,fs in os.walk(lisp_copie):
        for f in fs:
            fp  = os.path.join(r, f)
            rel = os.path.relpath(fp, lisp_copie)
            if rel not in fa:
                sub = os.path.dirname(os.path.join(lisp_archives, rel))
                move_item(fp, sub)
    rmtree(lisp_copie, 'doublon de lisp-archives')
else:
    say('  (lisp/lisp-copie/ introuvable — déjà traité ?)')

# ------------------------------------------------------------------
# [2-5] Renommages simples
# ------------------------------------------------------------------
print('\n[2] BIBLIOTHEQUE AUTOCAD/ -> autocad-dwg/')
src = j('BIBLIOTHEQUE AUTOCAD')
dst = j('autocad-dwg')
if os.path.exists(src) and not os.path.exists(dst):
    rename_folder(src, dst)
elif os.path.exists(dst):
    say('  (autocad-dwg/ existe déjà)')
else:
    say('  (BIBLIOTHEQUE AUTOCAD/ introuvable)')

print('\n[3] rubyLibraryDepot/ -> ruby/')
src = j('rubyLibraryDepot')
dst = j('ruby')
if os.path.exists(src) and not os.path.exists(dst):
    rename_folder(src, dst)
elif os.path.exists(dst):
    say('  (ruby/ existe déjà)')
else:
    say('  (rubyLibraryDepot/ introuvable)')

print('\n[4] CPP/ -> cpp/')
src = j('CPP')
dst = j('cpp')
if os.path.exists(src) and not os.path.exists(dst):
    rename_folder(src, dst)
elif os.path.exists(dst):
    say('  (cpp/ existe déjà)')
else:
    say('  (CPP/ introuvable)')

print('\n[5] 11-CODES EXEMPLES/ -> pytha-cao/')
src = j('11-CODES EXEMPLES')
dst = j('pytha-cao')
if os.path.exists(src) and not os.path.exists(dst):
    rename_folder(src, dst)
elif os.path.exists(dst):
    say('  (pytha-cao/ existe déjà)')
else:
    say('  (11-CODES EXEMPLES/ introuvable)')

# ------------------------------------------------------------------
# [6] Créer topo/ et y déplacer les sous-dossiers topo
# ------------------------------------------------------------------
print('\n[6] topo/ : regrouper dossiers topo')
TOPO_FOLDERS = ['AXE', 'Gisement et distance', 'menutopo', 'outils topo', 'polyroute']
for name in TOPO_FOLDERS:
    src = j(name)
    if os.path.exists(src):
        dst_dir = j('topo')
        dst = os.path.join(dst_dir, name)
        say(f'  MOVE_DIR : {name}/ -> topo/{name}/')
        if APPLY:
            os.makedirs(dst_dir, exist_ok=True)
            try:
                shutil.move(src, dst)
                moved += 1
            except Exception as e:
                say(f'  ERREUR : {e}')
                errors += 1
        else:
            moved += 1
    else:
        say(f'  (introuvable : {name}/)')

# ------------------------------------------------------------------
# [7] progs/macros acad/ → lisp/
# ------------------------------------------------------------------
print('\n[7] progs/macros acad/ -> lisp/')
macros = j('progs', 'macros acad')
if os.path.exists(macros):
    for f in os.listdir(macros):
        fp = os.path.join(macros, f)
        if os.path.isfile(fp):
            move_item(fp, j('lisp'))
    if APPLY and os.path.exists(macros):
        try:
            os.rmdir(macros)  # supprime si vide
        except:
            pass
else:
    say('  (progs/macros acad/ introuvable)')

# ------------------------------------------------------------------
# [8] progs/fileconverterjava_5_03/ : dédupliquer "(2)" et déplacer → logiciels-topo/
# ------------------------------------------------------------------
print('\n[8] progs/fileconverterjava_5_03/ -> logiciels-topo/ (sans doublons "(2)")')
fcj = j('progs', 'fileconverterjava_5_03')
if os.path.exists(fcj):
    dst_dir = j('logiciels-topo', 'fileconverterjava_5_03')
    for r, dirs, fs in os.walk(fcj):
        for f in fs:
            if ' (2)' in f:
                fp = os.path.join(r, f)
                say(f'  DELETE  (doublon) : {os.path.relpath(fp, BASE)}')
                if APPLY:
                    try:
                        os.remove(fp)
                        deleted += 1
                    except Exception as e:
                        say(f'  ERREUR : {e}')
                        errors += 1
                else:
                    deleted += 1
            else:
                fp = os.path.join(r, f)
                rel_sub = os.path.relpath(os.path.dirname(fp), fcj)
                target_dir = os.path.join(dst_dir, rel_sub) if rel_sub != '.' else dst_dir
                move_item(fp, target_dir)
    # Supprimer l'arborescence source (maintenant vide ou residus)
    if APPLY and os.path.exists(fcj):
        shutil.rmtree(fcj, ignore_errors=True)
    # Supprimer progs/ si vide
    progs = j('progs')
    remaining = sum(len(fs) for _,_,fs in os.walk(progs)) if os.path.exists(progs) else 0
    if remaining == 0 or not APPLY:
        say(f'  RMDIR  (vide) : progs/')
        if APPLY and os.path.exists(progs):
            shutil.rmtree(progs, ignore_errors=True)
    else:
        say(f'  (progs/ reste {remaining} fichiers — vérifier)')
else:
    say('  (progs/fileconverterjava_5_03/ introuvable)')

# ------------------------------------------------------------------
# [9] lisp/ -> autocad-lisp/
# ------------------------------------------------------------------
print('\n[9] lisp/ -> autocad-lisp/')
src = j('lisp')
dst = j('autocad-lisp')
if os.path.exists(src) and not os.path.exists(dst):
    rename_folder(src, dst)
elif os.path.exists(dst):
    say('  (autocad-lisp/ existe déjà)')
else:
    say('  (lisp/ introuvable)')

# ------------------------------------------------------------------
# [10] info/ -> docs/
# ------------------------------------------------------------------
print('\n[10] info/ -> docs/')
src = j('info')
dst = j('docs')
if os.path.exists(src) and not os.path.exists(dst):
    rename_folder(src, dst)
elif os.path.exists(dst):
    say('  (docs/ existe déjà)')
else:
    say('  (info/ introuvable)')

# ------------------------------------------------------------------
# [11] sources/ — signaler le fichier restant
# ------------------------------------------------------------------
print('\n[11] sources/ — contenu à vérifier manuellement')
sources = j('sources')
if os.path.exists(sources):
    for r,_,fs in os.walk(sources):
        for f in fs:
            say(f'  INFO : {os.path.relpath(os.path.join(r,f), BASE)}')
else:
    say('  (sources/ introuvable — déjà traité)')

# ------------------------------------------------------------------
print(f'\nResume : {moved} déplacés/renommés, {deleted} supprimés, {errors} erreurs')
