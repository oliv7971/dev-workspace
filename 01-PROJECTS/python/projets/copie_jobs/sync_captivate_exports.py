#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Synchronise automatiquement les exports Leica Captivate vers les répertoires d'activité du jour.

Règles :
- Source Leica : dossiers nommés "YYYYMMDD_LIEU_..." (ex. "20250818_GHA_4775_0818_191300").
- Dans chaque dossier source :
    * Fichiers .X… (XCF, X01, X02, etc.) + tous les sous-répertoires --> 1-carnet
    * Fichiers .txt, .gsi, .xyz --> 2-exports
- Cibles : sous TARGET_ROOT/YYYY/MM, tous les dossiers dont le nom commence par "YYYY-MM-DD"
          ET contient le LIEU (mot complet, insensible à la casse).
- Copie dans chaque cible candidate. Par défaut, pas d'écrasement : on suffixe si collision.
- Par défaut : dry-run (simulation). Ajouter --apply pour exécuter réellement.

Sélection :
    --date  YYYY-MM-DD  -> un seul jour
    --month YYYY-MM     -> tout le mois (accepte aussi YYYYMM)
    --all               -> tous les datasets détectés

Exemples :
    py sync_captivate_exports.py --month 2025-08 -v
    py sync_captivate_exports.py --month 202508 --apply
    py sync_captivate_exports.py --date 2025-08-18 --apply -v
    py sync_captivate_exports.py --all -v
"""

from __future__ import annotations
import argparse
import datetime as dt
import logging
import re
import shutil
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# --- À adapter au besoin ---
SOURCE_DBX_ROOT = Path(r"C:\Users\Public\Documents\Leica Captivate\CS\SD Card\DBX")
TARGET_ROOT     = Path(r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES")
# ---------------------------


LOG_FORMAT = "%(levelname)s - %(message)s"

X_EXPORTS_EXT_START = ".x"  # toute extension qui commence par ".x"
EXPORTS_2_EXTS = {".txt", ".gsi", ".xyz"}

def parse_source_dir_name(name: str) -> Optional[Tuple[dt.date, str]]:
    """
    Extrait (date, lieu) depuis un nom de dossier source Leica.
    Attendu: 'YYYYMMDD_LIEU_...' (ex. '20250818_GHA_...').
    """
    m = re.match(r"^(?P<date>\d{8})_(?P<lieu>[A-Za-z]+)(?:_|$)", name)

    if not m:
        return None
    d = m.group("date")
    try:
        the_date = dt.date(int(d[:4]), int(d[4:6]), int(d[6:8]))
    except ValueError:
        return None
    lieu = m.group("lieu").upper()
    return the_date, lieu

def parse_month(month_str: str) -> Tuple[int, int]:
    """
    Accepte 'YYYY-MM' ou 'YYYYMM'. Retourne (year, month).
    """
    m = re.fullmatch(r"(\d{4})-(\d{2})", month_str)
    if m:
        y, mm = int(m.group(1)), int(m.group(2))
    else:
        m2 = re.fullmatch(r"(\d{4})(\d{2})", month_str)
        if not m2:
            raise ValueError("Format de --month invalide (attendu YYYY-MM ou YYYYMM).")
        y, mm = int(m2.group(1)), int(m2.group(2))
    if not (1 <= mm <= 12):
        raise ValueError("Mois invalide (1..12).")
    return y, mm

def target_month_dir(root: Path, d: dt.date) -> Path:
    return root / f"{d.year}" / f"{d.month:02d}"

def find_day_targets(root: Path, the_date: dt.date, lieu: str) -> List[Path]:
    """
    Cherche les dossiers cibles dans TARGET_ROOT/YYYY/MM
    dont le nom commence par 'YYYY-MM-DD' ET contient le LIEU (mot complet).
    """
    ym_dir = target_month_dir(root, the_date)
    if not ym_dir.exists():
        return []
    date_prefix = the_date.strftime("%Y-%m-%d")
    token_re = re.compile(rf"(?<!\w){re.escape(lieu)}(?!\w)", re.IGNORECASE)

    candidates: List[Path] = []
    for p in ym_dir.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        if name.startswith(date_prefix) and token_re.search(name):
            candidates.append(p)
    return candidates

def ensure_dir(p: Path, dry_run: bool):
    if dry_run:
        logging.info(f"[SIMU] Créer dossier : {p}")
    else:
        p.mkdir(parents=True, exist_ok=True)

def safe_copy_file(src: Path, dst_dir: Path, overwrite: bool, dry_run: bool):
    dst = dst_dir / src.name
    if dst.exists() and not overwrite:
        stem = dst.stem
        suffix = dst.suffix
        k = 1
        while True:
            alt = dst_dir / f"{stem} (copie {k}){suffix}"
            if not alt.exists():
                dst = alt
                break
            k += 1
    if dry_run:
        logging.info(f"[SIMU] Copier fichier : {src}  ->  {dst}")
    else:
        shutil.copy2(src, dst)

def copy_tree(src: Path, dst: Path, overwrite: bool, dry_run: bool):
    """
    Copie récursive d'un répertoire.
    Si overwrite=False, on fusionne en préservant les fichiers existants (sans écraser).
    """
    if dry_run:
        logging.info(f"[SIMU] Copier dossier : {src}  ->  {dst}")
        return
    if overwrite:
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        for s in src.rglob("*"):
            rel = s.relative_to(src)
            t = dst / rel
            if s.is_dir():
                t.mkdir(parents=True, exist_ok=True)
            else:
                if t.exists():
                    stem, suf = t.stem, t.suffix
                    k = 1
                    while True:
                        alt = t.with_name(f"{stem} (copie {k}){suf}")
                        if not alt.exists():
                            t = alt
                            break
                        k += 1
                else:
                    t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, t)

def distribute_from_source(source_dir: Path, dst_day_dirs: Iterable[Path],
                           overwrite: bool, dry_run: bool):
    """
    Depuis un dossier source, répartit les fichiers dans 1-carnet / 2-exports
    puis copie vers chaque dossier cible du jour.
    """
    files_x = []
    files_2 = []
    subdirs = []

    for entry in source_dir.iterdir():
        if entry.is_dir():
            subdirs.append(entry)
            continue
        ext = entry.suffix.lower()
        if ext.startswith(X_EXPORTS_EXT_START):
            files_x.append(entry)
        elif ext in EXPORTS_2_EXTS:
            files_2.append(entry)
        else:
            pass

    if not files_x and not files_2 and not subdirs:
        logging.warning(f"Aucun contenu pertinent dans : {source_dir}")
        return

    for day_dir in dst_day_dirs:
        carnet = day_dir / "1-carnet"
        exp2   = day_dir / "2-exports"
        ensure_dir(carnet, dry_run)
        ensure_dir(exp2, dry_run)

        for f in files_x:
            safe_copy_file(f, carnet, overwrite, dry_run)

        for sub in subdirs:
            dst_sub = carnet / sub.name
            if dry_run:
                logging.info(f"[SIMU] Copier sous-dossier : {sub} -> {dst_sub}")
            copy_tree(sub, dst_sub, overwrite, dry_run)

        for f in files_2:
            safe_copy_file(f, exp2, overwrite, dry_run)

def list_source_datasets(root: Path) -> List[Path]:
    """Retourne les sous-dossiers de root qui ressemblent à des datasets Leica."""
    datasets = []
    for p in root.iterdir():
        if p.is_dir() and parse_source_dir_name(p.name):
            datasets.append(p)
    return sorted(datasets)

def main():
    parser = argparse.ArgumentParser(description="Copie les exports Leica Captivate vers les répertoires d'activités.")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--date", type=str, help="Date ciblée au format YYYY-MM-DD (ex. 2025-08-18).")
    g.add_argument("--month", type=str, help="Mois ciblé au format YYYY-MM ou YYYYMM (ex. 2025-08).")
    g.add_argument("--all", action="store_true", help="Traiter tous les datasets trouvés.")

    parser.add_argument("--apply", action="store_true", help="Exécuter réellement les copies (sinon simulation).")
    parser.add_argument("--overwrite", action="store_true", help="Autoriser l'écrasement de fichiers (sinon on suffixe).")
    parser.add_argument("--source", type=Path, default=SOURCE_DBX_ROOT, help="Racine des données Leica.")
    parser.add_argument("--target", type=Path, default=TARGET_ROOT, help="Racine des activités chantier.")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Plus de logs (-v, -vv).")

    args = parser.parse_args()

    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format=LOG_FORMAT)

    dry_run = not args.apply
    overwrite = args.overwrite

    datasets = list_source_datasets(args.source)
    if not datasets:
        logging.error(f"Aucun dataset détecté sous {args.source}")
        return

    # Sélection selon --date / --month / --all
    if args.all:
        selected = datasets

    elif args.month:
        try:
            y, m = parse_month(args.month)
        except ValueError as e:
            logging.error(str(e))
            return
        selected = []
        for d in datasets:
            parsed = parse_source_dir_name(d.name)
            if not parsed:
                continue
            ddate, _ = parsed
            if ddate.year == y and ddate.month == m:
                selected.append(d)
        if not selected:
            logging.warning(f"Aucun dataset trouvé pour le mois {y:04d}-{m:02d}.")
            return

    else:
        # --date (ou défaut = aujourd'hui)
        if args.date:
            try:
                target_date = dt.date.fromisoformat(args.date)
            except ValueError:
                logging.error("Format de --date invalide (attendu YYYY-MM-DD).")
                return
        else:
            target_date = dt.date.today()

        selected = []
        for d in datasets:
            parsed = parse_source_dir_name(d.name)
            if not parsed:
                continue
            ddate, _ = parsed
            if ddate == target_date:
                selected.append(d)
        if not selected:
            logging.warning(f"Aucun dataset trouvé pour la date {target_date.isoformat()}.")
            return

    # Traitement
    for source_dir in selected:
        parsed = parse_source_dir_name(source_dir.name)
        if not parsed:
            continue
        the_date, lieu = parsed
        dsts = find_day_targets(args.target, the_date, lieu)
        if not dsts:
            logging.warning(f"Aucune cible trouvée pour {source_dir.name} -> {the_date} / {lieu} sous {target_month_dir(args.target, the_date)}")
            continue

        logging.info(f"Dataset: {source_dir.name}  Date: {the_date}  Lieu: {lieu}  Cibles: {len(dsts)}")
        for d in dsts:
            logging.info(f"  - {d}")
        distribute_from_source(source_dir, dsts, overwrite=overwrite, dry_run=dry_run)

    if dry_run:
        print("\nSimulation terminée (aucune copie effectuée). Ajoutez --apply pour exécuter.")
    else:
        print("\nCopie terminée.")

if __name__ == "__main__":
    main()
