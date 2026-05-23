import os

base = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\33-controle voussoirs SMP4'
total_files = 0
total_size = 0

for r, dirs, files in os.walk(base):
    depth = r.replace(base, '').count(os.sep)
    if depth <= 2:
        rel = r.replace(base, '').lstrip('\\') or '(racine)'
        n = len(files)
        sz = sum(os.path.getsize(os.path.join(r, f)) for f in files)
        total_files += n
        total_size += sz
        if n > 0 or depth <= 1:
            indent = '  ' * depth
            print(f'{indent}{rel}  [{n} fich, {sz/1024/1024:.0f} Mo]')

print(f'\nTOTAL: {total_files} fichiers, {total_size/1024/1024/1024:.1f} Go')
