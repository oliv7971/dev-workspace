"""
Analyse des incohérences dans les noms de points :
1. Même nom avec angles différents
2. Angles identiques avec noms différents
"""

import re
from collections import defaultdict
import math

# Lire le fichier .geo
with open('POLYGCR-251121-E.geo', 'r', encoding='utf-8') as f:
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

print(f"Total de mesures analysées: {len(mesures)}")

# ============================================================================
# PARTIE 1: MÊME NOM AVEC ANGLES DIFFÉRENTS
# ============================================================================
print("\n" + "="*80)
print("PARTIE 1: POINTS AVEC LE MÊME NOM MAIS DES ANGLES DIFFÉRENTS")
print("="*80)

# Grouper les mesures par nom
mesures_par_nom = defaultdict(list)
for m in mesures:
    mesures_par_nom[m['nom']].append(m)

# Tolérance pour considérer que c'est le même point
TOLERANCE_HZ = 0.5  # gon
TOLERANCE_V = 0.5   # gon
TOLERANCE_DIST = 0.3  # m

problemes_noms = []
for nom, liste_mesures in sorted(mesures_par_nom.items()):
    if len(liste_mesures) > 1:
        # Comparer toutes les mesures entre elles
        groupes_angles = []
        
        for m in liste_mesures:
            trouve_groupe = False
            for groupe in groupes_angles:
                ref = groupe[0]
                diff_hz = abs(m['hz'] - ref['hz'])
                diff_v = abs(m['v'] - ref['v'])
                diff_dist = abs(m['dist'] - ref['dist'])
                
                # Gérer angle à 360°/0°
                if diff_hz > 200:
                    diff_hz = 400 - diff_hz
                
                if diff_hz < TOLERANCE_HZ and diff_v < TOLERANCE_V and diff_dist < TOLERANCE_DIST:
                    groupe.append(m)
                    trouve_groupe = True
                    break
            
            if not trouve_groupe:
                groupes_angles.append([m])
        
        # Si plusieurs groupes d'angles différents
        if len(groupes_angles) > 1:
            problemes_noms.append({
                'nom': nom,
                'groupes': groupes_angles
            })

if problemes_noms:
    print(f"\n⚠️  {len(problemes_noms)} points avec des ANGLES DIFFÉRENTS pour le MÊME NOM:\n")
    for prob in problemes_noms:
        print(f"\n{prob['nom']} : {len(prob['groupes'])} groupes d'angles différents ({sum(len(g) for g in prob['groupes'])} mesures)")
        for i, groupe in enumerate(prob['groupes'], 1):
            ref = groupe[0]
            print(f"  Groupe {i} ({len(groupe)} mesures): Hz≈{ref['hz']:.2f}° V≈{ref['v']:.2f}° D≈{ref['dist']:.2f}m")
            print(f"    Lignes: {', '.join(str(m['ligne']) for m in groupe[:5])}{'...' if len(groupe) > 5 else ''}")
else:
    print("\n✓ Aucun problème détecté : tous les points ont des angles cohérents")

# ============================================================================
# PARTIE 2: ANGLES IDENTIQUES AVEC NOMS DIFFÉRENTS
# ============================================================================
print("\n" + "="*80)
print("PARTIE 2: POINTS AVEC DES ANGLES IDENTIQUES MAIS DES NOMS DIFFÉRENTS")
print("="*80)

# Créer une clé pour chaque ensemble d'angles (arrondi)
PRECISION = 1  # arrondir à 0.1 gon et 0.1m
angles_dict = defaultdict(list)

for m in mesures:
    # Créer une clé unique basée sur les angles arrondis
    key = (
        round(m['hz'] * PRECISION) / PRECISION,
        round(m['v'] * PRECISION) / PRECISION,
        round(m['dist'] * PRECISION) / PRECISION
    )
    angles_dict[key].append(m)

# Chercher les groupes avec plusieurs noms différents
doublons_potentiels = []
for angles, liste_mesures in angles_dict.items():
    noms_uniques = set(m['nom'] for m in liste_mesures)
    if len(noms_uniques) > 1:
        doublons_potentiels.append({
            'angles': angles,
            'noms': sorted(noms_uniques),
            'mesures': liste_mesures
        })

# Trier par nombre de noms différents
doublons_potentiels.sort(key=lambda x: len(x['noms']), reverse=True)

if doublons_potentiels:
    print(f"\n⚠️  {len(doublons_potentiels)} groupes d'angles avec des NOMS DIFFÉRENTS:\n")
    
    # Montrer les plus significatifs (limiter l'affichage)
    for i, doublon in enumerate(doublons_potentiels[:20], 1):  # Top 20
        hz, v, dist = doublon['angles']
        noms = doublon['noms']
        nb_mesures = len(doublon['mesures'])
        
        print(f"\n{i}. Hz≈{hz:.1f}° V≈{v:.1f}° D≈{dist:.1f}m → {nb_mesures} mesures avec {len(noms)} noms différents:")
        print(f"   Noms: {', '.join(noms)}")
        
        # Montrer quelques exemples de lignes
        exemples = doublon['mesures'][:3]
        for ex in exemples:
            print(f"   - Ligne {ex['ligne']:4d}: {ex['nom']:20s} Hz={ex['hz']:.4f}° V={ex['v']:.4f}° D={ex['dist']:.3f}m")
    
    if len(doublons_potentiels) > 20:
        print(f"\n... et {len(doublons_potentiels) - 20} autres groupes")
else:
    print("\n✓ Aucun doublon détecté : tous les angles uniques ont un nom unique")

# ============================================================================
# STATISTIQUES GÉNÉRALES
# ============================================================================
print("\n" + "="*80)
print("STATISTIQUES GÉNÉRALES")
print("="*80)

print(f"\nNombre total de points différents: {len(mesures_par_nom)}")
print(f"Nombre de mesures total: {len(mesures)}")
print(f"Moyenne de mesures par point: {len(mesures) / len(mesures_par_nom):.1f}")

# Top 10 des points les plus mesurés
top_mesures = sorted(mesures_par_nom.items(), key=lambda x: len(x[1]), reverse=True)[:10]
print(f"\nTop 10 des points les plus mesurés:")
for nom, liste in top_mesures:
    print(f"  {nom:20s}: {len(liste):3d} mesures")
