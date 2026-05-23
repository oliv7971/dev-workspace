"""
Réorganisation de 09-BARRAGES RENAISON.

La structure actuelle est organisée par année (RENAISON 2012 ... RENAISON 2023).
Ce script range les dossiers orphelins restés à la racine :

  Vers RENAISON 2022/  (éléments clairement datés 2022) :
    SESSION MAI 2022            → RENAISON 2022/SESSION MAI 2022
                                  (RENAISON 2022/SESSION MAI 2022_racine si conflit)
    SESSION JUIN 2022           → RENAISON 2022/SESSION JUIN 2022
                                  (RENAISON 2022/SESSION JUIN 2022_racine si conflit)
    CCTP                        → RENAISON 2022/CCTP
                                  (RENAISON 2022/CCTP_racine si conflit)
    ZEnvoi à OB & RG 06-04-22  → RENAISON 2022/ZEnvoi à OB & RG 06-04-22
    _recu de FAbrice            → RENAISON 2022/_recu de FAbrice
                                  (+ _racine si conflit)
    EXPLICATIONS ROUCHAIN CHARTRAIN → RENAISON 2022/EXPLICATIONS ROUCHAIN CHARTRAIN

  Vers RENAISON 2012/  (données de terrain oct2012 + sept2014) :
    renaison monitoring         → RENAISON 2012/renaison monitoring

  Suppressions :
    Thumbs.db (racine)

  À faire manuellement (trop gros / incertains) :
    12-BARRAGE RENAISON  (37 Go – canal évacuateur, chevauchement RENAISON 2015)
    SCANS                (37.6 Go – gros exports mesh/ptx sans année claire)
    _a_classer           (4.7 Go – documents divers à trier)

Usage :
    python reorg_09_renaison.py           → dry-run (aperçu)
    python reorg_09_renaison.py --apply   → exécution réelle
"""
import sys, os, shutil

DRY_RUN = '--apply' not in sys.argv
BASE    = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON'
LOG     = os.path.abspath('reports/reorg_09_renaison_log.txt')

# Mapping : chemin_source_relatif -> chemin_destination_relatif (dans BASE)
# Si la destination existe déjà, le script ajoute un suffixe _racine.
MAPPING = {
    # --- Vers RENAISON 2022 ---
    'SESSION MAI 2022':               r'RENAISON 2022\SESSION MAI 2022',
    'SESSION JUIN 2022':              r'RENAISON 2022\SESSION JUIN 2022',
    'CCTP':                           r'RENAISON 2022\CCTP',
    'ZEnvoi à OB & RG 06-04-22':     r'RENAISON 2022\ZEnvoi à OB & RG 06-04-22',
    '_recu de FAbrice':               r'RENAISON 2022\_recu de FAbrice',
    'EXPLICATIONS ROUCHAIN CHARTRAIN': r'RENAISON 2022\EXPLICATIONS ROUCHAIN CHARTRAIN',

    # --- Vers RENAISON 2012 ---
    'renaison monitoring':            r'RENAISON 2012\renaison monitoring',
}

# Fichiers à supprimer (chemins relatifs depuis BASE)
DELETE = [
    'Thumbs.db',
]

# Dossiers à signaler (trop gros / ambigus)
MANUAL = {
    '12-BARRAGE RENAISON': '37 Go — canal évacuateur, chevauchement avec RENAISON 2015/CANAL EVACUATEUR',
    'SCANS':               '37.6 Go — exports mesh/ptx sans année identifiée',
    '_a_classer':          '4.7 Go — documents divers, à trier manuellement',
}


# ── Utilitaires ─────────────────────────────────────────────────────────────

def log(msg=''):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def do_move(src, dst):
    """Déplace src vers dst (crée le dossier parent si nécessaire)."""
    if DRY_RUN:
        log(f"  [DRY] MOVE  {src}")
        log(f"           →  {dst}")
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        log(f"  MOVE  {os.path.basename(src)}")
        log(f"     →  {dst}")

def do_delete(path):
    if DRY_RUN:
        log(f"  [DRY] DEL   {path}")
    else:
        os.remove(path)
        log(f"  DEL   {path}")


# ── Initialisation du log ────────────────────────────────────────────────────

open(LOG, 'w', encoding='utf-8').close()
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Réorganisation 09-BARRAGES RENAISON")
log('=' * 70)
log(f"  Base : {BASE}")
log()


# ── A) Déplacements ──────────────────────────────────────────────────────────

log("A) Déplacements des orphelins à la racine")
log('-' * 70)

moved = skipped = 0

for src_rel, dst_rel in MAPPING.items():
    src = os.path.join(BASE, src_rel)
    dst = os.path.join(BASE, dst_rel)

    if not os.path.exists(src):
        log(f"  SKIP (introuvable) : {src_rel}")
        skipped += 1
        continue

    # Gérer les conflits : si la destination existe déjà, ajouter _racine
    if os.path.exists(dst):
        dst_racine = dst + '_racine'
        log(f"  CONFLIT : {dst_rel} existe déjà")
        log(f"            → renommage destination en {os.path.basename(dst_racine)}")
        dst = dst_racine
        dst_rel = dst_rel + '_racine'

    do_move(src, dst)
    moved += 1
    log()

log()


# ── B) Suppressions ──────────────────────────────────────────────────────────

log("B) Suppressions")
log('-' * 70)

deleted = 0
for rel in DELETE:
    path = os.path.join(BASE, rel)
    if os.path.exists(path):
        do_delete(path)
        deleted += 1
    else:
        log(f"  SKIP (introuvable) : {rel}")

log()


# ── C) Éléments à traiter manuellement ───────────────────────────────────────

log("C) Dossiers à examiner manuellement (non touchés)")
log('-' * 70)
for nom, raison in MANUAL.items():
    path = os.path.join(BASE, nom)
    exists = os.path.exists(path)
    log(f"  {'[présent]' if exists else '[ABSENT]':10s} {nom}")
    log(f"             {raison}")
    log()


# ── Résumé ────────────────────────────────────────────────────────────────────

log('=' * 70)
log("RÉSUMÉ")
log('=' * 70)
log(f"  Déplacements {'simulés' if DRY_RUN else 'effectués'} : {moved}")
log(f"  Ignorés (introuvables) : {skipped}")
log(f"  Suppressions           : {deleted}")
if DRY_RUN:
    log()
    log("  → relancer avec --apply pour exécuter")
