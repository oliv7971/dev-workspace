# Script Python pour extraire les données d'auscultation (convergences + déplacements)
# depuis un fichier Excel de type SMC 5 cibles, avec mois de référence configurable

import pandas as pd
from datetime import datetime

# 📌 Paramètres configurables
fichier_excel = "03_105-GGS_SMC_C007_PM005_25_07_29.xlsm"
mois_cible = "2025-07"  # Format AAAA-MM

# Chargement des feuilles Excel
xls = pd.ExcelFile(fichier_excel)
df_conv = pd.read_excel(xls, sheet_name="Convergences", header=None)
df_depl = pd.read_excel(xls, sheet_name="Déplacements", header=None)

# 🔄 Fonction pour convertir les dates et filtrer par mois
def filtrer_par_mois(df, col_date=1, mois=mois_cible):
    df = df.copy()
    df = df[df[col_date].notna()]
    df["DATE"] = pd.to_datetime(df[col_date], errors="coerce")
    df = df[df["DATE"].notna()]
    df_mois = df[df["DATE"].dt.to_period("M") == mois]
    return df, df_mois

# ➕ Fonction pour extraire les dernières lignes utiles par colonne
def extraire_derniere_ligne_non_vide(df_data, colonnes):
    resultats = {}
    for col in colonnes:
        val = df_data[col].dropna()
        if not val.empty:
            resultats[col] = val.iloc[-1]
        else:
            resultats[col] = None
    return resultats

# ➖ Fonction pour calculer le diff entre deux dates (périodique)
def ecart_entre_deux(df_full, df_mois, colonnes):
    ligne_mois = df_mois.index.max()
    ligne_avant = df_full[df_full.index < ligne_mois].index.max()
    if pd.isna(ligne_mois) or pd.isna(ligne_avant):
        return {col: None for col in colonnes}
    ecarts = {}
    for col in colonnes:
        val_mois = df_full.at[ligne_mois, col] if pd.notna(df_full.at[ligne_mois, col]) else None
        val_avant = df_full.at[ligne_avant, col] if pd.notna(df_full.at[ligne_avant, col]) else None
        ecarts[col] = val_mois - val_avant if val_mois is not None and val_avant is not None else None
    return ecarts

# ✅ Traitement des convergences
_, df_conv_mois = filtrer_par_mois(df_conv)
colonnes_convergences = [3, 4, 5, 6, 7, 8]  # BG, HG, HD, BD, LH, LB
derniers_conv = extraire_derniere_ligne_non_vide(df_conv, colonnes_convergences)
ecart_conv = ecart_entre_deux(df_conv, df_conv_mois, colonnes_convergences)

# ✅ Traitement des déplacements
_, df_depl_mois = filtrer_par_mois(df_depl)
colonnes_depl = list(range(2, 17))  # DPM, DH, DZ pour chaque cible (5 cibles)
derniers_depl = extraire_derniere_ligne_non_vide(df_depl, colonnes_depl)
ecart_depl = ecart_entre_deux(df_depl, df_depl_mois, colonnes_depl)

# 🔢 Résultats
print("--- CONVERGENCES (cumulées) ---")
print(derniers_conv)
print("\n--- CONVERGENCES (périodiques) ---")
print(ecart_conv)

print("\n--- DÉPLACEMENTS (cumulés) ---")
print(derniers_depl)
print("\n--- DÉPLACEMENTS (périodiques) ---")
print(ecart_depl)
