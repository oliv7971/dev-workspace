"""
Dispatch du dossier 40-courrier vers les bonnes catégories de 01-ADMINISTRATIF.

Usage:
    python cleanup_40_courrier.py           # dry-run (simulation)
    python cleanup_40_courrier.py --apply   # applique les déplacements

Catégories de dispatch :
    sous-dossiers courriers2011/ → destinations thématiques
    fichiers racine 40-courrier/ → selon nom
    junk (pages web sauvegardées, Thumbs.db, Picasa.ini) → signalé pour suppression
    photos → signalé pour déplacement hors ADMINISTRATIF
"""

import os
import shutil
import sys
import re
from pathlib import Path

# Fix encoding pour Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(r"\\Nas_louhans_2\01-ds420-data\01-ADMINISTRATIF")
SRC = BASE / "40-courrier"
APPLY = "--apply" in sys.argv

# ─────────────────────────────────────────────────────────────────────────────
# Règles de dispatch pour les sous-dossiers de courriers2011/
# (src_subpath_relative_to_SRC, dest_folder_name)
# ─────────────────────────────────────────────────────────────────────────────
FOLDER_RULES = [
    # (chemin relatif dans 40-courrier, destination dans 01-ADMINISTRATIF)
    ("courriers2011/impots2004",                 "01-IMPOTS"),
    ("courriers2011/impots2007",                 "01-IMPOTS"),
    ("courriers2011/groupama",                   "02-ASSURANCES"),
    ("courriers2011/caisse-epargne",             "04-BANQUES"),
    ("courriers2011/23-proBTP",                  "07-RETRAITES"),
    ("courriers2011/logements",                  "10- LOGEMENTS"),
    ("courriers2011/resiliation freebox",        "11-ABONNEMENTS"),
    ("courriers2011/cles",                       "50-CODES"),
    ("courriers2011/surveillance_cerene",        "60-TRAVAIL"),
    ("courriers2011/divers",                     "06-EMPLOI"),
    ("courriers2011/Dossiers CVitae",            "06-EMPLOI"),
    ("courriers2011/06-ClassementVieCourante/travail/Fiche contrat.doc", "06-EMPLOI"),
]

# Sous-dossiers entiers à marquer comme PHOTOS (à déplacer hors ADMINISTRATIF)
PHOTO_FOLDERS = [
    "courriers2011/09-photos",
    "courriers2011/sahara_nov2006",
    "courrier",   # maisonbressane.jpg
]

# Sous-dossiers entiers à marquer comme JUNK (pages web sauvegardées, obsolète)
JUNK_FOLDERS = [
    "courriers2011/06-ClassementVieCourante/travail/adresses",
    "courriers2011/06-ClassementVieCourante/travail/offres",
    "courriers2011/06-ClassementVieCourante/travail/emplio_wissembourg_files",
    "courriers2011/06-ClassementVieCourante/travail/class_a5_files",
    "courriers2011/06-ClassementVieCourante/fiches pratiques",
    "courriers2011/06-ClassementVieCourante/pratique-troyes",
    "courriers2011/06-ClassementVieCourante/exs java",   # vieux exercices Java
    "courriers2011/06-ClassementVieCourante/Uméa (photos)",  # 2 fichiers txt candidatures
    "courriers2011/.filezilla",   # config FTP obsolète
    "courriers2011/reprise_geosiara",  # dossier vide ou trace projet ancien
]

# Fichiers individuels dans courriers2011/ à dispatcher
C2011_FILE_RULES = [
    # (pattern regex, destination)
    (r"(?i)offre.*emploi|annonce.*emploi|annonce.*GIS|annonce.*SIG|geomati|metiers.*geo|technicien.*trafic|cartographie|photogrammetrie", "06-EMPLOI"),
    (r"(?i)fiche.demarche.entreprise|tests.salaires",                         "06-EMPLOI"),
    (r"(?i)cv.*boissard|boissard.*cv",                                        "06-EMPLOI"),
    (r"(?i)Grand.Lyon.*AV20|Grand.Lyon.*SIG",                                 "06-EMPLOI"),
    (r"(?i)firewall|config.x8|procedure.connexion|CloudWorx|CDCF_GEO",       "60-TRAVAIL"),
    (r"(?i)diapos.*formation|Template.*firewall|RESUME_EN_13",                "60-TRAVAIL"),
    (r"(?i)etude.concurrence",                                                "60-TRAVAIL"),
    (r"(?i)FACTURATION.ELAGAGE",                                              "12-FACTURES"),
    (r"(?i)financements",                                                     "04-BANQUES"),
    (r"(?i)pense.bete.demenagement|etiquettes",                               "10- LOGEMENTS"),
    (r"(?i)no_tel",                                                           "32-CONTACT"),
    (r"(?i)\.bak$|essai_.*\.bak|test\.dbf",                                  None),  # junk -> ignorer
]

# Fichiers parasites à supprimer partout
JUNK_FILENAMES = {"Thumbs.db", "Picasa.ini", ".filezilla"}
JUNK_EXTENSIONS = {".BAK", ".class"}  # fichiers compilés Java, backups

# ─────────────────────────────────────────────────────────────────────────────
# Règles pour les fichiers directement à la racine de 40-courrier/
# ─────────────────────────────────────────────────────────────────────────────
ROOT_FILE_RULES = [
    # (pattern regex sur nom de fichier, destination)
    (r"(?i)attestation.*(cpam|maladie|secu|ameli)",     "03-MALADIE"),
    (r"(?i)attestation.*(pole.?emploi|chomage|ARE)",    "06-EMPLOI"),
    (r"(?i)attestation.*situation",                     "06-EMPLOI"),
    (r"(?i)avis.*(pole.?emploi|chomage)",               "06-EMPLOI"),
    (r"(?i)attestation.*(assurance|habitation)",        "02-ASSURANCES"),
    (r"(?i)BOISSARD.*attestationHabitation",            "02-ASSURANCES"),
    (r"(?i)candidature.*(bts|tsgt|scolarit)",           "08- SCOLARITE"),
    (r"(?i)B2_accueil",                                 "31- IDENTITE"),
    (r"(?i)demande.*plan|ouverture.*plan",              "04-BANQUES"),
    (r"(?i)Cahier.*Charges|Dossier Technique|doc-1",   "60-TRAVAIL"),
    (r"(?i)C03.0022.*Return.*Warranty",                "12-FACTURES"),
    (r"(?i)lettre_a_",                                  None),   # personnel, laisser
]


def normalize_path(rel: str) -> Path:
    """Convertit un chemin relatif avec / en Path."""
    return SRC / Path(rel.replace("/", os.sep))


def size_str(path: Path) -> str:
    try:
        total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        return f"{total / 1024:.0f} Ko" if total < 1_000_000 else f"{total / 1_048_576:.1f} Mo"
    except Exception:
        return "?"


def move_folder(src: Path, dest_parent: Path, label: str = ""):
    dest = dest_parent / src.name
    if not APPLY:
        extra = f"  [{size_str(src)}]" if src.is_dir() else ""
        print(f"  {'[DRY]':8} {src.relative_to(SRC)}  →  {dest.relative_to(BASE)}{extra}")
        return
    if dest.exists():
        print(f"  [SKIP] Destination existe déjà : {dest}")
        return
    dest_parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    print(f"  [MOVE] {src.relative_to(SRC)}  →  {dest.relative_to(BASE)}")


def delete_junk_files(root: Path):
    """Supprime Thumbs.db, Picasa.ini, .BAK, .class dans tout l'arbre."""
    deleted = []
    for f in root.rglob("*"):
        if f.is_file():
            if f.name in JUNK_FILENAMES or f.suffix in JUNK_EXTENSIONS:
                deleted.append(f)
                if APPLY:
                    f.unlink()
    return deleted


def main():
    mode = "APPLICATION" if APPLY else "DRY-RUN (simulation)"
    print(f"\n{'='*70}")
    print(f"  Dispatch 40-courrier  —  mode : {mode}")
    print(f"{'='*70}\n")

    # ── 1. Fichiers parasites (Thumbs.db, Picasa.ini…) ──────────────────────
    print("── Fichiers parasites (Thumbs.db, Picasa.ini, .BAK, .class) ──────")
    junk = delete_junk_files(SRC)
    if junk:
        for f in junk:
            action = "[DEL]" if APPLY else "[DRY-DEL]"
            print(f"  {action:10} {f.relative_to(SRC)}")
    else:
        print("  (aucun trouvé)")
    print()

    # ── 2. Dossiers → PHOTOS ────────────────────────────────────────────────
    print("── PHOTOS (à déplacer hors ADMINISTRATIF) ──────────────────────────")
    for rel in PHOTO_FOLDERS:
        p = normalize_path(rel)
        if p.exists():
            extra = size_str(p) if p.is_dir() else ""
            print(f"  [PHOTOS]  {p.relative_to(SRC)}  ({extra})  → à déplacer manuellement vers vos photos")
        else:
            print(f"  [?] introuvable : {rel}")
    print()

    # ── 3. Dossiers JUNK ────────────────────────────────────────────────────
    print("── JUNK (pages web sauvegardées, exercices Java obsolètes) ─────────")
    for rel in JUNK_FOLDERS:
        p = normalize_path(rel)
        if p.exists():
            extra = size_str(p) if p.is_dir() else ""
            if APPLY:
                if p.is_dir():
                    shutil.rmtree(str(p))
                else:
                    p.unlink()
                print(f"  [DELETED] {p.relative_to(SRC)}  ({extra})")
            else:
                print(f"  [DRY-DEL] {p.relative_to(SRC)}  ({extra})")
        else:
            print(f"  [?] introuvable : {rel}")
    print()

    # ── 4. Dispatch des sous-dossiers vers thématiques ──────────────────────
    print("── Dispatch dossiers → catégories thématiques ──────────────────────")
    for rel, dest_name in FOLDER_RULES:
        src_path = normalize_path(rel)
        if not src_path.exists():
            print(f"  [?] introuvable : {rel}")
            continue
        dest_parent = BASE / dest_name
        if src_path.is_dir():
            move_folder(src_path, dest_parent)
        else:
            # fichier isolé
            dest_file = dest_parent / src_path.name
            if not APPLY:
                print(f"  {'[DRY]':8} {src_path.relative_to(SRC)}  →  {dest_file.relative_to(BASE)}")
            else:
                dest_parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), str(dest_file))
                print(f"  [MOVE]    {src_path.relative_to(SRC)}  →  {dest_file.relative_to(BASE)}")
    print()

    # ── 5. Fichiers à la racine de 40-courrier/ ─────────────────────────────
    print("── Fichiers à la racine de 40-courrier/ ────────────────────────────")
    root_files = [f for f in SRC.iterdir() if f.is_file()]
    unmatched = []
    for f in root_files:
        matched = False
        for pattern, dest_name in ROOT_FILE_RULES:
            if re.search(pattern, f.name):
                if dest_name is None:
                    print(f"  [GARDER]  {f.name}  (courrier personnel)")
                    matched = True
                    break
                dest_parent = BASE / dest_name
                dest_file = dest_parent / f.name
                if not APPLY:
                    print(f"  {'[DRY]':8} {f.name}  →  {dest_name}/")
                else:
                    dest_parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(f), str(dest_file))
                    print(f"  [MOVE]    {f.name}  →  {dest_name}/")
                matched = True
                break
        if not matched:
            unmatched.append(f.name)

    if unmatched:
        print(f"\n  [À CLASSER MANUELLEMENT] :")
        for name in unmatched:
            print(f"    - {name}")
    print()

    # ── 6. Fichiers épars dans courriers2011/ ───────────────────────────────
    c2011 = SRC / "courriers2011"
    # Dossiers déjà traités en section 4 (ne pas les re-lister comme "manuels")
    handled_dirs = {normalize_path(rel).name for rel, _ in FOLDER_RULES if (normalize_path(rel)).parent == c2011}
    # Dossiers JUNK déjà traités
    junk_dir_names = {normalize_path(rel).name for rel in JUNK_FOLDERS if (normalize_path(rel)).parent == c2011}
    # Dossiers PHOTOS déjà traités
    photo_dir_names = {normalize_path(rel).name for rel in PHOTO_FOLDERS if (normalize_path(rel)).parent == c2011}
    skip_names = handled_dirs | junk_dir_names | photo_dir_names

    if c2011.exists():
        print("── Fichiers epars dans courriers2011/ ──────────────────────────────")
        still_remaining = []
        for item in sorted(c2011.iterdir()):
            if item.is_dir():
                if item.name not in skip_names:
                    still_remaining.append(item)  # sous-dossiers non encore traités
                continue  # les dossiers gérés par FOLDER_RULES sont déjà dispatché
            # Fichier
            matched = False
            for pattern, dest_name in C2011_FILE_RULES:
                if re.search(pattern, item.name):
                    if dest_name is None:
                        matched = True  # junk/skip, ne pas lister
                        break
                    dest_parent = BASE / dest_name
                    dest_file = dest_parent / item.name
                    if not APPLY:
                        print(f"  {'[DRY]':8} courriers2011/{item.name}  ->  {dest_name}/")
                    else:
                        dest_parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item), str(dest_file))
                        print(f"  [MOVE]    courriers2011/{item.name}  ->  {dest_name}/")
                    matched = True
                    break
            if not matched:
                still_remaining.append(item)

        if still_remaining:
            print(f"\n  [A CLASSER MANUELLEMENT] :")
            for p in still_remaining:
                marker = "/" if p.is_dir() else ""
                extra = f"  [{size_str(p)}]" if p.is_dir() else ""
                print(f"    courriers2011/{p.name}{marker}{extra}")
        print()

    print("─" * 70)
    if not APPLY:
        print("  → Relancer avec --apply pour appliquer les changements.")
    else:
        print("  → Dispatch terminé.")
    print()


if __name__ == "__main__":
    main()
