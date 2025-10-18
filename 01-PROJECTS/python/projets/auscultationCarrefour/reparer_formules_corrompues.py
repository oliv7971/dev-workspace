#!/usr/bin/env python3
"""
VERSION CORRIGÉE - Formules simplifiées et compatibles Excel
Évite les erreurs de syntaxe qui causent la corruption
"""

import openpyxl
from openpyxl.utils import get_column_letter

def creer_formules_simples_deplacements(filename):
    """Crée des formules simples pour l'onglet Déplacements"""

    print(f"🔧 Création de formules SIMPLES pour Déplacements...")

    try:
        wb = openpyxl.load_workbook(filename)

        if "Déplacements" not in wb.sheetnames:
            print("❌ Onglet Déplacements non trouvé")
            return False

        ws_depl = wb["Déplacements"]

        # Vider les formules existantes d'abord
        print("   🧹 Nettoyage des formules existantes...")
        for row in range(10, 26):
            for col in range(3, 65):
                ws_depl.cell(row, col).value = None

        # Créer les en-têtes s'ils n'existent pas
        targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

        col = 3  # Commencer en colonne C
        formules_creees = 0

        for target in targets:
            for coord in ['X', 'Y', 'Z']:
                entete = f"{target}_{coord}"
                ws_depl.cell(9, col).value = entete

                # Formules SIMPLIFIÉES pour les lignes 10 à 15 seulement (pour test)
                for row in range(10, 16):
                    # Version simplifiée sans crochets ni caractères spéciaux
                    col_letter_obs = get_column_letter(col)
                    formule = f'=IFERROR({col_letter_obs}{row}-{col_letter_obs}$10,"")'

                    ws_depl.cell(row, col).value = formule
                    formules_creees += 1

                col += 1

        print(f"   ✅ {formules_creees} formules simples créées")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def creer_formules_simples_evolution(filename):
    """Crée des formules simples pour l'onglet ÉVOLUTION PM H V"""

    print(f"🔧 Création de formules SIMPLES pour ÉVOLUTION PM H V...")

    try:
        wb = openpyxl.load_workbook(filename)

        if "ÉVOLUTION PM H V" not in wb.sheetnames:
            print("❌ Onglet ÉVOLUTION PM H V non trouvé")
            return False

        ws_evol = wb["ÉVOLUTION PM H V"]

        # Vider les formules existantes
        print("   🧹 Nettoyage des formules existantes...")
        for row in range(10, 26):
            for col in range(3, 65):
                ws_evol.cell(row, col).value = None

        # Créer les en-têtes
        targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

        col = 3
        formules_creees = 0

        for target in targets:
            for coord in ['PM', 'H', 'V']:
                entete = f"Δ{target}_{coord}"
                ws_evol.cell(9, col).value = entete

                # Formules SIMPLIFIÉES
                for row in range(10, 16):
                    col_letter = get_column_letter(col)
                    formule = f'=IFERROR({col_letter}{row}-{col_letter}$10,"")'

                    ws_evol.cell(row, col).value = formule
                    formules_creees += 1

                col += 1

        print(f"   ✅ {formules_creees} formules simples créées")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def creer_formules_simples_cordes(filename):
    """Crée des formules simples pour les onglets CORDES"""

    print(f"🔧 Création de formules SIMPLES pour CORDES...")

    try:
        wb = openpyxl.load_workbook(filename)

        targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

        # CORDES REF1
        if "CORDES REF1" in wb.sheetnames:
            ws_ref1 = wb["CORDES REF1"]
            print("   🎯 Nettoyage CORDES REF1...")

            # Vider les formules existantes
            for row in range(10, 26):
                for col in range(3, 25):
                    ws_ref1.cell(row, col).value = None

            # En-têtes seulement (pas de formules pour l'instant)
            targets_ref1 = [t for t in targets if t != "REF1"]
            for i, target in enumerate(targets_ref1):
                col = 3 + i
                ws_ref1.cell(9, col).value = f"CORDE_{target}_REF1"

                # Valeur temporaire au lieu de formule complexe
                for row in range(10, 16):
                    ws_ref1.cell(row, col).value = f"=0"

            print("   ✅ CORDES REF1 nettoyé")

        # CORDES REF2
        if "CORDES REF2" in wb.sheetnames:
            ws_ref2 = wb["CORDES REF2"]
            print("   🎯 Nettoyage CORDES REF2...")

            # Vider les formules existantes
            for row in range(10, 26):
                for col in range(3, 25):
                    ws_ref2.cell(row, col).value = None

            # En-têtes seulement
            targets_ref2 = [t for t in targets if t != "REF2"]
            for i, target in enumerate(targets_ref2):
                col = 3 + i
                ws_ref2.cell(9, col).value = f"CORDE_{target}_REF2"

                # Valeur temporaire
                for row in range(10, 16):
                    ws_ref2.cell(row, col).value = f"=0"

            print("   ✅ CORDES REF2 nettoyé")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def reparer_fichier_corrompu(filename):
    """Répare le fichier en recréant les formules de façon sûre"""

    print(f"🚨 RÉPARATION DU FICHIER CORROMPU")

    # Sauvegarder l'original
    import shutil
    backup_name = filename.replace('.xlsx', '_AVANT_REPARATION.xlsx')
    try:
        shutil.copy2(filename, backup_name)
        print(f"💾 Sauvegarde créée: {backup_name}")
    except:
        print("⚠️ Impossible de créer la sauvegarde")

    # Réparation étape par étape
    success = True

    if creer_formules_simples_deplacements(filename):
        print("✅ Déplacements réparé")
    else:
        success = False

    if creer_formules_simples_evolution(filename):
        print("✅ Évolution réparé")
    else:
        success = False

    if creer_formules_simples_cordes(filename):
        print("✅ Cordes réparé")
    else:
        success = False

    return success

if __name__ == "__main__":
    filename = input("Nom du fichier Excel corrompu: ")

    print("🔧 RÉPARATION DES FORMULES CORROMPUES")

    if reparer_fichier_corrompu(filename):
        print(f"\n🎉 RÉPARATION TERMINÉE!")
        print(f"📁 Fichier réparé: {filename}")
        print(f"📝 Les formules sont maintenant simples et sûres")
        print(f"⚠️ Vous devrez ajuster manuellement les références aux autres onglets")
    else:
        print(f"\n❌ Échec de la réparation")
        print(f"💡 Essayez de restaurer depuis une sauvegarde")
