"""
Consolide les paires NOM / NOM_racine dans RENAISON 2022 :
  - Les fichiers de NOM_racine uniques (non présents dans NOM) sont déplacés vers NOM/
  - Les fichiers identiques (même nom ET même taille) sont supprimés de NOM_racine
  - Le dossier NOM_racine vide est supprimé à la fin

Usage :
    python reorg_09_consolider_racine.py           → dry-run
    python reorg_09_consolider_racine.py --apply   → exécution réelle
"""
import sys, os, shutil, hashlib

DRY_RUN = '--apply' not in sys.argv
BASE22  = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\RENAISON 2022'
LOG     = os.path.abspath('reports/reorg_09_consolider_racine_log.txt')

PAIRES = [
    ('SESSION MAI 2022',   'SESSION MAI 2022_racine'),
    ('SESSION JUIN 2022',  'SESSION JUIN 2022_racine'),
    ('CCTP',               'CCTP_racine'),
    ('_recu de FAbrice',   '_recu de FAbrice_racine'),
]


def log(msg=''):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def md5_file(path, chunk=1 << 20):
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while True:
                data = f.read(chunk)
                if not data:
                    break
                h.update(data)
        return h.hexdigest()
    except OSError:
        return None


def list_files(folder):
    """Retourne {chemin_relatif: chemin_absolu} pour tous les fichiers."""
    result = {}
    for dirpath, _, filenames in os.walk(folder):
        for fn in filenames:
            abs_path = os.path.join(dirpath, fn)
            rel = os.path.relpath(abs_path, folder)
            result[rel] = abs_path
    return result


def remove_empty_dirs(folder):
    """Supprime récursivement les sous-dossiers vides, puis le dossier lui-même."""
    for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
        if not os.listdir(dirpath):
            if DRY_RUN:
                log(f"  [DRY] RMDIR {dirpath}")
            else:
                os.rmdir(dirpath)
                log(f"  RMDIR {dirpath}")


open(LOG, 'w', encoding='utf-8').close()
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Consolidation _racine → RENAISON 2022")
log('=' * 72)
log()

total_moved = total_deleted = total_skipped = 0

for nom, nom_racine in PAIRES:
    dst_folder = os.path.join(BASE22, nom)
    src_folder = os.path.join(BASE22, nom_racine)

    log(f"{'─'*72}")
    log(f"  {nom_racine}  →  {nom}")
    log()

    if not os.path.exists(src_folder):
        log(f"  SKIP — {nom_racine} introuvable (déjà consolidé ?)")
        log()
        continue

    if not os.path.exists(dst_folder):
        # Aucun conflit : renommer simplement
        log(f"  Destination {nom} absente — renommage direct")
        if DRY_RUN:
            log(f"  [DRY] RENAME {src_folder} → {dst_folder}")
        else:
            os.rename(src_folder, dst_folder)
            log(f"  RENAME OK")
        log()
        continue

    # Les deux existent : comparer fichier par fichier
    src_files = list_files(src_folder)
    dst_files = list_files(dst_folder)

    log(f"  Fichiers dans {nom_racine}   : {len(src_files)}")
    log(f"  Fichiers dans {nom}          : {len(dst_files)}")
    log()

    moved = deleted = skipped = 0

    for rel, src_abs in sorted(src_files.items()):
        dst_abs = os.path.join(dst_folder, rel)

        if rel in dst_files:
            # Même chemin relatif dans les deux → comparer taille puis hash
            src_sz = os.path.getsize(src_abs)
            dst_sz = os.path.getsize(dst_abs)
            same = src_sz == dst_sz
            if same:
                # Vérifier hash pour être sûr
                src_h = md5_file(src_abs)
                dst_h = md5_file(dst_abs)
                same = (src_h == dst_h) and src_h is not None

            if same:
                log(f"  DUP  {rel[:80]}")
                if DRY_RUN:
                    log(f"       [DRY] Suppression du doublon dans _racine")
                else:
                    os.remove(src_abs)
                    log(f"       DEL doublon")
                deleted += 1
            else:
                # Même nom mais contenu différent → renommer avec suffixe
                base, ext = os.path.splitext(os.path.basename(rel))
                dir_part  = os.path.dirname(rel)
                new_rel   = os.path.join(dir_part, f"{base}_racine{ext}")
                new_dst   = os.path.join(dst_folder, new_rel)
                log(f"  DIFF {rel[:70]}")
                log(f"       → renommé {new_rel[:70]}")
                if DRY_RUN:
                    log(f"       [DRY] MOVE src → {new_dst}")
                else:
                    os.makedirs(os.path.dirname(new_dst), exist_ok=True)
                    shutil.move(src_abs, new_dst)
                moved += 1
        else:
            # Fichier unique dans _racine → déplacer vers destination
            log(f"  NEW  {rel[:80]}")
            if DRY_RUN:
                log(f"       [DRY] MOVE → {dst_abs}")
            else:
                os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
                shutil.move(src_abs, dst_abs)
                log(f"       MOVE OK")
            moved += 1

    log()
    log(f"  → Déplacés : {moved}   Doublons supprimés : {deleted}   Ignorés : {skipped}")

    # Nettoyer les dossiers vides restants
    if not DRY_RUN:
        remove_empty_dirs(src_folder)
    else:
        # Simuler : vérifier si le dossier sera vide
        remaining = sum(1 for _ in os.walk(src_folder) for f in _[2])
        net_remaining = remaining - deleted
        if net_remaining <= 0:
            log(f"  [DRY] RMDIR {src_folder} (sera vide)")

    total_moved += moved
    total_deleted += deleted
    total_skipped += skipped
    log()

log('=' * 72)
log("RÉSUMÉ GLOBAL")
log('=' * 72)
log(f"  Fichiers déplacés (uniques _racine) : {total_moved}")
log(f"  Doublons supprimés                  : {total_deleted}")
log(f"  Ignorés                             : {total_skipped}")
if DRY_RUN:
    log()
    log("  → relancer avec --apply pour exécuter")
