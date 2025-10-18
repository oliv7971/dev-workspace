
import pandas as pd
from axe_routier import calculer_xyz_from_dataframes, calcul_inverse_xyz_from_dataframes, lire_options_excel

fichier = "modele_axe_routier.xlsx"
xls = pd.ExcelFile(fichier)

df_plan = xls.parse("axe_plan")
df_profil = xls.parse("profil_long")
df_xyz = xls.parse("xyz_depuis_pk")
df_coords = xls.parse("pk_depuis_xyz")
options = lire_options_excel(xls)
mode = options.get("mode_deport_vertical", "verticale").strip().lower()

# Calcul des PK_end
df_plan["PK_end"] = df_plan["PK"].shift(-1)
df_plan.iloc[-1, df_plan.columns.get_loc("PK_end")] = df_plan["PK"].iloc[-1] + 10
df_profil["PK_end"] = df_profil["PK_start"].shift(-1)
df_profil.iloc[-1, df_profil.columns.get_loc("PK_end")] = df_profil["PK_start"].iloc[-1] + 10

# Calcul direct : PK + déports => X, Y, Z
results_xyz = df_xyz.apply(
    lambda row: calculer_xyz_from_dataframes(
        df_plan, df_profil,
        row["PK"], row["deport"], row.get("deport_vertical", 0.0), mode
    ),
    axis=1, result_type="expand"
)
df_xyz["X"], df_xyz["Y"], df_xyz["Z"] = results_xyz[0], results_xyz[1], results_xyz[2]

# Calcul inverse : X, Y, Z => PK, déports
results_inverse = df_coords.apply(
    lambda row: calcul_inverse_xyz_from_dataframes(
        df_plan, df_profil, row["X"], row["Y"], row["Z"], mode
    ),
    axis=1, result_type="expand"
)
df_result = pd.DataFrame(results_inverse.values, columns=["PK", "deport_horizontal", "Zaxe", "Zmesuree"])
df_result["deport_vertical"] = df_result["Zmesuree"] - df_result["Zaxe"]

# Concaténer les résultats aux données d’origine
df_final = pd.concat([df_coords.reset_index(drop=True),
                      df_result[["PK", "deport_horizontal", "Zaxe", "Zmesuree", "deport_vertical"]]],
                     axis=1)

with pd.ExcelWriter(fichier, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
    df_xyz.to_excel(writer, sheet_name="xyz_depuis_pk", index=False)
    df_final.to_excel(writer, sheet_name="pk_depuis_xyz", index=False)
