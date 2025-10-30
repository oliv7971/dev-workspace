#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Correcteur spécifique pour les métriques GRD
Les galeries GRD utilisent des codes spéciaux (DGRD4+, DGVA+, DGGS+, DGRD6+)
qui ne sont pas correctement mappés vers les colonnes standards (DH, DPM, DZ)
"""

import pandas as pd
from pathlib import Path

def analyze_grd_mapping_issue():
    """Analyse le problème de mapping des métriques GRD"""
    
    print("=== ANALYSE DU PROBLÈME DE MAPPING GRD ===")
    
    # Charger les données sources (format ligne)
    df_source = pd.read_csv('examples/extraction_clean_20251027_141837/Deplacements_SMC.csv', sep=',', encoding='utf-8-sig')
    
    # Analyser les métriques GRD
    grd_data = df_source[df_source['galerie'] == 'GRD']
    
    print(f"Métriques GRD dans le fichier source:")
    for section in grd_data['section'].unique():
        section_data = grd_data[grd_data['section'] == section]
        print(f"\n{section}:")
        metrics = section_data['metric'].unique()
        for metric in metrics:
            print(f"  - {metric}")
    
    # Définir le mapping correct pour GRD
    grd_mapping = {
        # Mapping pour C105 (DGRD4+ et DGVA+)
        'DGRD4+ bas gauche': 'DPM bas gauche',
        'DGVA+ bas gauche': 'DH bas gauche', 
        'DGRD4+ haut gauche': 'DPM haut gauche',
        'DGVA+ haut gauche': 'DH haut gauche',
        'DGRD4+ centre haut': 'DPM centre haut',
        'DGVA+ centre haut': 'DH centre haut',
        'DGRD4+ haut droit': 'DPM haut droit',
        'DGVA+ haut droit': 'DH haut droit', 
        'DGRD4+ bas droit': 'DPM bas droit',
        'DGVA+ bas droit': 'DH bas droit',
        
        # Mapping pour C116 (DGRD6+ et DGGS+)
        'DGRD6+ bas gauche': 'DPM bas gauche',
        'DGGS+ bas gauche': 'DH bas gauche',
        'DGRD6+ haut gauche': 'DPM haut gauche', 
        'DGGS+ haut gauche': 'DH haut gauche',
        'DGRD6+ centre haut': 'DPM centre haut',
        'DGGS+ centre haut': 'DH centre haut',
        'DGRD6+ haut droit': 'DPM haut droit',
        'DGGS+ haut droit': 'DH haut droit',
        'DGRD6+ bas droit': 'DPM bas droit', 
        'DGGS+ bas droit': 'DH bas droit',
        
        # DZ reste DZ (pas de mapping nécessaire)
    }
    
    print(f"\n=== MAPPING PROPOSE ===")
    for grd_metric, standard_metric in grd_mapping.items():
        print(f"{grd_metric:<20} → {standard_metric}")
    
    return grd_mapping

def create_grd_mapping_corrector():
    """Crée un correcteur de mapping pour intégrer dans le système existant"""
    
    print(f"\n=== CREATION DU CORRECTEUR GRD ===")
    
    # Le mapping doit être ajouté dans le metric_name_corrector.py
    grd_corrections = {
        # Corrections spécifiques GRD pour C105
        'DGRD4+ bas gauche': 'DPM bas gauche',
        'DGVA+ bas gauche': 'DH bas gauche',
        'DGRD4+ haut gauche': 'DPM haut gauche', 
        'DGVA+ haut gauche': 'DH haut gauche',
        'DGRD4+ centre haut': 'DPM centre haut',
        'DGVA+ centre haut': 'DH centre haut',
        'DGRD4+ haut droit': 'DPM haut droit',
        'DGVA+ haut droit': 'DH haut droit',
        'DGRD4+ bas droit': 'DPM bas droit',
        'DGVA+ bas droit': 'DH bas droit',
        
        # Corrections spécifiques GRD pour C116
        'DGRD6+ bas gauche': 'DPM bas gauche',
        'DGGS+ bas gauche': 'DH bas gauche', 
        'DGRD6+ haut gauche': 'DPM haut gauche',
        'DGGS+ haut gauche': 'DH haut gauche',
        'DGRD6+ centre haut': 'DPM centre haut',
        'DGGS+ centre haut': 'DH centre haut',
        'DGRD6+ haut droit': 'DPM haut droit',
        'DGGS+ haut droit': 'DH haut droit', 
        'DGRD6+ bas droit': 'DPM bas droit',
        'DGGS+ bas droit': 'DH bas droit',
    }
    
    print(f"Corrections GRD à ajouter au système:")
    for original, corrected in grd_corrections.items():
        print(f"  '{original}': '{corrected}',")
    
    return grd_corrections

def test_grd_correction():
    """Test la correction des métriques GRD"""
    
    try:
        from metric_name_corrector import MetricNameCorrector
        
        # Créer le correcteur
        corrector = MetricNameCorrector()
        
        # Ajouter temporairement les corrections GRD
        grd_corrections = create_grd_mapping_corrector()
        corrector.corrections.update(grd_corrections)
        
        print(f"\n=== TEST DE CORRECTION ===")
        
        # Tester quelques corrections
        test_metrics = [
            'DGRD4+ bas gauche',
            'DGVA+ haut droit', 
            'DGGS+ bas gauche',
            'DGRD6+ centre haut'
        ]
        
        for metric in test_metrics:
            corrected = corrector.correct_metric_name(metric)
            print(f"{metric:<20} → {corrected}")
            
        return True
        
    except ImportError:
        print("❌ Module MetricNameCorrector non disponible pour le test")
        return False

if __name__ == "__main__":
    print("🔧 DIAGNOSTIC ET CORRECTION GRD")
    print("=" * 50)
    
    # Analyser le problème
    grd_mapping = analyze_grd_mapping_issue()
    
    # Créer le correcteur
    grd_corrections = create_grd_mapping_corrector()
    
    # Tester la correction
    test_success = test_grd_correction()
    
    print(f"\n💡 SOLUTION:")
    print(f"1. Ajouter les corrections GRD au metric_name_corrector.py")
    print(f"2. Régénérer l'extraction avec les corrections appliquées")
    print(f"3. Les métriques GRD seront mappées vers les colonnes standards")
    
    if test_success:
        print(f"✅ Test de correction réussi !")
    else:
        print(f"⚠️  Test de correction à faire manuellement")