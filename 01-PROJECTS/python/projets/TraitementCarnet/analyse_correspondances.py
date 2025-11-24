"""
Analyse des correspondances entre les mesures A.LB.XXXX et les mesures numérotées simples
en comparant les angles horizontaux et verticaux
"""

import re
from collections import defaultdict

# Lire le fichier .geo
with open('POLYGCR-251121-C.geo', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extraire toutes les mesures
mesures = []
for i, line in enumerate(lines):
    # Format: NNNNNN  Mesure  Nom  0.000000  Hz  V  Distance
    match = re.match(r'(\d{6})\s+Mesure\s+(\S+)\s+0\.000000\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', line)
    if match:
        num_mesure = match.group(1)
        nom = match.group(2)
        hz = float(match.group(3))
        v = float(match.group(4))
        dist = float(match.group(5))
        mesures.append({
            'ligne': i + 1,
            'num_mesure': num_mesure,
            'nom': nom,
            'hz': hz,
            'v': v,
            'dist': dist
        })

# Séparer les mesures A.LB.XXXX et les autres
mesures_alb = [m for m in mesures if m['nom'].startswith('A.LB.')]
mesures_autres = [m for m in mesures if not m['nom'].startswith('A.LB.') and not m['nom'].startswith('P') and not m['nom'].startswith('A141') and not m['nom'].startswith('A142') and not m['nom'].startswith('A122')]

print(f"Nombre de mesures A.LB.*: {len(mesures_alb)}")
print(f"Nombre d'autres mesures potentielles: {len(mesures_autres)}")
print("\nPremières mesures A.LB.*:")
for m in mesures_alb[:10]:
    print(f"  Ligne {m['ligne']}: {m['nom']:20s} Hz={m['hz']:10.4f}° V={m['v']:10.4f}° D={m['dist']:.3f}m")

print("\n" + "="*80)
print("RECHERCHE DE CORRESPONDANCES")
print("="*80)

# Tolérance pour la comparaison des angles (en degrés)
TOLERANCE_HZ = 0.5  # 0.5 gon
TOLERANCE_V = 0.5   # 0.5 gon
TOLERANCE_DIST = 0.1  # 0.1 m

# Pour chaque mesure A.LB.*, chercher les correspondances
correspondances = []
for alb in mesures_alb:
    candidats = []
    
    for autre in mesures_autres:
        # Vérifier si les angles sont proches
        diff_hz = abs(alb['hz'] - autre['hz'])
        diff_v = abs(alb['v'] - autre['v'])
        diff_dist = abs(alb['dist'] - autre['dist'])
        
        # Gérer le cas des angles à 360°/0° (modulo 400 gon)
        if diff_hz > 200:
            diff_hz = 400 - diff_hz
        
        if diff_hz < TOLERANCE_HZ and diff_v < TOLERANCE_V and diff_dist < TOLERANCE_DIST:
            candidats.append({
                'autre': autre,
                'diff_hz': diff_hz,
                'diff_v': diff_v,
                'diff_dist': diff_dist,
                'score': diff_hz + diff_v + diff_dist
            })
    
    # Trier par score (meilleur match en premier)
    candidats.sort(key=lambda x: x['score'])
    
    if candidats:
        meilleur = candidats[0]
        correspondances.append({
            'alb': alb,
            'match': meilleur['autre'],
            'diff_hz': meilleur['diff_hz'],
            'diff_v': meilleur['diff_v'],
            'diff_dist': meilleur['diff_dist']
        })
        
        print(f"\n{alb['nom']:20s} (ligne {alb['ligne']:4d}) -> {meilleur['autre']['nom']:20s} (ligne {meilleur['autre']['ligne']:4d})")
        print(f"  Hz: {alb['hz']:10.4f}° vs {meilleur['autre']['hz']:10.4f}°  (diff: {meilleur['diff_hz']:.4f}°)")
        print(f"  V:  {alb['v']:10.4f}° vs {meilleur['autre']['v']:10.4f}°  (diff: {meilleur['diff_v']:.4f}°)")
        print(f"  D:  {alb['dist']:8.3f}m vs {meilleur['autre']['dist']:8.3f}m  (diff: {meilleur['diff_dist']:.3f}m)")
    else:
        print(f"\n{alb['nom']:20s} (ligne {alb['ligne']:4d}) -> AUCUNE CORRESPONDANCE TROUVÉE")

print("\n" + "="*80)
print(f"RÉSUMÉ: {len(correspondances)} correspondances trouvées sur {len(mesures_alb)} mesures A.LB.*")
print("="*80)

# Générer les commandes de remplacement
if correspondances:
    print("\n\nCOMMANDES DE REMPLACEMENT:")
    print("-" * 80)
    for c in correspondances:
        ancien_nom = c['match']['nom']
        nouveau_nom = c['alb']['nom']
        print(f"{ancien_nom:20s} -> {nouveau_nom:20s}")
