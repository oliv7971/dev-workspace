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
    r"""^(?P<base>.+?)[-_]
         (?P<yy>\d{2})[-_](?P<mm>\d{2})[-_](?P<dd>\d{2})
         \.(?P<ext>xlsm|xlsx|xls)$
     """,
    re.VERBOSE | re.IGNORECASE,
)

ANCIENS_NAME = "_anciens"

def harmoniser_dossiers_anciens(racine: Path, dry_run: bool) -> None:
    """Renomme tous les dossiers 'anciens' en '_anciens' pour harmoniser."""
    dossiers_renommes = 0
    dossiers_fusionnes = 0
    
    # Chercher tous les dossiers nommés "anciens" (sans underscore)
    for d in racine.rglob("*"):
        if not d.is_dir():
            continue
        if d.name.lower() == "anciens":
            nouveau_nom = d.parent / ANCIENS_NAME
            if not nouveau_nom.exists():
                # Cas simple: renommage direct
                if dry_run:
                    print(f"[DRY-RUN] RENOMMER  {d}  ->  {nouveau_nom}")
                else:
                    d.rename(nouveau_nom)
                    print(f"[OK] RENOMMER  {d.name}  ->  {nouveau_nom.name}")
                dossiers_renommes += 1
            else:
                # Cas complexe: fusion du contenu puis suppression
                print(f"[FUSION] Dossier {nouveau_nom} existe déjà, fusion du contenu de {d}")
                
                # Déplacer tous les fichiers de 'anciens' vers '_anciens'
                try:
                    for item in d.iterdir():
                        destination = nouveau_nom / item.name
                        # Gérer les conflits de noms
                        if destination.exists():
                            stem, suffix = item.stem, item.suffix
                            i = 1
                            while destination.exists():
                                if item.is_file():
                                    destination = nouveau_nom / f"{stem} ({i}){suffix}"
                                else:
                                    destination = nouveau_nom / f"{stem} ({i})"
                                i += 1
                        
                        if dry_run:
                            print(f"  [DRY-RUN] DEPLACER  {item}  ->  {destination}")
                        else:
                            if item.is_file():
                                shutil.move(str(item), str(destination))
                            else:
                                shutil.move(str(item), str(destination))
                            print(f"  [OK] DEPLACER  {item.name}  ->  {destination}")
                    
                    # Supprimer le dossier 'anciens' maintenant vide
                    if dry_run:
                        print(f"  [DRY-RUN] SUPPRIMER dossier vide  {d}")
                    else:
                        d.rmdir()
                        print(f"  [OK] SUPPRIMER dossier vide  {d}")
                    
                    dossiers_fusionnes += 1
                except Exception as e:
                    print(f"  [ERREUR] Impossible de fusionner {d}: {e}")
    
    if dossiers_renommes > 0:
        print(f"✅ {dossiers_renommes} dossier(s) 'anciens' renommé(s) en '{ANCIENS_NAME}'")
    if dossiers_fusionnes > 0:
        print(f"✅ {dossiers_fusionnes} dossier(s) 'anciens' fusionné(s) dans '{ANCIENS_NAME}'")
    if dossiers_renommes == 0 and dossiers_fusionnes == 0:
        print("ℹ️ Aucun dossier 'anciens' à traiter trouvé")

def is_in_anciens(p: Path) -> bool:
    """Vrai si un des parents (ou le dossier lui-même) est nommé _anciens (case-insensitive)."""
    lower_parts = [part.lower() for part in p.parts]
    return ANCIENS_NAME.lower() in lower_parts or "anciens" in lower_parts

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

    # Compter les fichiers Excel trouvés
    fichiers_excel = 0
    for f in rep.iterdir():
        if not f.is_file():
            continue
        # Ignorer les fichiers déjà sous _anciens (par sécurité si lancé au niveau racine)
        if is_in_anciens(f):
            continue
        m = PATTERN.match(f.name)
        if not m:
            continue
        fichiers_excel += 1
        dt = parse_date(m["yy"], m["mm"], m["dd"])
        base = m["base"].strip()
        groupes.setdefault(base, []).append((dt, f))

    # Afficher info sur les fichiers trouvés
    if fichiers_excel > 0:
        print(f"  📄 {fichiers_excel} fichier(s) Excel trouvé(s) dans {rep}")

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
    
    # 🔧 ÉTAPE 1: Harmoniser les dossiers "anciens" en "_anciens"
    print(f"\n🔧 [HARMONISATION] Recherche des dossiers 'anciens' à renommer...")
    harmoniser_dossiers_anciens(racine, dry_run)
    
    # Compter les dossiers traités pour avoir un feedback
    dossiers_traites = 0
    
    # 🔍 ÉTAPE 2: Traiter d'abord la racine elle-même si ce n'est pas _anciens
    if not is_in_anciens(racine):
        print(f"\n🔍 [SCAN] Traitement du dossier racine: {racine}")
        traiter_repertoire(racine, copy=copy, dry_run=dry_run)
        dossiers_traites += 1

    # 🔍 ÉTAPE 3: Puis descendre récursivement en évitant tout chemin contenant _anciens
    print(f"\n🔍 [SCAN] Recherche récursive dans tous les sous-dossiers...")
    
    # Collecter d'abord tous les dossiers pour avoir une idée du volume
    tous_dossiers = [d for d in racine.rglob("*") if d.is_dir() and not is_in_anciens(d)]
    print(f"📁 [INFO] {len(tous_dossiers)} dossier(s) trouvé(s) à traiter")
    
    for i, d in enumerate(tous_dossiers, 1):
        print(f"\n🔍 [{i}/{len(tous_dossiers)}] Traitement: {d}")
        traiter_repertoire(d, copy=copy, dry_run=dry_run)
        dossiers_traites += 1

    print(f"\n✅ Terminé. {dossiers_traites} dossier(s) traité(s).")

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
