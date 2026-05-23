"""
Compare les fichiers de _extracted vs le reste du dossier
par nom + taille d'abord, puis hash MD5 sur les candidats.
"""
import sqlite3
import hashlib
import os
from collections import defaultdict

DB = "reports/inventory_voussoirs_smp4.db"
ROOT = "\\\\Nas_travail\\01-ds414-data\\31-GGC-DOSSIERS\\34-controle voussoirs SMP4\\"
EXTRACTED_PREFIX = ROOT + "_extracted\\"

def human_size(n):
    for u in ["o", "Ko", "Mo", "Go"]:
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} Go"

def md5(path, chunk=1024*1024):
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while True:
                data = f.read(chunk)
                if not data:
                    break
                h.update(data)
        return h.hexdigest()
    except Exception as e:
        return None

c = sqlite3.connect(DB)
rows = c.execute("SELECT path, size, filename FROM files WHERE size > 0").fetchall()
c.close()

# Séparer _extracted vs reste
extracted = {}   # {(filename, size): [paths]}
others = {}      # {(filename, size): [paths]}

for path, size, filename in rows:
    key = (filename, size)
    if path.startswith(EXTRACTED_PREFIX):
        extracted.setdefault(key, []).append(path)
    else:
        others.setdefault(key, []).append(path)

# Trouver les candidats (même nom + même taille dans les deux zones)
candidates = set(extracted.keys()) & set(others.keys())

print(f"Fichiers dans _extracted       : {len(extracted)}")
print(f"Fichiers hors _extracted       : {len(others)}")
print(f"Candidats doublons (nom+taille): {len(candidates)}")

total_size_candidates = sum(k[1] for k in candidates)
print(f"Taille totale candidates       : {human_size(total_size_candidates)}")

# Vérification MD5 sur un échantillon de candidats
# On prend les 50 plus gros pour valider
top_candidates = sorted(candidates, key=lambda k: -k[1])[:50]

print(f"\nVérification MD5 sur les {len(top_candidates)} plus gros candidats...")
confirmed_duplicates = []
different = []
errors = []

for i, (fname, size) in enumerate(top_candidates):
    ex_paths = extracted[(fname, size)]
    ot_paths = others[(fname, size)]
    
    # Prendre un exemplaire de chaque côté
    p1 = ex_paths[0]
    p2 = ot_paths[0]
    
    h1 = md5(p1)
    h2 = md5(p2)
    
    if h1 is None or h2 is None:
        errors.append((fname, size, p1, p2))
        status = "ERREUR"
    elif h1 == h2:
        confirmed_duplicates.append((fname, size, p1, p2))
        status = "IDENTIQUE"
    else:
        different.append((fname, size, p1, p2))
        status = "DIFFERENT"
    
    print(f"  [{i+1:2d}/{len(top_candidates)}] {status:10s}  {human_size(size):>10}  {fname[:60]}")

# Résumé
print(f"\n{'='*70}")
print(f"RÉSUMÉ VÉRIFICATION MD5")
print(f"{'='*70}")
print(f"  Identiques (vrais doublons) : {len(confirmed_duplicates)}")
print(f"  Différents (même nom/taille): {len(different)}")
print(f"  Erreurs d'accès            : {len(errors)}")

if different:
    print(f"\nFICHIERS DIFFÉRENTS malgré même nom+taille :")
    for fname, size, p1, p2 in different[:10]:
        print(f"  {human_size(size):>10}  {fname}")
        print(f"    _extracted : {p1[len(ROOT):]}")
        print(f"    autre      : {p2[len(ROOT):]}")

# Estimation de l'espace récupérable si on supprime _extracted
total_extracted_size = sum(v for (_, v) in extracted.keys())
confirmed_size = sum(size for (_, size, _, _) in confirmed_duplicates)
print(f"\nEspace total dans _extracted     : {human_size(sum(size for (_, size) in extracted.keys()))}")
print(f"Espace confirmé doublon (top 50) : {human_size(confirmed_size)}")
print(f"Candidats totaux (nom+taille)    : {len(candidates)} fichiers = {human_size(total_size_candidates)}")
