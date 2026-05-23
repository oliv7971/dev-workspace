"""Compare 'chambon 15&18 avril 2016' vs '01-AVRIL 2016 - 001 a 013' dans Phase 02."""
import os
import hashlib
from collections import defaultdict

BASE37 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'
SRC = os.path.join(BASE37, 'chambon 15&18 avril 2016')
DST = os.path.join(BASE37, '02-PHASE 02 - Eiffage 2016', '10-ACTIVITES TOPO', '01-AVRIL 2016 - 001 a 013')

def quick_hash(filepath, chunk=65536):
    try:
        h = hashlib.md5()
        h.update(str(os.path.getsize(filepath)).encode())
        with open(filepath, 'rb') as f:
            h.update(f.read(chunk))
        return h.hexdigest()
    except:
        return None

def scan(base):
    result = []
    for dp, dirs, files in os.walk(base):
        for f in files:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, base)
            try:
                sz = os.path.getsize(full)
                h = quick_hash(full)
                result.append((rel, f, sz, h))
            except:
                result.append((rel, f, 0, None))
    return result

def fmt(size):
    if size > 1073741824: return f'{size/1073741824:.2f} Go'
    if size > 1048576: return f'{size/1048576:.0f} Mo'
    if size > 1024: return f'{size/1024:.0f} Ko'
    return f'{size} o'

# 1) Lister les deux dossiers
print('=' * 90)
print('COMPARAISON')
print('  SRC: chambon 15&18 avril 2016')
print('  DST: 02-PHASE 02/.../01-AVRIL 2016 - 001 a 013')
print('=' * 90)

print('\n--- Contenu de SRC ---')
if not os.path.exists(SRC):
    print('  INTROUVABLE!')
    exit()
for name in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, name)
    if os.path.isdir(p):
        count = sum(len(files) for _, _, files in os.walk(p))
        size = sum(os.path.getsize(os.path.join(d,f)) for d,_,files in os.walk(p) for f in files)
        print(f'  {name:55s} {count:>5} fich  {fmt(size):>8}')
    else:
        sz = os.path.getsize(p)
        print(f'  [F] {name:52s} {fmt(sz):>8}')

print('\n--- Contenu de DST ---')
if not os.path.exists(DST):
    print('  INTROUVABLE!')
    exit()
for name in sorted(os.listdir(DST)):
    p = os.path.join(DST, name)
    if os.path.isdir(p):
        count = sum(len(files) for _, _, files in os.walk(p))
        size = sum(os.path.getsize(os.path.join(d,f)) for d,_,files in os.walk(p) for f in files)
        print(f'  {name:55s} {count:>5} fich  {fmt(size):>8}')
    else:
        sz = os.path.getsize(p)
        print(f'  [F] {name:52s} {fmt(sz):>8}')

# 2) Scanner et comparer
src_files = scan(SRC)
dst_files = scan(DST)

src_total = sum(sz for _, _, sz, _ in src_files)
dst_total = sum(sz for _, _, sz, _ in dst_files)
print(f'\nSRC: {len(src_files)} fichiers, {fmt(src_total)}')
print(f'DST: {len(dst_files)} fichiers, {fmt(dst_total)}')

# Index DST par hash et par nom+taille
dst_hashes = set()
dst_name_size = set()
for rel, fn, sz, h in dst_files:
    if h: dst_hashes.add(h)
    dst_name_size.add((fn.lower(), sz))

# Index SRC par hash et par nom+taille
src_hashes = set()
src_name_size = set()
for rel, fn, sz, h in src_files:
    if h: src_hashes.add(h)
    src_name_size.add((fn.lower(), sz))

# SRC -> doublons dans DST ?
print('\n--- SRC vu depuis DST ---')
src_dup_h = 0
src_dup_ns = 0
src_uniq = []
src_dup_sz = 0
src_uniq_sz = 0
for rel, fn, sz, h in src_files:
    if h and h in dst_hashes:
        src_dup_h += 1
        src_dup_sz += sz
    elif (fn.lower(), sz) in dst_name_size:
        src_dup_ns += 1
        src_dup_sz += sz
    else:
        src_uniq.append((rel, sz))
        src_uniq_sz += sz

print(f'Doublons hash:      {src_dup_h:>5}  {fmt(src_dup_sz - sum(sz for _, _, sz, _ in src_files if (_.lower() if _ else "", sz) in dst_name_size and not (_ and _ in dst_hashes)))}')
# Simplifions
t = len(src_files)
print(f'Doublons (hash):    {src_dup_h:>5} ({src_dup_h*100//max(t,1)}%)')
print(f'Doublons (nom+sz):  {src_dup_ns:>5} ({src_dup_ns*100//max(t,1)}%)')
print(f'Uniques dans SRC:   {len(src_uniq):>5} ({len(src_uniq)*100//max(t,1)}%)  {fmt(src_uniq_sz)}')

if src_uniq:
    print(f'\n--- Fichiers SRC uniques (pas dans DST) ---')
    src_uniq.sort(key=lambda x: -x[1])
    for rel, sz in src_uniq[:30]:
        print(f'  {fmt(sz):>8}  {rel}')
    if len(src_uniq) > 30:
        print(f'  ... et {len(src_uniq)-30} autres')

# DST -> doublons dans SRC ?
print('\n--- DST vu depuis SRC ---')
dst_uniq = []
dst_dup = 0
for rel, fn, sz, h in dst_files:
    if h and h in src_hashes:
        dst_dup += 1
    elif (fn.lower(), sz) in src_name_size:
        dst_dup += 1
    else:
        dst_uniq.append((rel, sz))

print(f'Doublons dans SRC:  {dst_dup:>5}')
print(f'Uniques dans DST:   {len(dst_uniq):>5}  {fmt(sum(s for _,s in dst_uniq))}')

if dst_uniq:
    print(f'\n--- Fichiers DST uniques (pas dans SRC) ---')
    dst_uniq.sort(key=lambda x: -x[1])
    for rel, sz in dst_uniq[:30]:
        print(f'  {fmt(sz):>8}  {rel}')
    if len(dst_uniq) > 30:
        print(f'  ... et {len(dst_uniq)-30} autres')

# Aussi comparer avec TOUT 10-ACTIVITES TOPO (pas juste 01-AVRIL)
print('\n--- SRC vs TOUT 10-ACTIVITES TOPO ---')
topo_base = os.path.join(BASE37, '02-PHASE 02 - Eiffage 2016', '10-ACTIVITES TOPO')
topo_hashes = set()
topo_ns = set()
for dp, dirs, files in os.walk(topo_base):
    for f in files:
        full = os.path.join(dp, f)
        try:
            sz = os.path.getsize(full)
            h = quick_hash(full)
            if h: topo_hashes.add(h)
            topo_ns.add((f.lower(), sz))
        except:
            pass

topo_dup_h = 0
topo_dup_ns = 0
topo_uniq = []
for rel, fn, sz, h in src_files:
    if h and h in topo_hashes:
        topo_dup_h += 1
    elif (fn.lower(), sz) in topo_ns:
        topo_dup_ns += 1
    else:
        topo_uniq.append((rel, sz))

print(f'Doublons hash:    {topo_dup_h:>5}')
print(f'Doublons nom+sz:  {topo_dup_ns:>5}')
print(f'Uniques:          {len(topo_uniq):>5}  {fmt(sum(s for _,s in topo_uniq))}')

if topo_uniq:
    print(f'\nFichiers SRC uniques meme vs tout 10-ACTIVITES TOPO:')
    topo_uniq.sort(key=lambda x: -x[1])
    for rel, sz in topo_uniq[:20]:
        print(f'  {fmt(sz):>8}  {rel}')
