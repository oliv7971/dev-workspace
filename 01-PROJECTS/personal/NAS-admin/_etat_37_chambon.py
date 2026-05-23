"""Etat actuel de 37-TUNNEL GRAND CHAMBON apres cleanup."""
import os

BASE = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'

print('=' * 90)
print('ETAT ACTUEL de 37-TUNNEL GRAND CHAMBON')
print('=' * 90)

total_files = 0
total_size = 0
entries = []

for name in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, name)
    if os.path.isdir(p):
        try:
            count = sum(len(files) for _, _, files in os.walk(p))
            size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(p) for f in files)
            entries.append(('D', name, count, size))
            total_files += count
            total_size += size
        except Exception as e:
            entries.append(('D', name, -1, 0))
    else:
        try:
            size = os.path.getsize(p)
            entries.append(('F', name, 1, size))
            total_files += 1
            total_size += size
        except:
            entries.append(('F', name, 1, 0))

for typ, name, count, size in entries:
    if size > 1073741824: sz = f'{size/1073741824:.2f} Go'
    elif size > 1048576: sz = f'{size/1048576:.0f} Mo'
    elif size > 1024: sz = f'{size/1024:.0f} Ko'
    else: sz = f'{size} o'
    
    if typ == 'D':
        if count >= 0:
            print(f'  {name + "/":60s} {count:>6} fich  {sz:>10}')
        else:
            print(f'  {name + "/":60s}  ERREUR')
    else:
        print(f'  [F] {name:57s} {sz:>10}')

print(f'\n  TOTAL: {total_files} fichiers, {total_size/1073741824:.2f} Go')

# Detail Phase 02
print(f'\n{"=" * 90}')
print('DETAIL de 02-PHASE 02 - Eiffage 2016')
print('=' * 90)
ph2 = os.path.join(BASE, '02-PHASE 02 - Eiffage 2016')
if os.path.exists(ph2):
    ph2_total_f = 0
    ph2_total_s = 0
    for name in sorted(os.listdir(ph2)):
        p = os.path.join(ph2, name)
        if os.path.isdir(p):
            try:
                count = sum(len(files) for _, _, files in os.walk(p))
                size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(p) for f in files)
                if size > 1073741824: sz = f'{size/1073741824:.2f} Go'
                elif size > 1048576: sz = f'{size/1048576:.0f} Mo'
                else: sz = f'{size/1024:.0f} Ko'
                print(f'  {name + "/":60s} {count:>6} fich  {sz:>10}')
                ph2_total_f += count
                ph2_total_s += size
            except:
                print(f'  {name + "/":60s}  ERREUR')
        else:
            sz = os.path.getsize(p)
            print(f'  [F] {name:57s} {sz}')
            ph2_total_f += 1
            ph2_total_s += sz
    print(f'\n  Phase 02 total: {ph2_total_f} fichiers, {ph2_total_s/1073741824:.2f} Go')
