#!/usr/bin/env python3
"""
SOLUTION RADICALE - Nettoyage complet pour éviter la corruption
"""

import openpyxl
from openpyxl.utils import get_column_letter

def nettoyer_completement_onglets(filename):
    """Nettoie complètement tous les onglets problématiques"""

    print(f"🧹 Nettoyage complet des onglets problématiques...")

    try:
        wb = openpyxl.load_workbook(filename)

        onglets_a_nettoyer = ["ÉVOLUTION PM H V", "Déplacements", "CORDES REF1", "CORDES REF2"]

        for nom_onglet in onglets_a_nettoyer:
            if nom_onglet in wb.sheetnames:
                ws = wb[nom_onglet]
                print(f"   🧽 Nettoyage de {nom_onglet}...")

                # Supprimer TOUTES les formules
                for row in range(10, 30):
                    for col in range(1, 65):
                        cell = ws.cell(row, col)
                        if cell.value and str(cell.value).startswith('='):
                            cell.value = None

                print(f"   ✅ {nom_onglet} nettoyé")

        wb.save(filename)
        wb.close()
        print("✅ Nettoyage terminé")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def creer_structure_minimale(filename):
    """Crée seulement la structure (en-têtes) sans formules"""

    print(f"📋 Création de la structure minimale...")

    try:
        wb = openpyxl.load_workbook(filename)

        targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

        # DÉPLACEMENTS - Structure seulement
        if "Déplacements" in wb.sheetnames:
            ws_depl = wb["Déplacements"]
            print("   📊 Structure Déplacements...")

            # En-têtes uniquement
            col = 3
            for target in targets:
                for coord in ['X', 'Y', 'Z']:
                    ws_depl.cell(9, col).value = f"{target}_{coord}"
                    # Pas de formules, juste des zéros
                    for row in range(10, 16):
                        ws_depl.cell(row, col).value = 0
                    col += 1

        wb.save(filename)
        wb.close()
        print("✅ Structure créée sans formules")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def creer_instructions_manuelles():
    """Crée un fichier d'instructions pour saisie manuelle"""

    instructions = """# INSTRUCTIONS POUR FORMULES MANUELLES

Le fichier Excel a été nettoyé pour éviter les corruptions.
Voici les formules à saisir MANUELLEMENT dans Excel :

## ONGLET DÉPLACEMENTS
Pour chaque colonne (C, D, E, F, etc.) en ligne 11 et suivantes :
Formule type: ='Résultats observations'.C11-'Résultats observations'.C$10

Exemple pour la colonne C (V1_X):
- C11: ='Résultats observations'.C11-'Résultats observations'.C$10
- C12: ='Résultats observations'.C12-'Résultats observations'.C$10

## ONGLET ÉVOLUTION PM H V
Pour chaque colonne (C, D, E, F, etc.) en ligne 11 et suivantes :
Formule type: ='Résultats Projection'.C11-'Résultats Projection'.C$10

## RECOMMANDATION
1. Commencez par UNE formule de test
2. Si ça marche, copiez-la vers le bas
3. Sauvegardez fréquemment !
"""

    with open("INSTRUCTIONS_FORMULES_MANUELLES.txt", "w", encoding="utf-8") as f:
        f.write(instructions)

    print("📝 Instructions créées: INSTRUCTIONS_FORMULES_MANUELLES.txt")

if __name__ == "__main__":
    filename = input("Nom du fichier Excel corrompu: ")

    print("🚨 SOLUTION RADICALE - NETTOYAGE COMPLET")

    # Sauvegarder avant nettoyage
    import shutil
    backup_name = filename.replace('.xlsx', '_AVANT_NETTOYAGE_RADICAL.xlsx')
    try:
        shutil.copy2(filename, backup_name)
        print(f"💾 Sauvegarde: {backup_name}")
    except:
        pass

    # Étapes de nettoyage
    if nettoyer_completement_onglets(filename):
        print("✅ Étape 1: Nettoyage terminé")

        if creer_structure_minimale(filename):
            print("✅ Étape 2: Structure créée")

            creer_instructions_manuelles()

            print(f"\n🎉 SOLUTION APPLIQUÉE!")
            print(f"📁 Fichier: {filename} (stable, sans formules)")
            print(f"📝 Instructions: INSTRUCTIONS_FORMULES_MANUELLES.txt")
            print(f"💡 Saisissez les formules manuellement dans Excel")
        else:
            print("❌ Échec création structure")
    else:
        print("❌ Échec du nettoyage")
