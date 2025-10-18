import pandas as pd
import numpy as np
from openpyxl import load_workbook

# ---------------------
# PARAMÈTRES GÉNÉRAUX
# ---------------------
fichier_excel = "analyseGVA2.xlsx"
feuille_source = "données"
feuille_axe = "axe"
feuille_resultat = "résultat"
onglet_non_associes_mes = "non_associés_mesurés"
onglet_non_associes_ref = "non_associés_references"
seuil = 0.1  # seuil de tolérance horizontale en mètres

# --- Lecture des données ---
df = pd.read_excel(fichier_excel, sheet_name=feuille_source, header=0,
                   usecols="A:H", names=["Nom1", "X1", "Y1", "Z1", "Nom2", "X2", "Y2", "Z2"])
df_refs = df[["Nom1", "X1", "Y1", "Z1"]].dropna()
df_mes = df[["Nom2", "X2", "Y2", "Z2"]].dropna()

# --- Lecture de l'axe ---
df_axe = pd.read_excel(fichier_excel, sheet_name=feuille_axe)
X0, Y0, Z0 = df_axe.loc[df_axe["Point"] == "Origine", ["X", "Y", "Z"]].values[0]
X1, Y1, Z1 = df_axe.loc[df_axe["Point"] == "Extrémité", ["X", "Y", "Z"]].values[0]
if "PM" in df_axe.columns and "PM Départ" in df_axe["Point"].values:
    PM_depart = df_axe.loc[df_axe["Point"] == "PM Départ", "PM"].values[0]
else:
    PM_depart = 0.0

# --- Calculs liés à l'axe ---
axe_vecteur = np.array([X1 - X0, Y1 - Y0])
longueur_axe = np.linalg.norm(axe_vecteur)
axe_unitaire = axe_vecteur / longueur_axe

def get_projection(X, Y, Z):
    vecteur = np.array([X - X0, Y - Y0])
    PM = PM_depart + np.dot(vecteur, axe_unitaire)
    proj_X = X0 + (PM - PM_depart) * axe_unitaire[0]
    proj_Y = Y0 + (PM - PM_depart) * axe_unitaire[1]
    HZ = np.linalg.norm([X - proj_X, Y - proj_Y])
    Z_proj = Z0 + (Z1 - Z0) * ((PM - PM_depart) / longueur_axe)
    DZ = Z - Z_proj
    return PM, HZ, DZ

# --- Association multiple ---
résultats = []
associés_ref = set()
associés_mes = set()

for _, ref in df_refs.iterrows():
    nom1, x1, y1, z1 = ref["Nom1"], ref["X1"], ref["Y1"], ref["Z1"]
    for _, mes in df_mes.iterrows():
        nom2, x2, y2, z2 = mes["Nom2"], mes["X2"], mes["Y2"], mes["Z2"]
        DH = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if DH < seuil:
            associés_ref.add(nom1)
            associés_mes.add(nom2)
            PM1, HZ1, DZ1 = get_projection(x1, y1, z1)
            PM2, HZ2, DZ2 = get_projection(x2, y2, z2)

            résultats.append({
                "Nom1": nom1, "X1": x1, "Y1": y1, "Z1": z1,
                "Nom2": nom2, "X2": x2, "Y2": y2, "Z2": z2,
                "PM1": PM1, "HZ1": HZ1, "DZ1": DZ1,
                "PM2": PM2, "HZ2": HZ2, "DZ2": DZ2,
                "diff_PM": PM2 - PM1,
                "diff_HZ": HZ2 - HZ1,
                "diff_DZ": DZ2 - DZ1,
                "DH": DH
            })

# --- Préparer les listes de non associés ---
non_associes_refs = df_refs[~df_refs["Nom1"].isin(associés_ref)].copy()
non_associes_mes = df_mes[~df_mes["Nom2"].isin(associés_mes)].copy()

# --- Écriture des résultats dans Excel ---
df_resultat = pd.DataFrame(résultats)
colonnes = ["Nom1", "X1", "Y1", "Z1", "Nom2", "X2", "Y2", "Z2",
            "PM1", "HZ1", "DZ1", "PM2", "HZ2", "DZ2",
            "diff_PM", "diff_HZ", "diff_DZ", "DH"]
df_resultat = df_resultat[colonnes]

with pd.ExcelWriter(fichier_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_resultat.to_excel(writer, sheet_name=feuille_resultat, index=False)
    non_associes_mes.to_excel(writer, sheet_name=onglet_non_associes_mes, index=False)
    non_associes_refs.to_excel(writer, sheet_name=onglet_non_associes_ref, index=False)

print("✅ Résultat mis à jour avec coordonnées X/Y/Z incluses.")


# --- Mise en forme des feuilles ---
from openpyxl import load_workbook
from openpyxl.styles import Alignment, PatternFill

wb = load_workbook(fichier_excel)
centered = Alignment(horizontal="center", vertical="center")
format_sheets = [feuille_resultat, onglet_non_associes_mes, onglet_non_associes_ref]

# Couleurs par direction
fill_PM = PatternFill(start_color="FFFACD", end_color="FFFACD", fill_type="solid")  # jaune clair
fill_HZ = PatternFill(start_color="FFE4B5", end_color="FFE4B5", fill_type="solid")  # orange clair
fill_DZ = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # rouge clair

for sheet_name in format_sheets:
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        col_dz = header.index("diff_DZ") + 1 if "diff_DZ" in header else None
        col_hz = header.index("diff_HZ") + 1 if "diff_HZ" in header else None
        col_pm = header.index("diff_PM") + 1 if "diff_PM" in header else None

        for row in ws.iter_rows(min_row=2):
            # Format général
            for cell in row:
                cell.alignment = centered
                if isinstance(cell.value, (int, float)):
                    cell.number_format = "0.000"

            # Coloration conditionnelle (1 seule couleur par ligne, priorité DZ > HZ > PM)
            fill_to_apply = None
            if col_dz:
                val = row[col_dz - 1].value
                if isinstance(val, (int, float)) and abs(val) > 0.010:
                    fill_to_apply = fill_DZ
            if col_hz:
                val = row[col_hz - 1].value
                if isinstance(val, (int, float)) and abs(val) > 0.010:
                    fill_to_apply = fill_HZ
            if col_pm:
                val = row[col_pm - 1].value
                if isinstance(val, (int, float)) and abs(val) > 0.010:
                    fill_to_apply = fill_PM

            if fill_to_apply:
                for cell in row:
                    cell.fill = fill_to_apply

wb.save(fichier_excel)
