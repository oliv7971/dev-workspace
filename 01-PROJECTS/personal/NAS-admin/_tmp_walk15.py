import os
base15 = r'\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\09-BARRAGES RENAISON\RENAISON 2015'
for r,d,f in os.walk(base15):
    depth = r.replace(base15,'').count(os.sep)
    if depth <= 3:
        rel = r.replace(base15,'') or '\\'
        print(f'  {"  "*depth}{rel}  [{len(f)} fich]')
