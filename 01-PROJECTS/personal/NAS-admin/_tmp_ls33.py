import os

base = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS'
for d in sorted(os.listdir(base)):
    if d.startswith('33'):
        full = os.path.join(base, d)
        print(f'{d}/')
        if os.path.isdir(full):
            for sub in sorted(os.listdir(full)):
                subfull = os.path.join(full, sub)
                if os.path.isdir(subfull):
                    print(f'  {sub}/')
                else:
                    sz = os.path.getsize(subfull)
                    print(f'  {sub}  ({sz//1024} Ko)')
