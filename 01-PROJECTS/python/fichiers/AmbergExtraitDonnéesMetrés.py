import pandas as pd
import os
import re
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# Dossier contenant tes CSV
DOSSIER = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\2025\07\2025-07-24-a-GRD6-metrés-quantités bétons estimées T2\2-tableaux des deviations"  # <-- à adapter
FICHIER_SORTIE = "CompilationTunnel.xlsx"

# Liste pour stocker les blocs
blocs = []

# Parcours des fichiers CSV
for fichier in sorted(os.listdir(DOSSIER)):
    if fichier.startswith("AnalysisData_PM_") and fichier.endswith(".csv"):
        # Extraction du PM depuis le nom de fichier
        match = re.search(r"PM_(\d+\.\d+)", fichier)
        if match:
            pm = float(match.group(1))
            chemin = os.path.join(DOSSIER, fichier)

            try:
                df = pd.read_csv(chemin, sep=";", encoding="utf-8", engine="python")
            except UnicodeDecodeError:
                df = pd.read_csv(chemin, sep=";", encoding="cp1252", engine="python")
            #df = pd.read_csv(chemin, sep=";", encoding="utf-8", engine="python")  # adapte sep si ce n'est pas ';'
            df.insert(0, "PM", pm)
            blocs.append(df)
            # Ajoute une ligne vide (ligne de NaN)
            blocs.append(pd.DataFrame([[""] * len(df.columns)], columns=df.columns))

# Concatène tous les blocs
df_final = pd.concat(blocs, ignore_index=True)

# Écrit dans Excel
df_final.to_excel(FICHIER_SORTIE, index=False)

# Mise en forme conditionnelle (rouge si déviation < 50)
wb = load_workbook(FICHIER_SORTIE)
ws = wb.active

# Recherche de l'indice de la colonne "Valeur de déviation"
header = [cell.value for cell in ws[1]]
try:
    col_deviation = header.index("Valeur de déviation") + 1  # Excel est 1-based
except ValueError:
    col_deviation = None

# Remplissage en rouge si < 50
if col_deviation:
    rouge = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")
    for row in ws.iter_rows(min_row=2, min_col=col_deviation, max_col=col_deviation):
        for cell in row:
            try:
                if cell.value not in ("", None) and float(cell.value) < 50:
                    cell.fill = rouge
            except:
                pass  # ignore erreurs de conversion

wb.save(FICHIER_SORTIE)
print("Fichier compilé et sauvegardé :", FICHIER_SORTIE)
