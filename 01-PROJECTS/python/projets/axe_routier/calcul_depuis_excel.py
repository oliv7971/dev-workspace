
import pandas as pd
from axe_routier import calculer_xyz_from_dataframes, calcul_inverse_xyz_from_dataframes

# Charger le fichier Excel
fichier = "modele_axe_routier.xlsx"
xls = pd.ExcelFile(fichier)

# Lire les données plan et profil
df_plan = xls.parse("axe_plan")
df_profil = xls.parse("profil_long")

# Calcul des PK -> XYZ
df_plan["PK_end"] = df_plan["PK"].shift(-1)
df_plan.iloc[-1, df_plan.columns.get_loc("PK_end")] = df_plan["PK"].iloc[-1] + 10
df_profil["PK_end"] = df_profil["PK_start"].shift(-1)
df_profil.iloc[-1, df_profil.columns.get_loc("PK_end")] = df_profil["PK_start"].iloc[-1] + 10

df_xyz = xls.parse("xyz_depuis_pk")
df_xyz[["X", "Y", "Z"]] = df_xyz.apply(
    lambda row: calculer_xyz_from_dataframes(df_plan, df_profil, row["PK"], row["deport"]),
    axis=1, result_type="expand"
)

# Calcul des XYZ -> PK/déport
df_coords = xls.parse("pk_depuis_xyz")
resultats = df_coords.apply(
    lambda row: calcul_inverse_xyz_from_dataframes(df_plan, df_profil, row["X"], row["Y"], row["Z"]),
    axis=1
)
df_result = pd.DataFrame(resultats.tolist())

# Écriture dans le fichier
with pd.ExcelWriter(fichier, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
    df_xyz.to_excel(writer, sheet_name="xyz_depuis_pk", index=False)
    final_df = pd.concat([df_coords, df_result], axis=1)
    final_df.to_excel(writer, sheet_name="pk_depuis_xyz", index=False)
