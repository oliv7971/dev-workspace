#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyseur de doublons de colonnes "bas droit" 
"""

import pandas as pd
from collections import Counter

def analyze_bas_droit_duplicates():
    """Analyse les doublons de colonnes 'bas droit' dans le fichier déplacements"""
    
    try:
        # Charger le fichier
        df = pd.read_csv('examples/format_apres/Deplacements_SMC.csv', sep=';', encoding='utf-8-sig')
        
        print("=== VERIFICATION DOUBLONS DANS LE FICHIER SOURCE ===")
        print(f"Fichier: Deplacements_SMC.csv ({len(df)} lignes)")
        
        # Compter toutes les métriques
        metrics_count = Counter(df['metric'])
        
        # Chercher les doublons "bas droit"
        doublons_bas_droit = {k: v for k, v in metrics_count.items() if v > 1 and 'bas droit' in str(k).lower()}
        
        if doublons_bas_droit:
            print(f"PROBLEME: Doublons 'bas droit' globaux: {doublons_bas_droit}")
        else:
            print("OK: Aucun doublon 'bas droit' global")
        
        print("\n=== ANALYSE PAR GALERIE/SECTION ===")
        
        problemes_par_section = []
        
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            metrics = group['metric'].tolist()
            
            # Compter les métriques "bas droit" dans cette section
            bas_droit_metrics = [m for m in metrics if 'bas droit' in str(m).lower()]
            
            if len(bas_droit_metrics) > 1:
                print(f"PROBLEME {galerie} {section}: {len(bas_droit_metrics)} metriques 'bas droit'")
                print(f"   Metriques: {bas_droit_metrics}")
                problemes_par_section.append((galerie, section, bas_droit_metrics))
            
            # Vérifier aussi les métriques DH/DPM/DZ pour équilibre
            dh_metrics = [m for m in metrics if str(m).startswith('DH ')]
            dpm_metrics = [m for m in metrics if str(m).startswith('DPM ')]
            dz_metrics = [m for m in metrics if str(m).startswith('DZ ')]
            
            # Compter haut vs bas pour chaque type
            for prefix, metric_list in [('DH', dh_metrics), ('DPM', dpm_metrics), ('DZ', dz_metrics)]:
                if metric_list:
                    haut_count = len([m for m in metric_list if 'haut' in m])
                    bas_count = len([m for m in metric_list if 'bas' in m])
                    inter_count = len([m for m in metric_list if 'inter' in m])
                    
                    if bas_count > haut_count and bas_count > 1:
                        print(f"ATTENTION {galerie} {section} {prefix}: {bas_count} 'bas' vs {haut_count} 'haut' vs {inter_count} 'inter'")
                        
                        # Afficher toutes les métriques de ce type pour diagnostic
                        print(f"   Détail {prefix}: {metric_list}")
        
        if not problemes_par_section:
            print("OK: Aucun probleme de doublon par section detecte")
        
        print(f"\n=== RESUME ===")
        print(f"Total sections analysees: {len(df.groupby(['galerie', 'section']))}")
        print(f"Sections avec problemes: {len(problemes_par_section)}")
        
        # Analyser aussi les fichiers originaux Excel si disponibles
        print(f"\n=== SUGGESTIONS DE CORRECTION ===")
        
        if problemes_par_section:
            print("Pour corriger manuellement les doublons:")
            for galerie, section, bas_droit_list in problemes_par_section:
                print(f"\n{galerie} {section}:")
                print(f"  - Verifier dans le fichier Excel source")
                print(f"  - Une des colonnes '{bas_droit_list[0]}' devrait probablement etre:")
                print(f"    * 'DH haut droit' ou 'DPM haut droit' ou 'DZ haut droit'")
                print(f"    * 'DH inter droit' ou 'DPM inter droit' ou 'DZ inter droit'")
        else:
            print("Aucune correction manuelle necessaire - les doublons ont ete corriges automatiquement!")
    
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    analyze_bas_droit_duplicates()