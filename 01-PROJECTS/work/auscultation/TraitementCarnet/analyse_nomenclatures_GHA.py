import re
from collections import defaultdict

# Lire le fichier
with open('carnet/GHA-auscultation 251201-A.geo', 'r', encoding='latin-1') as f:
    lignes = f.readlines()

# Extraire tous les points avec nomenclatures différentes
points_par_prefixe = defaultdict(list)

for ligne in lignes:
    match_point = re.match(r'\S+\s+Point\s+(\S+)', ligne)
    if match_point:
        nom = match_point.group(1)
        
        # Identifier le préfixe
        if re.match(r'\d+\.S\.GHA\.', nom):
            points_par_prefixe['xxx.S.GHA.xx'].append(nom)
        elif re.match(r'\d+\.i\.GHA\.', nom) or re.match(r'\d+i\.GHA\.', nom):
            points_par_prefixe['xxx.i.GHA.xx'].append(nom)
        elif re.match(r'\d+\.I\.GHA\.', nom):
            points_par_prefixe['xxx.I.GHA.xx'].append(nom)
        elif re.match(r'\d+GMA\.', nom):
            points_par_prefixe['xxGMA.xx'].append(nom)
        elif re.match(r'\d+\.GV3\.', nom) or re.match(r'\d+GV3\.', nom):
            points_par_prefixe['xxGV3.xx'].append(nom)
        elif re.match(r'C\.\d+', nom):
            points_par_prefixe['C.xxx'].append(nom)
        elif re.match(r'REF_S\d+', nom):
            points_par_prefixe['REF_Sxxxx'].append(nom)
        elif re.match(r'ST\.', nom):
            points_par_prefixe['ST.xxx'].append(nom)
        elif re.match(r'C\d+\.FRONT\.GHA', nom):
            points_par_prefixe['Cx.FRONT.GHA'].append(nom)

# Extraire les mesures avec préfixes P.xxx
mesures_p = defaultdict(list)
for ligne in lignes:
    match_mesure = re.match(r'\S+\s+Mesure\s+(P\.\d+[GD])', ligne)
    if match_mesure:
        nom = match_mesure.group(1)
        mesures_p['P.xxx'].append(nom)
    
    # Mesures avec préfixes S.xxx (stations de référence)
    match_s = re.match(r'\S+\s+Mesure\s+(S\.\d+)', ligne)
    if match_s:
        nom = match_s.group(1)
        mesures_p['S.xxx'].append(nom)
    
    # Mesures avec codes Sxxx (stations de référence sans point)
    match_s2 = re.match(r'\S+\s+Mesure\s+(S\d{3,4})', ligne)
    if match_s2:
        nom = match_s2.group(1)
        mesures_p['Sxxx'].append(nom)
    
    # Mesures avec codes C.xxx (repères)
    match_c = re.match(r'\S+\s+Mesure\s+(C\.\d+)', ligne)
    if match_c:
        nom = match_c.group(1)
        mesures_p['C.xxx_mesure'].append(nom)

print("=" * 100)
print("ANALYSE DES NOMENCLATURES DANS LE CARNET")
print("=" * 100)

print("\n📋 POINTS (définitions de coordonnées):")
print("-" * 100)
for prefixe, liste in sorted(points_par_prefixe.items()):
    print(f"\n{prefixe:20s} ({len(set(liste))} points uniques)")
    exemples = sorted(set(liste))[:5]
    for ex in exemples:
        print(f"  • {ex}")
    if len(set(liste)) > 5:
        print(f"  ... et {len(set(liste)) - 5} autres")

print("\n\n📐 MESURES (observations):")
print("-" * 100)
for prefixe, liste in sorted(mesures_p.items()):
    print(f"\n{prefixe:20s} ({len(set(liste))} mesures uniques)")
    exemples = sorted(set(liste))[:5]
    for ex in exemples:
        print(f"  • {ex}")
    if len(set(liste)) > 5:
        print(f"  ... et {len(set(liste)) - 5} autres")

print("\n" + "=" * 100)
print("CORRESPONDANCES À RECHERCHER")
print("=" * 100)

# Chercher les correspondances P.xxx
print("\n🔍 Correspondances potentielles P.xxx :")
mesures_p_uniques = sorted(set([m for m in mesures_p.get('P.xxx', [])]))
for mesure in mesures_p_uniques[:10]:
    # Extraire le numéro
    match = re.match(r'P\.(\d+)([GD])', mesure)
    if match:
        num = match.group(1).lstrip('0') or '0'
        cote = match.group(2)
        
        # Chercher dans les points
        candidats = []
        for pt_list in points_par_prefixe.values():
            for pt in pt_list:
                if f'{num}' in pt or f'{num.zfill(2)}' in pt or f'{num.zfill(3)}' in pt:
                    candidats.append(pt)
        
        if candidats:
            candidats_uniques = list(set(candidats))[:3]
            print(f"  {mesure:15s} → Candidats: {', '.join(candidats_uniques)}")
        else:
            print(f"  {mesure:15s} → Aucun candidat trouvé")

print("\n" + "=" * 100)
