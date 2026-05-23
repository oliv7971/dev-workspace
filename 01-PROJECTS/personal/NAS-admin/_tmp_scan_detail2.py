import os
canal = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\RENAISON 2015\00-DONNEES-BRUTES-CANAL\renaison_canal_evacuateur'

for sub in ['scan', '02-SCANS']:
    folder = os.path.join(canal, sub)
    print(f'\n=== {sub}/ ===')
    if not os.path.exists(folder):
        print('  INTROUVABLE')
        continue
    total_files = 0
    total_size = 0
    for r, d, f in os.walk(folder):
        rel = r.replace(canal, '').lstrip('\\') or sub
        for fn in f:
            fp = os.path.join(r, fn)
            sz = os.path.getsize(fp)
            total_files += 1
            total_size += sz
            print(f'  {rel}/{fn}  {sz//1024//1024} Mo')
    print(f'  TOTAL: {total_files} fichiers, {total_size//1024//1024} Mo')
