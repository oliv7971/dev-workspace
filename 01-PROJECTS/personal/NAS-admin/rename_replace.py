#!/usr/bin/env python3
"""
rename_replace.py
Parcourt recursivement un dossier et renomme fichiers/dossiers
en remplacant des chaines de caracteres dans leurs noms.

CONFIGURER :
  - BASE     : dossier racine a parcourir
  - REPLACEMENTS : liste de (chaine_a_remplacer, remplacement)
                   mettre "" comme remplacement pour supprimer la chaine

Usage:
    python rename_replace.py          # dry-run (simulation)
    python rename_replace.py --apply  # execution reelle
"""

import os
import re
import sys
import logging
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\40-VIDEOS")

# Liste des remplacements : (pattern, remplacement, is_regex)
# - is_regex=True  : pattern est une expression reguliere (re.sub)
# - is_regex=False : remplacement de chaine simple
# Les remplacements sont appliques dans l'ordre sur chaque nom.
REPLACEMENTS = [
    # Supprime tout ce qui est entre parentheses (et les parentheses elles-memes)
    # MAIS conserve les annees (YYYY) seules ex: "(2004)" reste intact
    # ex: "titre (HD)" --> "titre ", "film (360p)" --> "film ", "film (2004)" --> "film (2004)"
    (r'\s*\((?!\d{4}\))[^)]*\)', "", True),

    # Supprime tout ce qui est entre crochets (et les crochets eux-memes)
    # ex: "video [720p]" --> "video ", "film [FRENCH]" --> "film "
    (r'\s*\[[^\]]*\]', "", True),

    # Remplace les espaces multiples par un seul espace (nettoyage apres suppression)
    (r'  +', " ", True),

    # Supprime les espaces en debut/fin de nom (avant l'extension)
    # Note : gere dans apply_replacements via .strip()
]

# Types d'elements a renommer
RENAME_FILES   = True   # renommer les fichiers
RENAME_FOLDERS = True   # renommer les dossiers

# ──────────────────────────────────────────────────────────────────────────────

APPLY = "--apply" in sys.argv

LOG_FILE = Path("reports/rename_replace_log.txt")
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
    ],
)
log = logging.getLogger()

if not REPLACEMENTS:
    log.error("ERREUR: La liste REPLACEMENTS est vide. Configurez les remplacements dans le script.")
    sys.exit(1)

if APPLY:
    log.info("=== MODE EXECUTION ===")
else:
    log.info("=== DRY-RUN (simulation) — relancer avec --apply pour executer ===")

log.info(f"\nDossier : {BASE}")
log.info(f"Remplacements configures :")
for old, new, is_re in REPLACEMENTS:
    label = f'"{new}"' if new else '(suppression)'
    kind  = '[regex]' if is_re else '[texte]'
    log.info(f"  {kind} '{old}'  -->  {label}")
log.info("")


def apply_replacements(name: str) -> str:
    """Applique tous les remplacements sur un nom (stem seulement, sans extension)."""
    p = Path(name)
    # Separer stem et suffixe pour ne pas toucher l'extension
    stem = p.stem
    suffix = p.suffix  # ex: ".mp4", "" pour les dossiers

    result = stem
    for old, new, is_re in REPLACEMENTS:
        if is_re:
            result = re.sub(old, new, result)
        else:
            result = result.replace(old, new)
    result = result.strip()
    return result + suffix


def collect_entries(base: Path) -> list[tuple[Path, bool]]:
    """
    Collecte tous les fichiers et dossiers recursivement.
    Retourne une liste triee : fichiers d'abord (feuilles), puis dossiers du
    plus profond au moins profond (bottom-up) pour eviter les conflits de chemins.
    """
    files = []
    dirs  = []
    for root, subdirs, filenames in os.walk(base, topdown=False):
        root_path = Path(root)
        if root_path == base:
            continue  # ne pas renommer la racine elle-meme
        if RENAME_FILES:
            for f in filenames:
                files.append((root_path / f, False))
        if RENAME_FOLDERS:
            # bottom-up grace a topdown=False
            dirs.append((root_path, True))
    return files + dirs


log.info("=" * 70)
counters = {"renamed": 0, "skip_unchanged": 0, "skip_conflict": 0, "err": 0}

entries = collect_entries(BASE)
log.info(f"{len(entries)} elements analyses\n")

for path, is_dir in entries:
    name    = path.name
    newname = apply_replacements(name)

    if newname == name:
        counters["skip_unchanged"] += 1
        continue

    if not newname.strip():
        log.warning(f"  SKIP (nom vide apres remplacement) : {path}")
        counters["skip_conflict"] += 1
        continue

    new_path = path.parent / newname

    if new_path.exists():
        log.warning(f"  CONFLIT   {path.parent / name}  -->  {newname}  (existe deja)")
        counters["skip_conflict"] += 1
        continue

    kind = "DIR " if is_dir else "FILE"
    log.info(f"  {kind}  {path.relative_to(BASE)}")
    log.info(f"       -->  {newname}")

    counters["renamed"] += 1

    if APPLY:
        try:
            path.rename(new_path)
        except Exception as e:
            log.error(f"  ERREUR : {e}")
            counters["err"]    += 1
            counters["renamed"] -= 1

log.info("\n" + "=" * 70)
log.info("RESUME")
log.info("=" * 70)
if APPLY:
    log.info(f"  Renommages effectues   : {counters['renamed']}")
    log.info(f"  Inchanges              : {counters['skip_unchanged']}")
    log.info(f"  Conflits / ignores     : {counters['skip_conflict']}")
    log.info(f"  Erreurs                : {counters['err']}")
else:
    log.info(f"  Renommages prevus      : {counters['renamed']}")
    log.info(f"  Inchanges              : {counters['skip_unchanged']}")
    log.info(f"  Conflits / ignores     : {counters['skip_conflict']}")
    log.info(f"\n  --> relancer avec --apply pour executer")
