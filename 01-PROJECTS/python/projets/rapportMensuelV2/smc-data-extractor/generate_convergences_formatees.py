#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère un fichier Excel formaté pour les convergences
Une feuille par section avec uniquement les colonnes pertinentes (5 ou 7 cibles)
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Chemins
csv_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\2-extractions\smc_output\Convergences_Ligne_SMC_2025_11.csv"
output_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\2-extractions\smc_output\Convergences_Formatees_Complet.xlsx"

print("="*80)
print("GÉNÉRATION CONVERGENCES FORMATÉES PAR SECTION")
print("="*80)
print(f"Fichier source : {csv_path}")
print()

# Lire le CSV
df = pd.read_csv(csv_path)

# Créer le classeur Excel
wb = Workbook()
wb.remove(wb.active)  # Supprimer la feuille par défaut

# Styles
title_font = Font(name='Lucida Sans', size=9, bold=True, color="FFFFFF")
title_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
header_font = Font(name='Lucida Sans', size=9, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
data_font = Font(name='Lucida Sans', size=9)
mode_font = Font(name='Lucida Sans', size=9, bold=True)
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

def format_value(val):
    """Formate une valeur numérique"""
    if pd.isna(val) or val == '':
        return ''
    try:
        return round(float(val), 1)
    except:
        return val

def has_inter_targets(row):
    """Vérifie si la section a des cibles intermédiaires"""
    # Vérifier si les colonnes IG, ID ou LI ont des valeurs
    has_ig = pd.notna(row.get('IG', None)) and row.get('IG', 0) != 0
    has_id = pd.notna(row.get('ID', None)) and row.get('ID', 0) != 0
    has_li = pd.notna(row.get('LI', None)) and row.get('LI', 0) != 0
    
    return has_ig or has_id or has_li

def add_convergence_table(ws, section_data, start_row):
    """
    Ajoute un tableau de convergences formaté
    Adapte automatiquement les colonnes selon le nombre de cibles (5 ou 7)
    """
    galerie = section_data.iloc[0]['galerie']
    section = section_data.iloc[0]['section']
    
    # Déterminer si on a 7 cibles (avec inter) ou 5 cibles (sans inter)
    has_inter = has_inter_targets(section_data.iloc[0])
    
    # Titre
    cell = ws.cell(row=start_row, column=1)
    cell.value = f"{galerie} {section} - Convergences"
    cell.font = title_font
    cell.fill = title_fill
    cell.alignment = Alignment(horizontal='center', vertical='center')
    
    if has_inter:
        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=11)
        columns_7 = ['Mode', 'BG', 'IG', 'HG', 'HD', 'ID', 'BD', 'LH', 'LI', 'LB']
    else:
        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=8)
        columns_5 = ['Mode', 'BG', 'HG', 'HD', 'BD', 'LH', 'LB']
    
    # En-têtes
    current_row = start_row + 1
    if has_inter:
        for col_idx, col_name in enumerate(columns_7, start=1):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.value = col_name
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
    else:
        for col_idx, col_name in enumerate(columns_5, start=1):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.value = col_name
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
    
    # Données (périodique et cumulé)
    for _, row_data in section_data.iterrows():
        current_row += 1
        mode = row_data['mode']
        
        if has_inter:
            # Version 7 cibles
            values = [
                mode,
                format_value(row_data.get('BG')),
                format_value(row_data.get('IG')),
                format_value(row_data.get('HG')),
                format_value(row_data.get('HD')),
                format_value(row_data.get('ID')),
                format_value(row_data.get('BD')),
                format_value(row_data.get('LH')),
                format_value(row_data.get('LI')),
                format_value(row_data.get('LB'))
            ]
        else:
            # Version 5 cibles
            values = [
                mode,
                format_value(row_data.get('BG')),
                format_value(row_data.get('HG')),
                format_value(row_data.get('HD')),
                format_value(row_data.get('BD')),
                format_value(row_data.get('LH')),
                format_value(row_data.get('LB'))
            ]
        
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.value = value
            
            # Style selon la colonne
            if col_idx == 1:  # Colonne Mode
                cell.font = mode_font
            else:
                cell.font = data_font
                # Appliquer format numérique à 1 décimale pour les valeurs numériques
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '0.0'
            
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
    
    # Ajuster la largeur des colonnes
    num_cols = 11 if has_inter else 8
    for col in range(1, num_cols + 1):
        if col == 1:
            ws.column_dimensions[get_column_letter(col)].width = 12
        else:
            ws.column_dimensions[get_column_letter(col)].width = 10
    
    return current_row + 2


# Grouper par section
sections = df.groupby(['galerie', 'section'])

print(f"Traitement de {len(sections)} sections...")
print()

for (galerie, section), group in sections:
    # Créer une feuille par section
    sheet_name = f"{galerie} {section}"[:31]  # Max 31 caractères pour nom de feuille
    ws = wb.create_sheet(title=sheet_name)
    
    # Vérifier si c'est une section avec 5 ou 7 cibles
    has_inter = has_inter_targets(group.iloc[0])
    nb_cibles = 7 if has_inter else 5
    
    print(f"  Génération : {sheet_name} ({nb_cibles} cibles)")
    
    # Ajouter le tableau
    add_convergence_table(ws, group, start_row=1)

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
print("Chaque feuille contient : un tableau avec les colonnes adaptées (5 ou 7 cibles)")
