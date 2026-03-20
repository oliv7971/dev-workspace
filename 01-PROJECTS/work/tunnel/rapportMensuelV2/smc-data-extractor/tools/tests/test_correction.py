#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide de PDF Standardizer - Version corrigée
==================================================
"""

import os
import sys
from pathlib import Path

# Ajoute le répertoire du script au path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_standardizer import PDFStandardizer

def test_with_real_file():
    """Test avec le vrai fichier PDF du rapport mensuel."""
    
    # Chemin vers le fichier
    pdf_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\LS 34 G 911 EIF 0074 1 RP mensuel sept 2025 PARTIE TOPO annexes.pdf"
    
    print("=== TEST PDF STANDARDIZER - Version corrigee ===")
    print(f"Fichier test : {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print("ERREUR : Fichier PDF introuvable")
        print("Verifiez le chemin ou utilisez un autre fichier")
        return False
    
    # Dossier de sortie temporaire
    output_dir = Path(__file__).parent / "test_correction"
    output_dir.mkdir(exist_ok=True)
    
    # Initialise le standardisateur
    standardizer = PDFStandardizer(str(output_dir))
    
    print("\n1. Analyse des formats...")
    try:
        formats = standardizer.analyze_pdf_formats(pdf_path)
        print("Formats detectes :")
        for format_key, info in formats.items():
            format_type = standardizer.identify_format_type(info['width_mm'], info['height_mm'])
            pages_str = f"pages {', '.join(map(str, info['pages']))}"
            print(f"   - {format_key} ({format_type}) - {pages_str}")
    except Exception as e:
        print(f"Erreur d'analyse : {e}")
    
    print("\n2. Test de standardisation...")
    try:
        result = standardizer.standardize_single_pdf(pdf_path)
        
        if result:
            print(f"SUCCES ! Fichier standardise cree :")
            print(f"   {result}")
            
            # Vérifie que le fichier existe
            if os.path.exists(result):
                size_kb = os.path.getsize(result) / 1024
                print(f"   Taille : {size_kb:.1f} KB")
                print("\nLe fichier a ete cree avec succes !")
                return True
            else:
                print("ERREUR : Le fichier n'a pas ete cree")
                return False
        else:
            print("ERREUR : La standardisation a echoue")
            return False
            
    except Exception as e:
        print(f"ERREUR : {e}")
        return False

def main():
    """Test principal."""
    success = test_with_real_file()
    
    print("\n" + "="*50)
    if success:
        print("TEST REUSSI ! Le PDF Standardizer fonctionne.")
        print("\nVous pouvez maintenant utiliser :")
        print("   python run_pdf_standardizer_windows.py")
    else:
        print("TEST ECHOUE. Verifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()