#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un fichier Excel avec présentation spatiale des déplacements

FONCTIONNALITÉS :
- Lit le fichier CSV avec les déplacements et le nombre de cibles par section
- Crée une feuille Excel par section (9 sections total)
- Chaque feuille contient 2 tableaux : PÉRIODIQUE et CUMULÉ
- Adapte automatiquement la disposition selon le nombre de cibles (5 ou 7)

DISPOSITION SPATIALE :
    5 cibles:              7 cibles:
    BG      HG             BG      IG
        CH                 HG      CH
    HD      BD             HD      ID      BD

FORMATAGE :
- Police : Lucida Sans 8.5
- Largeur colonnes : 11.29 unités Excel
- Fond blanc (#FFFFFF) avec bordures fines
- Bordures uniquement sur les cellules du tableau (pas sur les cellules intermédiaires)

VERSION : 2.0 (4 novembre 2025)
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Chemins
csv_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\2-extractions\smc_output\Deplacements_Ligne_SMC_2025_11_avec_nb_cibles.csv"
output_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\2-extractions\smc_output\Deplacements_Spatial_Complet.xlsx"

print("="*80)
print("GÉNÉRATION PRÉSENTATION SPATIALE DES DÉPLACEMENTS")
print("="*80)
print(f"Fichier source : {csv_path}")
print()

# Lire le CSV
df = pd.read_csv(csv_path, sep=';')

# Filtrer les lignes valides (enlever les lignes d'en-tête parasites)
df = df[df['type'] == 'Déplacements']

# Créer le classeur Excel
wb = Workbook()
wb.remove(wb.active)  # Supprimer la feuille par défaut

# Styles
title_font = Font(name='Lucida Sans', size=8.5, bold=True, color="000000")
title_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
header_font = Font(name='Lucida Sans', size=8.5, bold=True, color="000000")
header_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
data_font = Font(name='Lucida Sans', size=8.5)
label_font = Font(name='Lucida Sans', size=8.5, bold=True)
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

def format_value(val):
    """Formate une valeur numérique à 1 décimale"""
    if pd.isna(val) or val == '':
        return ''
    try:
        return round(float(val), 1)
    except:
        return val

def add_spatial_layout_5_targets(ws, row_data, start_row, mode_label):
    """
    Ajoute la disposition spatiale pour 5 cibles
    Layout:
        BG          HG
            CH
        HD          BD
    """
    galerie = row_data['galerie']
    section = row_data['section']
    
    # Titre
    cell = ws.cell(row=start_row, column=2)
    cell.value = f"{galerie} {section} - Déplacements {mode_label}"
    cell.font = title_font
    cell.fill = title_fill
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border
    ws.merge_cells(start_row=start_row, start_column=2, end_row=start_row, end_column=10)
    
    # Appliquer les bordures sur toutes les cellules fusionnées du titre
    for col in range(2, 11):
        ws.cell(row=start_row, column=col).border = thin_border
    
    current_row = start_row + 2
    
    # Liste des cellules qui font partie du tableau (pour appliquer bordures)
    table_cells = []
    
    # Ligne 1: BG et HG
    row1 = current_row
    # BG (Bas Gauche)
    ws.cell(row=row1, column=3, value="DPM bas gauche")
    ws.cell(row=row1, column=4, value="DH bas gauche")
    ws.cell(row=row1, column=5, value="DZ bas gauche")
    ws.cell(row=row1+1, column=3, value=format_value(row_data.get('DPM BG')))
    ws.cell(row=row1+1, column=4, value=format_value(row_data.get('DH BG')))
    ws.cell(row=row1+1, column=5, value=format_value(row_data.get('DZ BG')))
    table_cells.extend([(row1, 3), (row1, 4), (row1, 5), (row1+1, 3), (row1+1, 4), (row1+1, 5)])
    
    # HG (Haut Gauche)
    ws.cell(row=row1, column=7, value="DPM haut gauche")
    ws.cell(row=row1, column=8, value="DH haut gauche")
    ws.cell(row=row1, column=9, value="DZ haut gauche")
    ws.cell(row=row1+1, column=7, value=format_value(row_data.get('DPM HG')))
    ws.cell(row=row1+1, column=8, value=format_value(row_data.get('DH HG')))
    ws.cell(row=row1+1, column=9, value=format_value(row_data.get('DZ HG')))
    table_cells.extend([(row1, 7), (row1, 8), (row1, 9), (row1+1, 7), (row1+1, 8), (row1+1, 9)])
    
    current_row += 3
    
    # Ligne 2: CH (Clé Haute / Voute)
    row2 = current_row
    ws.cell(row=row2, column=3, value="DPM centre haut")
    ws.cell(row=row2, column=4, value="DH centre haut")
    ws.cell(row=row2, column=5, value="DZ centre haut")
    ws.cell(row=row2+1, column=3, value=format_value(row_data.get('DPM CH')))
    ws.cell(row=row2+1, column=4, value=format_value(row_data.get('DH CH')))
    ws.cell(row=row2+1, column=5, value=format_value(row_data.get('DZ CH')))
    table_cells.extend([(row2, 3), (row2, 4), (row2, 5), (row2+1, 3), (row2+1, 4), (row2+1, 5)])
    
    # HD (Haut Droit)
    ws.cell(row=row2, column=7, value="DPM haut droit")
    ws.cell(row=row2, column=8, value="DH haut droit")
    ws.cell(row=row2, column=9, value="DZ haut droit")
    ws.cell(row=row2+1, column=7, value=format_value(row_data.get('DPM HD')))
    ws.cell(row=row2+1, column=8, value=format_value(row_data.get('DH HD')))
    ws.cell(row=row2+1, column=9, value=format_value(row_data.get('DZ HD')))
    table_cells.extend([(row2, 7), (row2, 8), (row2, 9), (row2+1, 7), (row2+1, 8), (row2+1, 9)])
    
    current_row += 3
    
    # Ligne 3: BD (Bas Droit)
    row3 = current_row
    ws.cell(row=row3, column=5, value="DPM bas droit")
    ws.cell(row=row3, column=6, value="DH bas droit")
    ws.cell(row=row3, column=7, value="DZ bas droit")
    ws.cell(row=row3+1, column=5, value=format_value(row_data.get('DPM BD')))
    ws.cell(row=row3+1, column=6, value=format_value(row_data.get('DH BD')))
    ws.cell(row=row3+1, column=7, value=format_value(row_data.get('DZ BD')))
    table_cells.extend([(row3, 5), (row3, 6), (row3, 7), (row3+1, 5), (row3+1, 6), (row3+1, 7)])
    
    # Appliquer les styles sur toutes les cellules du tableau
    for row, col in table_cells:
        cell = ws.cell(row=row, column=col)
        if cell.value is not None and cell.value != '':
            if 'DPM' in str(cell.value) or 'DH' in str(cell.value) or 'DZ' in str(cell.value):
                cell.font = header_font
                cell.fill = header_fill
            else:
                cell.font = data_font
                # Appliquer format numérique à 1 décimale pour les valeurs numériques
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '0.0'
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    
    return current_row + 3


def add_spatial_layout_7_targets(ws, row_data, start_row, mode_label):
    """
    Ajoute la disposition spatiale pour 7 cibles
    Layout:
        BG      IG
        HG      CH
        HD      ID      BD
    """
    galerie = row_data['galerie']
    section = row_data['section']
    
    # Titre
    cell = ws.cell(row=start_row, column=2)
    cell.value = f"{galerie} {section} - Déplacements {mode_label}"
    cell.font = title_font
    cell.fill = title_fill
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border
    ws.merge_cells(start_row=start_row, start_column=2, end_row=start_row, end_column=10)
    
    # Appliquer les bordures sur toutes les cellules fusionnées du titre
    for col in range(2, 11):
        ws.cell(row=start_row, column=col).border = thin_border
    
    current_row = start_row + 2
    
    # Liste des cellules qui font partie du tableau (pour appliquer bordures)
    table_cells = []
    
    # Ligne 1: BG, IG, HG
    row1 = current_row
    # BG (Bas Gauche)
    ws.cell(row=row1, column=3, value="DPM bas gauche")
    ws.cell(row=row1, column=4, value="DH bas gauche")
    ws.cell(row=row1, column=5, value="DZ bas gauche")
    ws.cell(row=row1+1, column=3, value=format_value(row_data.get('DPM BG')))
    ws.cell(row=row1+1, column=4, value=format_value(row_data.get('DH BG')))
    ws.cell(row=row1+1, column=5, value=format_value(row_data.get('DZ BG')))
    table_cells.extend([(row1, 3), (row1, 4), (row1, 5), (row1+1, 3), (row1+1, 4), (row1+1, 5)])
    
    # IG (Inter Gauche)
    ws.cell(row=row1, column=7, value="DPM inter gauche")
    ws.cell(row=row1, column=8, value="DH inter gauche")
    ws.cell(row=row1, column=9, value="DZ inter gauche")
    ws.cell(row=row1+1, column=7, value=format_value(row_data.get('DPM IG')))
    ws.cell(row=row1+1, column=8, value=format_value(row_data.get('DH IG')))
    ws.cell(row=row1+1, column=9, value=format_value(row_data.get('DZ IG')))
    table_cells.extend([(row1, 7), (row1, 8), (row1, 9), (row1+1, 7), (row1+1, 8), (row1+1, 9)])
    
    current_row += 3
    
    # Ligne 2: HG et CH (Centre Haut / Voute)
    row2 = current_row
    # HG (Haut Gauche)
    ws.cell(row=row2, column=3, value="DPM haut gauche")
    ws.cell(row=row2, column=4, value="DH haut gauche")
    ws.cell(row=row2, column=5, value="DZ haut gauche")
    ws.cell(row=row2+1, column=3, value=format_value(row_data.get('DPM HG')))
    ws.cell(row=row2+1, column=4, value=format_value(row_data.get('DH HG')))
    ws.cell(row=row2+1, column=5, value=format_value(row_data.get('DZ HG')))
    table_cells.extend([(row2, 3), (row2, 4), (row2, 5), (row2+1, 3), (row2+1, 4), (row2+1, 5)])
    
    # CH (Centre Haut / Voute)
    ws.cell(row=row2, column=7, value="DPM centre haut")
    ws.cell(row=row2, column=8, value="DH centre haut")
    ws.cell(row=row2, column=9, value="DZ centre haut")
    ws.cell(row=row2+1, column=7, value=format_value(row_data.get('DPM CH')))
    ws.cell(row=row2+1, column=8, value=format_value(row_data.get('DH CH')))
    ws.cell(row=row2+1, column=9, value=format_value(row_data.get('DZ CH')))
    table_cells.extend([(row2, 7), (row2, 8), (row2, 9), (row2+1, 7), (row2+1, 8), (row2+1, 9)])
    
    current_row += 3
    
    # Ligne 4: HD, ID
    row4 = current_row
    # HD (Haut Droit)
    ws.cell(row=row4, column=3, value="DPM haut droit")
    ws.cell(row=row4, column=4, value="DH haut droit")
    ws.cell(row=row4, column=5, value="DZ haut droit")
    ws.cell(row=row4+1, column=3, value=format_value(row_data.get('DPM HD')))
    ws.cell(row=row4+1, column=4, value=format_value(row_data.get('DH HD')))
    ws.cell(row=row4+1, column=5, value=format_value(row_data.get('DZ HD')))
    table_cells.extend([(row4, 3), (row4, 4), (row4, 5), (row4+1, 3), (row4+1, 4), (row4+1, 5)])
    
    # ID (Inter Droit)
    ws.cell(row=row4, column=7, value="DPM inter droit")
    ws.cell(row=row4, column=8, value="DH inter droit")
    ws.cell(row=row4, column=9, value="DZ inter droit")
    ws.cell(row=row4+1, column=7, value=format_value(row_data.get('DPM ID')))
    ws.cell(row=row4+1, column=8, value=format_value(row_data.get('DH ID')))
    ws.cell(row=row4+1, column=9, value=format_value(row_data.get('DZ ID')))
    table_cells.extend([(row4, 7), (row4, 8), (row4, 9), (row4+1, 7), (row4+1, 8), (row4+1, 9)])
    
    current_row += 3
    
    # Ligne 5: BD (Bas Droit)
    row5 = current_row
    ws.cell(row=row5, column=5, value="DPM bas droit")
    ws.cell(row=row5, column=6, value="DH bas droit")
    ws.cell(row=row5, column=7, value="DZ bas droit")
    ws.cell(row=row5+1, column=5, value=format_value(row_data.get('DPM BD')))
    ws.cell(row=row5+1, column=6, value=format_value(row_data.get('DH BD')))
    ws.cell(row=row5+1, column=7, value=format_value(row_data.get('DZ BD')))
    table_cells.extend([(row5, 5), (row5, 6), (row5, 7), (row5+1, 5), (row5+1, 6), (row5+1, 7)])
    
    # Appliquer les styles sur toutes les cellules du tableau
    for row, col in table_cells:
        cell = ws.cell(row=row, column=col)
        if cell.value is not None and cell.value != '':
            if 'DPM' in str(cell.value) or 'DH' in str(cell.value) or 'DZ' in str(cell.value):
                cell.font = header_font
                cell.fill = header_fill
            else:
                cell.font = data_font
                # Appliquer format numérique à 1 décimale pour les valeurs numériques
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '0.0'
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border
    
    return current_row + 3


# Grouper par section
sections = df.groupby(['galerie', 'section'])

print(f"Traitement de {len(sections)} sections...")
print()

for (galerie, section), group in sections:
    # Créer une feuille par section
    sheet_name = f"{galerie} {section}"[:31]  # Max 31 caractères pour nom de feuille
    ws = wb.create_sheet(title=sheet_name)
    
    print(f"  Génération : {sheet_name}")
    
    # Largeur des colonnes
    for col in range(1, 12):
        ws.column_dimensions[get_column_letter(col)].width = 11.29
    
    current_row = 1
    
    # Récupérer le nombre de cibles
    nb_cibles = int(group.iloc[0]['Nb_cibles'])
    
    # Trouver les lignes périodique et cumulé
    row_periodique = group[group['mode'] == 'périodique'].iloc[0]
    row_cumule = group[group['mode'] == 'cumulé'].iloc[0]
    
    print(f"    Nombre de cibles détecté : {nb_cibles}")
    
    # Disposition PÉRIODIQUE
    if nb_cibles == 5:
        current_row = add_spatial_layout_5_targets(ws, row_periodique, current_row, "PÉRIODIQUE")
    else:
        current_row = add_spatial_layout_7_targets(ws, row_periodique, current_row, "PÉRIODIQUE")
    
    current_row += 2  # Espacement
    
    # Disposition CUMULÉ
    if nb_cibles == 5:
        current_row = add_spatial_layout_5_targets(ws, row_cumule, current_row, "CUMULÉ")
    else:
        current_row = add_spatial_layout_7_targets(ws, row_cumule, current_row, "CUMULÉ")

print()
print("="*80)
print("Sauvegarde du fichier Excel...")
wb.save(output_path)

print("="*80)
print(f"SUCCÈS ! Fichier généré :")
print(f"{output_path}")
print("="*80)
print()
print(f"Nombre de feuilles créées : {len(wb.worksheets)}")
print("Chaque feuille contient : PÉRIODIQUE + CUMULÉ")
