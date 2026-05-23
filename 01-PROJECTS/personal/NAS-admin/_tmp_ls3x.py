import os

base = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS'
for d in sorted(os.listdir(base)):
    if d.startswith('3'):
        print(f'  {d}/')
