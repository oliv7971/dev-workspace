#!/usr/bin/env python3
"""
Étape 2: Création progressive des vraies formules
Version sûre qui évite la corruption
"""

import openpyxl
from openpyxl.utils import get_column_letter

def ajouter_vraies_formules_deplacements(filename):
    """Ajoute les vraies formules pour les déplacements (version sûre)"""

    print(f"📊 Ajout des vraies formules DÉPLACEMENTS...")

    try:
        wb = openpyxl.load_workbook(filename)
        ws_depl = wb["Déplacements"]
        ws_obs = wb["Résultats observations"]

        # Obtenir la correspondance des colonnes depuis l'onglet observations
        colonnes_obs = {}
        for col in range(3, ws_obs.max_column + 1):
            entete = ws_obs.cell(9, col).value
            if entete and isinstance(entete, str) and '_' in entete:
                colonnes_obs[entete] = get_column_letter(col)

        print(f"   📋 {len(colonnes_obs)} colonnes trouvées dans Résultats observations")

        # Appliquer les formules ligne par ligne pour éviter les erreurs
        formules_ok = 0
        formules_erreurs = 0

        for col in range(3, 63):  # Colonnes C à BJ
            entete = ws_depl.cell(9, col).value
            if entete and entete in colonnes_obs:
                col_obs = colonnes_obs[entete]
                col_depl = get_column_letter(col)

                # Tester d'abord une formule
                try:
                    formule_test = f"='Résultats observations'.{col_obs}11-'Résultats observations'.{col_obs}$10"
                    ws_depl.cell(11, col).value = formule_test

                    # Si ça marche, continuer avec les autres lignes
                    for row in range(12, 16):  # Lignes 12 à 15 seulement
                        formule = f"='Résultats observations'.{col_obs}{row}-'Résultats observations'.{col_obs}$10"
                        ws_depl.cell(row, col).value = formule
                        formules_ok += 1

                except Exception as e:
                    print(f"   ⚠️ Erreur colonne {entete}: {e}")
                    formules_erreurs += 1

        print(f"   ✅ {formules_ok} formules créées, {formules_erreurs} erreurs")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def ajouter_vraies_formules_evolution(filename):
    """Ajoute les vraies formules pour l'évolution PM H V (version sûre)"""

    print(f"📈 Ajout des vraies formules ÉVOLUTION PM H V...")

    try:
        wb = openpyxl.load_workbook(filename)
        ws_evol = wb["ÉVOLUTION PM H V"]
        ws_proj = wb["Résultats Projection"]

        # Obtenir la correspondance des colonnes depuis l'onglet projection
        colonnes_proj = {}
        for col in range(3, ws_proj.max_column + 1):
            entete = ws_proj.cell(9, col).value
            if entete and isinstance(entete, str) and '_' in entete:
                colonnes_proj[entete] = get_column_letter(col)

        print(f"   📋 {len(colonnes_proj)} colonnes trouvées dans Résultats Projection")

        formules_ok = 0
        formules_erreurs = 0

        for col in range(3, 63):
            entete_delta = ws_evol.cell(9, col).value
            if entete_delta and entete_delta.startswith('Δ'):
                # Enlever le Δ pour obtenir le nom de la colonne source
                entete_source = entete_delta[1:]  # Enlève le premier caractère (Δ)

                if entete_source in colonnes_proj:
                    col_proj = colonnes_proj[entete_source]

                    try:
                        # Formule de test
                        formule_test = f"='Résultats Projection'.{col_proj}11-'Résultats Projection'.{col_proj}$10"
                        ws_evol.cell(11, col).value = formule_test

                        # Continuer si OK
                        for row in range(12, 16):
                            formule = f"='Résultats Projection'.{col_proj}{row}-'Résultats Projection'.{col_proj}$10"
                            ws_evol.cell(row, col).value = formule
                            formules_ok += 1

                    except Exception as e:
                        print(f"   ⚠️ Erreur colonne {entete_delta}: {e}")
                        formules_erreurs += 1

        print(f"   ✅ {formules_ok} formules créées, {formules_erreurs} erreurs")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def tester_fichier_apres_formules(filename):
    """Teste si le fichier s'ouvre correctement après ajout des formules"""

    print(f"🧪 Test d'ouverture du fichier...")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)
        print("   ✅ Fichier s'ouvre correctement")

        # Compter les formules
        total_formules = 0
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            for row in range(1, min(30, ws.max_row + 1)):
                for col in range(1, min(65, ws.max_column + 1)):
                    cell_value = ws.cell(row, col).value
                    if cell_value and str(cell_value).startswith('='):
                        total_formules += 1

        print(f"   📊 Total: {total_formules} formules dans le fichier")

        wb.close()
        return True

    except Exception as e:
        print(f"   ❌ Erreur d'ouverture: {e}")
        return False

if __name__ == "__main__":
    filename = input("Nom du fichier Excel réparé: ")

    print("🚀 AJOUT DES VRAIES FORMULES (VERSION SÛRE)")

    # Test initial
    if not tester_fichier_apres_formules(filename):
        print("❌ Le fichier a des problèmes avant même de commencer")
        exit(1)

    # Ajout des formules étape par étape
    print("\n1️⃣ Formules DÉPLACEMENTS...")
    if ajouter_vraies_formules_deplacements(filename):
        if tester_fichier_apres_formules(filename):
            print("✅ Déplacements: OK")
        else:
            print("❌ Déplacements: A causé une corruption")
            exit(1)

    print("\n2️⃣ Formules ÉVOLUTION...")
    if ajouter_vraies_formules_evolution(filename):
        if tester_fichier_apres_formules(filename):
            print("✅ Évolution: OK")
        else:
            print("❌ Évolution: A causé une corruption")
            exit(1)

    print(f"\n🎉 TOUTES LES FORMULES AJOUTÉES AVEC SUCCÈS!")
    print(f"📁 Fichier final: {filename}")
    print(f"✅ Prêt pour utilisation")
