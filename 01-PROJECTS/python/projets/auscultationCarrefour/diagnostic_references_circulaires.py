#!/usr/bin/env python3
"""
Script de diagnostic des références circulaires
"""

import openpyxl
from openpyxl.utils import get_column_letter
import re

def analyser_references_circulaires(filename):
    """Analyse complète des références circulaires dans le fichier Excel"""

    print(f"🔍 Diagnostic approfondi des références circulaires dans: {filename}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)

        problemes = []
        references_suspectes = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            print(f"\n📋 Analyse de l'onglet: {sheet_name}")

            cellules_avec_formules = 0

            for row in range(1, min(50, ws.max_row + 1)):
                for col in range(1, min(200, ws.max_column + 1)):  # Étendu pour BJ
                    cell = ws.cell(row, col)
                    if cell.value and str(cell.value).startswith('='):
                        cellules_avec_formules += 1
                        formule = str(cell.value)
                        cell_ref = f"{get_column_letter(col)}{row}"

                        # 1. Vérifier autoréférence directe
                        if cell_ref in formule:
                            problemes.append({
                                'type': 'AUTORÉFÉRENCE',
                                'onglet': sheet_name,
                                'cellule': cell_ref,
                                'formule': formule[:150] + '...' if len(formule) > 150 else formule
                            })

                        # 2. Chercher des patterns suspects
                        # Trop d'INDEX/MATCH imbriqués
                        if formule.count('INDEX') > 3:
                            references_suspectes.append({
                                'type': 'FORMULE_COMPLEXE',
                                'onglet': sheet_name,
                                'cellule': cell_ref,
                                'detail': f"INDEX répété {formule.count('INDEX')} fois"
                            })

                        # Références vers la même feuille avec chemins différents
                        patterns_feuille = re.findall(r'[A-Z]+\.[A-Z]+\d*:\d*', formule)
                        if len(patterns_feuille) > 2:
                            references_suspectes.append({
                                'type': 'MULTIPLES_REFS',
                                'onglet': sheet_name,
                                'cellule': cell_ref,
                                'detail': f"Références multiples: {len(patterns_feuille)}"
                            })

                        # LET mal formé (peut causer des circularités)
                        if 'LET(' in formule and formule.count('LET(') != formule.count(')'):
                            problemes.append({
                                'type': 'LET_MAL_FORME',
                                'onglet': sheet_name,
                                'cellule': cell_ref,
                                'formule': formule[:150] + '...' if len(formule) > 150 else formule
                            })

            print(f"   📊 {cellules_avec_formules} cellules avec formules analysées")

        # Rapport final
        print(f"\n" + "="*60)
        if problemes:
            print(f"❌ PROBLÈMES DÉTECTÉS ({len(problemes)}):")
            for i, pb in enumerate(problemes, 1):
                print(f"\n{i}. {pb['type']} - {pb['onglet']}.{pb['cellule']}")
                print(f"   Formule: {pb['formule']}")
        else:
            print(f"✅ Aucune référence circulaire directe détectée")

        if references_suspectes:
            print(f"\n⚠️  RÉFÉRENCES SUSPECTES ({len(references_suspectes)}):")
            for i, ref in enumerate(references_suspectes, 1):
                print(f"{i}. {ref['type']} - {ref['onglet']}.{ref['cellule']}: {ref['detail']}")

        # Recommandations
        print(f"\n🔧 RECOMMANDATIONS:")
        if problemes:
            print("1. Vérifiez les formules LET pour les parenthèses manquantes")
            print("2. Assurez-vous qu'aucune cellule ne se référence elle-même")
            print("3. Simplifiez les formules INDEX/MATCH trop complexes")
        else:
            print("1. Le fichier semble correct au niveau des références")
            print("2. Si Excel signale encore une circularité, essayez:")
            print("   - Fichier > Options > Formules > Cocher 'Calcul itératif'")
            print("   - Ou utilisez Ctrl+Alt+F9 pour forcer le recalcul")

        wb.close()
        return problemes, references_suspectes

    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        return [], []

def reparer_references_courantes(filename, backup=True):
    """Répare les problèmes de références les plus courants"""

    if backup:
        import shutil
        backup_name = filename.replace('.xlsx', '_backup.xlsx')
        shutil.copy2(filename, backup_name)
        print(f"💾 Sauvegarde créée: {backup_name}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)
        modifications = 0

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]

            for row in range(1, min(50, ws.max_row + 1)):
                for col in range(1, min(200, ws.max_column + 1)):
                    cell = ws.cell(row, col)
                    if cell.value and str(cell.value).startswith('='):
                        formule_orig = str(cell.value)
                        formule_new = formule_orig
                        cell_ref = f"{get_column_letter(col)}{row}"

                        # Supprime les autoréférences évidentes
                        if cell_ref in formule_new:
                            # Remplace par une référence vide ou 0
                            formule_new = formule_new.replace(cell_ref, "0")
                            modifications += 1

                        # Corrige les LET mal formés
                        if 'LET(' in formule_new:
                            parentheses_ouvertes = formule_new.count('(')
                            parentheses_fermees = formule_new.count(')')
                            if parentheses_ouvertes > parentheses_fermees:
                                formule_new += ')' * (parentheses_ouvertes - parentheses_fermees)
                                modifications += 1

                        if formule_new != formule_orig:
                            cell.value = formule_new
                            print(f"🔧 Corrigé: {sheet_name}.{cell_ref}")

        if modifications > 0:
            wb.save(filename)
            print(f"✅ {modifications} corrections appliquées")
        else:
            print("ℹ️  Aucune correction nécessaire")

        wb.close()

    except Exception as e:
        print(f"❌ Erreur lors de la réparation: {e}")

if __name__ == "__main__":
    print("🔧 DIAGNOSTIC DES RÉFÉRENCES CIRCULAIRES")

    filename = input("Nom du fichier Excel à analyser: ")

    # Diagnostic
    problemes, suspects = analyser_references_circulaires(filename)

    # Option de réparation
    if problemes:
        reponse = input(f"\n🛠️  Voulez-vous tenter une réparation automatique? (o/n): ")
        if reponse.lower() in ['o', 'oui', 'y', 'yes']:
            reparer_references_courantes(filename)

    print(f"\n🎯 Diagnostic terminé!")
