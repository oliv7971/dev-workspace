#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour analyser les patterns de nommage HA21
"""

import os
import re
from collections import defaultdict

BASE_PATH = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

ALVEOLES = [
    "ALVEOLE HA21",
    "ALVEOLE HA21-E1", 
    "ALVEOLE HA21-E2",
    "ALVEOLE HA21-E3"
]

def detecter_alveole(nom_dossier):
    """
    Détecte à quelle alvéole appartient un dossier selon son nom
    Retourne: 'E1', 'E2', 'E3', 'HA21' (générique), ou None
    """
    nom_upper = nom_dossier.upper()
    
    # Patterns pour E3 (en premier car plus spécifique)
    if any(p in nom_upper for p in ['HA21-E3', 'HA213', 'HA21-3', 'HA21E3']):
        return 'E3'
    
    # Patterns pour E2
    if any(p in nom_upper for p in ['HA21-E2', 'HA212', 'HA21-2', 'HA21E2']):
        return 'E2'
    
    # Patterns pour E1
    if any(p in nom_upper for p in ['HA21-E1', 'HA211', 'HA21-1', 'HA21E1']):
        return 'E1'
    
    # HA21 générique (sans précision d'alvéole)
    if 'HA21' in nom_upper and not any(x in nom_upper for x in ['E1', 'E2', 'E3', '1', '2', '3']):
        return 'HA21'
    
    return None

def analyser():
    """
    Analyse la répartition des dossiers dans chaque alvéole
    """
    print("Analyse des dossiers HA21...")
    print()
    
    for alveole in ALVEOLES:
        chemin_alveole = os.path.join(BASE_PATH, alveole)
        
        if not os.path.exists(chemin_alveole):
            print(f"[!] {alveole} n'existe pas")
            continue
        
        print(f"=== {alveole} ===")
        
        # Statistiques par type détecté
        stats = defaultdict(list)
        
        # Parcourir tous les sous-dossiers
        for root, dirs, files in os.walk(chemin_alveole):
            for d in dirs:
                type_detecte = detecter_alveole(d)
                if type_detecte:
                    chemin_relatif = os.path.join(root, d).replace(chemin_alveole, "")
                    stats[type_detecte].append((d, chemin_relatif))
        
        # Afficher les résultats
        if not stats:
            print("  Aucun dossier HA21 détecté")
        else:
            for type_alv in ['HA21', 'E1', 'E2', 'E3']:
                if type_alv in stats:
                    print(f"  {type_alv}: {len(stats[type_alv])} dossiers")
                    
                    # Afficher quelques exemples
                    if len(stats[type_alv]) <= 10:
                        for nom, chemin in stats[type_alv]:
                            print(f"    - {nom}")
                    else:
                        # Afficher les 5 premiers
                        for nom, chemin in stats[type_alv][:5]:
                            print(f"    - {nom}")
                        print(f"    ... et {len(stats[type_alv]) - 5} autres")
        
        print()
    
    print("\n=== RECOMMANDATION ===")
    print("Avant de déplacer automatiquement, il faudrait:")
    print("1. Vérifier manuellement quelques dossiers suspects")
    print("2. Confirmer les patterns de nommage utilisés")
    print("3. Définir une règle claire pour les cas ambigus")

if __name__ == "__main__":
    analyser()
