# analyse_devp_cpp.py -- Analyse DEVP vs CPP : sont-ils vraiment identiques ?
# Compare par nom+taille, puis identifie les uniques de chaque cote

import os
from collections import defaultdict

BASE = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT'
DEVP = os.path.join(BASE, 'DEVP')
CPP  = os.path.join(BASE, 'CPP')

def collect(folder):
    files = {}
    for root, dirs, fnames in os.walk(folder):
        for f in fnames:
            fp = os.path.join(root, f)
            rel = fp[len(folder)+1:]
            try:
                sz = os.path.getsize(fp)
            except OSError:
                sz = -1
            key_path = rel.lower()
            key_name = (f.lower(), sz)
            files[key_path] = (rel, sz, key_name)
    return files

print('Collecte DEVP...')
devp = collect(DEVP)
print('Collecte CPP...')
cpp  = collect(CPP)

print(f'\nDEVP : {len(devp)} fichiers')
print(f'CPP  : {len(cpp)} fichiers')

# Comparaison par chemin relatif (meme arborescence ?)
same_path_same_size = []
same_path_diff_size = []
only_devp = []
only_cpp  = []

all_paths = set(devp.keys()) | set(cpp.keys())
for p in sorted(all_paths):
    if p in devp and p in cpp:
        if devp[p][1] == cpp[p][1]:
            same_path_same_size.append(p)
        else:
            same_path_diff_size.append((p, devp[p][1], cpp[p][1]))
    elif p in devp:
        only_devp.append(devp[p])
    else:
        only_cpp.append(cpp[p])

print(f'\nMeme chemin + meme taille : {len(same_path_same_size)}')
print(f'Meme chemin + taille diff : {len(same_path_diff_size)}')
print(f'Uniquement dans DEVP      : {len(only_devp)}')
print(f'Uniquement dans CPP       : {len(only_cpp)}')

if same_path_diff_size:
    print('\nChemins communs avec taille differente (premiers 10) :')
    for p, s1, s2 in same_path_diff_size[:10]:
        print(f'  {p}  DEVP:{s1}  CPP:{s2}')

print('\n--- Uniques dans DEVP (absents de CPP) ---')
for rel, sz, _ in sorted(only_devp, key=lambda x: x[0])[:40]:
    print(f'  {rel}')
if len(only_devp) > 40:
    print(f'  ... et {len(only_devp)-40} autres')

print('\n--- Uniques dans CPP (absents de DEVP) ---')
for rel, sz, _ in sorted(only_cpp, key=lambda x: x[0])[:40]:
    print(f'  {rel}')
if len(only_cpp) > 40:
    print(f'  ... et {len(only_cpp)-40} autres')

# Extensions des uniques
def ext_count(items):
    d = defaultdict(int)
    for rel, sz, _ in items:
        d[os.path.splitext(rel)[1].lower() or '(none)'] += 1
    return sorted(d.items(), key=lambda x: -x[1])

print('\nExtensions uniques DEVP :', dict(ext_count(only_devp)[:10]))
print('Extensions uniques CPP  :', dict(ext_count(only_cpp)[:10]))

# Sous-dossiers de premier niveau
def subdirs(folder):
    try:
        return sorted(e.name for e in os.scandir(folder) if e.is_dir())
    except:
        return []

print('\nSous-dossiers DEVP :', subdirs(DEVP))
print('Sous-dossiers CPP  :', subdirs(CPP))
