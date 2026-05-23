"""
Réorganisation de 01-SFTRF :
Distribution des données 51-TMS et 52-CYCLONE vers les dossiers par zone géographique.

Principe : les données TMS (station totale) et CYCLONE (nuage de points) sont actuellement
dans des dossiers par logiciel. On les redistribue vers les dossiers par zone.

Usage:
  python reorg_sftrf.py            # Dry-run
  python reorg_sftrf.py --execute  # Exécution réelle
"""
import os
import sys
import shutil

BASE = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\01-SFTRF"
DRY_RUN = "--execute" not in sys.argv

def format_size(b):
    for u in ['o','Ko','Mo','Go','To']:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024

def folder_size(path):
    """Taille totale d'un dossier ou fichier."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
    except:
        pass
    return total

# ═══════════════════════════════════════════════════════════════════════
# RÈGLES DE DÉPLACEMENT
# Format : (source_relative, dest_relative, description)
# Les chemins sont relatifs à BASE
# ═══════════════════════════════════════════════════════════════════════

moves = [
    # ── 51-TMS → 01-TUNNEL ROUTIER FREJUS ──
    ("51-TMS\\01 - TUNNEL ROUTIER DU FREJUS",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\01 - TUNNEL ROUTIER DU FREJUS",
     "TMS tunnel routier → dossier tunnel routier"),

    ("51-TMS\\02-ROUTIER NOUVEAU AXE- OB 20170420",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\02-ROUTIER NOUVEAU AXE- OB 20170420",
     "TMS nouvel axe routier → dossier tunnel routier"),

    ("51-TMS\\axes etude frejus",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\axes etude frejus",
     "Axes d'étude → tunnel routier"),

    ("51-TMS\\nouv axe test",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\nouv axe test",
     "Test nouvel axe → tunnel routier"),

    ("51-TMS\\FREJUS-SPINX-2019",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\FREJUS-SPINX-2019",
     "SPINX 2019 → tunnel routier"),

    ("51-TMS\\FREJUS-st318.zip",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\FREJUS-st318.zip",
     "Archive ST318 → tunnel routier"),

    ("51-TMS\\test",
     "01-TUNNEL ROUTIER FREJUS\\51-tms\\test",
     "Tests → tunnel routier"),

    # ── 51-TMS → 02-GALERIE SECU FREJUS (tunnelier + entrée) ──
    ("51-TMS\\FREJUS-MARS17-RAZEL AXE LISSE",
     "02-GALERIE SECU FREJUS\\51-tms-tunnelier\\FREJUS-MARS17-RAZEL AXE LISSE",
     "TMS tunnelier Razel mars 2017 → galerie sécu"),

    ("51-TMS\\Chambre mont&lancmt",
     "02-GALERIE SECU FREJUS\\51-tms-tunnelier\\Chambre montage et lancement",
     "TMS chambre de montage → galerie sécu"),

    ("51-TMS\\rampe caverne",
     "02-GALERIE SECU FREJUS\\51-tms-tunnelier\\rampe caverne",
     "TMS rampe caverne → galerie sécu"),

    ("51-TMS\\scantbm",
     "02-GALERIE SECU FREJUS\\51-tms-tunnelier\\scantbm",
     "Scans TBM → galerie sécu"),

    ("51-TMS\\frejus-tbm-pour-tests",
     "02-GALERIE SECU FREJUS\\51-tms-tunnelier\\frejus-tbm-pour-tests",
     "Tests TBM → galerie sécu"),

    ("51-TMS\\FREJUS DECEMBRE 2015 - nouvel axe",
     "02-GALERIE SECU FREJUS\\51-tms-entree\\FREJUS DECEMBRE 2015 - nouvel axe",
     "TMS entrée tunnel déc 2015 → galerie sécu"),

    ("51-TMS\\FREJUS DECEMBRE 2015 - nouvel axe.zip",
     "02-GALERIE SECU FREJUS\\51-tms-entree\\FREJUS DECEMBRE 2015 - nouvel axe.zip",
     "Archive entrée tunnel → galerie sécu"),

    # ── 51-TMS → 16-RAMEAUX ET BP (rameaux + abris) ──
    ("51-TMS\\Rameau3 abri",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\Rameau3 abri",
     "TMS Rameau 3 abri → rameaux"),

    ("51-TMS\\Rameau 6 abri",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\Rameau 6 abri",
     "TMS Rameau 6 abri → rameaux"),

    ("51-TMS\\Rameau2 abri",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\Rameau2 abri",
     "TMS Rameau 2 abri → rameaux"),

    ("51-TMS\\Rameau2 SAS",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\Rameau2 SAS",
     "TMS Rameau 2 SAS → rameaux"),

    ("51-TMS\\rameau9 abri",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\rameau9 abri",
     "TMS Rameau 9 abri → rameaux"),

    ("51-TMS\\fréjus rameau1",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\frejus rameau1",
     "TMS Rameau 1 → rameaux"),

    ("51-TMS\\porteram1.1",
     "16-RAMEAUX ET BP\\51-tms-rameaux\\porteram1.1",
     "TMS porte rameau 1 → rameaux"),

    # ── 51-TMS → 11-SOCAMO ──
    ("51-TMS\\socamo",
     "11-SOCAMO\\51-tms-socamo",
     "TMS Socamo → dossier Socamo"),

    # ── 51-TMS → GEM/PUITS (nouveau dossier) ──
    ("51-TMS\\GEM puits",
     "05-GEM-PUITS\\tms",
     "TMS GEM puits → nouveau dossier GEM"),

    # ── 51-TMS → _ACLASSER (pas lié au SFTRF) ──
    ("51-TMS\\A43 Chy OASncf",
     "_ACLASSER\\A43 Chy OASncf",
     "A43 pas lié à SFTRF → à classer"),

    # ═══════════════════════════════════════════════════════════════
    # 52-CYCLONE → zones
    # ═══════════════════════════════════════════════════════════════

    # ── 52-CYCLONE → 16-RAMEAUX ET BP (BP + rameaux) ──
    ("52-CYCLONE\\FREJUS_BP3",
     "16-RAMEAUX ET BP\\52-cyclone-bp\\FREJUS_BP3",
     "Cyclone BP3 → rameaux/BP"),

    ("52-CYCLONE\\FREJUS_BP4",
     "16-RAMEAUX ET BP\\52-cyclone-bp\\FREJUS_BP4",
     "Cyclone BP4 → rameaux/BP"),

    ("52-CYCLONE\\FERJUS_BP4",
     "16-RAMEAUX ET BP\\52-cyclone-bp\\FREJUS_BP4_ancien",
     "Cyclone BP4 (typo FERJUS corrigée) → rameaux/BP"),

    ("52-CYCLONE\\rameau6",
     "16-RAMEAUX ET BP\\52-cyclone-rameaux\\rameau6",
     "Cyclone rameau 6 → rameaux"),

    # ── 52-CYCLONE → GEM ──
    ("52-CYCLONE\\frejus-gem",
     "05-GEM-PUITS\\cyclone",
     "Cyclone GEM → GEM/puits"),

    # ── 52-CYCLONE → GAF/GAV ──
    ("52-CYCLONE\\frejus-debouche-gav",
     "15-GAF GAV\\cyclone-debouche-gav",
     "Cyclone débouché GAV → GAF/GAV"),

    # ── 52-CYCLONE → tests restent ──
    ("52-CYCLONE\\tests_frejus",
     "52-CYCLONE\\tests_frejus",
     None),  # reste en place

    # ═══════════════════════════════════════════════════════════════
    # RENOMMAGES de top-level pour clarifier ce qui reste
    # ═══════════════════════════════════════════════════════════════

    # 51-TMS ne contiendra plus que frejus2010 (29 Go) et FREJUS (22 Go)
    # = données TMS mixtes multi-zones de 2010+ et stations techniques
    # On renomme pour clarifier
]

# Renommages séparés (après les moves)
renames = [
    ("51-TMS", "51-TMS-DONNEES-MIXTES",
     "Renommer 51-TMS (ne contient plus que frejus2010 + FREJUS = données mixtes)"),

    ("52-CYCLONE", "52-CYCLONE-GENERAL",
     "Renommer 52-CYCLONE (ne contient plus que le workspace général 'frejus')"),
]

# ═══════════════════════════════════════════════════════════════════════
# EXÉCUTION
# ═══════════════════════════════════════════════════════════════════════

print("=" * 80)
print("RÉORGANISATION DE 01-SFTRF")
print("Distribution des données TMS et CYCLONE par zone géographique")
print("=" * 80)

# Filter out no-ops
moves = [(s, d, desc) for s, d, desc in moves if desc is not None]

# Phase 1: Verify sources exist
print("\n--- VÉRIFICATION DES SOURCES ---")
valid_moves = []
missing = 0
for src_rel, dst_rel, desc in moves:
    src = os.path.join(BASE, src_rel)
    exists = os.path.exists(src)
    status = "✅" if exists else "❌ MANQUANT"
    if exists:
        sz = folder_size(src)
        print(f"  {status} {src_rel:60s} ({format_size(sz)})")
        valid_moves.append((src_rel, dst_rel, desc, sz))
    else:
        print(f"  {status} {src_rel}")
        missing += 1

print(f"\n  Sources valides : {len(valid_moves)}/{len(moves)}")
if missing:
    print(f"  Sources manquantes : {missing} (ignorées)")

# Phase 2: Show plan
print("\n" + "=" * 80)
print("PLAN DE DÉPLACEMENT")
print("=" * 80)

total_move_size = 0
for src_rel, dst_rel, desc, sz in valid_moves:
    total_move_size += sz
    print(f"\n  📦 {desc}")
    print(f"     DE:  {src_rel}")
    print(f"     VERS: {dst_rel}")
    print(f"     Taille: {format_size(sz)}")

print(f"\n  Total à déplacer: {format_size(total_move_size)} ({len(valid_moves)} dossiers/fichiers)")

# Phase 2b: Show renames
print("\n" + "=" * 80)
print("RENOMMAGES")
print("=" * 80)
for old_rel, new_rel, desc in renames:
    old = os.path.join(BASE, old_rel)
    if os.path.exists(old):
        print(f"  📝 {desc}")
        print(f"     {old_rel} → {new_rel}")

if DRY_RUN:
    print("\n🔍 DRY-RUN : aucun déplacement effectué.")
    print("   Relancez avec --execute pour exécuter.")
else:
    print(f"\n🚚 DÉPLACEMENTS EN COURS...")
    success = 0
    errors = 0

    for src_rel, dst_rel, desc, sz in valid_moves:
        src = os.path.join(BASE, src_rel)
        dst = os.path.join(BASE, dst_rel)

        try:
            # Créer le dossier parent de destination
            dst_parent = os.path.dirname(dst)
            if not os.path.exists(dst_parent):
                os.makedirs(dst_parent)

            # Vérifier que la destination n'existe pas déjà
            if os.path.exists(dst):
                print(f"  ⚠️  Destination existe déjà: {dst_rel}")
                errors += 1
                continue

            # Déplacer (os.rename = instantané sur même volume)
            try:
                os.rename(src, dst)
            except OSError:
                # Fallback: shutil.move (plus lent mais cross-device)
                shutil.move(src, dst)

            success += 1
            print(f"  ✅ {desc} ({format_size(sz)})")

        except Exception as e:
            errors += 1
            print(f"  ❌ ERREUR: {desc}")
            print(f"     {e}")

    # Renommages
    print(f"\n📝 RENOMMAGES EN COURS...")
    for old_rel, new_rel, desc in renames:
        old = os.path.join(BASE, old_rel)
        new = os.path.join(BASE, new_rel)
        try:
            if os.path.exists(old) and not os.path.exists(new):
                os.rename(old, new)
                print(f"  ✅ {old_rel} → {new_rel}")
            elif not os.path.exists(old):
                print(f"  ⚠️  {old_rel} n'existe plus (déjà déplacé/renommé ?)")
            else:
                print(f"  ⚠️  {new_rel} existe déjà")
        except Exception as e:
            print(f"  ❌ ERREUR: {e}")

    print(f"\n✅ Terminé !")
    print(f"  Déplacements réussis : {success}/{len(valid_moves)}")
    if errors:
        print(f"  Erreurs : {errors}")

# Summary of new structure
print("\n" + "=" * 80)
print("STRUCTURE RÉSULTANTE (après réorganisation)")
print("=" * 80)
print("""
  01-SFTRF/
    01-TUNNEL ROUTIER FREJUS/
      ├── 51-tms/                    ← TMS tunnel routier (depuis 51-TMS)
      ├── 60-PROJETS RECAP/          (existant)
      ├── TUNNEL DU FREJUS/          (existant)
      ├── convergences.../           (existant)
      └── ...

    02-GALERIE SECU FREJUS/
      ├── 51-tms-tunnelier/          ← TMS tunnelier/TBM (depuis 51-TMS)
      ├── 51-tms-entree/             ← TMS entrée tunnel (depuis 51-TMS)
      ├── 01b Controles topos.../    (existant)
      └── ...

    03-POLYGONALE/                   (inchangé)
    04-MONITORING/                   (inchangé)
    05-AUSCULTATIONS/                (inchangé → renommé de 05-)
    05-GEM-PUITS/
      ├── tms/                       ← TMS GEM (depuis 51-TMS)
      └── cyclone/                   ← Cyclone GEM (depuis 52-CYCLONE)

    11-SOCAMO/
      ├── TMS socamo/                (existant)
      └── 51-tms-socamo/             ← TMS Socamo (depuis 51-TMS)

    12-GOLET/                        (inchangé)
    13-USINES/                       (inchangé)
    15-GAF GAV/
      ├── leve_gafgav13aout/         (existant)
      └── cyclone-debouche-gav/      ← Cyclone GAV (depuis 52-CYCLONE)

    16-RAMEAUX ET BP/
      ├── 51-tms-rameaux/            ← TMS rameaux/abris (depuis 51-TMS)
      ├── 52-cyclone-bp/             ← Cyclone BP3+BP4 (depuis 52-CYCLONE)
      ├── 52-cyclone-rameaux/        ← Cyclone rameau6 (depuis 52-CYCLONE)
      ├── SCAN BP3.../               (existant)
      ├── SCAN BP4.../               (existant)
      └── ...

    20-limite frontiere/             (inchangé)
    21-Documents d'exécution/        (inchangé)
    40-Photos/                       (inchangé)

    51-TMS-DONNEES-MIXTES/           ← Renommé (reste frejus2010 + FREJUS)
    52-CYCLONE-GENERAL/              ← Renommé (reste workspace 'frejus')

    _ACLASSER/                       (+ A43 Chy OASncf)
""")
