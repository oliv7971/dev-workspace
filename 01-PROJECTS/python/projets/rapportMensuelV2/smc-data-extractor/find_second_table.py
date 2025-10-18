"""
Script pour trouver le second tableau de convergences (après les cellules fusionnées)
"""

import openpyxl
from pathlib import Path

def find_second_table():
    """Trouve le second tableau de convergences"""
    
    excel_path = Path(r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250901-rapport mensuel aout\1-tableaux\GGS\03_104-GGS_SMC_C003_PM001_25_08-25.xlsm")
    
    if not excel_path.exists():
        print(f"Fichier non trouvé: {excel_path}")
        return
    
    print(f"🔍 Analyse: {excel_path.name}")
    
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb['Convergences']
    
    print(f"📏 Dimensions feuille: {ws.max_row} x {ws.max_column}")
    
    # Chercher toutes les cellules fusionnées
    print(f"\n🔗 Cellules fusionnées:")
    for merged_range in ws.merged_cells.ranges:
        print(f"  {merged_range}")
        
        # Regarder autour de cette zone fusionnée
        top_left = merged_range.min_row
        bottom_right = merged_range.max_row
        
        print(f"    Contenu près de la zone fusionnée (lignes {top_left}-{bottom_right}):")
        for row in range(max(1, top_left-2), min(ws.max_row+1, bottom_right+10)):
            row_content = []
            for col in range(1, 15):
                value = ws.cell(row, col).value
                row_content.append(str(value)[:15] if value else "")
            print(f"      Ligne {row}: {row_content}")
    
    # Chercher toutes les occurrences de BG dans la feuille
    print(f"\n🔍 Recherche de toutes les occurrences de 'BG':")
    bg_locations = []
    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            value = ws.cell(row, col).value
            if value and str(value).strip() == 'BG':
                bg_locations.append((row, col))
                print(f"  BG trouvé à: Ligne {row}, Col {col}")
    
    # Analyser chaque location BG
    for row, col in bg_locations:
        print(f"\n📊 Analyse BG à ligne {row}, col {col}:")
        
        # Regarder les en-têtes autour
        print(f"    En-têtes ligne {row}:")
        header_row = []
        for c in range(max(1, col-3), min(ws.max_column+1, col+10)):
            header = ws.cell(row, c).value
            header_row.append(f"Col{c}:{str(header)[:8]}" if header else f"Col{c}:''")
        print(f"      {header_row}")
        
        # Regarder quelques lignes de données
        print(f"    Données (5 premières lignes après {row}):")
        for r in range(row+1, min(row+6, ws.max_row+1)):
            data_row = []
            for c in range(max(1, col-3), min(ws.max_column+1, col+10)):
                val = ws.cell(r, c).value
                if val is not None:
                    data_row.append(f"Col{c}:{str(val)[:8]}")
                else:
                    data_row.append(f"Col{c}:''")
            print(f"      Ligne {r}: {data_row}")
            
        # Si on trouve des données numériques dans la colonne BG, afficher plus
        print(f"    Valeurs BG récentes (dernières 5 lignes):")
        for r in range(max(row+1, ws.max_row-4), ws.max_row+1):
            bg_value = ws.cell(r, col).value
            date_value = ws.cell(r, 2).value  # Colonne B pour date
            print(f"      Ligne {r}: Date={date_value}, BG={bg_value}")

if __name__ == "__main__":
    find_second_table()
