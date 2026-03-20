"""
Analyse des doublons et cas ambigus dans les correspondances
"""

import re
from collections import defaultdict

# Lire le fichier .geo
with open('POLYGCR-251121-C.geo', 'r', encoding='utf-8') as f:
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

# Grouper les mesures par nom
mesures_par_nom = defaultdict(list)
for m in mesures:
    mesures_par_nom[m['nom']].append(m)

# Chercher les noms avec des valeurs différentes (pas juste des répétitions)
print("="*80)
print("ANALYSE DES POINTS AVEC VALEURS MULTIPLES")
print("="*80)

noms_suspects = []
for nom, liste_mesures in sorted(mesures_par_nom.items()):
    if len(liste_mesures) > 1:
        # Vérifier si les angles sont identiques ou différents
        angles_hz = set(round(m['hz'], 2) for m in liste_mesures)
        angles_v = set(round(m['v'], 2) for m in liste_mesures)
        distances = set(round(m['dist'], 2) for m in liste_mesures)
        
        if len(angles_hz) > 1 or len(angles_v) > 1 or len(distances) > 1:
            noms_suspects.append(nom)
            print(f"\n⚠️  {nom} : {len(liste_mesures)} mesures avec valeurs DIFFÉRENTES")
            for m in liste_mesures[:5]:  # Montrer max 5 exemples
                print(f"    Ligne {m['ligne']:4d}: Hz={m['hz']:10.4f}° V={m['v']:10.4f}° D={m['dist']:.3f}m")

# Analyser spécifiquement les cas problématiques identifiés
print("\n" + "="*80)
print("ANALYSE DÉTAILLÉE DES CAS PROBLÉMATIQUES")
print("="*80)

problemes = {
    '201': ['A.LB.1576', 'A.LB.1676'],
    '401': ['A.LB.1627'],
    '402': ['A.LB.1607'],
    '101': ['A.LB.1665'],
    '102': ['A.LB.1625'],
    '103': ['A.LB.1605'],
    '202': ['A.LB.1646'],
    '301': ['A.LB.1667'],
    '303': ['A.LB.1667'],
    '304': ['A.LB.1626'],
    '305': ['A.LB.1606'],
}

for ancien_nom, nouveaux_noms in problemes.items():
    if ancien_nom in mesures_par_nom:
        print(f"\n{ancien_nom} ({len(mesures_par_nom[ancien_nom])} occurrences) -> {', '.join(nouveaux_noms)}")
        
        # Grouper par angles similaires
        groupes = defaultdict(list)
        for m in mesures_par_nom[ancien_nom]:
            key = (round(m['hz'], 1), round(m['v'], 1), round(m['dist'], 1))
            groupes[key].append(m)
        
        if len(groupes) > 1:
            print(f"  ⚠️  {len(groupes)} groupes d'angles différents détectés !")
            for i, (key, groupe) in enumerate(groupes.items(), 1):
                hz, v, dist = key
                print(f"    Groupe {i}: Hz≈{hz}° V≈{v}° D≈{dist}m ({len(groupe)} mesures)")
                for m in groupe[:2]:
                    print(f"      Ligne {m['ligne']:4d}: Hz={m['hz']:10.4f}° V={m['v']:10.4f}° D={m['dist']:.3f}m")
        else:
            print(f"  ✓ Toutes les mesures ont des angles similaires")
            exemple = mesures_par_nom[ancien_nom][0]
            print(f"    Hz≈{exemple['hz']:.4f}° V≈{exemple['v']:.4f}° D≈{exemple['dist']:.3f}m")

# Vérifier les A.LB avec doublons
print("\n" + "="*80)
print("VÉRIFICATION DES POINTS A.LB.* IDENTIQUES")
print("="*80)

alb_1576 = mesures_par_nom.get('A.LB.1576', [])
alb_1676 = mesures_par_nom.get('A.LB.1676', [])

if alb_1576 and alb_1676:
    print(f"\nA.LB.1576: {len(alb_1576)} occurrences")
    if alb_1576:
        exemple = alb_1576[0]
        print(f"  Hz={exemple['hz']:.4f}° V={exemple['v']:.4f}° D={exemple['dist']:.3f}m")
    
    print(f"\nA.LB.1676: {len(alb_1676)} occurrences")
    if alb_1676:
        exemple = alb_1676[0]
        print(f"  Hz={exemple['hz']:.4f}° V={exemple['v']:.4f}° D={exemple['dist']:.3f}m")
    
    # Comparer
    if alb_1576 and alb_1676:
        diff_hz = abs(alb_1576[0]['hz'] - alb_1676[0]['hz'])
        diff_v = abs(alb_1576[0]['v'] - alb_1676[0]['v'])
        diff_dist = abs(alb_1576[0]['dist'] - alb_1676[0]['dist'])
        print(f"\n  Différences: ΔHz={diff_hz:.4f}° ΔV={diff_v:.4f}° ΔD={diff_dist:.3f}m")
        
        if diff_hz < 0.01 and diff_v < 0.01 and diff_dist < 0.01:
            print("  → Ce sont probablement des DOUBLONS (même point)")
        else:
            print("  → Ce sont des POINTS DIFFÉRENTS")

print("\n" + "="*80)
print("RECOMMANDATION")
print("="*80)
print("\nIl faut vérifier manuellement :")
print("1. Si A.LB.1576 et A.LB.1676 sont vraiment le même point")
print("2. Si oui, lequel garder pour renommer le point '201'")
print("3. Vérifier les autres correspondances multiples")
