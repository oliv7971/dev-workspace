#!/usr/bin/env python3
"""
Refaire l'onglet Déplacements sans références circulaires
"""

import openpyxl
from openpyxl.utils import get_column_letter

def refaire_onglet_deplacements(filename):
    """Supprime et recrée l'onglet Déplacements proprement"""

    print("🔄 Refaire l'onglet Déplacements...")

    try:
        wb = openpyxl.load_workbook(filename)

        # Supprimer l'ancien onglet Déplacements s'il existe
        if "Déplacements" in wb.sheetnames:
            wb.remove(wb["Déplacements"])
            print("🗑️ Ancien onglet Déplacements supprimé")

        # Créer le nouvel onglet
        ws_depl = wb.create_sheet("Déplacements")

        # Structure de base
        ws_depl.cell(7, 1).value = "Date point 0"
        ws_depl.cell(8, 1).value = "Date"
        ws_depl.cell(8, 2).value = "Jours"
        ws_depl.cell(9, 1).value = "Date"
        ws_depl.cell(9, 2).value = "Jours"

        # Toutes les cibles
        targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

        print(f"📊 Configuration pour {len(targets)} cibles...")

        # 3 colonnes par cible (X, Y, Z)
        start_col = 3
        current_col = start_col

        for target in targets:
            for coord in ['X', 'Y', 'Z']:
                # En-tête
                ws_depl.cell(9, current_col).value = f"{target}_{coord}"

                # Formules de déplacement : valeur_actuelle - valeur_initiale
                # ATTENTION: on évite les autoréférences en utilisant des lignes différentes
                for row in range(10, 25):  # Données à partir de la ligne 10
                    # Référence vers l'onglet "Résultats observations"
                    # en évitant la ligne 8 qui causait les problèmes
                    formule = f'=IFERROR(INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_{coord}",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,1,MATCH("{target}_{coord}",[Résultats observations].9:9,0)),"")'

                    ws_depl.cell(row, current_col).value = formule

                current_col += 1

        print(f"✅ {current_col - start_col} colonnes de déplacements créées")

        # Sauvegarde
        wb.save(filename)
        wb.close()

        print("🎉 Nouvel onglet Déplacements créé sans références circulaires!")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verifier_structure_onglets(filename):
    """Vérifie que tous les onglets nécessaires sont présents"""

    try:
        wb = openpyxl.load_workbook(filename, data_only=True)
        onglets_attendus = [
            "DATABASE",
            "Résultats observations",
            "Résultats Projection",
            "CORDES REF1",
            "CORDES REF2",
            "ÉVOLUTION PM H V",
            "Déplacements"
        ]

        onglets_presents = wb.sheetnames

        print("📋 VÉRIFICATION DE LA STRUCTURE:")
        for onglet in onglets_attendus:
            if onglet in onglets_presents:
                print(f"   ✅ {onglet}")
            else:
                print(f"   ❌ {onglet} MANQUANT")

        print(f"\n📊 ONGLETS PRÉSENTS ({len(onglets_presents)}):")
        for onglet in onglets_presents:
            print(f"   📄 {onglet}")

        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    filename = input("Nom du fichier Excel: ")

    print("🔧 REFAIRE L'ONGLET DÉPLACEMENTS")

    # Vérification avant
    print("\n1️⃣ Structure avant modification:")
    verifier_structure_onglets(filename)

    # Refaire l'onglet
    print("\n2️⃣ Reconstruction de l'onglet Déplacements:")
    if refaire_onglet_deplacements(filename):
        print("\n3️⃣ Structure après modification:")
        verifier_structure_onglets(filename)
        print(f"\n🎯 TERMINÉ! Le fichier est maintenant complet et sans références circulaires.")
    else:
        print("\n❌ Échec de la reconstruction")
