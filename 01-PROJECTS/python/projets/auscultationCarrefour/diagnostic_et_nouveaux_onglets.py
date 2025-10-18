#!/usr/bin/env python3
"""
Diagnostic et correction des références circulaires
+ Création des onglets CORDES et ÉVOLUTION
"""

import openpyxl
from openpyxl.utils import get_column_letter

def diagnostiquer_references_circulaires(filename):
    """Diagnostic des références circulaires dans le fichier Excel"""

    print(f"🔍 Diagnostic des références circulaires dans: {filename}")

    try:
        wb = openpyxl.load_workbook(filename, data_only=False)

        problemes = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            print(f"\\n📋 Analyse de l'onglet: {sheet_name}")

            for row in range(1, min(50, ws.max_row + 1)):
                for col in range(1, min(100, ws.max_column + 1)):
                    cell = ws.cell(row, col)
                    if cell.value and str(cell.value).startswith('='):
                        formule = str(cell.value)
                        cell_ref = f"{get_column_letter(col)}{row}"

                        # Vérifier si la cellule se référence elle-même
                        if cell_ref in formule:
                            problemes.append({
                                'onglet': sheet_name,
                                'cellule': cell_ref,
                                'formule': formule[:100] + '...' if len(formule) > 100 else formule
                            })

                        # Chercher des patterns suspects
                        if formule.count('$A') > 5:  # Trop de références absolues
                            print(f"   ⚠️ Formule complexe en {cell_ref}: {formule[:50]}...")

        if problemes:
            print(f"\\n❌ RÉFÉRENCES CIRCULAIRES TROUVÉES:")
            for pb in problemes:
                print(f"   {pb['onglet']}.{pb['cellule']}: {pb['formule']}")
        else:
            print(f"\\n✅ Aucune référence circulaire évidente détectée")

        wb.close()
        return problemes

    except Exception as e:
        print(f"❌ Erreur lors du diagnostic: {e}")
        return []

def creer_onglet_cordes_ref1():
    """Crée l'onglet pour les cordes vers REF1"""

    print(f"\\n📏 Création de l'onglet CORDES REF1...")

    # Code de base pour l'onglet
    script_cordes_ref1 = '''
def ajouter_onglet_cordes_ref1(filename):
    wb = openpyxl.load_workbook(filename)
    ws_cordes = wb.create_sheet("CORDES REF1")

    # En-têtes
    ws_cordes.cell(7, 1).value = "Date point 0"
    ws_cordes.cell(8, 1).value = "Date"
    ws_cordes.cell(8, 2).value = "Jours"
    ws_cordes.cell(9, 1).value = "Date"
    ws_cordes.cell(9, 2).value = "Jours"

    # Cibles (sans REF1 elle-même)
    targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF2"]

    start_col = 3
    for i, target in enumerate(targets):
        col = start_col + i
        ws_cordes.cell(9, col).value = f"CORDE_{target}_REF1"

        # Formules de calcul de distance 3D
        for row in range(10, 25):
            formule = f"""=IFERROR(
                SQRT(
                    (INDEX(Observations.C:BJ,{row-9},MATCH("{target}_X",Observations.9:9,0)) -
                     INDEX(Observations.C:BJ,{row-9},MATCH("REF1_X",Observations.9:9,0)))^2 +
                    (INDEX(Observations.C:BJ,{row-9},MATCH("{target}_Y",Observations.9:9,0)) -
                     INDEX(Observations.C:BJ,{row-9},MATCH("REF1_Y",Observations.9:9,0)))^2 +
                    (INDEX(Observations.C:BJ,{row-9},MATCH("{target}_Z",Observations.9:9,0)) -
                     INDEX(Observations.C:BJ,{row-9},MATCH("REF1_Z",Observations.9:9,0)))^2
                ),
                ""
            )"""
            ws_cordes.cell(row, col).value = ' '.join(formule.split())

    wb.save(filename)
    wb.close()
'''

    return script_cordes_ref1

def creer_onglet_evolution():
    """Crée l'onglet pour l'évolution des déports"""

    print(f"\\n📈 Création de l'onglet ÉVOLUTION...")

    script_evolution = '''
def ajouter_onglet_evolution(filename):
    wb = openpyxl.load_workbook(filename)
    ws_evol = wb.create_sheet("ÉVOLUTION PM H V")

    # En-têtes
    ws_evol.cell(7, 1).value = "Date point 0"
    ws_evol.cell(8, 1).value = "Date"
    ws_evol.cell(8, 2).value = "Jours"
    ws_evol.cell(9, 1).value = "Date"
    ws_evol.cell(9, 2).value = "Jours"

    # Toutes les cibles
    targets = ["V1","V2","V3"] + [f"H{i}" for i in range(1,6)] + [f"B{i}" for i in range(1,6)] + [f"M{i}" for i in range(1,6)] + ["REF1","REF2"]

    start_col = 3
    current_col = start_col

    for target in targets:
        # 3 colonnes par cible: ΔPMPM, ΔH, ΔV
        for coord in ['PM', 'H', 'V']:
            ws_evol.cell(9, current_col).value = f"Δ{target}_{coord}"

            # Formules: valeur actuelle - première valeur
            for row in range(10, 25):
                formule = f"""=IFERROR(
                    INDEX(PROJECTION.C:BJ,{row-9},MATCH("{target}_{coord}",PROJECTION.9:9,0)) -
                    INDEX(PROJECTION.C:BJ,1,MATCH("{target}_{coord}",PROJECTION.9:9,0)),
                    ""
                )"""
                ws_evol.cell(row, current_col).value = ' '.join(formule.split())

            current_col += 1

    wb.save(filename)
    wb.close()
'''

    return script_evolution

def creer_script_complet():
    """Crée le script complet pour tous les onglets"""

    script_complet = f'''#!/usr/bin/env python3
"""
Script complet pour ajouter les onglets CORDES et ÉVOLUTION
"""

import openpyxl
from openpyxl.utils import get_column_letter

{creer_onglet_cordes_ref1()}

{creer_onglet_evolution()}

def ajouter_onglet_cordes_ref2(filename):
    """Ajoute l'onglet CORDES REF2 (similaire à REF1)"""
    wb = openpyxl.load_workbook(filename)
    ws_cordes = wb.create_sheet("CORDES REF2")

    # En-têtes identiques
    ws_cordes.cell(7, 1).value = "Date point 0"
    ws_cordes.cell(8, 1).value = "Date"
    ws_cordes.cell(8, 2).value = "Jours"
    ws_cordes.cell(9, 1).value = "Date"
    ws_cordes.cell(9, 2).value = "Jours"

    # Cibles (sans REF2 elle-même)
    targets = ["V1","V2","V3"] + [f"H{{i}}" for i in range(1,6)] + [f"B{{i}}" for i in range(1,6)] + [f"M{{i}}" for i in range(1,6)] + ["REF1"]

    start_col = 3
    for i, target in enumerate(targets):
        col = start_col + i
        ws_cordes.cell(9, col).value = f"CORDE_{{target}}_REF2"

        # Formules vers REF2 au lieu de REF1
        for row in range(10, 25):
            formule = f"""=IFERROR(
                SQRT(
                    (INDEX(Observations.C:BJ,{{row-9}},MATCH("{{target}}_X",Observations.9:9,0)) -
                     INDEX(Observations.C:BJ,{{row-9}},MATCH("REF2_X",Observations.9:9,0)))^2 +
                    (INDEX(Observations.C:BJ,{{row-9}},MATCH("{{target}}_Y",Observations.9:9,0)) -
                     INDEX(Observations.C:BJ,{{row-9}},MATCH("REF2_Y",Observations.9:9,0)))^2 +
                    (INDEX(Observations.C:BJ,{{row-9}},MATCH("{{target}}_Z",Observations.9:9,0)) -
                     INDEX(Observations.C:BJ,{{row-9}},MATCH("REF2_Z",Observations.9:9,0)))^2
                ),
                ""
            )"""
            ws_cordes.cell(row, col).value = ' '.join(formule.split())

    wb.save(filename)
    wb.close()

if __name__ == "__main__":
    filename = input("Nom du fichier Excel: ")

    print("🚀 Ajout des onglets CORDES et ÉVOLUTION...")

    try:
        ajouter_onglet_cordes_ref1(filename)
        print("✅ Onglet CORDES REF1 ajouté")

        ajouter_onglet_cordes_ref2(filename)
        print("✅ Onglet CORDES REF2 ajouté")

        ajouter_onglet_evolution(filename)
        print("✅ Onglet ÉVOLUTION PM H V ajouté")

        print(f"\\n🎉 TERMINÉ!")
        print(f"📊 3 nouveaux onglets ajoutés au fichier")

    except Exception as e:
        print(f"❌ Erreur: {{e}}")
'''

    with open("ajouter_onglets_cordes_evolution.py", "w", encoding="utf-8") as f:
        f.write(script_complet)

    print("✅ Script créé: ajouter_onglets_cordes_evolution.py")

if __name__ == "__main__":
    print("🔧 DIAGNOSTIC ET CRÉATION DES NOUVEAUX ONGLETS")

    # 1. Diagnostic (vous devrez fournir le nom du fichier)
    print("\\n1️⃣ DIAGNOSTIC DES RÉFÉRENCES CIRCULAIRES")
    print("   (Indiquez le nom de votre fichier pour le diagnostic)")

    # 2. Création des scripts
    print("\\n2️⃣ CRÉATION DES SCRIPTS POUR LES NOUVEAUX ONGLETS")
    creer_script_complet()

    print(f"\\n🎯 PROCHAINES ÉTAPES:")
    print(f"1. Diagnostic: python -c 'import ce_script; diagnostiquer_references_circulaires(\"votre_fichier.xlsx\")'")
    print(f"2. Ajout onglets: python ajouter_onglets_cordes_evolution.py")
    print(f"3. Entrez le nom de votre fichier quand demandé")
