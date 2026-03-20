#!/usr/bin/env python3
"""
Créer un onglet PROJECTION avec les déports PM, H, V
"""

import openpyxl
from openpyxl.utils import get_column_letter
import shutil

def creer_onglet_projection():
    """Crée un onglet PROJECTION avec les calculs PM, H, V"""

    input_file = "AUSCULTATION_FORMULES_CORRIGEES.xlsx"
    output_file = "AUSCULTATION_AVEC_PROJECTION.xlsx"

    print(f"🎯 Création de l'onglet PROJECTION...")
    print(f"📂 Entrée: {input_file}")
    print(f"📁 Sortie: {output_file}")

    # Copier le fichier existant
    shutil.copy2(input_file, output_file)

    # Ouvrir le fichier
    wb = openpyxl.load_workbook(output_file)

    # Créer le nouvel onglet PROJECTION
    ws_proj = wb.create_sheet("PROJECTION")

    print("📊 Configuration de l'onglet PROJECTION...")

    # === Structure identique à Observations mais avec PM, H, V ===

    # En-têtes fixes
    ws_proj.cell(7, 1).value = "Date point 0"
    ws_proj.cell(8, 1).value = "Date"
    ws_proj.cell(8, 2).value = "Jours"

    # Ligne 9: En-têtes des colonnes
    ws_proj.cell(9, 1).value = "Date"
    ws_proj.cell(9, 2).value = "Jours"

    # === Définir les 20 cibles avec PM, H, V ===
    targets = []
    for i in range(1, 4): targets.append(f"V{i}")    # V1,V2,V3
    for i in range(1, 6): targets.append(f"H{i}")    # H1-H5
    for i in range(1, 6): targets.append(f"B{i}")    # B1-B5
    for i in range(1, 6): targets.append(f"M{i}")    # M1-M5
    targets.extend(["REF1", "REF2"])                 # REF1,REF2

    print(f"🎯 Ajout des {len(targets)} cibles avec PM, H, V...")

    # Paramètres de l'axe
    axe_params = {
        'X_DEBUT': 823216.6581,
        'Y_DEBUT': 1091503.0821,
        'X_FIN': 823258.9200,
        'Y_FIN': 1091412.4514,
        'Z_REF': -123.621,
        'PK_DEBUT': 0.0
    }

    # Calculer DX, DY, LONGUEUR_AXE
    dx_axe = axe_params['X_FIN'] - axe_params['X_DEBUT']
    dy_axe = axe_params['Y_FIN'] - axe_params['Y_DEBUT']
    longueur_axe = (dx_axe**2 + dy_axe**2)**0.5

    start_col = 3  # Colonne C
    current_col = start_col

    for target_id in targets:
        print(f"   📍 {target_id} -> {get_column_letter(current_col)}-{get_column_letter(current_col+2)} (PM, H, V)")

        # En-têtes pour PM, H, V
        coords = ['PM', 'H', 'V']
        for coord_idx, coord in enumerate(coords):
            col = current_col + coord_idx

            # En-têtes ligne 9
            ws_proj.cell(9, col).value = f"{target_id}_{coord}"

            # Créer les formules selon le type de coordonnée
            for row in range(10, 25):  # Lignes de données

                if coord == 'PM':  # Position le long de l'axe (PK)
                    # Formule pour calculer le PK projeté
                    formule = f'''=IFERROR(
                        LET(
                            x_mes, INDEX(DATABASE.X:X,MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_id}"),0)),
                            y_mes, INDEX(DATABASE.Y:Y,MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_id}"),0)),
                            dx_mes, x_mes-{axe_params['X_DEBUT']},
                            dy_mes, y_mes-{axe_params['Y_DEBUT']},
                            proj_long, (dx_mes*{dx_axe} + dy_mes*{dy_axe})/{longueur_axe},
                            {axe_params['PK_DEBUT']} + proj_long
                        ),
                        ""
                    )'''

                elif coord == 'H':  # Déport latéral/transversal
                    # Formule pour calculer le déport transversal
                    formule = f'''=IFERROR(
                        LET(
                            x_mes, INDEX(DATABASE.X:X,MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_id}"),0)),
                            y_mes, INDEX(DATABASE.Y:Y,MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_id}"),0)),
                            dx_mes, x_mes-{axe_params['X_DEBUT']},
                            dy_mes, y_mes-{axe_params['Y_DEBUT']},
                            proj_long, (dx_mes*{dx_axe} + dy_mes*{dy_axe})/{longueur_axe},
                            ratio, proj_long/{longueur_axe},
                            x_proj, {axe_params['X_DEBUT']} + ratio*{dx_axe},
                            y_proj, {axe_params['Y_DEBUT']} + ratio*{dy_axe},
                            dx_trans, x_mes-x_proj,
                            dy_trans, y_mes-y_proj,
                            deport_abs, SQRT(dx_trans^2+dy_trans^2),
                            signe, IF(({dx_axe}*dy_trans - {dy_axe}*dx_trans)<0, -1, 1),
                            deport_abs * signe
                        ),
                        ""
                    )'''

                elif coord == 'V':  # Déport vertical
                    # Formule pour calculer le déport vertical
                    formule = f'''=IFERROR(
                        INDEX(DATABASE.Z:Z,MATCH(1,(DATABASE.DATE:DATE=$A{row})*(DATABASE.NO:NO="{target_id}"),0)) - {axe_params['Z_REF']},
                        ""
                    )'''

                # Nettoyer la formule (supprimer les retours à la ligne)
                formule_clean = ' '.join(formule.split())
                ws_proj.cell(row, col).value = formule_clean

        current_col += 3  # Passer aux 3 colonnes suivantes

    print("📅 Ajout des dates d'exemple...")

    # Ajouter les dates d'exemple
    sample_dates = [
        '2024-08-28', '2024-09-05', '2024-09-09',
        '2024-09-13', '2024-09-17', '2024-09-18'
    ]

    for i, date in enumerate(sample_dates):
        row = 10 + i
        ws_proj.cell(row, 1).value = date  # Colonne A = Date

        # Colonne B = Jours écoulés
        if i == 0:
            ws_proj.cell(row, 2).value = 0
        else:
            ws_proj.cell(row, 2).value = f"=A{row}-A$10"

    # Sauvegarder
    wb.save(output_file)
    wb.close()

    print(f"✅ Fichier avec onglet PROJECTION créé: {output_file}")
    return output_file

def creer_info_projection():
    """Crée un fichier d'information sur l'onglet PROJECTION"""

    info = f"""
📐 ONGLET PROJECTION - SYSTÈME DE COORDONNÉES CHANTIER

NOMENCLATURE:
- PM : Position le long de l'axe (équivalent PK)
- H  : Déport latéral/transversal (+ = droite, - = gauche)
- V  : Déport vertical (par rapport à Z = -123.621 m)

AXE DE RÉFÉRENCE:
- Origine: PK 0 → X=823216.6581, Y=1091503.0821, Z=-123.621
- Fin: PK 100 → X=823258.9200, Y=1091412.4514, Z=-123.621
- Azimut: 172.2222 gr
- Pente: 0.0%

COLONNES CRÉÉES:
C: V1_PM    D: V1_H     E: V1_V
F: V2_PM    G: V2_H     H: V2_V
I: V3_PM    J: V3_H     K: V3_V
L: H1_PM    M: H1_H     N: H1_V
... (jusqu'à REF2)

CALCULS:
- PM: Projection sur l'axe depuis l'origine
- H: Distance perpendiculaire à l'axe (signe selon côté)
- V: Différence avec l'altitude de référence

UTILISATION:
1. Ajoutez vos mesures XYZ dans l'onglet DATABASE
2. Les projections PM, H, V apparaissent automatiquement
3. Analysez les déplacements dans le système d'axe du chantier
"""

    with open("INFO_ONGLET_PROJECTION.txt", "w", encoding="utf-8") as f:
        f.write(info)

    print("📝 Information sauvée: INFO_ONGLET_PROJECTION.txt")

if __name__ == "__main__":
    print("🚀 Création de l'onglet PROJECTION avec nomenclature chantier...")

    try:
        projection_file = creer_onglet_projection()
        creer_info_projection()

        print(f"\\n🎉 ONGLET PROJECTION CRÉÉ!")
        print(f"📁 Fichier: {projection_file}")
        print(f"📋 Info: INFO_ONGLET_PROJECTION.txt")

        print(f"\\n📐 NOMENCLATURE CHANTIER:")
        print(f"   PM = Position sur axe (PK)")
        print(f"   H  = Déport latéral")
        print(f"   V  = Déport vertical")

        print(f"\\n💡 MAINTENANT VOUS AVEZ:")
        print(f"   - Onglet DATABASE: Coordonnées XYZ brutes")
        print(f"   - Onglet Observations: Coordonnées XYZ calculées")
        print(f"   - Onglet PROJECTION: Déports PM, H, V")

    except Exception as e:
        print(f"❌ Erreur: {e}")
