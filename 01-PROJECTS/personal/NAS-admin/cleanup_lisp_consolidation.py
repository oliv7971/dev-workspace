"""
Consolidation des dossiers AutoLISP épars dans lisp\.
Fusionne : lisp - copie (top), scripts lisp (top), EXERCICES AUTOLISP, 13 - lisp
vers : lisp\
Dry-run par défaut, --apply pour exécuter.
"""
import sys
import shutil
from pathlib import Path

DRY_RUN = '--apply' not in sys.argv

BASE  = Path(r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT')
LISP  = BASE / 'lisp'

# Sources à fusionner → sous-dossier cible dans lisp\
MERGES = [
    # (source_top_level, nom_sous_dossier_destination)
    (BASE / 'lisp - copie',               'lisp-copie'),
    (BASE / 'EXERCICES AUTOLISP du cours','exercices-autolisp'),
    (BASE / '13 - lisp',                  '13-lisp'),
]

# scripts lisp (top) : probablement doublon de lisp\scripts lisp → vérifier
SRC_SCRIPTS = BASE / 'scripts lisp'
DST_SCRIPTS = LISP / 'scripts lisp'

moved = 0
skipped = 0
errors = 0

def move_or_skip(src: Path, dst: Path):
    global moved, skipped, errors
    if dst.exists():
        print(f"  SKIP (existe) : {dst.relative_to(BASE)}")
        skipped += 1
        return
    print(f"  MOVE : {src.relative_to(BASE)}  →  {dst.relative_to(BASE)}")
    if not DRY_RUN:
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(src), str(dst))
            moved += 1
        except Exception as e:
            print(f"    ERREUR : {e}")
            errors += 1
    else:
        moved += 1

print("=" * 60)
print(f"MODE : {'DRY-RUN' if DRY_RUN else 'APPLY'}")
print("=" * 60)

# 1. Fusionner les dossiers vers lisp\<sous-dossier>
for src_dir, dst_name in MERGES:
    if not src_dir.exists():
        print(f"\n[SKIP] {src_dir.name} — introuvable (déjà déplacé ?)")
        continue
    dst_dir = LISP / dst_name
    print(f"\n[MERGE] {src_dir.name}  →  lisp\\{dst_name}")
    # Déplacer chaque enfant direct
    children = list(src_dir.iterdir())
    if not children:
        print("  (vide)")
        if not DRY_RUN:
            src_dir.rmdir()
        continue
    for child in children:
        move_or_skip(child, dst_dir / child.name)
    # Supprimer le dossier source si vide après déplacement
    if not DRY_RUN:
        remaining = list(src_dir.iterdir())
        if not remaining:
            src_dir.rmdir()
            print(f"  → {src_dir.name} supprimé (vide)")
        else:
            print(f"  ⚠ {src_dir.name} non vide après merge : {[c.name for c in remaining]}")

# 2. scripts lisp (top) : comparer avec lisp\scripts lisp
print(f"\n[CHECK] scripts lisp (top) vs lisp\\scripts lisp")
if SRC_SCRIPTS.exists():
    src_items = {c.name.lower(): c for c in SRC_SCRIPTS.iterdir()}
    dst_items = {c.name.lower(): c for c in DST_SCRIPTS.iterdir()} if DST_SCRIPTS.exists() else {}
    unique_in_src = [v for k, v in src_items.items() if k not in dst_items]
    print(f"  Éléments dans scripts lisp (top) : {len(src_items)}")
    print(f"  Éléments uniques (absents de lisp\\scripts lisp) : {len(unique_in_src)}")
    if unique_in_src:
        for u in unique_in_src:
            print(f"    UNIQUE: {u.name}")
            move_or_skip(u, DST_SCRIPTS / u.name)
    else:
        print("  → Doublon complet, suppression de scripts lisp (top)")
        if not DRY_RUN:
            shutil.rmtree(str(SRC_SCRIPTS))
            print("  → Supprimé")
else:
    print("  scripts lisp (top) introuvable — déjà traité ?")

print()
print("=" * 60)
print(f"Résumé : {moved} déplacés, {skipped} ignorés (existants), {errors} erreurs")
if DRY_RUN:
    print("→ Relancer avec --apply pour exécuter")
print("=" * 60)
