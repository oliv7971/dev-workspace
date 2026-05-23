import os, random

src_root = r'\\Nas_louhans_2\01-ds420-data\10-INFORMATIQUE\11-DEVELOPPEMENT\dataroom'
dst_root = r'\\Nas_louhans_2\01-ds420-data\30-RESSOURCES\05-GEOMATIQUE\dataroom'

# Compter par sous-dossier de niveau 1
print('=== Comparaison par sous-dossier de niveau 1 ===')
for folder in sorted(os.scandir(src_root), key=lambda e: e.name):
    src_path = folder.path
    dst_path = os.path.join(dst_root, folder.name)
    if folder.is_dir():
        # Compter seulement les sous-dossiers immédiats
        src_subs = [e.name for e in os.scandir(src_path)]
        dst_subs = [e.name for e in os.scandir(dst_path)] if os.path.exists(dst_path) else []
        src_top = set(src_subs)
        dst_top = set(dst_subs)
        missing_in_dst = src_top - dst_top
        print(f'  {folder.name}/  src:{len(src_subs)}  dst:{len(dst_subs)}  absent_dst:{len(missing_in_dst)}')
        if missing_in_dst:
            print(f'    manquants: {list(missing_in_dst)[:5]}')
    else:
        dst_file = os.path.join(dst_root, folder.name)
        if os.path.exists(dst_file):
            ok = os.path.getsize(folder.path) == os.path.getsize(dst_file)
            print(f'  {folder.name}  {"OK" if ok else "DIFF-SIZE"}')
        else:
            print(f'  {folder.name}  ABSENT-DST')

# Echantillon de 50 fichiers dans Raster (premier niveau)
print('\n=== Echantillon 50 fichiers dans DATA/Raster/ ===')
raster_src = os.path.join(src_root, 'DATA', 'Raster')
raster_dst = os.path.join(dst_root, 'DATA', 'Raster')
if os.path.exists(raster_src):
    files = list(os.scandir(raster_src))
    # Ne prendre que les fichiers directs (pas de walk)
    direct_files = [e for e in files if e.is_file()]
    sample = random.sample(direct_files, min(50, len(direct_files)))
    ok = 0
    absent = 0
    for f in sample:
        dst_f = os.path.join(raster_dst, f.name)
        if os.path.exists(dst_f):
            ok += 1
        else:
            absent += 1
            print(f'  ABSENT DST : {f.name}')
    print(f'  {ok}/50 presents en destination, {absent} absents')
    print(f'  (Raster/ a {len(files)} items directs au total)')
