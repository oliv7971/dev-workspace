#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'utilisation simple pour standardiser les PDF - Version Windows
======================================================================

Usage rapide pour homogénéiser tous les PDF d'un dossier en A4.
Version sans emojis pour compatibilité Windows.
"""

import os
import sys
from pathlib import Path

# Ajoute le répertoire du script au path pour import
sys.path.insert(0, str(Path(__file__).parent))

from pdf_standardizer import PDFStandardizer

def standardize_rapport_mensuel():
    """Standardise les PDF du rapport mensuel de septembre 2025."""
    
    # Dossier source (à adapter selon votre structure)
    source_dir = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre"
    
    # Dossier de sortie (PDF standardisés)
    output_dir = os.path.join(source_dir, "PDF_standardises_A4")
    
    print("=== PDF STANDARDIZER - Rapport Mensuel Septembre 2025 ===")
    print(f"Source : {source_dir}")
    print(f"Sortie : {output_dir}")
    print()
    
    # Vérifie que le dossier source existe
    if not os.path.exists(source_dir):
        print("ERREUR : Dossier source introuvable :")
        print(f"   {source_dir}")
        print()
        print("Solution :")
        print("   1. Vérifiez le chemin du dossier")
        print("   2. Ou modifiez la variable 'source_dir' dans le script")
        return False
    
    # Initialise le standardisateur
    standardizer = PDFStandardizer(output_dir)
    
    # Traite tous les PDF du dossier
    try:
        print("Recherche des fichiers PDF...")
        standardized_files = standardizer.standardize_directory(source_dir)
        
        if standardized_files:
            print(f"\nSUCCES : {len(standardized_files)} fichier(s) standardise(s) !")
            print("\nRAPPORT DETAILLE :")
            print(standardizer.generate_report())
            
            # Propose la fusion
            print("\n" + "="*50)
            response = input("Voulez-vous fusionner tous les PDF en un seul document ? (o/N) : ")
            
            if response.lower() in ['o', 'oui', 'y', 'yes']:
                final_name = "LS_34_G_911_EIF_0074_1_RP_mensuel_sept_2025_PARTIE_TOPO_annexes_A4.pdf"
                final_path = os.path.join(output_dir, final_name)
                
                print(f"\nFusion en cours vers : {final_name}")
                if standardizer.merge_standardized_pdfs(standardized_files, final_path):
                    print(f"SUCCES : Document final cree !")
                    print(f"Emplacement : {final_path}")
                else:
                    print("ERREUR lors de la fusion")
        else:
            print("ERREUR : Aucun fichier PDF traite avec succes")
            
    except Exception as e:
        print(f"ERREUR : {e}")
        return False
    
    return True

def standardize_custom_directory():
    """Interface pour traiter un dossier personnalisé."""
    print("=== PDF STANDARDIZER - Dossier personnalise ===")
    
    # Demande le dossier source
    source_dir = input("Dossier contenant les PDF a traiter : ").strip().strip('"')
    
    if not os.path.exists(source_dir):
        print(f"ERREUR : Dossier introuvable : {source_dir}")
        return False
    
    # Dossier de sortie
    output_dir = os.path.join(source_dir, "PDF_standardises_A4")
    print(f"Les PDF standardises seront sauves dans : {output_dir}")
    
    # Initialise et traite
    standardizer = PDFStandardizer(output_dir)
    
    try:
        standardized_files = standardizer.standardize_directory(source_dir)
        
        if standardized_files:
            print(f"\nSUCCES : {len(standardized_files)} fichier(s) standardise(s) !")
            print("\n" + standardizer.generate_report())
            
            # Propose la fusion
            response = input("\nFusionner tous les PDF ? (o/N) : ")
            if response.lower() in ['o', 'oui', 'y', 'yes']:
                final_name = "Document_fusionne_A4.pdf"
                final_path = os.path.join(output_dir, final_name)
                
                if standardizer.merge_standardized_pdfs(standardized_files, final_path):
                    print(f"SUCCES : Document fusionne : {final_path}")
        else:
            print("ERREUR : Aucun fichier traite")
            
    except Exception as e:
        print(f"ERREUR : {e}")
        return False
    
    return True

def main():
    """Menu principal."""
    print("SELECTIONNEZ UNE OPTION :")
    print("1. Traiter le rapport mensuel septembre 2025")
    print("2. Traiter un dossier personnalise")
    print("3. Quitter")
    print()
    
    while True:
        choice = input("Votre choix (1-3) : ").strip()
        
        if choice == '1':
            standardize_rapport_mensuel()
            break
        elif choice == '2':
            standardize_custom_directory()
            break
        elif choice == '3':
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Entrez 1, 2 ou 3.")

if __name__ == "__main__":
    main()