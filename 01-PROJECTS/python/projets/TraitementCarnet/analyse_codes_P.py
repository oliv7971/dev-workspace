import re

# Lire le fichier
with open('carnet/auscultations GGS-251128 -A.geo', 'r', encoding='latin-1') as f:
    lignes = f.readlines()

# Extraire les points GGS
points_gps = {}
for ligne in lignes:
    match = re.match(r'\S+\s+Point\s+(\d+)\.GGS\.(\d+)([GD])', ligne)
    if match:
        numero = match.group(1)
        code = match.group(2)
        cote = match.group(3)
        if numero not in points_gps:
            points_gps[numero] = {}
        points_gps[numero][cote] = code

# Extraire les mesures Pxxx
mesures_p = {}
for ligne in lignes:
    match = re.match(r'\S+\s+Mesure\s+S[12]\.P(\d+)([GD])', ligne)
    if match:
        numero = match.group(1).lstrip('0')  # Enlever les zéros de tête
        cote = match.group(2)
        if numero not in mesures_p:
            mesures_p[numero] = set()
        mesures_p[numero].add(cote)

# Afficher les correspondances trouvées
print("=" * 80)
print("CORRESPONDANCES DÉTECTÉES")
print("=" * 80)

correspondances = []
for num_p in sorted(mesures_p.keys(), key=int):
    if num_p in points_gps:
        for cote in sorted(mesures_p[num_p]):
            if cote in points_gps[num_p]:
                code_gps = points_gps[num_p][cote]
                ancien = f"P{num_p.zfill(3)}{cote}"
                nouveau = f"{num_p}.GGS.{code_gps}{cote}"
                correspondances.append((ancien, nouveau))
                print(f"✓ P{num_p.zfill(3)}{cote:1s}  →  {num_p}.GGS.{code_gps}{cote}")

# Afficher les mesures P sans correspondance
print(f"\n{'=' * 80}")
print("MESURES P SANS POINT GGS CORRESPONDANT")
print("=" * 80)

sans_correspondance = []
for num_p in sorted(mesures_p.keys(), key=int):
    if num_p not in points_gps:
        for cote in sorted(mesures_p[num_p]):
            ancien = f"P{num_p.zfill(3)}{cote}"
            sans_correspondance.append(ancien)
            print(f"⚠️  P{num_p.zfill(3)}{cote:1s}  →  Pas de point {num_p}.GGS.xx{cote} trouvé")
    else:
        for cote in sorted(mesures_p[num_p]):
            if cote not in points_gps[num_p]:
                ancien = f"P{num_p.zfill(3)}{cote}"
                sans_correspondance.append(ancien)
                print(f"⚠️  P{num_p.zfill(3)}{cote:1s}  →  {num_p}.GGS.??{cote} (côté manquant)")

# Points GGS sans mesure P
print(f"\n{'=' * 80}")
print("POINTS GGS SANS MESURE P")
print("=" * 80)

for num in sorted(points_gps.keys(), key=int):
    if num not in mesures_p:
        for cote, code in sorted(points_gps[num].items()):
            print(f"ℹ️  {num}.GGS.{code}{cote}  →  Pas de mesure P{num.zfill(3)}{cote}")

print(f"\n{'=' * 80}")
print(f"RÉSUMÉ : {len(correspondances)} correspondances | {len(sans_correspondance)} sans correspondance")
print("=" * 80)
