import os

CANAL = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\RENAISON 2015\00-DONNEES-BRUTES-CANAL\renaison_canal_evacuateur'

# Fichiers à la racine
print("=== Fichiers racine renaison_canal_evacuateur/ ===")
for fn in sorted(os.listdir(CANAL)):
    fp = os.path.join(CANAL, fn)
    if os.path.isfile(fp):
        print(f"  {fn}  ({os.path.getsize(fp)//1024} Ko)")

# Sous-dossiers ambigus
print()
for sub in ['renaison_bassinCentral.1', 'Setoutrenaison_bassinCentral', 'Setoutrenaison_canalEV', '10-TRUVIEW']:
    folder = os.path.join(CANAL, sub)
    if not os.path.exists(folder):
        print(f"=== {sub}/ : INTROUVABLE ===")
        continue
    total = [(os.path.join(r,fn), os.path.getsize(os.path.join(r,fn)))
             for r,d,f in os.walk(folder) for fn in f]
    size_mb = sum(s for _,s in total) // 1024 // 1024
    print(f"=== {sub}/ : {len(total)} fichiers, {size_mb} Mo ===")
    for fp, sz in sorted(total):
        rel = fp.replace(CANAL+'\\', '')
        print(f"  {rel}  ({sz//1024} Ko)")

# scan/ RENAISON 20150617
print()
scan617 = os.path.join(CANAL, 'scan', 'RENAISON 20150617')
if os.path.exists(scan617):
    total = [(os.path.join(r,fn), os.path.getsize(os.path.join(r,fn)))
             for r,d,f in os.walk(scan617) for fn in f]
    print(f"=== scan/RENAISON 20150617/ : {len(total)} fichiers ===")
    for fp, sz in sorted(total):
        rel = fp.replace(CANAL+'\\', '')
        print(f"  {rel}  ({sz//1024//1024} Mo)")
