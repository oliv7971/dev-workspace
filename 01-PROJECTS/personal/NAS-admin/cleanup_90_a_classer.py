#!/usr/bin/env python3
"""
cleanup_90_a_classer.py
Reorganise le contenu de Nas_louhans_2/01-ds420-data/90-a_classer
vers les dossiers thematiques appropries du meme NAS.

Usage:
    python cleanup_90_a_classer.py          # dry-run (simulation)
    python cleanup_90_a_classer.py --apply  # exécution réelle
"""

import os
import sys
import shutil
import logging
from pathlib import Path

BASE_NAS = Path(r"\\Nas_louhans_2\01-ds420-data")
SRC = BASE_NAS / "90-a_classer"

APPLY = "--apply" in sys.argv

LOG_FILE = Path("reports/cleanup_90_a_classer_log.txt")
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

if APPLY:
    log.info("=== MODE EXÉCUTION ===")
else:
    log.info("=== DRY-RUN (simulation) — relancer avec --apply pour exécuter ===")

# ──────────────────────────────────────────────────────────────────────────────
# Déplacements : (nom_dans_90-a_classer, dossier_destination_relatif, description)
# ──────────────────────────────────────────────────────────────────────────────
MOVES = [
    # → 10-INFORMATIQUE
    ("20-Logiciels",                  "10-INFORMATIQUE", "Logiciels / installeurs"),
    ("lisp",                          "10-INFORMATIQUE", "Scripts AutoLisp"),
    ("X17-59009.iso",                 "10-INFORMATIQUE", "ISO Windows"),
    ("RepairDiscWindows7-64-bit.iso", "10-INFORMATIQUE", "ISO Windows Repair 64-bit"),
    ("RepairDiscWindows7-32-bit.iso", "10-INFORMATIQUE", "ISO Windows Repair 32-bit"),
    ("HASP_USB_KEY_GUIDE.pdf",        "10-INFORMATIQUE", "Guide dongle HASP"),
    ("QuickNetsentinel_fr.pdf",       "10-INFORMATIQUE", "Logiciel réseau"),
    ("connexion_livebox_mmorel.png",  "10-INFORMATIQUE", "Config réseau"),
    ("SquareTrade_laptop_reliability_1109.pdf", "10-INFORMATIQUE", "Doc fiabilité hardware"),
    ("wifi adapter properties 1.png", "10-INFORMATIQUE", "Config réseau"),
    ("wifi adapter properties 2.png", "10-INFORMATIQUE", "Config réseau"),
    ("commande windows premium pour notebook.png", "10-INFORMATIQUE", "Achat Windows"),

    # → 30-RESSOURCES
    ("31-documentation",              "30-RESSOURCES", "Documentation technique (6418 fichiers)"),
    ("30-mode d'emploi",              "30-RESSOURCES", "Manuels"),
    ("guide_beton_coffre_en_tunnel_cle5d3179.pdf", "30-RESSOURCES", "Doc technique béton"),
    ("Blaue Reihe des Lehrstuhls für Geodäsie - Heft 21 - ENGLISCHE VERSION.pdf_c596330a1O.pdf",
                                      "30-RESSOURCES", "Doc géodésie"),

    # → 42-PHOTOS
    ("photos",                        "42-PHOTOS", "Photos"),
    ("photos xcore",                  "42-PHOTOS", "Photos topographie"),
    ("PrintScreen Files",             "42-PHOTOS", "Captures écran"),
    ("PrintScreen Files 2",           "42-PHOTOS", "Captures écran (2)"),
    ("copies ecran",                  "42-PHOTOS", "Copies d'écran"),
    ("photos.zip",                    "42-PHOTOS", "Archive photos"),

    # → 50-DONNEES
    ("50-OLIVIER (perso)",            "50-DONNEES", "Données personnelles Olivier"),
    ("olivier",                       "50-DONNEES", "Données personnelles Olivier"),
    ("DOCUMENTS",                     "50-DONNEES", "Documents personnels"),

    # → 01-ADMINISTRATIF
    ("scans",                         "01-ADMINISTRATIF", "Scans"),
    ("check-list_acheteur.pdf",       "01-ADMINISTRATIF", "Check-list achat immobilier"),
    ("justificatif.pdf",              "01-ADMINISTRATIF", "Justificatif"),
    ("facture CONNECTIFY.png",        "01-ADMINISTRATIF", "Facture"),
    ("COMMANDE TOPCLAVIER.png",       "01-ADMINISTRATIF", "Commande"),
    ("TRANSACTION EZYSHOES.png",      "01-ADMINISTRATIF", "Transaction"),
    ("Salon_Autos_2013.pdf",          "01-ADMINISTRATIF", "Salon auto 2013"),
    ("48_22428_daciaduster_essais_fr_final_9e0aaa58.pdf",
                                      "01-ADMINISTRATIF", "Doc auto"),
]

# ──────────────────────────────────────────────────────────────────────────────
# Suppressions (dossiers vides / fichiers système)
# ──────────────────────────────────────────────────────────────────────────────
TO_DELETE = [
    ("3DReshaper 2015 (x64)", "Dossier vide"),
    ("Thumbs.db",             "Fichier système Windows"),
]

# ──────────────────────────────────────────────────────────────────────────────
# Éléments conservés dans 90-a_classer — traitement manuel ultérieur
# ──────────────────────────────────────────────────────────────────────────────
KEEP = [
    "tri",       # 11.7 Go, 4 772 fichiers — tri manuel nécessaire
    "data",      # 5.1 Go, 163 fichiers — nature inconnue
    "ARCHIVES",  # 56 Mo, 556 fichiers — à analyser
    "recent",    # 15 Mo, 62 fichiers — à trier
    "COF-41011-D-Plan d'ensemble - Coffrage Tablier",  # Projet GéomètrE
    "dmPDF.pdf",
    "Moyens-humains.html",
]

counters = {"moves_ok": 0, "moves_skip": 0, "moves_err": 0, "deletes": 0}

log.info(f"\nSource      : {SRC}")
log.info(f"Destination : {BASE_NAS}\n")


def dir_size(p: Path) -> float:
    """Retourne la taille d'un dossier en Mo (best-effort)."""
    try:
        return sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) / 1024 ** 2
    except Exception:
        return 0.0


# ── Suppressions ────────────────────────────────────────────────────────────
log.info("=" * 70)
log.info("SUPPRESSIONS")
log.info("=" * 70)
for name, desc in TO_DELETE:
    src_path = SRC / name
    if not src_path.exists():
        log.info(f"  ABSENT   {name}")
        continue
    log.info(f"  DEL      {name}  ({desc})")
    if APPLY:
        try:
            if src_path.is_dir():
                shutil.rmtree(src_path)
            else:
                src_path.unlink()
            counters["deletes"] += 1
        except Exception as e:
            log.error(f"  ERREUR   {name}: {e}")


# ── Déplacements ─────────────────────────────────────────────────────────────
log.info("\n" + "=" * 70)
log.info("DÉPLACEMENTS")
log.info("=" * 70)

# Regrouper par destination pour l'affichage
current_dest = None
for name, dest_rel, desc in MOVES:
    if dest_rel != current_dest:
        log.info(f"\n  ▸ → {dest_rel}")
        current_dest = dest_rel

    src_path = SRC / name
    dst_dir  = BASE_NAS / dest_rel
    dst_path = dst_dir / name

    if not src_path.exists():
        log.info(f"      ABSENT   {name}")
        counters["moves_skip"] += 1
        continue

    if dst_path.exists():
        log.warning(f"      CONFLIT  {name}  (existe déjà dans {dest_rel}) → SKIP")
        counters["moves_skip"] += 1
        continue

    if APPLY:
        mo = dir_size(src_path) if src_path.is_dir() else src_path.stat().st_size / 1024**2
        size_str = f"{mo:.0f} Mo — "
    else:
        size_str = ""
    log.info(f"      MOVE     {name}  ({size_str}{desc})")

    if APPLY:
        try:
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            counters["moves_ok"] += 1
        except Exception as e:
            log.error(f"      ERREUR   {name}: {e}")
            counters["moves_err"] += 1
    else:
        counters["moves_ok"] += 1


# ── Éléments conservés ───────────────────────────────────────────────────────
log.info("\n" + "=" * 70)
log.info("CONSERVÉS dans 90-a_classer (traitement manuel)")
log.info("=" * 70)
for name in KEEP:
    p = SRC / name
    if p.exists():
        if APPLY:
            mo = dir_size(p) if p.is_dir() else p.stat().st_size / 1024**2
            log.info(f"  KEEP     {name}  ({mo:.0f} Mo)")
        else:
            log.info(f"  KEEP     {name}")
    else:
        log.info(f"  ABSENT   {name}")


# ── Résumé ────────────────────────────────────────────────────────────────────
log.info("\n" + "=" * 70)
log.info("RÉSUMÉ")
log.info("=" * 70)
if APPLY:
    log.info(f"  Déplacements effectués  : {counters['moves_ok']}")
    log.info(f"  Suppressions            : {counters['deletes']}")
    log.info(f"  Ignorés (absent/conflit): {counters['moves_skip']}")
    log.info(f"  Erreurs                 : {counters['moves_err']}")
else:
    log.info(f"  Actions planifiées      : {counters['moves_ok']} déplacements")
    log.info(f"  Ignorés (absent/conflit): {counters['moves_skip']}")
    log.info(f"  Suppressions planifiées : {len(TO_DELETE)}")
    log.info(f"\n  → relancer avec --apply pour exécuter")
