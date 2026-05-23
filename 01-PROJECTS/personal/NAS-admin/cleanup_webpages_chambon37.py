"""Supprime les pages web sauvegardées dans 37-TUNNEL GRAND CHAMBON.

Cible :
 - Dossiers *_fichiers  (pages IE/Chrome sauvegardées)
 - Fichiers sans extension dans des contextes web connus (dyndns, presse...)
 - Fichiers .htm / .html associés à des pages sauvegardées

Usage :
  python cleanup_webpages_chambon37.py           → dry-run
  python cleanup_webpages_chambon37.py --execute → suppression réelle
"""
import os, sys, shutil, sqlite3

BASE    = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON"
DB      = "reports/inventory_chambon37.db"
EXECUTE = "--execute" in sys.argv

def human_size(n):
    if not n: n = 0
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

# Identifie les dossiers *_fichiers sur le filesystem
targets_dirs  = []   # dossiers entiers à supprimer
targets_files = []   # fichiers isolés à supprimer

print(f"\n{'='*72}")
print(f"SUPPRESSION PAGES WEB SAUVEGARDÉES — {'EXÉCUTION' if EXECUTE else 'DRY-RUN'}")
print(f"{'='*72}\n")

total_size = 0
total_count = 0

for dirpath, dirnames, filenames in os.walk(BASE, topdown=True):
    # Dossiers *_fichiers (pages web IE/Firefox)
    for d in list(dirnames):
        if d.endswith("_fichiers"):
            full = os.path.join(dirpath, d)
            # Compter contenu
            cnt = sum(len(fs) for _, _, fs in os.walk(full))
            sz  = sum(os.path.getsize(os.path.join(dp, f))
                      for dp, _, fs in os.walk(full) for f in fs)
            rel = full[len(BASE)+1:]
            print(f"  📁  {rel[:65]}  ({cnt} fich., {human_size(sz)})")
            targets_dirs.append((full, cnt, sz))
            total_count += cnt
            total_size  += sz
            dirnames.remove(d)   # ne pas descendre dedans

    # Fichiers .htm/.html autonomes (page sauvegardée principale)
    for f in filenames:
        if f.lower().endswith((".htm", ".html")):
            full = os.path.join(dirpath, f)
            # Vérifie qu'un dossier _fichiers du même nom existe à côté
            base_name = os.path.splitext(f)[0]
            companion = os.path.join(dirpath, base_name + "_fichiers")
            if os.path.isdir(companion) or not os.path.isfile(full):
                continue
            # Même sans companion, on inclut les .htm dans les dossiers connus
            rel = full[len(BASE)+1:]
            if any(kw in rel.lower() for kw in ["presse", "dyndns", "_fichiers"]):
                sz = os.path.getsize(full)
                print(f"  📄  {rel[:65]}  ({human_size(sz)})")
                targets_files.append((full, sz))
                total_count += 1
                total_size  += sz

print(f"\n  Total à supprimer : {total_count} fichiers  {human_size(total_size)}")

if not EXECUTE:
    print(f"\n⚠️  DRY-RUN — aucun fichier supprimé.")
    print(f"   Relancer avec : python cleanup_webpages_chambon37.py --execute")
    sys.exit(0)

# --- Exécution ---
deleted_dirs = 0
deleted_files = 0
errors = 0

for full, cnt, sz in targets_dirs:
    try:
        shutil.rmtree(full)
        deleted_dirs += 1
    except Exception as e:
        print(f"  ❌  {full[-60:]}  — {e}")
        errors += 1

for full, sz in targets_files:
    try:
        os.remove(full)
        deleted_files += 1
    except Exception as e:
        print(f"  ❌  {full[-60:]}  — {e}")
        errors += 1

print(f"\n✅ Dossiers supprimés : {deleted_dirs}")
print(f"✅ Fichiers supprimés : {deleted_files}")
if errors:
    print(f"❌ Erreurs           : {errors}")
print(f"   Volume libéré      : {human_size(total_size)}")
