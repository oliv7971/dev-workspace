"""
Cleanup 'chambon 15&18 avril 2016': fusionner les 13 uniques dans 01-AVRIL, puis supprimer.

Usage:
    python cleanup_chambon_avril.py          # dry-run
    python cleanup_chambon_avril.py --apply  # execution
"""
import os
import sys
import shutil
import hashlib

DRY_RUN = '--apply' not in sys.argv

BASE37 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\37-TUNNEL GRAND CHAMBON'
SRC = os.path.join(BASE37, 'chambon 15&18 avril 2016')
DST_AVRIL = os.path.join(BASE37, '02-PHASE 02 - Eiffage 2016', '10-ACTIVITES TOPO', '01-AVRIL 2016 - 001 a 013')

# Mapping des sous-dossiers SRC -> DST
# Basé sur l'analyse de correspondance
MAPPING = {
    '001-controle coherence polygo tete aval': '0001-validation polygonale primaire & secondaire - 160415',
    '002-controle coherence Psecondaire - polygo aval': '0003-polygonale tunnel existant - validation et densification 160415',
    '003-controle coherence Psecondaire tunnel & densification 1': '0003-polygonale tunnel existant - validation et densification 160415',
    '004-controle coherence Psecondaire tunnel & densification 2': '0003-polygonale tunnel existant - validation et densification 160415',
    '005-polygonale reservoir': '0002-polygo & leve RESERVOIR - 160415',
    '006_lever_cabane': '0002-polygo & leve RESERVOIR - 160415',
    '007-polygo tete amont': '0004-polygonale tete amont -160415',
    '008-convergences gdtunnel amont': '0010-Convergences existantes - Tunnel Gd & petit Chambon -160418',
    '009-implantation galerie secours': '0006-tabulation axe galerie secours -160414',
    '010-implantation revetement tunnel deviation': '0005-tabulation axe tunnel deviation -160414',
    '011-implantation PM tous 20m': '0009-implantation des pm tunnel existant -160418',
    '012-convergences gd tunnel aval': '0010-Convergences existantes - Tunnel Gd & petit Chambon -160418',
    '013-convergences petit tunnel': '0010-Convergences existantes - Tunnel Gd & petit Chambon -160418',
    'CONVERGENCES GD&PT TUNNEL CHAMBON_tableaux excel': '0010-Convergences existantes - Tunnel Gd & petit Chambon -160418',
}

def quick_hash(filepath, chunk=65536):
    try:
        h = hashlib.md5()
        h.update(str(os.path.getsize(filepath)).encode())
        with open(filepath, 'rb') as f:
            h.update(f.read(chunk))
        return h.hexdigest()
    except:
        return None

def fmt(size):
    if size > 1073741824: return f'{size/1073741824:.2f} Go'
    if size > 1048576: return f'{size/1048576:.0f} Mo'
    if size > 1024: return f'{size/1024:.0f} Ko'
    return f'{size} o'

print('=' * 80)
print(f'CLEANUP chambon 15&18 avril 2016')
print(f'Mode: {"DRY-RUN" if DRY_RUN else "APPLY"}')
print('=' * 80)

if not os.path.exists(SRC):
    print('ERREUR: dossier source introuvable!')
    sys.exit(1)

# Construire index DST par hash et nom+taille
print('\n--- Index de 01-AVRIL ---')
dst_hashes = set()
dst_name_size = set()
for dp, dirs, files in os.walk(DST_AVRIL):
    for f in files:
        full = os.path.join(dp, f)
        try:
            sz = os.path.getsize(full)
            h = quick_hash(full)
            if h: dst_hashes.add(h)
            dst_name_size.add((f.lower(), sz))
        except:
            pass
print(f'  {len(dst_hashes)} hashes indexes')

# Scanner SRC et identifier les uniques
print('\n--- Analyse des fichiers ---')
copied = 0
skipped = 0
errors = 0
total_copy_size = 0

for src_subdir in sorted(os.listdir(SRC)):
    src_path = os.path.join(SRC, src_subdir)
    if not os.path.isdir(src_path):
        # Fichier a la racine - ignorer ou copier
        continue
    
    dst_subdir = MAPPING.get(src_subdir)
    if not dst_subdir:
        print(f'  WARN: pas de mapping pour {src_subdir}')
        continue
    
    dst_base = os.path.join(DST_AVRIL, dst_subdir)
    
    for dp, dirs, files in os.walk(src_path):
        for f in files:
            src_file = os.path.join(dp, f)
            try:
                sz = os.path.getsize(src_file)
                h = quick_hash(src_file)
            except:
                continue
            
            is_dup = False
            if h and h in dst_hashes:
                is_dup = True
            elif (f.lower(), sz) in dst_name_size:
                is_dup = True
            
            if is_dup:
                skipped += 1
                continue
            
            # Fichier unique - copier vers le bon sous-dossier
            # On place dans un sous-dossier du nom d'origine pour garder la trace
            rel = os.path.relpath(src_file, src_path)
            dst_file = os.path.join(dst_base, src_subdir, rel)
            
            print(f'  COPY {src_subdir}/{rel}')
            print(f'    -> {dst_subdir}/{src_subdir}/{rel}')
            
            if not DRY_RUN:
                try:
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    print(f'    OK')
                    copied += 1
                    total_copy_size += sz
                except Exception as e:
                    print(f'    ERREUR: {e}')
                    errors += 1
            else:
                copied += 1
                total_copy_size += sz

# Suppression
print(f'\n--- Suppression de chambon 15&18 avril 2016 ---')
del_files = sum(len(files) for _, _, files in os.walk(SRC))
del_size = sum(os.path.getsize(os.path.join(d, f)) for d, _, files in os.walk(SRC) for f in files)
print(f'  A supprimer: {del_files} fichiers, {fmt(del_size)}')
print(f'  DELETE {os.path.basename(SRC)}/')

if not DRY_RUN:
    if errors > 0:
        print(f'  ABANDON: {errors} erreurs, on ne supprime pas')
    else:
        try:
            shutil.rmtree(SRC)
            print(f'    OK')
        except Exception as e:
            print(f'    ERREUR: {e}')
else:
    print(f'    (dry-run)')

# Resume
print(f'\n{"=" * 80}')
print(f'RESULTAT')
print(f'{"=" * 80}')
print(f'  Fichiers copies:    {copied} ({fmt(total_copy_size)})')
print(f'  Doublons ignores:   {skipped}')
if not DRY_RUN:
    print(f'  Erreurs:            {errors}')
else:
    print(f'  A liberer:          {fmt(del_size)}')
    print(f'\n  -> Relancer avec --apply pour executer')
