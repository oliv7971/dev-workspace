"""
Fusionne 01-SESSION SCAN NOV2015 dans 01-PROJETS SCANS BPNL SUD NOV2015 :
  - Copie les fichiers uniques de SESSION vers PROJETS (si absent par hash)
  - Ignore les fichiers deja presents (meme hash)
  - Supprime SESSION apres verification (avec --delete)

Usage:
  python merge_session_into_projets.py           (dry-run, aucune action)
  python merge_session_into_projets.py --delete  (copie + supprime SESSION)
"""
import sys
import os
import shutil
import hashlib
import sqlite3

DRY_RUN = '--delete' not in sys.argv

SESSION = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\46-BPNL\01-scans BPNL\01-SESSION SCAN NOV2015'
PROJETS = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\46-BPNL\01-scans BPNL\01-PROJETS SCANS BPNL SUD NOV2015'
DB      = os.path.abspath('inventaires/inventaire_46-BPNL.db')

LOG = os.path.abspath('reports/merge_session_log.txt')

def compute_hash(path, chunk=65536):
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while True:
                d = f.read(chunk)
                if not d: break
                h.update(d)
        return h.hexdigest()
    except OSError:
        return None

def log(msg):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Charger les hashes deja presents dans PROJETS (depuis la base)
conn = sqlite3.connect(DB)
projets_hashes = set(r[0] for r in conn.execute(
    "SELECT hash_md5 FROM files WHERE path LIKE '%PROJETS%' AND hash_md5 IS NOT NULL"
).fetchall())
session_files = conn.execute(
    "SELECT path, hash_md5, size FROM files WHERE path LIKE '%SESSION%'"
).fetchall()
conn.close()

to_copy = [(p, h, s) for p, h, s in session_files if h not in projets_hashes]
to_skip  = len(session_files) - len(to_copy)

log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Fusion SESSION -> PROJETS")
log(f"  Fichiers SESSION total : {len(session_files):,}")
log(f"  Deja dans PROJETS (skip) : {to_skip:,}")
log(f"  A copier (uniques)      : {len(to_copy):,}")
log("")

copied = 0
errors = 0

for src_path, h, size in sorted(to_copy, key=lambda x: -x[2]):
    # Reconstruire le chemin destination : remplacer SESSION par PROJETS
    rel = src_path[len(SESSION):]
    dst_path = PROJETS + rel

    log(f"  COPIE {size/1024**2:.1f} Mo : {os.path.basename(src_path)}")
    log(f"    src: {src_path}")
    log(f"    dst: {dst_path}")

    if not DRY_RUN:
        try:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            # Verifier le hash apres copie
            dst_hash = compute_hash(dst_path)
            if dst_hash == h:
                log(f"    => OK (hash verifie)")
                copied += 1
            else:
                log(f"    => ERREUR hash mismatch !")
                errors += 1
        except Exception as e:
            log(f"    => ERREUR : {e}")
            errors += 1
    else:
        copied += 1

log("")
log(f"  Copies {'simulees' if DRY_RUN else 'effectuees'} : {copied:,}")
log(f"  Erreurs : {errors:,}")

# Suppression de SESSION
if not DRY_RUN and errors == 0:
    log(f"\n  Suppression de SESSION...")
    try:
        shutil.rmtree(SESSION)
        log(f"  => SESSION supprime avec succes.")
    except Exception as e:
        log(f"  => ERREUR suppression : {e}")
elif DRY_RUN:
    log("\n[DRY-RUN] Aucune action effectuee. Relancez avec --delete pour executer.")
elif errors > 0:
    log(f"\n  ATTENTION : {errors} erreurs detectees. SESSION non supprime par securite.")
