#!/usr/bin/env python3
"""
SOLUTION ULTRA-MINIMALISTE
Formules les plus simples possibles pour éviter toute corruption
"""

import openpyxl
from openpyxl.utils import get_column_letter

def nettoyer_completement_o                print("❌ Échec création structure")
    else:
        print("❌ Échec du nettoyage")ts(filename):
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

        # ÉVOLUTION PM H V - Structure seulement
        if "ÉVOLUTION PM H V" in wb.sheetnames:
            ws_evol = wb["ÉVOLUTION PM H V"]
            print("   📈 Structure Évolution...")

            col = 3
            for target in targets:
                for coord in ['PM', 'H', 'V']:
                    ws_evol.cell(9, col).value = f"Δ{target}_{coord}"
                    # Pas de formules, juste des zéros
                    for row in range(10, 16):
                        ws_evol.cell(row, col).value = 0
                    col += 1

        # CORDES - Structure seulement
        for ref_name in ["REF1", "REF2"]:
            onglet_name = f"CORDES {ref_name}"
            if onglet_name in wb.sheetnames:
                ws_cordes = wb[onglet_name]
                print(f"   📏 Structure {onglet_name}...")

                targets_filtres = [t for t in targets if t != ref_name]
                col = 3
                for target in targets_filtres:
                    ws_cordes.cell(9, col).value = f"CORDE_{target}_{ref_name}"
                    # Pas de formules, juste des zéros
                    for row in range(10, 16):
                        ws_cordes.cell(row, col).value = 0
                    col += 1

        wb.save(filename)
        wb.close()
        print("✅ Structure créée sans formules")
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def tester_stabilite_fichier(filename):
    """Teste la stabilité du fichier sans formules"""

    print(f"🧪 Test de stabilité...")

    try:
        # Test d'ouverture
        wb = openpyxl.load_workbook(filename)
        print("   ✅ Ouverture OK")

        # Test de sauvegarde
        wb.save(filename)
        print("   ✅ Sauvegarde OK")

        # Compter les formules restantes
        formules_count = 0
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            for row in range(1, min(30, ws.max_row + 1)):
                for col in range(1, min(65, ws.max_column + 1)):
                    cell_value = ws.cell(row, col).value
                    if cell_value and str(cell_value).startswith('='):
                        formules_count += 1

        print(f"   📊 {formules_count} formules restantes dans le fichier")

        wb.close()
        return True

    except Exception as e:
        print(f"   ❌ Erreur de stabilité: {e}")
        return False

def creer_manuel_instructions(filename):
    """Crée un fichier d'instructions pour saisie manuelle"""

    instructions = f"""
# INSTRUCTIONS POUR FORMULES MANUELLES
# Fichier: {filename}

Le fichier Excel a été nettoyé pour éviter les corruptions.
Voici les formules à saisir MANUELLEMENT dans Excel :

## ONGLET DÉPLACEMENTS
Pour chaque colonne (C, D, E, F, etc.) en ligne 11 et suivantes :
Formule type: ='Résultats observations'.C11-'Résultats observations'.C$10

Exemple pour la colonne C (V1_X):
- C11: ='Résultats observations'.C11-'Résultats observations'.C$10
- C12: ='Résultats observations'.C12-'Résultats observations'.C$10
- etc.

## ONGLET ÉVOLUTION PM H V
Pour chaque colonne (C, D, E, F, etc.) en ligne 11 et suivantes :
Formule type: ='Résultats Projection'.C11-'Résultats Projection'.C$10

Exemple pour la colonne C (ΔV1_PM):
- C11: ='Résultats Projection'.C11-'Résultats Projection'.C$10
- C12: ='Résultats Projection'.C12-'Résultats Projection'.C$10
- etc.

## ONGLET CORDES REF1
Pour chaque colonne, calculer la distance 3D :
=SQRT(('Résultats observations'.C11-'Résultats observations'.BG11)^2+('Résultats observations'.D11-'Résultats observations'.BH11)^2+('Résultats observations'.E11-'Résultats observations'.BI11)^2)

(Adapter les références de colonnes selon vos données)

## ONGLET CORDES REF2
Même principe que REF1 mais avec les colonnes de REF2.

## RECOMMANDATION
1. Commencez par UNE formule de test
2. Si ça marche, copiez-la vers le bas
3. Puis passez à la colonne suivante
4. Sauvegardez fréquemment !
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

            if tester_stabilite_fichier(filename):
                print("✅ Étape 3: Fichier stable")

                creer_manuel_instructions(filename)

                print(f"\\n🎉 SOLUTION APPLIQUÉE!")
                print(f"📁 Fichier: {filename} (stable, sans formules)")
                print(f"📝 Instructions: INSTRUCTIONS_FORMULES_MANUELLES.txt")
                print(f"💡 Vous devrez saisir les formules manuellement dans Excel")
                print(f"⚠️ Mais au moins le fichier ne se corrompra plus!")
            else:
                print("❌ Fichier toujours instable")
        else:
            print("❌ Échec création structure")
    else:
        print("❌ Échec du nettoyage")
"""
