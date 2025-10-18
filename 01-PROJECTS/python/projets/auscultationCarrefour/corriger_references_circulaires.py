#!/usr/bin/env python3
"""
CORRECTIF URGENT pour les références circulaires détectées
"""

import openpyxl
import shutil

def corriger_references_circulaires_template():
    """Corrige les autoréférences dans l'onglet Déplacements"""

    filename = "AUSCULTATION CARREFOUR_TEMPLATE.xlsm"

    # Sauvegarde
    backup_name = "AUSCULTATION CARREFOUR_TEMPLATE_BACKUP.xlsm"
    shutil.copy2(filename, backup_name)
    print(f"💾 Sauvegarde créée: {backup_name}")

    try:
        wb = openpyxl.load_workbook(filename)
        ws_depl = wb["Déplacements"]

        print("🔧 Correction des autoréférences en ligne 8...")

        # Colonnes problématiques identifiées
        colonnes_probleme = ['C', 'F', 'I', 'L', 'O', 'R', 'U', 'X', 'AA', 'AD', 'AG', 'AJ', 'AM', 'AP', 'AS', 'AV', 'AY', 'BB', 'BE']

        corrections = 0
        for col_letter in colonnes_probleme:
            cell = ws_depl[f"{col_letter}8"]
            if cell.value and str(cell.value).startswith("='Résultats observations'!"):
                # Remplace par une référence différente ou une valeur
                # Option 1: Vider la cellule
                cell.value = ""
                corrections += 1
                print(f"   ✅ Corrigé: {col_letter}8")

        # Sauvegarde
        wb.save(filename)
        wb.close()

        print(f"🎉 {corrections} autoréférences corrigées!")
        print(f"📁 Fichier corrigé: {filename}")
        print(f"💾 Sauvegarde: {backup_name}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🚨 CORRECTIF RÉFÉRENCES CIRCULAIRES")
    print("Correction des autoréférences détectées dans l'onglet Déplacements...")

    if corriger_references_circulaires_template():
        print("\n✅ PROBLÈME RÉSOLU!")
        print("Vous pouvez maintenant ouvrir le fichier sans références circulaires.")
    else:
        print("\n❌ Échec de la correction")
        print("Vérifiez manuellement les formules dans l'onglet Déplacements ligne 8")
