"""
Analyse des correspondances pour les points G.LB.*
"""

import re
from collections import defaultdict

# Lire le fichier .geo
with open('POLYGCR-251121-D.geo', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extraire toutes les mesures
mesures = []
for i, line in enumerate(lines):
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

# Séparer les mesures G.LB.* et les autres (avant ligne 694)
mesures_glb = [m for m in mesures if m['nom'].startswith('G.LB.')]
mesures_avant = [m for m in mesures if m['ligne'] < 694 and not m['nom'].startswith('G.LB.') and not m['nom'].startswith('A.LB.') and not m['nom'].startswith('P') and not m['nom'].startswith('A1')]

print(f"Nombre de mesures G.LB.*: {len(mesures_glb)}")
print(f"Nombre d'autres mesures avant ligne 694: {len(mesures_avant)}")

# Afficher les points G.LB.* trouvés
points_glb = sorted(set(m['nom'] for m in mesures_glb))
print(f"\nPoints G.LB.* trouvés: {points_glb}")

print("\n" + "="*80)
print("RECHERCHE DE CORRESPONDANCES POUR LES POINTS G.LB.*")
print("="*80)

# Tolérance pour la comparaison des angles (en degrés/gon)
TOLERANCE_HZ = 1.0  # 1 gon de marge
TOLERANCE_V = 1.0   # 1 gon de marge
TOLERANCE_DIST = 0.5  # 0.5 m de marge

# Pour chaque mesure G.LB.*, chercher les correspondances
correspondances = []
for glb in mesures_glb:
    candidats = []
    
    for autre in mesures_avant:
        # Vérifier si les angles sont proches
        diff_hz = abs(glb['hz'] - autre['hz'])
        diff_v = abs(glb['v'] - autre['v'])
        diff_dist = abs(glb['dist'] - autre['dist'])
        
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
            'glb': glb,
            'match': meilleur['autre'],
            'diff_hz': meilleur['diff_hz'],
            'diff_v': meilleur['diff_v'],
            'diff_dist': meilleur['diff_dist']
        })
        
        # Ne montrer que les premières occurrences uniques par nom
        if not any(c['glb']['nom'] == glb['nom'] and c['glb']['ligne'] < glb['ligne'] for c in correspondances[:-1]):
            print(f"\n{glb['nom']:20s} (ligne {glb['ligne']:4d}) -> {meilleur['autre']['nom']:20s} (ligne {meilleur['autre']['ligne']:4d})")
            print(f"  Hz: {glb['hz']:10.4f}° vs {meilleur['autre']['hz']:10.4f}°  (diff: {meilleur['diff_hz']:.4f}°)")
            print(f"  V:  {glb['v']:10.4f}° vs {meilleur['autre']['v']:10.4f}°  (diff: {meilleur['diff_v']:.4f}°)")
            print(f"  D:  {glb['dist']:8.3f}m vs {meilleur['autre']['dist']:8.3f}m  (diff: {meilleur['diff_dist']:.3f}m)")
            
            # Montrer d'autres candidats proches s'il y en a
            if len(candidats) > 1:
                print(f"  Autres candidats possibles:")
                for i, cand in enumerate(candidats[1:min(4, len(candidats))], 2):
                    print(f"    {i}. {cand['autre']['nom']:20s} (ligne {cand['autre']['ligne']:4d}) - score: {cand['score']:.4f}")

print("\n" + "="*80)
print(f"RÉSUMÉ: {len(correspondances)} correspondances trouvées")
print("="*80)

# Résumé par point unique
correspondances_uniques = {}
for c in correspondances:
    nom_glb = c['glb']['nom']
    nom_ancien = c['match']['nom']
    if nom_glb not in correspondances_uniques:
        correspondances_uniques[nom_glb] = nom_ancien

print("\n\nCOMMANDES DE REMPLACEMENT PROPOSÉES:")
print("-" * 80)
for glb, ancien in sorted(correspondances_uniques.items()):
    print(f"{ancien:20s} -> {glb}")
