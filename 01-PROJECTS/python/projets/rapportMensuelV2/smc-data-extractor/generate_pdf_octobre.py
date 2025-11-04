#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple de generation de PDF pour octobre 2025
Sans emojis pour eviter les problemes d'encodage Windows
"""

import sys
import os
from pathlib import Path

# Configuration
os.chdir(r"C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\smc-data-extractor")
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from excel_to_pdf_native import print_excel_files_native

input_dir = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\1-tableaux"
output_dir = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\3-pdf-annexes"

print("="*70)
print("GENERATION DES PDF - OCTOBRE 2025")
print("="*70)
print(f"Source : {input_dir}")
print(f"Sortie : {output_dir}")
print("="*70)
print()
print("Demarrage (cela peut prendre plusieurs minutes)...")
print()

# Lancer sans callback pour eviter les emojis
try:
    success = print_excel_files_native(
        root_folder=input_dir,
        output_folder=output_dir,
        month="2025-10",
        log_callback=None
    )
    
    print()
    print("="*70)
    if success:
        print("SUCCES - PDF generes")
        # Lister les fichiers crees
        pdf_files = list(Path(output_dir).glob("*.pdf"))
        print(f"Nombre de PDF : {len(pdf_files)}")
        if pdf_files:
            print("\nFichiers crees :")
            for pdf in sorted(pdf_files):
                size_mb = pdf.stat().st_size / (1024*1024)
                print(f"  - {pdf.name} ({size_mb:.2f} MB)")
    else:
        print("ERREUR - Verifiez les logs")
    print("="*70)
    
except Exception as e:
    print(f"\nERREUR: {e}")
    import traceback
    traceback.print_exc()
