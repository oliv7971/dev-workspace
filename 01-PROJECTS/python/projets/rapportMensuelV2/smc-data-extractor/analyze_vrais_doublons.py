#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyseur de vrais doublons - même type + même position
"""

import pandas as pd
from collections import Counter

def analyze_true_duplicates():
    """Analyse les vrais doublons : même type de métrique + même position"""
    
    try:
        # Charger le fichier
        df = pd.read_csv('examples/format_apres/Deplacements_SMC.csv', sep=';', encoding='utf-8-sig')
        
        print("=== ANALYSE DES VRAIS DOUBLONS (même type + même position) ===")
        print(f"Fichier: Deplacements_SMC.csv ({len(df)} lignes)")
        
        # Compter toutes les métriques
        metrics_count = Counter(df['metric'])
        
        # Chercher les vrais doublons (même nom exact)
        vrais_doublons = {k: v for k, v in metrics_count.items() if v > 1}
        
        if vrais_doublons:
            print(f"\nPROBLEME: Vrais doublons detectes:")
            for metric, count in vrais_doublons.items():
                print(f"  - '{metric}': {count} occurrences")
        else:
            print("\nOK: Aucun vrai doublon global detecte")
        
        print(f"\n=== ANALYSE PAR GALERIE/SECTION ===")
        
        problemes_par_section = []
        
        for (galerie, section), group in df.groupby(['galerie', 'section']):
            metrics = group['metric'].tolist()
            
            # Compter les occurrences de chaque métrique dans cette section
            section_metrics_count = Counter(metrics)
            section_doublons = {k: v for k, v in section_metrics_count.items() if v > 1}
            
            if section_doublons:
                print(f"\nPROBLEME {galerie} {section}:")
                for metric, count in section_doublons.items():
                    print(f"  - '{metric}': {count} occurrences")
                    
                    # Trouver les index de ces doublons pour correction manuelle
                    indices = [i for i, m in enumerate(metrics) if m == metric]
                    group_indices = group.index.tolist()
                    real_indices = [group_indices[i] for i in indices]
                    print(f"    Lignes dans le fichier: {real_indices}")
                
                problemes_par_section.append((galerie, section, section_doublons))
            else:
                print(f"OK {galerie} {section}: Aucun doublon")
        
        print(f"\n=== RESUME ===")
        print(f"Total sections analysees: {len(df.groupby(['galerie', 'section']))}")
        print(f"Sections avec vrais doublons: {len(problemes_par_section)}")
        
        if problemes_par_section:
            print(f"\n=== SUGGESTIONS DE CORRECTION MANUELLE ===")
            print("Pour chaque doublon, une des occurences devrait probablement etre:")
            
            for galerie, section, doublons in problemes_par_section:
                print(f"\n{galerie} {section}:")
                for metric, count in doublons.items():
                    print(f"  Metric '{metric}' (x{count}):")
                    
                    # Suggérer des corrections basées sur le type de métrique
                    if metric.startswith('DH '):
                        suggestions = ['DH haut droit', 'DH inter droit', 'DH centre haut']
                    elif metric.startswith('DPM '):
                        suggestions = ['DPM haut droit', 'DPM inter droit', 'DPM centre haut']
                    elif metric.startswith('DZ '):
                        suggestions = ['DZ haut droit', 'DZ inter droit', 'DZ centre haut']
                    else:
                        suggestions = ['Verifier dans le fichier Excel source']
                    
                    print(f"    Suggestions: {', '.join(suggestions)}")
        else:
            print("\nOK: Aucune correction manuelle necessaire !")
            print("Les métriques DH/DPM/DZ pour chaque position sont uniques par section.")
    
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    analyze_true_duplicates()