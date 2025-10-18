#!/usr/bin/env python3
"""
Création des formules pour les onglets du fichier v2
- DÉPLACEMENTS : écart vs ligne 10 de "Résultats observations"
- ÉVOLUTION PM H V : écart vs ligne 10 de "Résultats Projection"
- CORDES REF1/REF2 : distances 3D vers les références
"""

import openpyxl
from openpyxl.utils import get_column_letter

def analyser_structure_v2(filename):
    """Analyse la structure du fichier v2"""

    print(f"🔍 Analyse de la structure de: {filename}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=True)

        print(f"\n📋 ONGLETS PRÉSENTS ({len(wb.sheetnames)}):")
        for i, sheet_name in enumerate(wb.sheetnames, 1):
            ws = wb[sheet_name]
            print(f"{i:2d}. {sheet_name} ({ws.max_row} lignes, {ws.max_column} colonnes)")

        # Analyse spécifique des onglets cibles
        onglets_cibles = ["Résultats observations", "Résultats Projection", "DÉPLACEMENTS", "ÉVOLUTION PM H V", "CORDES REF1", "CORDES REF2"]

        print(f"\n🎯 ANALYSE DES ONGLETS CIBLES:")
        for onglet in onglets_cibles:
            if onglet in wb.sheetnames:
                ws = wb[onglet]
                print(f"✅ {onglet}")

                # Vérifier la ligne 9 (en-têtes) et 10 (première donnée)
                if ws.max_row >= 10:
                    entetes_ligne9 = []
                    for col in range(1, min(21, ws.max_column + 1)):
                        val = ws.cell(9, col).value
                        if val and isinstance(val, str) and ('_' in val or val in ['Date', 'Jours']):
                            entetes_ligne9.append(f"{get_column_letter(col)}:{val}")

                    if entetes_ligne9:
                        print(f"   📊 En-têtes (ligne 9): {', '.join(entetes_ligne9[:5])}{'...' if len(entetes_ligne9) > 5 else ''}")

                    # Vérifier les données ligne 10
                    donnees_ligne10 = []
                    for col in range(1, min(11, ws.max_column + 1)):
                        val = ws.cell(10, col).value
                        if val is not None:
                            donnees_ligne10.append(f"{get_column_letter(col)}:{val}")

                    if donnees_ligne10:
                        print(f"   📈 Données (ligne 10): {', '.join(donnees_ligne10[:3])}{'...' if len(donnees_ligne10) > 3 else ''}")
                else:
                    print(f"   ⚠️ Pas assez de lignes (max: {ws.max_row})")
            else:
                print(f"❌ {onglet} MANQUANT")

        wb.close()
        return wb.sheetnames

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

def creer_formules_deplacements(filename):
    """Crée les formules pour l'onglet DÉPLACEMENTS"""

    print(f"\n📊 Création des formules DÉPLACEMENTS...")

    try:
        wb = openpyxl.load_workbook(filename)

        if "DÉPLACEMENTS" not in wb.sheetnames:
            print("❌ Onglet DÉPLACEMENTS non trouvé")
            return False

        ws_depl = wb["DÉPLACEMENTS"]

        # Identifier les colonnes avec des en-têtes de type "CIBLE_COORD"
        entetes_colonnes = {}
        for col in range(1, ws_depl.max_column + 1):
            entete = ws_depl.cell(9, col).value
            if entete and isinstance(entete, str) and '_' in entete:
                entetes_colonnes[col] = entete

        print(f"   🎯 {len(entetes_colonnes)} colonnes de données détectées")

        formules_creees = 0
        for col, entete in entetes_colonnes.items():
            col_letter = get_column_letter(col)

            # Formules pour les lignes 11 à 25 (données)
            for row in range(11, 26):
                # Formule: valeur_actuelle - valeur_ligne_10
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

def creer_formules_evolution_pmhv(filename):
    """Crée les formules pour l'onglet ÉVOLUTION PM H V"""

    print(f"\n📈 Création des formules ÉVOLUTION PM H V...")

    try:
        wb = openpyxl.load_workbook(filename)

        if "ÉVOLUTION PM H V" not in wb.sheetnames:
            print("❌ Onglet ÉVOLUTION PM H V non trouvé")
            return False

        ws_evol = wb["ÉVOLUTION PM H V"]

        # Identifier les colonnes avec des en-têtes de type "ΔCIBLE_COORD"
        entetes_colonnes = {}
        for col in range(1, ws_evol.max_column + 1):
            entete = ws_evol.cell(9, col).value
            if entete and isinstance(entete, str) and 'Δ' in entete:
                # Extraire le nom de la cible et coordonnée (ex: "ΔV1_PM" -> "V1_PM")
                nom_cible = entete.replace('Δ', '')
                entetes_colonnes[col] = nom_cible

        print(f"   🎯 {len(entetes_colonnes)} colonnes d'évolution détectées")

        formules_creees = 0
        for col, nom_cible in entetes_colonnes.items():
            col_letter = get_column_letter(col)

            # Formules pour les lignes 11 à 25 (données)
            for row in range(11, 26):
                # Formule: valeur_actuelle - valeur_ligne_10 (depuis Résultats Projection)
                formule = f'=IFERROR(INDEX([Résultats Projection].C:BJ,{row-9},MATCH("{nom_cible}",[Résultats Projection].9:9,0))-INDEX([Résultats Projection].C:BJ,1,MATCH("{nom_cible}",[Résultats Projection].9:9,0)),"")'

                ws_evol.cell(row, col).value = formule
                formules_creees += 1

        print(f"   ✅ {formules_creees} formules créées")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def creer_formules_cordes(filename):
    """Crée les formules pour les onglets CORDES REF1 et REF2"""

    print(f"\n📏 Création des formules CORDES...")

    try:
        wb = openpyxl.load_workbook(filename)

        # Liste des cibles
        targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

        formules_totales = 0

        # CORDES REF1
        if "CORDES REF1" in wb.sheetnames:
            ws_ref1 = wb["CORDES REF1"]
            print("   🎯 Traitement CORDES REF1...")

            # Cibles vers REF1 (exclure REF1 elle-même)
            targets_ref1 = [t for t in targets if t != "REF1"]

            for i, target in enumerate(targets_ref1):
                col = 3 + i  # Colonnes à partir de C

                # En-tête
                ws_ref1.cell(9, col).value = f"CORDE_{target}_REF1"

                # Formules pour lignes 10-25
                for row in range(10, 26):
                    formule = f'=IFERROR(SQRT((INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_X",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,{row-9},MATCH("REF1_X",[Résultats observations].9:9,0)))^2+(INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_Y",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,{row-9},MATCH("REF1_Y",[Résultats observations].9:9,0)))^2+(INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_Z",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,{row-9},MATCH("REF1_Z",[Résultats observations].9:9,0)))^2),"")'

                    ws_ref1.cell(row, col).value = formule
                    formules_totales += 1

            print(f"   ✅ CORDES REF1: {len(targets_ref1)} colonnes")

        # CORDES REF2
        if "CORDES REF2" in wb.sheetnames:
            ws_ref2 = wb["CORDES REF2"]
            print("   🎯 Traitement CORDES REF2...")

            # Cibles vers REF2 (exclure REF2 elle-même)
            targets_ref2 = [t for t in targets if t != "REF2"]

            for i, target in enumerate(targets_ref2):
                col = 3 + i  # Colonnes à partir de C

                # En-tête
                ws_ref2.cell(9, col).value = f"CORDE_{target}_REF2"

                # Formules pour lignes 10-25
                for row in range(10, 26):
                    formule = f'=IFERROR(SQRT((INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_X",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,{row-9},MATCH("REF2_X",[Résultats observations].9:9,0)))^2+(INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_Y",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,{row-9},MATCH("REF2_Y",[Résultats observations].9:9,0)))^2+(INDEX([Résultats observations].C:BJ,{row-9},MATCH("{target}_Z",[Résultats observations].9:9,0))-INDEX([Résultats observations].C:BJ,{row-9},MATCH("REF2_Z",[Résultats observations].9:9,0)))^2),"")'

                    ws_ref2.cell(row, col).value = formule
                    formules_totales += 1

            print(f"   ✅ CORDES REF2: {len(targets_ref2)} colonnes")

        print(f"   📊 Total: {formules_totales} formules de cordes créées")

        wb.save(filename)
        wb.close()
        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    filename = input("Nom du fichier Excel (v2): ")

    print("🚀 CRÉATION DES FORMULES POUR LE FICHIER V2")

    # 1. Analyse de la structure
    print("="*60)
    onglets = analyser_structure_v2(filename)

    if not onglets:
        print("❌ Impossible d'analyser le fichier")
        exit(1)

    # 2. Création des formules
    print("\n" + "="*60)
    print("🔧 CRÉATION DES FORMULES...")

    # DÉPLACEMENTS
    if creer_formules_deplacements(filename):
        print("✅ Formules DÉPLACEMENTS créées")

    # ÉVOLUTION PM H V
    if creer_formules_evolution_pmhv(filename):
        print("✅ Formules ÉVOLUTION PM H V créées")

    # CORDES
    if creer_formules_cordes(filename):
        print("✅ Formules CORDES créées")

    print(f"\n🎉 TERMINÉ!")
    print(f"📁 Fichier mis à jour: {filename}")
    print(f"📊 Toutes les formules ont été générées automatiquement")
