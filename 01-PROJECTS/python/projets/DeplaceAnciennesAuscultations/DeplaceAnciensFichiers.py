#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import argparse
import re
from pathlib import Path
from datetime import date
import shutil
from typing import Dict, List, Tuple

PATTERN = re.compile(
    r"""^(?P<base>.+?)_
         (?P<yy>\d{2})_(?P<mm>\d{2})_(?P<dd>\d{2})
         \.(?P<ext>xlsm|xlsx|xls)$
     """,
    re.VERBOSE | re.IGNORECASE,
)

ANCIENS_NAME = "_anciens"

def is_in_anciens(p: Path) -> bool:
    """Vrai si un des parents (ou le dossier lui-même) est nommé _anciens (case-insensitive)."""
    lower_parts = [part.lower() for part in p.parts]
    return ANCIENS_NAME.lower() in lower_parts

def parse_date(yy: str, mm: str, dd: str) -> date:
    y = 2000 + int(yy)   # adapter si besoin
    return date(y, int(mm), int(dd))

def safe_move_or_copy(src: Path, dst_dir: Path, copy: bool, dry_run: bool) -> Path:
    # Ne jamais re-déplacer ce qui est déjà sous _anciens
    if is_in_anciens(src):
        print(f"[SKIP] Déjà sous {ANCIENS_NAME}: {src}")
        return src

    dst_dir.mkdir(parents=True, exist_ok=True)
    candidate = dst_dir / src.name
    if candidate.exists():
        stem, suffix = candidate.stem, candidate.suffix
        i = 1
        while candidate.exists():
            candidate = dst_dir / f"{stem} ({i}){suffix}"
            i += 1
    action = "COPIE" if copy else "DEPLACE"
    if dry_run:
        print(f"[DRY-RUN] {action}  {src}  ->  {candidate}")
        return candidate
    if copy:
        shutil.copy2(src, candidate)
    else:
        shutil.move(str(src), str(candidate))
    print(f"[OK] {action}  {src.name}  ->  {candidate}")
    return candidate

def traiter_repertoire(rep: Path, copy: bool, dry_run: bool) -> None:
    # Ignorer les dossiers _anciens
    if is_in_anciens(rep):
        return

    groupes: Dict[str, List[Tuple[date, Path]]] = {}

    for f in rep.iterdir():
        if not f.is_file():
            continue
        # Ignorer les fichiers déjà sous _anciens (par sécurité si lancé au niveau racine)
        if is_in_anciens(f):
            continue
        m = PATTERN.match(f.name)
        if not m:
            continue
        dt = parse_date(m["yy"], m["mm"], m["dd"])
        base = m["base"].strip()
        groupes.setdefault(base, []).append((dt, f))

    if not groupes:
        return

    anciens = rep / ANCIENS_NAME

    for base, versions in groupes.items():
        versions.sort(key=lambda t: t[0])  # plus anciennes d'abord
        latest_dt, latest_path = versions[-1]
        older = [p for _, p in versions[:-1]]

        if older:
            print(f"\nDossier: {rep}")
            print(f"Base    : {base}")
            print(f"Dernière: {latest_path.name}  (date {latest_dt.isoformat()})")
            print(f"A archiver ({len(older)} fichier(s)) -> {anciens}")

        for p in older:
            safe_move_or_copy(p, anciens, copy=copy, dry_run=dry_run)

def parcourir_racine(racine: Path, copy: bool, dry_run: bool) -> None:
    print(f"Racine : {racine.resolve()}")

    # Traiter d'abord la racine elle-même si ce n’est pas _anciens
    traiter_repertoire(racine, copy=copy, dry_run=dry_run)

    # Puis descendre récursivement en évitant tout chemin contenant _anciens
    for d in racine.rglob("*"):
        if not d.is_dir():
            continue
        if is_in_anciens(d):
            continue
        traiter_repertoire(d, copy=copy, dry_run=dry_run)

    print("\nTerminé.")

def main():
    import sys
    ap = argparse.ArgumentParser(description="Classement auto des mesures topographiques")
    ap.add_argument("racine", type=Path, help="Dossier racine à traiter (récursif)")
    ap.add_argument("--copy", action="store_true", help="Copier au lieu de déplacer")
    ap.add_argument("--dry-run", action="store_true", help="Afficher sans modifier")
    args = ap.parse_args()

    if not args.racine.exists():
        ap.error(f"Le dossier '{args.racine}' n'existe pas.")

    try:
        parcourir_racine(args.racine, copy=args.copy, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur.", file=sys.stderr)

if __name__ == "__main__":
    main()
