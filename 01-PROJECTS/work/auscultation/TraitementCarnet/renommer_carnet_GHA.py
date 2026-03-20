import re

# Lire le fichier
with open('carnet/GHA-auscultation 251201-A.geo', 'r', encoding='latin-1') as f:
    lignes = f.readlines()

# Liste des renommages
renommages = [
    ('P.001G', '01GMA.11G'),
    ('P.001D', '01GMA.13D'),
    ('P.009G', '009.i.GHA.4G'),
    ('P.009D', '009.i.GHA.4D'),
    ('P.017G', '017.i.GHA.3G'),
    ('P.022D', '022.i.GHA.2D'),
    ('P.036G', '036.i.GHA.1G'),
    ('P.036D', '036.i.GHA.1D'),
    ('P.093G', '93GV3.12G'),
    ('P.096D', '96.GV3.7D'),
    ('P.097D', '100.GV3.7D'),
    ('P.104D', '104GV3.1D'),
    ('P.106G', '107GV3.1G'),
]

# Identifier la station 3 et traiter P.011G et P.010G
nouvelles_lignes = []
dans_station_3 = False
station_actuelle = None

for i, ligne in enumerate(lignes):
    # Détecter les changements de station
    if 'Station' in ligne and not 'Mesure' in ligne:
        match = re.match(r'\d+\s+Station\s+(\S+)', ligne)
        if match:
            station_actuelle = match.group(1)
            dans_station_3 = (station_actuelle == 'S3')
    
    # Dans station 3 : supprimer P.010G, renommer P.011G
    if dans_station_3 and 'Mesure' in ligne:
        if 'P.010G' in ligne or 'P010G' in ligne:
            print(f"❌ Suppression ligne {i+1} (S3): {ligne.strip()}")
            continue  # Ignore cette ligne
        
        if 'P.011G' in ligne or 'P011G' in ligne:
            ligne_modif = re.sub(r'P\.?011G', '010.i.GHA.2G', ligne)
            print(f"✓ Renommage S3 ligne {i+1}: P.011G → 010.i.GHA.2G")
            nouvelles_lignes.append(ligne_modif)
            continue
    
    # Appliquer les renommages normaux (hors station 3)
    ligne_modifiee = ligne
    for ancien, nouveau in renommages:
        if ancien in ligne:
            # Vérifier qu'on n'est pas dans un cas spécial (P.011G en S3 déjà traité)
            if ancien == 'P.011G' and dans_station_3:
                continue
            
            pattern = r'(?<=\s)' + re.escape(ancien) + r'(?=\s)'
            if re.search(pattern, ligne_modifiee):
                ligne_modifiee = re.sub(pattern, nouveau, ligne_modifiee)
                print(f"✓ Renommage ligne {i+1}: {ancien} → {nouveau}")
    
    nouvelles_lignes.append(ligne_modifiee)

# Sauvegarder dans version B
with open('carnet/GHA-auscultation 251201-B.geo', 'w', encoding='latin-1') as f:
    f.writelines(nouvelles_lignes)

print(f"\n{'='*80}")
print(f"✓ Fichier traité : carnet/GHA-auscultation 251201-B.geo")
print(f"✓ Total lignes : {len(nouvelles_lignes)}/{len(lignes)}")
print(f"✓ Lignes supprimées : {len(lignes) - len(nouvelles_lignes)}")
print(f"{'='*80}")
