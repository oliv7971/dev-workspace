#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des noms de points dans POLYGGS-251204-B.geo
Détecte les patterns, incohérences et points similaires
"""

import re
from collections import defaultdict

def lire_points(fichier):
    """Lit tous les points du fichier"""
    points = []
    mesures = []
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            parties = ligne.strip().split()
            if len(parties) < 3:
                continue
            
            if parties[1] == 'Point':
                nom = parties[2]
                type_pt = parties[3]
                points.append({'nom': nom, 'type': type_pt, 'ligne': ligne.strip()})
            
            elif parties[1] == 'Mesure':
                nom = parties[2]
                mesures.append({'nom': nom, 'ligne': ligne.strip()})
    
    return points, mesures

def analyser_patterns(points, mesures):
    """Analyse les patterns de nommage"""
    
    # Séparer par type
    references = [p for p in points if p['type'] == '3']
    calcules = [p for p in points if p['type'] == '0']
    
    # Extraire les noms
    noms_ref = [p['nom'] for p in references]
    noms_calc = [p['nom'] for p in calcules]
    noms_mesures = [m['nom'] for m in mesures]
    
    print("=" * 100)
    print("ANALYSE DES NOMS DE POINTS - POLYGGS-251204-B.geo")
    print("=" * 100)
    print()
    print(f"Points de référence (type 3) : {len(references)}")
    print(f"Points calculés (type 0)     : {len(calcules)}")
    print(f"Points visés (mesures)       : {len(mesures)}")
    print()
    
    # Analyser les patterns de nommage
    print("=" * 100)
    print("PATTERNS DE NOMMAGE")
    print("=" * 100)
    
    # Références
    patterns_ref = defaultdict(list)
    for nom in noms_ref:
        # Extraire le pattern
        if nom.startswith('REF_'):
            patterns_ref['REF_xxxx'].append(nom)
        elif nom.startswith('ref_'):
            patterns_ref['ref_xxxx'].append(nom)
        elif re.match(r'\d+\.GGS\.\d+[GD]', nom):
            patterns_ref['NN.GGS.NNG/D'].append(nom)
        elif re.match(r'\d+GGS\.\d+[GD]', nom):
            patterns_ref['NNGGS.NNG/D'].append(nom)
        elif nom.startswith('CX.'):
            patterns_ref['CX.xxxx'].append(nom)
        else:
            patterns_ref['Autre'].append(nom)
    
    print("\nRÉFÉRENCES (type 3) :")
    for pattern, liste in sorted(patterns_ref.items()):
        print(f"  {pattern:<20} : {len(liste):3d} points")
        if len(liste) <= 5:
            for nom in liste:
                print(f"    - {nom}")
    
    # Mesures
    patterns_mes = defaultdict(list)
    for nom in noms_mesures:
        if nom.startswith('GGS.'):
            # Extraire le type après GGS.
            if '.P' in nom:
                patterns_mes['GGS.Pxx'].append(nom)
            elif '.S' in nom:
                patterns_mes['GGS.Sxx'].append(nom)
            elif '.C' in nom:
                patterns_mes['GGS.Cxx'].append(nom)
            else:
                patterns_mes['GGS.autre'].append(nom)
        else:
            patterns_mes['Autre'].append(nom)
    
    print("\nMESURES :")
    for pattern, liste in sorted(patterns_mes.items()):
        print(f"  {pattern:<20} : {len(liste):3d} mesures")
    
    # Comparer références vs mesures
    print()
    print("=" * 100)
    print("COMPARAISON RÉFÉRENCES <-> MESURES")
    print("=" * 100)
    
    # Points mesurés qui existent en référence
    communs = set(noms_ref) & set(noms_mesures)
    print(f"\nPoints communs (mesurés + références) : {len(communs)}")
    
    # Points mesurés qui n'existent pas en référence
    mesures_uniques = set(noms_mesures) - set(noms_ref)
    print(f"Points mesurés sans référence         : {len(mesures_uniques)}")
    
    if mesures_uniques:
        print("\nPoints mesurés SANS référence (échantillon) :")
        for nom in sorted(list(mesures_uniques))[:20]:
            print(f"  - {nom}")
        if len(mesures_uniques) > 20:
            print(f"  ... et {len(mesures_uniques) - 20} autres")
    
    # Chercher des correspondances possibles
    print()
    print("=" * 100)
    print("CORRESPONDANCES POSSIBLES")
    print("=" * 100)
    
    correspondances = []
    
    for nom_mes in sorted(mesures_uniques):
        # Chercher des noms similaires dans les références
        for nom_ref in noms_ref:
            # Similarité simple
            if nom_mes.replace('GGS.', '').replace('P', '') == nom_ref.replace('.GGS.', '').replace('GGS.', ''):
                correspondances.append((nom_mes, nom_ref, "Pattern similaire"))
            
            # GGS.PxxG/D -> xx.GGS.xxG/D
            match_mes = re.match(r'GGS\.P(\d+)([GD])', nom_mes)
            match_ref = re.match(r'(\d+)\.GGS\.\d+([GD])', nom_ref)
            if match_mes and match_ref:
                num_mes = match_mes.group(1)
                dir_mes = match_mes.group(2)
                num_ref = match_ref.group(1)
                dir_ref = match_ref.group(2)
                if num_mes == num_ref and dir_mes == dir_ref:
                    correspondances.append((nom_mes, nom_ref, f"Numéro {num_mes}{dir_mes}"))
            
            # GGS.Sxx.x -> ref_Sxxx
            match_mes_s = re.match(r'GGS\.S(\d+)\.', nom_mes)
            match_ref_s = re.match(r'ref_S(\d+)', nom_ref)
            if match_mes_s and match_ref_s:
                if match_mes_s.group(1) == match_ref_s.group(1):
                    correspondances.append((nom_mes, nom_ref, f"Station S{match_mes_s.group(1)}"))
    
    if correspondances:
        print(f"\n{len(correspondances)} correspondance(s) potentielle(s) détectée(s) :")
        print()
        for mes, ref, raison in correspondances[:30]:
            print(f"  {mes:<25} <-> {ref:<25} ({raison})")
        if len(correspondances) > 30:
            print(f"\n  ... et {len(correspondances) - 30} autres correspondances")
    else:
        print("\nAucune correspondance évidente détectée")
    
    print()
    print("=" * 100)
    
    return correspondances

# Main
fichier = "carnet/POLYGGS-251204-B.geo"
points, mesures = lire_points(fichier)
correspondances = analyser_patterns(points, mesures)

# Proposer des renommages
if correspondances:
    print()
    print("PROPOSITION DE RENOMMAGES")
    print("=" * 100)
    print()
    print("Points à renommer (de mesure -> référence) :")
    for mes, ref, raison in correspondances:
        print(f"  {mes:<25} -> {ref}")
