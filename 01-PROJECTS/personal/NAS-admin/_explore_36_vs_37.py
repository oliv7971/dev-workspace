"""Compare 36-TUNNEL GRAND CHAMBON (sous-dossier de 37) avec le contenu de 37."""
import os
import hashlib
from collections import defaultdict

BASE37 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'
PATH36_IN_37 = os.path.join(BASE37, '36-TUNNEL GRAND CHAMBON')
BASE36_SEPARATE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\36-TUNNEL GRAND CHAMBON'

def quick_hash(filepath, chunk=65536):
    """Hash rapide basé sur taille + premiers 64Ko."""
    try:
        size = os.path.getsize(filepath)
        h = hashlib.md5()
        h.update(str(size).encode())
        with open(filepath, 'rb') as f:
            h.update(f.read(chunk))
        return h.hexdigest()
    except:
        return None

def scan_dir(base):
    """Retourne {relpath: (size, hash)} pour tous les fichiers."""
    result = {}
    for dirpath, dirs, files in os.walk(base):
        for f in files:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, base)
            try:
                size = os.path.getsize(full)
                result[rel] = (size, quick_hash(full))
            except:
                result[rel] = (0, None)
    return result

# 1) Lister L1 de 37 (etat actuel)
print('=' * 80)
print('ETAT ACTUEL de 37-TUNNEL GRAND CHAMBON (L1)')
print('=' * 80)
total_files = 0
total_size = 0
for name in sorted(os.listdir(BASE37)):
    p = os.path.join(BASE37, name)
    if os.path.isdir(p):
        try:
            count = sum(len(files) for _, _, files in os.walk(p))
            size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(p) for f in files)
            if size > 1073741824: sz = f'{size/1073741824:.2f} Go'
            elif size > 1048576: sz = f'{size/1048576:.0f} Mo'
            else: sz = f'{size/1024:.0f} Ko'
            print(f'  {name:60s} {count:>6} fich  {sz:>10}')
            total_files += count
            total_size += size
        except Exception as e:
            print(f'  {name:60s} ERREUR: {e}')
    else:
        sz = os.path.getsize(p)
        print(f'  [F] {name:57s} {sz:>10}')
        total_files += 1
        total_size += sz

print(f'\nTotal: {total_files} fichiers, {total_size/1073741824:.2f} Go')

# 2) Verifier si 36-TUNNEL GRAND CHAMBON existe dans 37
print()
print('=' * 80)
if os.path.exists(PATH36_IN_37):
    print(f'36-TUNNEL GRAND CHAMBON EXISTE dans 37 (sous-dossier)')
    print('=' * 80)
    
    # Lister son contenu
    for name in sorted(os.listdir(PATH36_IN_37)):
        p = os.path.join(PATH36_IN_37, name)
        if os.path.isdir(p):
            try:
                count = sum(len(files) for _, _, files in os.walk(p))
                size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(p) for f in files)
                if size > 1073741824: sz = f'{size/1073741824:.2f} Go'
                elif size > 1048576: sz = f'{size/1048576:.0f} Mo'
                else: sz = f'{size/1024:.0f} Ko'
                print(f'  {name:60s} {count:>6} fich  {sz:>10}')
            except Exception as e:
                print(f'  {name:60s} ERREUR: {e}')
        else:
            sz = os.path.getsize(p)
            print(f'  [F] {name:57s} {sz:>10}')
    
    # Scanner les fichiers de 36 dans 37
    print('\n--- Analyse des doublons ---')
    files_36 = scan_dir(PATH36_IN_37)
    print(f'Fichiers dans 36-TUNNEL GRAND CHAMBON: {len(files_36)}')
    total_36_size = sum(s for s, _ in files_36.values())
    print(f'Taille totale: {total_36_size/1073741824:.2f} Go')
    
    # Construire un index par hash de tout le reste de 37
    print('\nConstruction index du reste de 37...')
    hash_index_37 = {}  # hash -> [(relpath, size)]
    name_size_index_37 = {}  # (name, size) -> [relpath]
    
    for name in os.listdir(BASE37):
        if name == '36-TUNNEL GRAND CHAMBON':
            continue
        p = os.path.join(BASE37, name)
        if os.path.isdir(p):
            for dirpath, dirs, files in os.walk(p):
                for f in files:
                    full = os.path.join(dirpath, f)
                    rel = os.path.relpath(full, BASE37)
                    try:
                        size = os.path.getsize(full)
                        h = quick_hash(full)
                        if h:
                            hash_index_37.setdefault(h, []).append((rel, size))
                        name_size_index_37.setdefault((f.lower(), size), []).append(rel)
                    except:
                        pass
        else:
            try:
                size = os.path.getsize(p)
                h = quick_hash(p)
                if h:
                    hash_index_37.setdefault(h, []).append((name, size))
                name_size_index_37.setdefault((name.lower(), size), []).append(name)
            except:
                pass
    
    print(f'Index construit: {len(hash_index_37)} hashes uniques dans le reste de 37')
    
    # Comparer
    found_by_hash = 0
    found_by_name_size = 0
    unique_files = []
    found_size = 0
    unique_size = 0
    
    for rel, (size, h) in files_36.items():
        matched = False
        if h and h in hash_index_37:
            found_by_hash += 1
            found_size += size
            matched = True
        elif not matched:
            fname = os.path.basename(rel).lower()
            if (fname, size) in name_size_index_37:
                found_by_name_size += 1
                found_size += size
                matched = True
        
        if not matched:
            unique_files.append((rel, size))
            unique_size += size
    
    print(f'\n--- RESULTATS ---')
    print(f'Doublons par hash:        {found_by_hash:>6} fichiers  ({found_by_hash*100/len(files_36):.1f}%)')
    print(f'Doublons par nom+taille:  {found_by_name_size:>6} fichiers  ({found_by_name_size*100/len(files_36):.1f}%)')
    print(f'Fichiers uniques:         {len(unique_files):>6} fichiers  ({len(unique_files)*100/len(files_36):.1f}%)')
    print(f'\nTaille doublons:  {found_size/1073741824:.2f} Go')
    print(f'Taille uniques:   {unique_size/1073741824:.2f} Go')
    
    if unique_files:
        print(f'\n--- Fichiers uniques (top 30 par taille) ---')
        unique_files.sort(key=lambda x: -x[1])
        for rel, size in unique_files[:30]:
            if size > 1048576: sz = f'{size/1048576:.0f} Mo'
            elif size > 1024: sz = f'{size/1024:.0f} Ko'
            else: sz = f'{size} o'
            print(f'  {sz:>8}  {rel}')
        if len(unique_files) > 30:
            print(f'  ... et {len(unique_files) - 30} autres')
    
    # Grouper uniques par sous-dossier L1
    if unique_files:
        print(f'\n--- Uniques par sous-dossier ---')
        by_dir = defaultdict(lambda: [0, 0])
        for rel, size in unique_files:
            parts = rel.split(os.sep)
            top = parts[0] if len(parts) > 1 else '(racine)'
            by_dir[top][0] += 1
            by_dir[top][1] += size
        for d, (cnt, sz) in sorted(by_dir.items(), key=lambda x: -x[1][1]):
            if sz > 1048576: szs = f'{sz/1048576:.0f} Mo'
            else: szs = f'{sz/1024:.0f} Ko'
            print(f'  {d:55s} {cnt:>5} fich  {szs:>8}')

else:
    print('36-TUNNEL GRAND CHAMBON n\'existe PAS dans 37')

# 3) Verifier aussi si 36 existe comme dossier separe
print()
print('=' * 80)
if os.path.exists(BASE36_SEPARATE):
    print('36-TUNNEL GRAND CHAMBON existe AUSSI comme dossier separe au niveau 31-GGC-DOSSIERS')
    count = sum(len(files) for _, _, files in os.walk(BASE36_SEPARATE))
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(BASE36_SEPARATE) for f in files)
    print(f'  {count} fichiers, {size/1073741824:.2f} Go')
else:
    print('36-TUNNEL GRAND CHAMBON n\'existe PAS comme dossier separe')
print('=' * 80)
