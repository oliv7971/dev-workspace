"""
Analyse les conflits entre les dossiers d'activités avant fusion,
puis fusionne tout dans 01-ACTIVITES.

Stratégie de fusion :
  - Si fichier identique (nom + taille) → skip (garder 1 copie)
  - Si conflit (même chemin relatif, taille différente) → renommer la source
  - Si pas de conflit → déplacer

Usage :
  python merge_siaix_activites.py           → dry-run
  python merge_siaix_activites.py --execute → exécution réelle
"""
import os
import sys
import shutil
from collections import defaultdict

ROOT   = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\38-TUNNEL DE SIAIX"
# Nom du dossier cible DIFFÉRENT de tous les dossiers sources
# pour éviter la collision case-insensitive sur NAS Synology (SMB)
TARGET = os.path.join(ROOT, "_ACTIVITES_MERGE_")

# Dossiers sources à fusionner → sous-dossier cible dans _ACTIVITES_MERGE_
SOURCES = [
    ("01-activites",               "01-activites"),
    ("01-activites réalisées OB",  "01-activites réalisées OB"),
    ("01-activites realisées ob",  "01-activites realisées ob"),
    ("04-activites ob derniere semaine", "04-activites ob derniere semaine"),
    ("04-activites restitution",   "04-activites restitution"),
]

DRY = "--execute" not in sys.argv

def fmt(n):
    if n >= 1_073_741_824: return f"{n/1_073_741_824:.1f} Go"
    if n >= 1_048_576:     return f"{n/1_048_576:.0f} Mo"
    return f"{n/1024:.0f} Ko"

print(f"{'=== DRY-RUN ===' if DRY else '=== EXÉCUTION ==='}\n")

# ── Phase 1 : analyser les chevauchements entre OB et ob ─────────────────────
print("ANALYSE DES CHEVAUCHEMENTS : 01-activites réalisées OB  vs  01-activites realisées ob")
print("-"*80)

src_ob  = os.path.join(ROOT, "01-activites réalisées OB")
src_ob2 = os.path.join(ROOT, "01-activites realisées ob")

# Indexer les deux dossiers par chemin relatif
def index_dir(base):
    idx = {}
    for root, dirs, files in os.walk(base):
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, base)
            try:
                idx[rel] = os.path.getsize(fp)
            except OSError:
                pass
    return idx

idx1 = index_dir(src_ob)  if os.path.exists(src_ob)  else {}
idx2 = index_dir(src_ob2) if os.path.exists(src_ob2) else {}

identical = 0
conflicts = []
only_in_1 = 0
only_in_2 = 0

for rel, sz1 in idx1.items():
    if rel in idx2:
        if sz1 == idx2[rel]:
            identical += 1
        else:
            conflicts.append((rel, sz1, idx2[rel]))
    else:
        only_in_1 += 1

for rel in idx2:
    if rel not in idx1:
        only_in_2 += 1

print(f"  Fichiers identiques (même nom+taille) : {identical:>6}  → seront dédupliqués")
print(f"  Conflits (même chemin, taille diff)   : {len(conflicts):>6}  → seront renommés")
print(f"  Uniquement dans 'réalisées OB'        : {only_in_1:>6}")
print(f"  Uniquement dans 'realisées ob'        : {only_in_2:>6}")

if conflicts:
    print(f"\n  Détail des conflits (max 20) :")
    for rel, sz1, sz2 in conflicts[:20]:
        print(f"    {rel}")
        print(f"      OB  : {fmt(sz1)}   ob : {fmt(sz2)}")

# ── Phase 2 : fusion ─────────────────────────────────────────────────────────
print(f"\n\nFUSION → {TARGET}")
print("="*80)

moved = skipped = renamed = errors = 0

for src_name, dst_subdir in SOURCES:
    src = os.path.join(ROOT, src_name)
    if not os.path.exists(src):
        print(f"\n  [ABSENT] {src_name}")
        continue

    dst_base = os.path.join(TARGET, dst_subdir)
    src_files = []
    for root, dirs, files in os.walk(src):
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, src)
            src_files.append((fp, rel))

    n_move = n_skip = n_rename = 0
    for fp, rel in src_files:
        dst = os.path.join(dst_base, rel)
        try:
            src_sz = os.path.getsize(fp)
        except OSError:
            continue

        if os.path.exists(dst):
            try:
                dst_sz = os.path.getsize(dst)
            except OSError:
                dst_sz = -1

            if src_sz == dst_sz:
                # Identique → skip
                n_skip += 1
                skipped += 1
                continue
            else:
                # Conflit → renommer la source avec suffixe _conflict
                base, ext = os.path.splitext(dst)
                dst = base + "_conflict" + ext
                n_rename += 1
                renamed += 1

        if not DRY:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(fp, dst)
        n_move += 1
        moved += 1

    print(f"\n  {src_name}")
    print(f"    Déplacés : {n_move}   Ignorés (doublons) : {n_skip}   Renommés (conflits) : {n_rename}")

# NE PAS supprimer les sources automatiquement — à vérifier manuellement
# (rmtree est dangereux sur NAS case-insensitif : le target peut == source)
if not DRY:
    print("\n  ⚠️  Dossiers sources non supprimés automatiquement.")
    print("     Vérifiez le contenu de _ACTIVITES_MERGE_ puis supprimez les sources à la main.")

print(f"\n{'='*80}")
print(f"TOTAL : déplacés={moved}  ignorés(doublons)={skipped}  renommés(conflits)={renamed}")
if DRY:
    print("\nRelancer avec --execute pour appliquer.")
