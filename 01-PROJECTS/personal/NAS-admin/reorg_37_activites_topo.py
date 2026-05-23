"""Reorganisation de 10-ACTIVITES TOPO.
Les dossiers 0xxx-description-YYMMDD à la racine doivent etre classes
dans les dossiers mois (01-AVRIL, 02-MAI, etc.).

On analyse chaque dossier numerote, determine son mois, et verifie
s'il est deja present dans le dossier mois.

Usage:
  python reorg_37_activites_topo.py           # analyse seule
  python reorg_37_activites_topo.py --apply   # deplacement
"""
import os
import sys
import re
import hashlib
from collections import defaultdict

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON\02-PHASE 02 - Eiffage 2016\10-ACTIVITES TOPO'
APPLY = '--apply' in sys.argv

# Mapping mois par plage de numeros (d'apres les noms de dossiers mois existants)
# 01-AVRIL 2016 - 001 a 013
# 02-MAI 2016 - 014 a 057
# 03-JUIN 2016 - 058 a 156
# 04-JULLET 2016 - 156 a 265
# 05-AOUT 2016 - 265 a 340
# 06-SEPTEMBRE 2016 - 340 a 446
# 07-OCTOBRE 2016   (447+)
# 08-NOVEMBRE 2016
# 09-DECEMBRE 2016

MONTH_RANGES = [
    (1, 13, '01-AVRIL 2016 - 001 a 013'),
    (14, 57, '02-MAI 2016 - 014 a 057'),
    (58, 155, '03-JUIN 2016 - 058 a 156'),
    (156, 265, '04-JULLET 2016 - 156 a 265'),
    (265, 340, '05-AOUT 2016 - 265 a 340'),
    (340, 446, '06-SEPTEMBRE 2016 - 340 a 446'),
]

# Pour les numeros > 446, on utilise la date dans le nom pour determiner le mois
MONTH_BY_DATE = {
    '10': '07-OCTOBRE 2016',
    '11': '08-NOVEMBRE 2016',
    '12': '09-DECEMBRE 2016',
}

# Aussi utiliser les dates 1604=avril, 1605=mai, etc
DATE_MONTH_MAP = {
    '04': '01-AVRIL 2016 - 001 a 013',
    '05': '02-MAI 2016 - 014 a 057',
    '06': '03-JUIN 2016 - 058 a 156',
    '07': '04-JULLET 2016 - 156 a 265',
    '08': '05-AOUT 2016 - 265 a 340',
    '09': '06-SEPTEMBRE 2016 - 340 a 446',
    '10': '07-OCTOBRE 2016',
    '11': '08-NOVEMBRE 2016',
    '12': '09-DECEMBRE 2016',
}

def get_month_by_number(num):
    """Determine le dossier mois par le numero d'activite."""
    for lo, hi, folder in MONTH_RANGES:
        if lo <= num <= hi:
            return folder
    return None

def get_month_by_date_in_name(name):
    """Essaie d'extraire une date du nom pour determiner le mois."""
    # Pattern YYMMDD ou YYYYMMDD
    m = re.search(r'(\d{2})(\d{2})(\d{2})(?!\d)', name)
    if m:
        yy, mm, dd = m.groups()
        if yy == '16' or yy == '20':
            if yy == '20':
                # Chercher YYYYMMDD
                m2 = re.search(r'2016(\d{2})(\d{2})', name)
                if m2:
                    mm = m2.group(1)
            if mm in DATE_MONTH_MAP:
                return DATE_MONTH_MAP[mm]
    
    # Pattern -160XXX ou 2016XX
    m = re.search(r'16(\d{2})\d{2}', name)
    if m:
        mm = m.group(1)
        if mm in DATE_MONTH_MAP:
            return DATE_MONTH_MAP[mm]
    
    m = re.search(r'2016(\d{2})', name)
    if m:
        mm = m.group(1)
        if mm in DATE_MONTH_MAP:
            return DATE_MONTH_MAP[mm]
    
    return None

def count_files(path):
    """Compte les fichiers recursivement."""
    total = 0
    for _, _, files in os.walk(path):
        total += len(files)
    return total

def get_file_hashes(path):
    """Retourne un set de (filename, size) pour comparaison rapide."""
    result = set()
    for dirpath, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(dirpath, f)
            try:
                result.add((f, os.path.getsize(fp)))
            except:
                pass
    return result

# Lister les elements a la racine
print("=" * 110)
print("ANALYSE DE 10-ACTIVITES TOPO")
print("=" * 110)
print(f"Mode: {'APPLY' if APPLY else 'ANALYSE'}")
print()

items = sorted(os.listdir(BASE))

# Separer les dossiers mois, les dossiers numerotes, et les autres
month_dirs = []
numbered_dirs = []
other_items = []

for name in items:
    path = os.path.join(BASE, name)
    if os.path.isdir(path):
        # Dossier mois : commence par 01- a 09- suivi d'un mois
        if re.match(r'^\d{2}-(AVRIL|MAI|JUIN|JULLET|AOUT|SEPTEMBRE|OCTOBRE|NOVEMBRE|DECEMBRE)', name):
            month_dirs.append(name)
        # Dossier numerote : commence par 0XXX-
        elif re.match(r'^0\d{2,3}[\s-]', name):
            numbered_dirs.append(name)
        # Dossier numerote sans zero : comme 563-, 998-, 999-
        elif re.match(r'^\d{3}[\s-]', name):
            numbered_dirs.append(name)
        else:
            other_items.append(('D', name))
    else:
        other_items.append(('F', name))

print(f"Dossiers mois: {len(month_dirs)}")
print(f"Dossiers numerotes a la racine: {len(numbered_dirs)}")
print(f"Autres: {len(other_items)}")

# Inventorier ce qui est deja dans les dossiers mois
print(f"\n{'=' * 110}")
print("CONTENU DES DOSSIERS MOIS")
print("=" * 110)

month_subdirs = {}  # month_name -> set of subdir names
for md in month_dirs:
    md_path = os.path.join(BASE, md)
    subs = set()
    for s in os.listdir(md_path):
        if os.path.isdir(os.path.join(md_path, s)):
            subs.add(s)
    month_subdirs[md] = subs
    print(f"\n  {md}/ ({len(subs)} sous-dossiers)")
    for s in sorted(subs)[:5]:
        print(f"    {s}/")
    if len(subs) > 5:
        print(f"    ... et {len(subs)-5} autres")

# Analyser chaque dossier numerote
print(f"\n{'=' * 110}")
print("DOSSIERS NUMEROTES A CLASSER")
print("=" * 110)

actions = []  # (source_name, target_month, status, details)

for name in numbered_dirs:
    src_path = os.path.join(BASE, name)
    n_files = count_files(src_path)
    
    # Extraire le numero
    m = re.match(r'^0*(\d+)', name)
    num = int(m.group(1)) if m else 0
    
    # Determiner le mois cible
    target = get_month_by_number(num)
    if not target:
        target = get_month_by_date_in_name(name)
    
    if not target:
        actions.append((name, None, 'INCONNU', f'{n_files} fich, pas de mois identifie'))
        continue
    
    # Verifier si deja present dans le dossier mois
    if target in month_subdirs and name in month_subdirs[target]:
        # Deja present - comparer le contenu
        dest_path = os.path.join(BASE, target, name)
        src_files = get_file_hashes(src_path)
        dst_files = get_file_hashes(dest_path)
        
        common = src_files & dst_files
        only_src = src_files - dst_files
        
        if not only_src:
            actions.append((name, target, 'DOUBLON', f'{n_files} fich, 100% dans {target}/{name}'))
        else:
            actions.append((name, target, 'PARTIEL', f'{n_files} fich, {len(only_src)} uniques'))
    else:
        actions.append((name, target, 'A_DEPLACER', f'{n_files} fich -> {target}/'))

# Afficher les resultats
by_status = defaultdict(list)
for name, target, status, details in actions:
    by_status[status].append((name, target, details))

for status in ['DOUBLON', 'PARTIEL', 'A_DEPLACER', 'INCONNU']:
    items = by_status.get(status, [])
    if not items:
        continue
    print(f"\n  [{status}] ({len(items)} dossiers)")
    for name, target, details in items:
        print(f"    {name:65s} {details}")

# Autres elements
if other_items:
    print(f"\n  [AUTRES] ({len(other_items)} elements)")
    for typ, name in other_items:
        print(f"    {'[D]' if typ == 'D' else '[F]'} {name}")

# Resume
print(f"\n{'=' * 110}")
print("RESUME")
print("=" * 110)
doublons = by_status.get('DOUBLON', [])
partiels = by_status.get('PARTIEL', [])
a_deplacer = by_status.get('A_DEPLACER', [])
inconnus = by_status.get('INCONNU', [])

print(f"  Doublons (supprimables): {len(doublons)}")
print(f"  Partiels (fusionner): {len(partiels)}")
print(f"  A deplacer: {len(a_deplacer)}")
print(f"  Inconnus: {len(inconnus)}")

if not APPLY:
    print(f"\nRelancer avec --apply pour executer les deplacements")
else:
    import shutil
    
    moved = 0
    fused = 0
    deleted = 0
    errors = []
    
    # 1. Deplacer les A_DEPLACER
    print(f"\n--- DEPLACEMENTS ---")
    for name, target, details in a_deplacer:
        src = os.path.join(BASE, name)
        dst = os.path.join(BASE, target, name)
        print(f"  MOVE {name} -> {target}/")
        if os.path.exists(dst):
            print(f"    SKIP: destination existe deja")
            continue
        try:
            shutil.move(src, dst)
            moved += 1
            print(f"    OK")
        except Exception as e:
            print(f"    ERREUR: {e}")
            errors.append((name, str(e)))
    
    # 2. Fusionner les PARTIEL (copier les uniques, puis supprimer)
    print(f"\n--- FUSIONS ---")
    for name, target, details in partiels:
        src_path = os.path.join(BASE, name)
        dst_path = os.path.join(BASE, target, name)
        
        if not os.path.exists(dst_path):
            # Pas de destination = deplacer tout
            print(f"  MOVE {name} -> {target}/")
            try:
                shutil.move(src_path, dst_path)
                moved += 1
                print(f"    OK")
            except Exception as e:
                print(f"    ERREUR: {e}")
                errors.append((name, str(e)))
            continue
        
        # Destination existe, copier les uniques
        src_files = get_file_hashes(src_path)
        dst_files = get_file_hashes(dst_path)
        only_src = src_files - dst_files
        
        if only_src:
            print(f"  FUSION {name}: {len(only_src)} fichiers uniques -> {target}/{name}/")
            for fn, sz in only_src:
                # Trouver le fichier source
                for dirpath, _, files in os.walk(src_path):
                    if fn in files:
                        src_file = os.path.join(dirpath, fn)
                        rel = os.path.relpath(dirpath, src_path)
                        dst_dir = os.path.join(dst_path, rel) if rel != '.' else dst_path
                        dst_file = os.path.join(dst_dir, fn)
                        if not os.path.exists(dst_file):
                            os.makedirs(dst_dir, exist_ok=True)
                            try:
                                shutil.copy2(src_file, dst_file)
                                fused += 1
                                print(f"    COPY {fn}")
                            except Exception as e:
                                print(f"    ERREUR copy {fn}: {e}")
                                errors.append((fn, str(e)))
                        break
        
        # Supprimer le dossier source
        print(f"  DELETE {name}/")
        try:
            shutil.rmtree(src_path)
            deleted += 1
            print(f"    OK")
        except Exception as e:
            print(f"    ERREUR delete: {e}")
            errors.append((name, str(e)))
    
    # 3. Supprimer les DOUBLON
    print(f"\n--- SUPPRESSIONS DOUBLONS ---")
    for name, target, details in doublons:
        src = os.path.join(BASE, name)
        print(f"  DELETE {name}/")
        try:
            shutil.rmtree(src)
            deleted += 1
            print(f"    OK")
        except Exception as e:
            print(f"    ERREUR: {e}")
            errors.append((name, str(e)))
    
    # 4. Gerer les petits orphelins
    # _160918 -> 06-SEPTEMBRE (date 160918)
    orphan_moves = {
        '_160918': '06-SEPTEMBRE 2016 - 340 a 446',
        '563-auscultation amont 161026': '07-OCTOBRE 2016',
        '_temp plan fond de fouille amont': None,  # garder
    }
    # Les fichiers racine et dossiers inconnus: deplacer dans _a_trier
    a_trier = os.path.join(BASE, '_a_trier')
    
    print(f"\n--- ORPHELINS ---")
    for typ, name in other_items:
        src = os.path.join(BASE, name)
        if name in orphan_moves and orphan_moves[name]:
            dst = os.path.join(BASE, orphan_moves[name], name)
            print(f"  MOVE {name} -> {orphan_moves[name]}/")
        else:
            os.makedirs(a_trier, exist_ok=True)
            dst = os.path.join(a_trier, name)
            print(f"  MOVE {name} -> _a_trier/")
        
        if os.path.exists(dst):
            print(f"    SKIP: existe deja")
            continue
        try:
            shutil.move(src, dst)
            moved += 1
            print(f"    OK")
        except Exception as e:
            print(f"    ERREUR: {e}")
            errors.append((name, str(e)))
    
    # Dossiers inconnus -> _a_trier
    for name, target, details in inconnus:
        src = os.path.join(BASE, name)
        os.makedirs(a_trier, exist_ok=True)
        dst = os.path.join(a_trier, name)
        print(f"  MOVE {name} -> _a_trier/")
        if os.path.exists(dst):
            print(f"    SKIP: existe deja")
            continue
        try:
            shutil.move(src, dst)
            moved += 1
            print(f"    OK")
        except Exception as e:
            print(f"    ERREUR: {e}")
            errors.append((name, str(e)))
    
    print(f"\n{'=' * 110}")
    print(f"RESULTAT")
    print(f"{'=' * 110}")
    print(f"  Deplaces: {moved}")
    print(f"  Fichiers fusionnes: {fused}")
    print(f"  Dossiers supprimes: {deleted}")
    if errors:
        print(f"  Erreurs: {len(errors)}")
        for n, e in errors:
            print(f"    {n}: {e}")
