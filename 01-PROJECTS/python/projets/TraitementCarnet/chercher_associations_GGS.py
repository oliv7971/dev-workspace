#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recherche automatique d'associations entre points mesurés et références
dans POLYGGS-251204-F.geo
"""

import re
from difflib import SequenceMatcher

def lire_fichier(fichier):
    """Lit les points et mesures"""
    points_ref = {}
    mesures = set()
    
    with open(fichier, 'r', encoding='utf-8') as f:
        for ligne in f:
            parties = ligne.strip().split()
            if len(parties) < 3:
                continue
            
            if parties[1] == 'Point' and parties[3] == '3':
                # Point de référence
                nom = parties[2]
                points_ref[nom] = ligne.strip()
            
            elif parties[1] == 'Mesure':
                # Mesure
                mesures.add(parties[2])
    
    return points_ref, mesures

def similarite(s1, s2):
    """Calcule la similarité entre deux chaînes"""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def trouver_correspondances(points_ref, mesures):
    """Trouve les correspondances entre mesures et références"""
    
    # Points mesurés sans référence exacte
    manquants = [m for m in mesures if m not in points_ref]
    refs_disponibles = list(points_ref.keys())
    
    correspondances = []
    
    for mesure in manquants:
        meilleures = []
        
        # Patterns spécifiques
        
        # 1. GGS.Sxxx.y -> ref_Sxxx
        match_s = re.match(r'GGS\.S(\d+)\.', mesure)
        if match_s:
            num = match_s.group(1)
            for ref in refs_disponibles:
                if ref == f'ref_S{num}':
                    correspondances.append((mesure, ref, "Pattern Station", 0.95))
                    continue
        
        # 2. GGS.Sxxx -> ref_Sxxx
        match_s2 = re.match(r'GGS\.S(\d+)$', mesure)
        if match_s2:
            num = match_s2.group(1)
            for ref in refs_disponibles:
                if ref == f'ref_S{num}1' or ref == f'ref_S{num}':
                    correspondances.append((mesure, ref, "Station simple", 0.9))
                    continue
        
        # 3. GVA.Sxxx -> ref_Sxxx (secteur GVA)
        match_gva_s = re.match(r'GVA\.S(\d+)$', mesure)
        if match_gva_s:
            num = match_gva_s.group(1)
            for ref in refs_disponibles:
                if ref == f'ref_S{num}1' or ref == f'ref_S{num}':
                    correspondances.append((mesure, ref, "Station GVA", 0.9))
                    continue
        
        # 4. GGS.Txxx -> xx.GGS.xxX
        match_t = re.match(r'GGS\.T(\d+)([GD])$', mesure)
        if match_t:
            num = match_t.group(1)
            dir = match_t.group(2)
            for ref in refs_disponibles:
                match_ref = re.match(r'(\d+)\.GGS\.\d+([GD])$', ref)
                if match_ref and match_ref.group(1) == num and match_ref.group(2) == dir:
                    correspondances.append((mesure, ref, f"Terrain {num}{dir}", 0.85))
        
        # 5. GGS.Axxx -> similaire
        if mesure.startswith('GGS.A'):
            for ref in refs_disponibles:
                if mesure.replace('GGS.', '') in ref or ref.replace('REF_', '').replace('ref_', '') in mesure:
                    sim = similarite(mesure, ref)
                    if sim > 0.7:
                        correspondances.append((mesure, ref, "Similarité A", sim))
        
        # 6. GGS.Cxxx -> REF_xxxx ou CX.xxx
        match_c = re.match(r'GGS\.C(\d+)$', mesure)
        if match_c:
            num = match_c.group(1)
            for ref in refs_disponibles:
                if num in ref and ('CX.' in ref or 'REF_' in ref):
                    sim = similarite(mesure, ref)
                    if sim > 0.5:
                        correspondances.append((mesure, ref, f"Point C{num}", sim))
        
        # 7. GVA.Cxxx -> similaire
        match_gva_c = re.match(r'GVA\.C(\d+)$', mesure)
        if match_gva_c:
            num = match_gva_c.group(1)
            for ref in refs_disponibles:
                if num in ref and 'C' in ref:
                    sim = similarite(mesure, ref)
                    if sim > 0.5:
                        correspondances.append((mesure, ref, f"Point GVA C{num}", sim))
        
        # 8. GVA.Pxxx -> similaire
        match_gva_p = re.match(r'GVA\.P(\d+)([GD])$', mesure)
        if match_gva_p:
            num = match_gva_p.group(1)
            dir = match_gva_p.group(2)
            for ref in refs_disponibles:
                if num in ref and dir in ref and ('GVA' in ref or 'P' in ref):
                    sim = similarite(mesure, ref)
                    if sim > 0.6:
                        correspondances.append((mesure, ref, f"Point GVA P{num}{dir}", sim))
        
        # 9. G04.Pxxx -> similaire
        match_g04 = re.match(r'G04\.P(\d+)([GD])$', mesure)
        if match_g04:
            num = match_g04.group(1)
            dir = match_g04.group(2)
            for ref in refs_disponibles:
                if num in ref and dir in ref:
                    sim = similarite(mesure, ref)
                    if sim > 0.6:
                        correspondances.append((mesure, ref, f"Point G04 P{num}{dir}", sim))
        
        # 10. GRD.xxx -> similaire
        if mesure.startswith('GRD.'):
            num = mesure.replace('GRD.', '')
            for ref in refs_disponibles:
                if num in ref and 'GRD' in ref:
                    sim = similarite(mesure, ref)
                    if sim > 0.7:
                        correspondances.append((mesure, ref, f"Point GRD {num}", sim))
    
    return correspondances

fichier = "carnet/POLYGGS-251204-F.geo"
points_ref, mesures = lire_fichier(fichier)

print("=" * 100)
print("RECHERCHE AUTOMATIQUE DE CORRESPONDANCES - POLYGGS-251204-F.geo")
print("=" * 100)
print()

correspondances = trouver_correspondances(points_ref, mesures)

# Trier par confiance décroissante
correspondances_triees = sorted(correspondances, key=lambda x: x[3], reverse=True)

# Éliminer les doublons (garder la meilleure correspondance par mesure)
vues = set()
uniques = []
for mes, ref, raison, conf in correspondances_triees:
    if mes not in vues:
        uniques.append((mes, ref, raison, conf))
        vues.add(mes)

print(f"Correspondances trouvées : {len(uniques)}")
print()
print("-" * 100)
print(f"{'Point mesuré':<30} {'Point référence':<30} {'Raison':<25} {'Confiance':<10}")
print("-" * 100)

for mes, ref, raison, conf in uniques:
    if conf >= 0.8:
        flag = "✓✓"
    elif conf >= 0.6:
        flag = "✓"
    else:
        flag = "?"
    print(f"{mes:<30} {ref:<30} {raison:<25} {conf:>5.1%}  {flag}")

print("-" * 100)
print()

# Séparer par niveau de confiance
haute_conf = [c for c in uniques if c[3] >= 0.85]
moyenne_conf = [c for c in uniques if 0.6 <= c[3] < 0.85]
basse_conf = [c for c in uniques if c[3] < 0.6]

print("=" * 100)
print(f"RÉSUMÉ")
print("=" * 100)
print(f"Haute confiance (≥85%)   : {len(haute_conf)} correspondances ✓✓")
print(f"Moyenne confiance (60-85%) : {len(moyenne_conf)} correspondances ✓")
print(f"Basse confiance (<60%)   : {len(basse_conf)} correspondances ?")
print()

if haute_conf:
    print("PROPOSITION DE RENOMMAGES (haute confiance) :")
    print("-" * 100)
    for mes, ref, raison, conf in haute_conf:
        print(f"  {mes:<30} -> {ref}")
    print()
