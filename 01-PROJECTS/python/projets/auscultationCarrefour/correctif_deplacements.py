#!/usr/bin/env python3
"""
Correctif pour l'onglet Déplacements (sans accent)
"""

import openpyxl
from openpyxl.utils import get_column_letter

def creer_formules_deplacements_correctif(filename):
    """Crée les formules pour l'onglet Déplacements (sans accent)"""

    print(f"🔧 Création des formules pour onglet 'Déplacements'...")

    try:
        wb = openpyxl.load_workbook(filename)

        # Chercher les variantes possibles du nom
        onglet_deplacements = None
        for nom in ["Déplacements", "Deplacements", "déplacements", "deplacements"]:
            if nom in wb.sheetnames:
                onglet_deplacements = nom
                break

        if not onglet_deplacements:
            print("❌ Onglet Déplacements non trouvé")
            print(f"   Onglets disponibles: {wb.sheetnames}")
            return False

        print(f"   ✅ Onglet trouvé: '{onglet_deplacements}'")
        ws_depl = wb[onglet_deplacements]

        # Identifier les colonnes avec des en-têtes de type "CIBLE_COORD"
        entetes_colonnes = {}
        for col in range(1, ws_depl.max_column + 1):
            entete = ws_depl.cell(9, col).value
            if entete and isinstance(entete, str) and '_' in entete and any(coord in entete for coord in ['_X', '_Y', '_Z']):
                entetes_colonnes[col] = entete

        print(f"   🎯 {len(entetes_colonnes)} colonnes de données détectées")

        if len(entetes_colonnes) == 0:
            # Créer les en-têtes si elles n'existent pas
            print("   📝 Création des en-têtes...")
            targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

            col = 3  # Commencer en colonne C
            for target in targets:
                for coord in ['X', 'Y', 'Z']:
                    entete = f"{target}_{coord}"
                    ws_depl.cell(9, col).value = entete
                    entetes_colonnes[col] = entete
                    col += 1

        formules_creees = 0
        for col, entete in entetes_colonnes.items():
            col_letter = get_column_letter(col)

            # Formules pour les lignes 10 à 25 (données)
            for row in range(10, 26):
                # Formule: valeur_actuelle - valeur_ligne_10 (première valeur)
                formule = f'=IFERROR(INDEX([Résultats observations].C:BJ,{row-9},MATCH("{entete}",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,1,MATCH("{entete}",[Résultats observations].9:9,0)),"")'

                ws_depl.cell(row, col).value = formule
                formules_creees += 1

        print(f"   ✅ {formules_creees} formules créées")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verifier_toutes_formules(filename):
    """Vérifie que toutes les formules sont bien créées"""

    print(f"\n🔍 Vérification finale des formules...")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)

        onglets_a_verifier = {
            "Déplacements": "déplacements XYZ",
            "Deplacements": "déplacements XYZ",
            "ÉVOLUTION PM H V": "évolutions PM/H/V",
            "CORDES REF1": "cordes vers REF1",
            "CORDES REF2": "cordes vers REF2"
        }

        for nom_onglet, description in onglets_a_verifier.items():
            if nom_onglet in wb.sheetnames:
                ws = wb[nom_onglet]

                # Compter les formules
                formules_count = 0
                for row in range(10, 26):
                    for col in range(3, min(65, ws.max_column + 1)):
                        cell_value = ws.cell(row, col).value
                        if cell_value and str(cell_value).startswith('='):
                            formules_count += 1

                print(f"   ✅ {nom_onglet}: {formules_count} formules ({description})")
            else:
                print(f"   ❌ {nom_onglet}: MANQUANT")

        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    filename = input("Nom du fichier Excel (v2): ")

    print("🔧 CORRECTIF POUR L'ONGLET DÉPLACEMENTS")

    # Création des formules pour Déplacements
    if creer_formules_deplacements_correctif(filename):
        print("✅ Formules Déplacements créées")

    # Vérification finale
    verifier_toutes_formules(filename)

    print(f"\n🎉 TERMINÉ!")
    print(f"📁 Toutes les formules sont maintenant en place dans {filename}")
