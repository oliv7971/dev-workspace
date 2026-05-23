"""
Réorganisation de 00-DONNEES-BRUTES-CANAL — phase 3 :
  Corrections des incohérences internes.

Opérations :
  A) Déplacer les données bassin central égarées dans renaison_canal_evacuateur/
       → renaison_bassinCentral.CFG/.PJD/_BStore.xml  →  RENAISON 2015/BASSIN CENTRAL/
       → scan/RENAISON 20150617/ (7 archives .zfs brutes bassin central)
         → RENAISON 2015/BASSIN CENTRAL/00-DONNEES-BRUTES/
       → 3 dossiers vides (renaison_bassinCentral.1/, Setoutrenaison_bassinCentral/,
         Setoutrenaison_canalEV/) → supprimés

  B) Déduplication scan/renaison 20150401/ vs 02-SCANS/
       25 fichiers .PTS de scan/ confirmés doublons MD5 de 02-SCANS/ → supprimés.
       Résidus (ErrorLog.txt, LatestFSStagerScript.xml) → supprimés car fichiers
       de log/config sans valeur archivistique.
       scan/ vide à la fin → supprimé.

Usage :
    python reorg_09_renaison3.py           → dry-run
    python reorg_09_renaison3.py --apply   → exécution réelle
"""
import sys, os, shutil, sqlite3

DRY_RUN = '--apply' not in sys.argv
BASE09  = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON'
BASE15  = os.path.join(BASE09, 'RENAISON 2015')
BASSIN  = os.path.join(BASE15, 'BASSIN CENTRAL')
CANAL   = os.path.join(BASE09, r'RENAISON 2015\00-DONNEES-BRUTES-CANAL\renaison_canal_evacuateur')
LOG     = os.path.abspath('reports/reorg_09_renaison3_log.txt')
DB      = r'inventaires/inventaire_09-BARRAGES RENAISON.db'

# MD5 confirmés en amont (via _tmp_pts_dedup.py)
PTS_DUPLICATES = {
    'AMTP5003_20150401093336_5030_0.zfs.PTS',
    'AMTP5003_20150401094312_5050_0.zfs.PTS',
    'AMTP5003_20150401095115_5070_0.zfs.PTS',
    'AMTP5003_20150401100255_5095_0.zfs.PTS',
    'AMTP5003_20150401112323_4010_0.zfs.PTS',
    'AMTP5003_20150401113722_6000_0.zfs.PTS',
    'AMTP5003_20150401114322_6010_0.zfs.PTS',
    'AMTP5003_20150401115108_6020_0.zfs.PTS',
    'AMTP5003_20150401120044_6030_0.zfs.PTS',
    'AMTP5003_20150401121155_6040_0.zfs.PTS',
    'AMTP5003_20150401122156_6050_0.zfs.PTS',
    'AMTP5003_20150401123031_6060_0.zfs.PTS',
    'AMTP5003_20150401133946_6070_0.zfs.PTS',
    'AMTP5003_20150401134557_6080_0.zfs.PTS',
    'AMTP5003_20150401135218_6090_0.zfs.PTS',
    'AMTP5003_20150401140250_6095_0.zfs.PTS',
    'AMTP5003_20150401142531_6110_0.zfs.PTS',
    'AMTP5003_20150401144350_6120_0.zfs.PTS',
    'AMTP5003_20150401151110_6140_0.zfs.PTS',
    'AMTP5003_20150401165301_6150_0.zfs.PTS',
    'AMTP5003_20150401170336_6170_0.zfs.PTS',
    'AMTP5003_20150401180747_6180_0.zfs.PTS',
    'AMTP5003_20150401181416_6181_0.zfs.PTS',
    'AMTP5003_20150401183046_6200_0.zfs.PTS',
    'AMTP5003_20150401184724_6230_0.zfs.PTS',
}

# Résidus sans valeur à supprimer dans scan/
SCAN_JUNK = {'ErrorLog.txt', 'LatestFSStagerScript.xml'}


def log(msg=''):
    print(msg)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


def do_move(src, dst):
    if DRY_RUN:
        log(f"  [DRY] MOVE  {os.path.relpath(src, BASE09)}")
        log(f"           →  {os.path.relpath(dst, BASE09)}")
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        log(f"  MOVE  {os.path.relpath(src, BASE09)}")
        log(f"     →  {os.path.relpath(dst, BASE09)}")


def do_delete(path, reason=''):
    if DRY_RUN:
        log(f"  [DRY] DEL   {os.path.relpath(path, BASE09)}  {reason}")
    else:
        os.remove(path)
        log(f"  DEL   {os.path.relpath(path, BASE09)}  {reason}")


def do_rmdir(path, reason=''):
    if DRY_RUN:
        log(f"  [DRY] RMDIR {os.path.relpath(path, BASE09)}  {reason}")
    else:
        if os.path.isdir(path) and not os.listdir(path):
            os.rmdir(path)
            log(f"  RMDIR {os.path.relpath(path, BASE09)}  {reason}")
        elif os.path.isdir(path):
            log(f"  SKIP RMDIR (non vide) {os.path.relpath(path, BASE09)}")


def remove_empty_tree(folder):
    """Supprime récursivement les dossiers vides (bottom-up)."""
    for dirpath, _, _ in os.walk(folder, topdown=False):
        if os.path.isdir(dirpath) and not os.listdir(dirpath):
            do_rmdir(dirpath)


# ── Init log ─────────────────────────────────────────────────────────────────

open(LOG, 'w', encoding='utf-8').close()
log(f"{'[DRY-RUN] ' if DRY_RUN else ''}Réorganisation 09 — phase 3 : corrections internes")
log('=' * 72)
log()

cnt = {'move_a': 0, 'rmdir_a': 0, 'del_b': 0}


# ════════════════════════════════════════════════════════════════════════════
# A1) Fichiers projet Cyclone bassin central à la racine
# ════════════════════════════════════════════════════════════════════════════

log("A1) Fichiers projet Cyclone bassin central → RENAISON 2015/BASSIN CENTRAL/")
log('─' * 72)

for fn in ['renaison_bassinCentral.CFG', 'renaison_bassinCentral.PJD',
           'renaison_bassinCentral_BStore.xml']:
    src = os.path.join(CANAL, fn)
    dst = os.path.join(BASSIN, fn)
    if not os.path.exists(src):
        log(f"  SKIP (introuvable) : {fn}")
        continue
    if os.path.exists(dst):
        log(f"  SKIP (conflit) : {fn} existe déjà dans BASSIN CENTRAL/")
    else:
        do_move(src, dst)
        cnt['move_a'] += 1

log()


# ════════════════════════════════════════════════════════════════════════════
# A2) Archives brutes bassin central (scan/RENAISON 20150617/)
#     → BASSIN CENTRAL/00-DONNEES-BRUTES/
# ════════════════════════════════════════════════════════════════════════════

log("A2) Archives brutes bassin central scan/RENAISON 20150617/ → BASSIN CENTRAL/00-DONNEES-BRUTES/")
log('─' * 72)

src_617 = os.path.join(CANAL, 'scan', 'RENAISON 20150617')
dst_617 = os.path.join(BASSIN, '00-DONNEES-BRUTES', 'RENAISON 20150617')

if not os.path.exists(src_617):
    log("  SKIP — scan/RENAISON 20150617/ introuvable")
elif os.path.exists(dst_617):
    log("  SKIP — BASSIN CENTRAL/00-DONNEES-BRUTES/RENAISON 20150617/ existe déjà")
else:
    do_move(src_617, dst_617)
    cnt['move_a'] += 1

log()


# ════════════════════════════════════════════════════════════════════════════
# A3) Dossiers vides bassin central → suppression
# ════════════════════════════════════════════════════════════════════════════

log("A3) Dossiers vides bassin central → suppression")
log('─' * 72)

for sub in ['renaison_bassinCentral.1', 'Setoutrenaison_bassinCentral', 'Setoutrenaison_canalEV']:
    path = os.path.join(CANAL, sub)
    if not os.path.exists(path):
        log(f"  SKIP (introuvable) : {sub}/")
        continue
    total_files = sum(len(f) for _, _, f in os.walk(path))
    if total_files > 0:
        log(f"  SKIP (non vide : {total_files} fichiers) : {sub}/")
    else:
        do_rmdir(path, '(vide)')
        cnt['rmdir_a'] += 1

log()


# ════════════════════════════════════════════════════════════════════════════
# B) Suppression des doublons dans scan/renaison 20150401/
#    + résidus dans scan/
# ════════════════════════════════════════════════════════════════════════════

log("B) Suppression des doublons .PTS et résidus de scan/")
log('─' * 72)

scan_dir = os.path.join(CANAL, 'scan')
if not os.path.exists(scan_dir):
    log("  SKIP — scan/ introuvable")
else:
    scan_avr = os.path.join(scan_dir, 'renaison 20150401')

    # B1 : doublons .PTS
    if os.path.exists(scan_avr):
        for fn in sorted(os.listdir(scan_avr)):
            fp = os.path.join(scan_avr, fn)
            if not os.path.isfile(fp):
                continue
            if fn in PTS_DUPLICATES:
                do_delete(fp, '(doublon MD5 confirmé de 02-SCANS/)')
                cnt['del_b'] += 1
            elif fn in SCAN_JUNK:
                do_delete(fp, '(résidu de log/config)')
                cnt['del_b'] += 1
            else:
                log(f"  INCONNU (conservé) : renaison 20150401/{fn}")
    else:
        log("  SKIP — scan/renaison 20150401/ introuvable")

    log()

    # B2 : résidus à la racine de scan/
    for fn in sorted(os.listdir(scan_dir)):
        fp = os.path.join(scan_dir, fn)
        if os.path.isfile(fp) and fn in SCAN_JUNK:
            do_delete(fp, '(résidu de log/config)')
            cnt['del_b'] += 1

    # B3 : supprimer scan/ si sera vide
    log()
    if not DRY_RUN:
        remove_empty_tree(scan_dir)
    else:
        n = sum(len(f2) for _, _, f2 in os.walk(scan_dir))
        net = n - cnt['del_b']
        log(f"  [DRY] scan/ : {n} fichiers présents, {cnt['del_b']} seront supprimés → {max(0, net)} resteront")
        if net <= 0:
            log("  [DRY] RMDIR scan/ (sera entièrement vide)")

log()


# ── Résumé ────────────────────────────────────────────────────────────────────

log('=' * 72)
log("RÉSUMÉ")
log('=' * 72)
log(f"  A) Fichiers/dossiers bassin central déplacés : {cnt['move_a']}")
log(f"  A) Dossiers vides supprimés : {cnt['rmdir_a']}")
log(f"  B) Doublons/résidus scan/ supprimés : {cnt['del_b']}")
if DRY_RUN:
    log()
    log("  → relancer avec --apply pour exécuter")
