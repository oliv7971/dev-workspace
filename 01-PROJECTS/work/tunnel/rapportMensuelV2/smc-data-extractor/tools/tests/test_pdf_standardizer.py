#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du PDF Standardizer
========================

Script de test pour vérifier le bon fonctionnement du standardisateur PDF.
"""

import os
import sys
from pathlib import Path

# Ajoute le répertoire du script au path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Teste l'import des modules requis."""
    print("🔍 Test des imports...")
    
    try:
        import PyPDF2
        print(f"✅ PyPDF2 v{PyPDF2.__version__}")
    except ImportError as e:
        print(f"❌ PyPDF2 : {e}")
        return False
    
    try:
        import fitz  # PyMuPDF
        print(f"✅ PyMuPDF v{fitz.version[0]}")
    except ImportError as e:
        print(f"❌ PyMuPDF : {e}")
        return False
    
    try:
        import reportlab
        from reportlab.lib.pagesizes import A4
        print(f"✅ ReportLab v{reportlab.Version}")
    except ImportError as e:
        print(f"❌ ReportLab : {e}")
        return False
    
    return True

def test_pdf_standardizer():
    """Teste l'import du module PDF Standardizer."""
    print("\n🔍 Test du module PDF Standardizer...")
    
    try:
        from pdf_standardizer import PDFStandardizer
        print("✅ Module PDF Standardizer importé avec succès")
        
        # Test d'initialisation
        standardizer = PDFStandardizer()
        print("✅ Classe PDFStandardizer initialisée")
        
        return True
    except ImportError as e:
        print(f"❌ Import PDF Standardizer : {e}")
        return False
    except Exception as e:
        print(f"❌ Initialisation : {e}")
        return False

def create_test_pdf():
    """Crée un PDF de test simple."""
    print("\n🔍 Création d'un PDF de test...")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A3, letter
        
        test_dir = Path(__file__).parent / "test_pdfs"
        test_dir.mkdir(exist_ok=True)
        
        # PDF A3
        a3_path = test_dir / "test_A3.pdf"
        c = canvas.Canvas(str(a3_path), pagesize=A3)
        c.drawString(100, 750, "Test PDF - Format A3")
        c.drawString(100, 700, "Ce PDF doit être converti en A4")
        c.save()
        print(f"✅ PDF A3 créé : {a3_path}")
        
        # PDF Letter
        letter_path = test_dir / "test_Letter.pdf"
        c = canvas.Canvas(str(letter_path), pagesize=letter)
        c.drawString(100, 750, "Test PDF - Format Letter")
        c.drawString(100, 700, "Ce PDF doit être converti en A4")
        c.save()
        print(f"✅ PDF Letter créé : {letter_path}")
        
        return [str(a3_path), str(letter_path)]
        
    except Exception as e:
        print(f"❌ Erreur création PDF test : {e}")
        return []

def test_standardization():
    """Teste la standardisation sur les PDF de test."""
    print("\n🔍 Test de standardisation...")
    
    # Crée les PDF de test
    test_pdfs = create_test_pdf()
    if not test_pdfs:
        return False
    
    try:
        from pdf_standardizer import PDFStandardizer
        
        # Initialise le standardisateur
        output_dir = Path(__file__).parent / "test_output"
        standardizer = PDFStandardizer(str(output_dir))
        
        # Teste l'analyse des formats
        print("\n📏 Analyse des formats...")
        for pdf_path in test_pdfs:
            formats = standardizer.analyze_pdf_formats(pdf_path)
            print(f"   {Path(pdf_path).name}: {list(formats.keys())}")
        
        # Teste la standardisation
        print("\n🔄 Standardisation...")
        results = standardizer.standardize_multiple_pdfs(test_pdfs)
        
        if results:
            print(f"✅ {len(results)} fichier(s) standardisé(s)")
            
            # Affiche le rapport
            print("\n📊 Rapport :")
            print(standardizer.generate_report())
            
            return True
        else:
            print("❌ Aucun fichier standardisé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de standardisation : {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🧪 TEST PDF STANDARDIZER")
    print("=" * 25)
    
    success = True
    
    # Test des imports
    if not test_imports():
        success = False
    
    # Test du module principal
    if not test_pdf_standardizer():
        success = False
    
    # Test de standardisation
    if not test_standardization():
        success = False
    
    print("\n" + "=" * 25)
    if success:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("\n💡 Le PDF Standardizer est prêt à utiliser :")
        print("   python run_pdf_standardizer.py")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n💡 Vérifiez l'installation des dépendances :")
        print("   pip install -r requirements_pdf.txt")

if __name__ == "__main__":
    main()