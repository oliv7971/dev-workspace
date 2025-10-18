import pandas as pd
import openpyxl
import os
import glob

# === Configuration ===
input_folder = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\01-PARTIE FRANCE"
#input_folder = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\02-PARTIE ITALIE"
output_file = "analyse_evolution_toutes_cordes.xlsx"

# === Traitement ===
xlsx_files = sorted(glob.glob(os.path.join(input_folder, "*.xlsx")))
results = []

for file in xlsx_files:
    wb = openpyxl.load_workbook(file, data_only=True)
    if "tableau" not in wb.sheetnames:
        continue

    ws = wb["tableau"]
    df_temp = pd.DataFrame(ws.values)

    # Repérer la ligne de titre contenant "DATE"
    header_row_index = None
    for i, row in df_temp.iterrows():
        if isinstance(row[0], str) and "DATE" in row[0].upper():
            header_row_index = i
            break
    if header_row_index is None:
        continue

    # Trouver les colonnes CONV associées à chaque base
    conv_cols = {}
    row_above = df_temp.iloc[header_row_index - 2]
    row_conv = df_temp.iloc[header_row_index]
    for i, label in enumerate(row_above):
        if isinstance(label, str) and "base" in label.lower():
            if i + 1 < len(row_conv) and isinstance(row_conv[i + 1], str) and "conv" in row_conv[i + 1].lower():
                conv_cols[label.strip()] = i + 1

    # Extraire les deux dernières lignes de données
    df_data = df_temp.iloc[header_row_index + 1:].copy()
    df_data = df_data[df_data[0].notna()]
    if len(df_data) < 2:
        continue
    last = df_data.iloc[-1]
    prev = df_data.iloc[-2]

    # Calcul des évolutions
    for base, conv_idx in conv_cols.items():
        try:
            conv_last = pd.to_numeric(last[conv_idx], errors="coerce")
            conv_prev = pd.to_numeric(prev[conv_idx], errors="coerce")
        except Exception:
            continue

        if pd.isna(conv_last) or pd.isna(conv_prev):
            delta = None
        else:
            delta = conv_last - conv_prev

        def classify(delta):
            if delta is None:
                return "manquant"
            if abs(delta) <= 0.3:
                return "stable"
            elif abs(delta) <= 0.5:
                return "quasi stable"
            elif abs(delta) <= 0.7:
                return "légère évolution"
            elif abs(delta) <= 1.0:
                return "évolution"
            else:
                return "forte évolution"

        results.append({
            "fichier": os.path.basename(file),
            "corde": base,
            "Δ CONV (mm)": delta,
            "classification": classify(delta)
        })

# === Export Excel ===
df_result = pd.DataFrame(results)
df_result.to_excel(output_file, index=False)
print(f"✅ Analyse terminée : {output_file}")
