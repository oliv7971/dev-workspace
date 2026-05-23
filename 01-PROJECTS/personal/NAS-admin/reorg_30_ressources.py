#!/usr/bin/env python3
"""
reorg_30_ressources.py
Réorganisation de 30-RESSOURCES :

  A) Résoudre les conflits de numérotation
     - 30-mode d'emploi  (doublon de 30-TECHNOLOGIES)
       → contenu déplacé dans 81-modes d'emploi  (même thème)
     - 31-documentation  (doublon de 31-ELECTROTECHNIQUE, contenu divers)
       → contenu déplacé dans RESSOURCES A CLASSER

  B) Renommer RESSOURCES A CLASSER → 90-a_classer

  C) Ranger les éléments orphelins à la racine
     - menutopo/ → 01-TOPOGRAPHIE/menutopo
     - *.pdf      → 01-TOPOGRAPHIE/

  D) Harmoniser la casse des noms de dossiers
     - 14-bureautique        → 14-BUREAUTIQUE
     - 41-immobilier         → 41-IMMOBILIER
     - 45-voitures           → 45-VOITURES
     - 81-modes d'emploi     → 81-MODES-EMPLOI  (après fusion A)

Usage:
    python reorg_30_ressources.py          # dry-run
    python reorg_30_ressources.py --apply  # exécution réelle
"""

import os, sys, io, shutil, logging
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE  = Path(r"\\Nas_louhans_2\01-ds420-data\30-RESSOURCES")
APPLY = "--apply" in sys.argv

LOG_FILE = Path("reports/reorg_30_ressources_log.txt")
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger()

log.info("=== MODE EXECUTION ===" if APPLY else "=== DRY-RUN — relancer avec --apply ===")
log.info(f"Dossier : {BASE}\n")

counters = {"move": 0, "rename": 0, "skip": 0, "err": 0}


def move_contents(src: Path, dst: Path, label: str):
    """Déplace le contenu de src dans dst (pas le dossier lui-même)."""
    if not src.exists():
        log.warning(f"  SKIP (introuvable) : {src.name}")
        counters["skip"] += 1
        return
    dst.mkdir(parents=True, exist_ok=True) if APPLY else None
    try:
        items = list(src.iterdir())
    except Exception as e:
        log.error(f"  ERREUR listage {src}: {e}")
        return
    if not items:
        log.info(f"  {label} : dossier vide, rien à déplacer")
        return
    for item in items:
        dst_item = dst / item.name
        if dst_item.exists():
            log.warning(f"  CONFLIT  {item.name}  (existe déjà dans dst)")
            counters["skip"] += 1
            continue
        log.info(f"  MOVE  {src.name}/{item.name}")
        log.info(f"        --> {dst.name}/{item.name}")
        counters["move"] += 1
        if APPLY:
            try:
                shutil.move(str(item), str(dst_item))
            except Exception as e:
                log.error(f"  ERREUR : {e}")
                counters["err"] += 1
                counters["move"] -= 1
    # Supprimer le dossier src s'il est vide après déplacement
    if APPLY:
        try:
            remaining = list(src.iterdir())
            if not remaining:
                src.rmdir()
                log.info(f"  RMDIR  {src.name}  (vide après déplacement)")
            else:
                log.warning(f"  ATTENTION : {src.name} non vide après déplacement ({len(remaining)} éléments restants)")
        except Exception as e:
            log.error(f"  ERREUR suppression dossier vide {src}: {e}")


def move_item(src: Path, dst: Path, label: str):
    """Déplace src (fichier ou dossier) vers dst."""
    if not src.exists():
        log.warning(f"  SKIP (introuvable) : {src.name}")
        counters["skip"] += 1
        return
    if dst.exists():
        log.warning(f"  CONFLIT  {src.name}  (destination existe déjà)")
        counters["skip"] += 1
        return
    log.info(f"  MOVE  {label}")
    log.info(f"        {src.relative_to(BASE)}  -->  {dst.relative_to(BASE)}")
    counters["move"] += 1
    if APPLY:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        except Exception as e:
            log.error(f"  ERREUR : {e}")
            counters["err"] += 1
            counters["move"] -= 1


def rename_dir(src: Path, new_name: str, label: str):
    """Renomme un dossier."""
    if not src.exists():
        log.warning(f"  SKIP (introuvable) : {src.name}")
        counters["skip"] += 1
        return
    dst = src.parent / new_name
    if dst.exists():
        log.warning(f"  CONFLIT renommage : {new_name} existe déjà")
        counters["skip"] += 1
        return
    log.info(f"  RENAME  {src.name}  -->  {new_name}  ({label})")
    counters["rename"] += 1
    if APPLY:
        try:
            src.rename(dst)
        except Exception as e:
            log.error(f"  ERREUR : {e}")
            counters["err"] += 1
            counters["rename"] -= 1


# ══════════════════════════════════════════════════════════════════════════════
# A) Résoudre les conflits de numérotation
# ══════════════════════════════════════════════════════════════════════════════
log.info("=" * 70)
log.info("A) Résolution conflits de numérotation")
log.info("=" * 70)

# 30-mode d'emploi → contenu vers 81-modes d'emploi
log.info("\n  [30-mode d'emploi] → contenu vers [81-modes d'emploi]")
move_contents(
    src=BASE / "30-mode d'emploi",
    dst=BASE / "81-modes d'emploi",
    label="30-mode d'emploi"
)

# 31-documentation → contenu vers RESSOURCES A CLASSER
log.info("\n  [31-documentation] → contenu vers [RESSOURCES A CLASSER]")
move_contents(
    src=BASE / "31-documentation",
    dst=BASE / "RESSOURCES A CLASSER",
    label="31-documentation"
)

# ══════════════════════════════════════════════════════════════════════════════
# B) Renommer RESSOURCES A CLASSER → 90-a_classer
# ══════════════════════════════════════════════════════════════════════════════
log.info("\n" + "=" * 70)
log.info("B) Renommage RESSOURCES A CLASSER → 90-a_classer")
log.info("=" * 70 + "\n")
rename_dir(BASE / "RESSOURCES A CLASSER", "90-a_classer", "a_classer standard")

# ══════════════════════════════════════════════════════════════════════════════
# C) Ranger les orphelins à la racine
# ══════════════════════════════════════════════════════════════════════════════
log.info("\n" + "=" * 70)
log.info("C) Ranger les éléments orphelins à la racine")
log.info("=" * 70 + "\n")

topo = BASE / "01-TOPOGRAPHIE"

# menutopo/ → 01-TOPOGRAPHIE/menutopo
move_item(
    src=BASE / "menutopo",
    dst=topo / "menutopo",
    label="menutopo → 01-TOPOGRAPHIE"
)

# PDFs à la racine → 01-TOPOGRAPHIE
for f in BASE.iterdir() if BASE.exists() else []:
    if f.is_file() and f.suffix.lower() == ".pdf":
        move_item(src=f, dst=topo / f.name, label=f"PDF racine → 01-TOPOGRAPHIE")

# ══════════════════════════════════════════════════════════════════════════════
# D) Harmoniser la casse
# ══════════════════════════════════════════════════════════════════════════════
log.info("\n" + "=" * 70)
log.info("D) Harmonisation de la casse")
log.info("=" * 70 + "\n")

renames = [
    ("14-bureautique",    "14-BUREAUTIQUE",   "casse"),
    ("41-immobilier",     "41-IMMOBILIER",    "casse"),
    ("45-voitures",       "45-VOITURES",      "casse"),
    ("81-modes d'emploi", "81-MODES-EMPLOI",  "casse + tiret"),
]
for old, new, reason in renames:
    rename_dir(BASE / old, new, reason)

# ══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ
# ══════════════════════════════════════════════════════════════════════════════
log.info("\n" + "=" * 70)
log.info("RÉSUMÉ")
log.info("=" * 70)
action = "effectués" if APPLY else "prévus"
log.info(f"  Déplacements {action}  : {counters['move']}")
log.info(f"  Renom. {action}        : {counters['rename']}")
log.info(f"  Ignorés / conflits     : {counters['skip']}")
log.info(f"  Erreurs                : {counters['err']}")
log.info("")
