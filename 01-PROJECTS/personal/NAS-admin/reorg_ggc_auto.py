#!/usr/bin/env python3
"""
reorg_ggc_auto.py
Réorganise un (ou tous les) dossier(s) GGC vers la structure standard :
  00-ADMIN / 01-DONNEES / 02-TRAVAIL / 03-LIVRAISON / 04-ARCHIVES

Classification automatique par mots-clés sur le nom du sous-dossier.
Tout ce qui ne correspond à rien va dans 02-TRAVAIL (catégorie par défaut).

Usage:
    python reorg_ggc_auto.py                         # dry-run tous dossiers non organisés
    python reorg_ggc_auto.py --dossier "06-TUNNEL CORNILLON"   # un seul dossier
    python reorg_ggc_auto.py --apply                 # exécution réelle (tous)
    python reorg_ggc_auto.py --dossier "06-TUNNEL CORNILLON" --apply

Les conflits (nom déjà existant dans la cible) sont toujours ignorés.
"""

import sys, os, shutil, logging, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ──────────────────────────────────────────────────────────────────────────────
GGC_BASE = Path(r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS")
TARGET_STRUCT = ['00-ADMIN', '01-DONNEES', '02-TRAVAIL', '03-LIVRAISON', '04-ARCHIVES']
DEFAULT_CAT   = '02-TRAVAIL'

# Dossiers déjà organisés (à ignorer)
ALREADY_DONE = {'02-STRASBOURG ETOILE', '03-BALESMES', '04-TUNNEL MONTETS', '05-CROIX ROUSSE'}

# ──────────────────────────────────────────────────────────────────────────────
# Règles de classification par mots-clés (appliquées au nom en minuscules)
# Ordre : plus spécifique en premier
# ──────────────────────────────────────────────────────────────────────────────
RULES = [
    # 00-ADMIN
    ('00-ADMIN', [
        'admin', 'administratif', 'contrat', 'commande', 'compte rendu',
        'reunion', 'offre', 'devis', 'facture', 'frais', 'note', 'cctp',
        'bordereau', 'marche', 'ordre de service', 'convention', 'appel offre',
        'correspondance', 'courrier', 'planning', 'budget',
    ]),
    # 01-DONNEES
    ('01-DONNEES', [
        'donnes', 'donnees', 'données', 'donnée', 'scan', 'nuage', 'cloud',
        'mesure', 'terrain', 'gps', 'reference', 'repere', 'repères', 'brut',
        'leve', 'levé', 'carnets', 'carnet', 'pts', 'xyz', 'ptcloud',
        'cyclone', 'lidar', 'brutes', 'entree', 'entrée', 'recu', 'reçu',
        'reception', 'réception', 'base', 'geo', 'geodesiq',
    ]),
    # 03-LIVRAISON
    ('03-LIVRAISON', [
        'livraison', 'livrais', 'livr', 'rapport', 'rendu', 'export',
        'final', 'envoi', 'envoy', 'version finale', 'dossier final',
        'compte rendu final',
    ]),
    # 04-ARCHIVES
    ('04-ARCHIVES', [
        'archive', 'ancien', 'backup', 'old', 'sauvegarde', 'historique',
        'precedent', 'v1', 'v2', 'ancienne', 'anciens',
    ]),
    # 02-TRAVAIL (par défaut, mais aussi mots explicites)
    ('02-TRAVAIL', [
        'calcul', 'travail', 'travaux', 'preparation', 'essai', 'test',
        'projet', 'polygo', 'polygonale', 'auscult', 'convergence',
        'monitoring', 'mission', 'activite', 'activités', 'implant',
        'implantation', 'profil', 'comparaison', 'carto', 'cartographie',
        'process', 'maillage',
    ]),
]

# Noms de sous-dossiers cibles (ne pas déplacer)
TARGET_SET = set(TARGET_STRUCT)


def classify(name: str) -> str:
    """Retourne la catégorie cible pour un nom de sous-dossier."""
    n = name.lower()
    for cat, keywords in RULES:
        for kw in keywords:
            if kw in n:
                return cat
    return DEFAULT_CAT


def analyze_project(proj_path: Path) -> list[tuple[str, str]]:
    """Retourne la liste (nom_sous_dossier, categorie) pour un dossier projet."""
    mapping = []
    try:
        items = sorted(proj_path.iterdir())
    except Exception:
        return []
    for item in items:
        if not item.is_dir():
            continue
        if item.name in TARGET_SET:
            continue  # déjà organisé
        cat = classify(item.name)
        mapping.append((item.name, cat))
    return mapping


def reorg_project(proj_path: Path, apply: bool, log):
    name = proj_path.name
    mapping = analyze_project(proj_path)

    if not mapping:
        log.info(f"  {name} : rien à déplacer (déjà organisé ou vide)")
        return 0, 0

    log.info(f"\n{'='*70}")
    log.info(f"  {name}")
    log.info(f"{'='*70}")

    # Créer la structure cible
    for cat in TARGET_STRUCT:
        dst = proj_path / cat
        if apply:
            dst.mkdir(exist_ok=True)
        else:
            if not dst.exists():
                log.info(f"  MKDIR  {cat}/")

    moved = 0; skipped = 0
    for subname, cat in mapping:
        src = proj_path / subname
        dst = proj_path / cat / subname
        if dst.exists():
            log.info(f"  CONFLIT  {subname}  -->  {cat}/  (existe déjà)")
            skipped += 1
            continue
        log.info(f"  MOVE  {subname}")
        log.info(f"        --> {cat}/")
        if apply:
            try:
                shutil.move(str(src), str(dst))
                moved += 1
            except Exception as e:
                log.error(f"  ERREUR : {e}")
                skipped += 1
        else:
            moved += 1

    return moved, skipped


# ──────────────────────────────────────────────────────────────────────────────
APPLY   = "--apply" in sys.argv
DOSSIER = None
for i, arg in enumerate(sys.argv):
    if arg == "--dossier" and i+1 < len(sys.argv):
        DOSSIER = sys.argv[i+1]

LOG_FILE = Path("reports/reorg_ggc_auto_log.txt")
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

# Sélection des dossiers à traiter
if DOSSIER:
    proj_list = [GGC_BASE / DOSSIER]
else:
    proj_list = [
        p for p in sorted(GGC_BASE.iterdir())
        if p.is_dir()
        and p.name not in ALREADY_DONE
        and p.name not in ('98-ANCIENS_DOSSIERS', '99-AUTRES DOSSIERS', '01-SFTRF')
        and not all((p / cat).exists() for cat in TARGET_STRUCT)
    ]

log.info(f"\n{len(proj_list)} dossiers à traiter\n")

total_moved = 0; total_skip = 0
for proj in proj_list:
    if not proj.exists():
        log.warning(f"  INTROUVABLE : {proj.name}")
        continue
    m, s = reorg_project(proj, APPLY, log)
    total_moved += m
    total_skip  += s

log.info(f"\n{'='*70}")
log.info("RÉSUMÉ GLOBAL")
log.info(f"{'='*70}")
action = "effectués" if APPLY else "prévus"
log.info(f"  Déplacements {action}  : {total_moved}")
log.info(f"  Conflits / ignorés     : {total_skip}")
log.info("")
