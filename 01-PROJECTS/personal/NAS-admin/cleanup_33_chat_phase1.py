"""
Nettoyage 33-TUNNEL DU CHAT — Phase 1
Suppression des dossiers 100% inclus dans d'autres.

Étape A : Suppression directe (inclusions 100% vérifiées)
  - TUNNEL DU CHAT - 2017  (copie de 03-tunnel chat, 31.8 Go)
  - rep pytha scooter ordi chat  (copie de 99-olivier)
  - 10-Tunnel du Chat  (copie de 20150904-CHAT)
  - 01-donnees avant projet 2017- PAUL & LUDO & TMS
      (copie de TUNNEL DU CHAT - 2017 - 19mai2017)

Étape B : Inclusions quasi-totales — déplacer les fichiers manquants
          puis supprimer le dossier source
  - 21-travaux-bureau-proj → 99-olivier (2 manquants)
  - 70-sauvegardes cartes TPS1200 → carte tps 170615 (1 manquant)
  - Migration TMS Amberg chat → LUDO (7 manquants)
  - LUDO → 01-donnees avant projet 2017... (4 manquants)
    NOTE: 01-donnees... sera supprimé à l'étape A,
    donc LUDO doit être fusionné dans TUNNEL DU CHAT - 2017 - 19mai2017

Usage :
    python cleanup_33_chat_phase1.py            → dry-run
    python cleanup_33_chat_phase1.py --apply    → exécution réelle
"""
import sys, os, shutil, sqlite3

DRY_RUN = '--apply' not in sys.argv
BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-TUNNEL DU CHAT'
LOG  = os.path.abspath('reports/cleanup_33_chat_phase1_log.txt')
DB   = r'inventaires/inventaire_33-TUNNEL DU CHAT.db'

def log(msg=''):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def do_move(src, dst):
    if DRY_RUN:
        log(f"  [DRY] MOVE  {os.path.relpath(src, BASE)}")
        log(f"           →  {os.path.relpath(dst, BASE)}")
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        log(f"  MOVE  {os.path.relpath(src, BASE)}")
        log(f"     →  {os.path.relpath(dst, BASE)}")

def do_rmtree(path, reason=''):
    rel = os.path.relpath(path, BASE)
    if DRY_RUN:
        # Compter les fichiers et la taille
        n = sum(len(f) for _, _, f in os.walk(path))
        sz = sum(os.path.getsize(os.path.join(r, f))
                 for r, _, fs in os.walk(path) for f in fs)
        log(f"  [DRY] RMTREE {rel}  ({n} fichiers, {sz/1024**3:.1f} Go)  {reason}")
    else:
        shutil.rmtree(path)
        log(f"  RMTREE {rel}  {reason}")


# ── Init ─────────────────────────────────────────────────────────────────
open(LOG, 'w', encoding='utf-8').close()
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Nettoyage 33-TUNNEL DU CHAT — Phase 1")
log('=' * 72)
log()

cnt = {'rmtree': 0, 'moved': 0, 'go_freed': 0}


# ════════════════════════════════════════════════════════════════════════
# B) D'abord : fusionner les fichiers manquants des quasi-inclus
#    (avant de supprimer les dossiers en A)
# ════════════════════════════════════════════════════════════════════════

log("B) Fusion des fichiers manquants avant suppression")
log('─' * 72)

# B1: 21-travaux-bureau-proj → 99-olivier
#     Manquants: 113TE7~D.PDF, Thumbs.db
for fn in ['113TE7~D.PDF', 'Thumbs.db']:
    # Chercher le fichier dans 21-travaux-bureau-proj
    src_dir = os.path.join(BASE, '21-travaux-bureau-proj')
    for r, d, files in os.walk(src_dir):
        if fn in files:
            src = os.path.join(r, fn)
            # Chemin relatif dans le dossier source
            rel_in = os.path.relpath(src, src_dir)
            dst = os.path.join(BASE, '99-olivier', rel_in)
            if not os.path.exists(dst):
                do_move(src, dst)
                cnt['moved'] += 1
            else:
                log(f"  SKIP (existe déjà) : 99-olivier\\{rel_in}")
            break

log()

# B2: 70-sauvegardes cartes TPS1200 → carte tps 170615
#     Manquant: taskDump.txt
src_dir = os.path.join(BASE, '70-sauvegardes cartes TPS1200')
for r, d, files in os.walk(src_dir):
    if 'taskDump.txt' in files:
        src = os.path.join(r, 'taskDump.txt')
        rel_in = os.path.relpath(src, src_dir)
        dst = os.path.join(BASE, 'carte tps 170615', rel_in)
        if not os.path.exists(dst):
            do_move(src, dst)
            cnt['moved'] += 1
        else:
            log(f"  SKIP (existe déjà) : carte tps 170615\\{rel_in}")
        break

log()

# B3: Migration TMS Amberg chat → LUDO (7 manquants)
missing_migration = [
    'CHAT-TunRoutier2.xml',
    'thprof_ligne R 0001.dxf',
    'thprof_ligne S 00010002.dxf',
    'thprof_ligne_R0001.txt',
    'thprof_ligne_S00010002.txt',
    'chat-polygoRoutierR2.XCF',
    'routier2.LPR',
]
src_dir = os.path.join(BASE, 'Migration TMS Amberg chat')
for fn in missing_migration:
    for r, d, files in os.walk(src_dir):
        if fn in files:
            src = os.path.join(r, fn)
            rel_in = os.path.relpath(src, src_dir)
            dst = os.path.join(BASE, 'LUDO', rel_in)
            if not os.path.exists(dst):
                do_move(src, dst)
                cnt['moved'] += 1
            else:
                log(f"  SKIP (existe déjà) : LUDO\\{rel_in}")
            break

log()

# B4: LUDO → TUNNEL DU CHAT - 2017 - 19mai2017 (4 manquants)
#     (car 01-donnees... sera supprimé en A, donc LUDO fusionne directement
#      dans le dossier qui survit : TUNNEL DU CHAT - 2017 - 19mai2017)
missing_ludo = ['rameau1.PJD', 'rameau1.TPD', 'rameau2.PJD', 'rameau2.TPD']
src_dir = os.path.join(BASE, 'LUDO')
dst_base = os.path.join(BASE, 'TUNNEL DU CHAT - 2017 - 19mai2017')
for fn in missing_ludo:
    for r, d, files in os.walk(src_dir):
        if fn in files:
            src = os.path.join(r, fn)
            rel_in = os.path.relpath(src, src_dir)
            # Place dans LUDO/ sous-dossier de la destination
            dst = os.path.join(dst_base, 'LUDO', rel_in)
            if not os.path.exists(dst):
                do_move(src, dst)
                cnt['moved'] += 1
            else:
                log(f"  SKIP (existe déjà)")
            break

log()
log(f"  → Fichiers fusionnés : {cnt['moved']}")
log()


# ════════════════════════════════════════════════════════════════════════
# A) Suppression des dossiers 100% inclus (+ quasi-inclus après fusion)
# ════════════════════════════════════════════════════════════════════════

log("A) Suppression des dossiers doublons")
log('─' * 72)

to_delete = [
    ('TUNNEL DU CHAT - 2017',               'doublon de 03-tunnel chat'),
    ('rep pytha scooter ordi chat',          'doublon de 99-olivier'),
    ('10-Tunnel du Chat',                    'doublon de 20150904-CHAT'),
    ('01-donnees avant projet 2017- PAUL & LUDO & TMS',
                                             'doublon de TUNNEL DU CHAT - 2017 - 19mai2017'),
    ('21-travaux-bureau-proj',               'fusionné dans 99-olivier'),
    ('70-sauvegardes cartes TPS1200',        'fusionné dans carte tps 170615'),
    ('Migration TMS Amberg chat',            'fusionné dans LUDO'),
    ('LUDO',                                 'fusionné dans TUNNEL DU CHAT - 2017 - 19mai2017'),
]

for dirname, reason in to_delete:
    path = os.path.join(BASE, dirname)
    if os.path.exists(path):
        do_rmtree(path, f'({reason})')
        cnt['rmtree'] += 1
    else:
        log(f"  SKIP (introuvable) : {dirname}")

log()


# ── Résumé ────────────────────────────────────────────────────────────────
log('=' * 72)
log("RÉSUMÉ")
log('=' * 72)
log(f"  Fichiers fusionnés avant suppression : {cnt['moved']}")
log(f"  Dossiers supprimés : {cnt['rmtree']}")
if DRY_RUN:
    log()
    log("  → relancer avec --apply pour exécuter")
