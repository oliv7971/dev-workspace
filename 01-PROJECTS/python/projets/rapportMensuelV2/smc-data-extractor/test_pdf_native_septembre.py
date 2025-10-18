#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Excel to PDF Native - Septembre 2025
Lance l'impression PDF native sur les fichiers d'auscultation de septembre
"""

import sys
from pathlib import Path

# Ajouter le chemin src
sys.path.append(str(Path(__file__).parent / "src"))

from src.excel_to_pdf_native import print_excel_files_native

def test_pdf_native_septembre():
    """Test de l'impression PDF native pour septembre 2025"""

    print("🖨️ Test Excel to PDF Native - Septembre 2025")
    print("=" * 60)

    # Configuration
    root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\1-tableaux"
    output_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250902-rapport mensuel septembre\2-extractions\PDF"
    month = "2025-09"

    print(f"📁 Dossier source: {root_folder}")
    print(f"💾 Dossier sortie: {output_folder}")
    print(f"📅 Mois: {month}")
    print()

    # Vérifier que le dossier source existe
    root_path = Path(root_folder)
    if not root_path.exists():
        print("❌ Dossier source non trouvé")
        print("🔍 Vérifiez le chemin ou ajustez-le selon votre structure")
        return False

    # Créer le dossier de sortie
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    def log_callback(message):
        """Callback pour afficher les logs"""
        print(f"[LOG] {message}")

    try:
        print("🚀 Lancement de l'impression PDF native...")
        print()

        success = print_excel_files_native(
            root_folder=root_folder,
            output_folder=output_folder,
            month=month,
            log_callback=log_callback
        )

        if success:
            print()
            print("✅ Impression PDF native terminée avec succès !")
            print(f"📂 Vérifiez le dossier: {output_folder}")

            # Lister les PDF générés
            pdf_files = list(output_path.glob("*.pdf"))
            if pdf_files:
                print(f"\n📄 {len(pdf_files)} fichier(s) PDF généré(s):")
                for pdf_file in sorted(pdf_files):
                    print(f"   • {pdf_file.name}")

            return True
        else:
            print("\n❌ Échec de l'impression PDF native")
            return False

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_pdf_native_septembre()

    if success:
        print("\n🎉 Test réussi ! Vos PDF sont prêts.")
    else:
        print("\n💡 Conseils de dépannage:")
        print("   1. Vérifiez que Excel est installé")
        print("   2. Vérifiez le chemin du dossier source")
        print("   3. Assurez-vous qu'aucun fichier Excel n'est ouvert")
        print("   4. Vérifiez les permissions d'écriture")

if __name__ == "__main__":
    main()
