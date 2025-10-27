#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de régénération des fichiers colonnes avec corrections GRD
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

def regenerate_with_grd_corrections():
    """Régénère les fichiers colonnes avec les corrections GRD"""
    
    print("🔧 RÉGÉNÉRATION AVEC CORRECTIONS GRD")
    print("=" * 50)
    
    try:
        from ligne_summary_generator import LigneSummaryGenerator
        
        # Chemins
        input_folder = "examples/extraction_clean_20251027_141837"
        output_folder = "examples/extraction_clean_corrected_grd"
        month = "2025-09"
        
        print(f"📁 Source: {input_folder}")
        print(f"💾 Sortie: {output_folder}")
        print(f"📅 Mois: {month}")
        
        # Créer le générateur
        generator = LigneSummaryGenerator(
            csv_folder=input_folder,
            output_folder=output_folder,
            month=month
        )
        
        print(f"\n🔄 Génération en cours...")
        
        # Générer les fichiers CSV colonnes
        success = generator.generate_csv_ligne_summaries()
        
        if success:
            print(f"✅ Régénération réussie !")
            print(f"📁 Fichiers dans: {output_folder}")
            
            # Vérifier les données GRD dans le nouveau fichier
            verify_grd_corrections(output_folder)
        else:
            print(f"❌ Échec de la régénération")
            
        return success
        
    except ImportError as e:
        print(f"❌ Impossible d'importer le générateur: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_grd_corrections(output_folder):
    """Vérifie que les corrections GRD ont bien été appliquées"""
    
    try:
        import pandas as pd
        
        # Charger le fichier déplacements généré
        depl_file = Path(output_folder) / "Deplacements_Ligne_SMC_2025_09.csv"
        
        if depl_file.exists():
            df = pd.read_csv(depl_file, sep=';')
            
            print(f"\n🔍 Vérification des corrections GRD:")
            
            # Filtrer les lignes GRD
            grd_lines = df[df['galerie'] == 'GRD']
            
            if len(grd_lines) > 0:
                print(f"✅ {len(grd_lines)} lignes GRD trouvées")
                
                # Vérifier les colonnes DPM et DH pour GRD
                for idx, row in grd_lines.iterrows():
                    galerie = row['galerie']
                    section = row['section']
                    mode = row['mode']
                    
                    # Compter les colonnes avec des données
                    dpm_cols = [col for col in df.columns if col.startswith('DPM ')]
                    dh_cols = [col for col in df.columns if col.startswith('DH ')]
                    
                    dpm_values = [row[col] for col in dpm_cols if pd.notna(row[col]) and row[col] != '']
                    dh_values = [row[col] for col in dh_cols if pd.notna(row[col]) and row[col] != '']
                    
                    print(f"  {galerie} {section} ({mode}): {len(dpm_values)} DPM + {len(dh_values)} DH = {len(dpm_values) + len(dh_values)} métriques")
            else:
                print(f"❌ Aucune ligne GRD trouvée dans le fichier généré")
        else:
            print(f"❌ Fichier {depl_file} non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    success = regenerate_with_grd_corrections()
    
    if success:
        print(f"\n🎉 Les données GRD devraient maintenant être correctement")
        print(f"   mappées dans les colonnes standards DPM et DH !")
    else:
        print(f"\n😞 Problème lors de la régénération")