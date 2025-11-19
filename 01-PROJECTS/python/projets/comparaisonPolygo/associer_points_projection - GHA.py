import pandas as pd
import numpy as np
import os
from openpyxl import load_workbook

# ---------------------
# PARAMÈTRES GÉNÉRAUX
# ---------------------
import os

# DEBUG MODE - Décommentez la ligne suivante pour activer
DEBUG_MODE = True  # Changez en False pour désactiver

def debug_print(message):
    """Affiche un message seulement en mode debug"""
    if DEBUG_MODE:
        print(f"🐛 DEBUG: {message}")

# Configuration pour fonctionnement en debug VS Code
DEBUG_VSCODE = False  # Mettez True si debug VS Code ne fonctionne pas
FORCE_DIRECTORY = r"c:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\comparaisonPolygo" if DEBUG_VSCODE else None

# Obtenir le répertoire du script Python
# Solution robuste pour debug VS Code et exécution normale
if __name__ == "__main__":
    if FORCE_DIRECTORY:
        script_dir = FORCE_DIRECTORY
        debug_print(f"Mode debug forcé: {script_dir}")
    else:
        # En mode debug VS Code, __file__ peut être différent
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Vérification pour debug VS Code (chercher le fichier Excel)
        if not os.path.exists(os.path.join(script_dir, "analyseGHA.xlsx")):
            # Probablement en debug VS Code, chercher dans le bon répertoire
            possible_dirs = [
                os.path.dirname(__file__),
                os.getcwd(),
                r"c:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\comparaisonPolygo"
            ]

            for possible_dir in possible_dirs:
                if os.path.exists(os.path.join(possible_dir, "analyseGHA-251030.xlsx")):
                    script_dir = possible_dir
                    debug_print(f"Excel trouvé dans: {script_dir}")
                    break

    fichier_excel = os.path.join(script_dir, "analyseGHA-251030.xlsx")
debug_print(f"Répertoire script: {script_dir}")
debug_print(f"Fichier Excel: {fichier_excel}")

# Vérification de l'existence du fichier
if not os.path.exists(fichier_excel):
    print(f"❌ ERREUR: Le fichier {fichier_excel} n'existe pas!")
    print(f"📁 Répertoire du script: {script_dir}")
    print("📋 Fichiers présents dans le répertoire:")
    for f in os.listdir(script_dir):
        if f.endswith(('.xlsx', '.xls')):
            print(f"   📄 {f}")
    exit(1)
else:
    print(f"✅ Fichier trouvé: {fichier_excel}")

# ---------------------
# MODE RÉINITIALISATION
# ---------------------
RESET_MODE = False  # Mettre True pour réinitialiser le fichier Excel
KEEP_REFERENCES = True  # Garder les 4 premières colonnes (références) dans l'onglet "données"
seuil_coloration = 0.003  # seuil de coloration des écarts en mètres (3mm par défaut)

def reset_excel_file():
    """Réinitialise le fichier Excel en gardant uniquement les en-têtes et l'onglet axe"""
    print("🔄 MODE RÉINITIALISATION ACTIVÉ")
    
    wb = load_workbook(fichier_excel)
    
    # Traiter l'onglet "données"
    feuille_source = "données"
    if feuille_source in wb.sheetnames:
        ws = wb[feuille_source]
        if KEEP_REFERENCES:
            # Garder les 4 premières colonnes (Nom1, X1, Y1, Z1) et supprimer les colonnes 5-8
            print(f"  📋 {feuille_source}: Conservation des références (colonnes A-D), suppression des mesures (E-H)")
            # Supprimer toutes les lignes de données sauf l'en-tête
            max_row = ws.max_row
            if max_row > 1:
                ws.delete_rows(2, max_row - 1)
            # Effacer les colonnes E à H (mesures)
            for row in ws.iter_rows(min_row=1, max_row=1, min_col=5, max_col=8):
                for cell in row:
                    cell.value = ["Nom2", "X2", "Y2", "Z2"][cell.column - 5]
        else:
            # Tout supprimer sauf l'en-tête
            print(f"  📋 {feuille_source}: Suppression de toutes les données")
            max_row = ws.max_row
            if max_row > 1:
                ws.delete_rows(2, max_row - 1)
    
    # Réinitialiser les autres onglets (garder uniquement les en-têtes)
    for sheet_name in ["résultat", "non_associés_mesurés", "non_associés_references"]:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            max_row = ws.max_row
            if max_row > 1:
                ws.delete_rows(2, max_row - 1)
                print(f"  📋 {sheet_name}: Données effacées, en-têtes conservés")
        else:
            # Créer l'onglet avec les en-têtes appropriés
            ws = wb.create_sheet(sheet_name)
            if sheet_name == "résultat":
                headers = ["Nom1", "X1", "Y1", "Z1", "Nom2", "X2", "Y2", "Z2",
                          "PM1", "HZ1", "DZ1", "PM2", "HZ2", "DZ2",
                          "diff_PM", "diff_HZ", "diff_DZ", "DH"]
            elif sheet_name == "non_associés_mesurés":
                headers = ["Nom2", "X2", "Y2", "Z2"]
            else:  # "non_associés_references"
                headers = ["Nom1", "X1", "Y1", "Z1"]
            for col, header in enumerate(headers, start=1):
                ws.cell(row=1, column=col, value=header)
            print(f"  📋 {sheet_name}: Onglet créé avec en-têtes")
    
    # L'onglet "axe" n'est jamais touché
    if "axe" in wb.sheetnames:
        print(f"  🔒 axe: Préservé intact")
    
    wb.save(fichier_excel)
    print("✅ Réinitialisation terminée !\n")
    print("ℹ️  Pour désactiver ce mode, mettez RESET_MODE = False")
    exit(0)

# Exécuter la réinitialisation si demandé
if RESET_MODE:
    reset_excel_file()

feuille_source = "données"
feuille_axe = "axe"
feuille_resultat = "résultat"
onglet_non_associes_mes = "non_associés_mesurés"
onglet_non_associes_ref = "non_associés_references"
seuil = 0.1  # seuil de tolérance horizontale en mètres

# --- Lecture des données ---
debug_print("Début lecture des données Excel")
df = pd.read_excel(fichier_excel, sheet_name=feuille_source, header=0,
                   usecols="A:H", names=["Nom1", "X1", "Y1", "Z1", "Nom2", "X2", "Y2", "Z2"])
df_refs = df[["Nom1", "X1", "Y1", "Z1"]].dropna()
df_mes = df[["Nom2", "X2", "Y2", "Z2"]].dropna()
debug_print(f"Points de référence: {len(df_refs)}")
debug_print(f"Points mesurés: {len(df_mes)}")

# --- Lecture de l'axe ---
debug_print("Lecture de l'axe de projection")
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
debug_print("Début de l'association des points")
résultats = []
associés_ref = set()
associés_mes = set()

for i, (_, ref) in enumerate(df_refs.iterrows()):
    if DEBUG_MODE and i % 50 == 0:  # Affichage tous les 50 points
        debug_print(f"Traitement point référence {i+1}/{len(df_refs)}")

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

debug_print(f"Association terminée: {len(résultats)} associations trouvées")

# --- Préparer les listes de non associés ---
non_associes_refs = df_refs[~df_refs["Nom1"].isin(associés_ref)].copy()
non_associes_mes = df_mes[~df_mes["Nom2"].isin(associés_mes)].copy()

# --- Écriture des résultats dans Excel ---
debug_print("Préparation de l'écriture des résultats")
df_resultat = pd.DataFrame(résultats)
colonnes = ["Nom1", "X1", "Y1", "Z1", "Nom2", "X2", "Y2", "Z2",
            "PM1", "HZ1", "DZ1", "PM2", "HZ2", "DZ2",
            "diff_PM", "diff_HZ", "diff_DZ", "DH"]
df_resultat = df_resultat[colonnes]

try:
    debug_print("Tentative d'écriture dans Excel...")
    with pd.ExcelWriter(fichier_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_resultat.to_excel(writer, sheet_name=feuille_resultat, index=False)
        non_associes_mes.to_excel(writer, sheet_name=onglet_non_associes_mes, index=False)
        non_associes_refs.to_excel(writer, sheet_name=onglet_non_associes_ref, index=False)
    debug_print("Écriture Excel réussie !")
except PermissionError:
    print("❌ ERREUR: Le fichier Excel est ouvert dans un autre programme !")
    print("💡 Solution: Fermez Excel et relancez le script")
    print(f"📁 Fichier concerné: {fichier_excel}")
    exit(1)
except Exception as e:
    print(f"❌ ERREUR lors de l'écriture: {e}")
    exit(1)

print("✅ Résultat mis à jour avec coordonnées X/Y/Z incluses.")
print(f"📊 {len(résultats)} associations trouvées")
print(f"📉 {len(non_associes_refs)} points de référence non associés")
print(f"📈 {len(non_associes_mes)} points mesurés non associés")
print(f"📁 Résultats dans: {fichier_excel}")
print("📋 Onglets: 'résultat', 'non_associés_mesurés', 'non_associés_references'")


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
                if isinstance(val, (int, float)) and abs(val) > seuil_coloration:
                    fill_to_apply = fill_DZ
            if col_hz:
                val = row[col_hz - 1].value
                if isinstance(val, (int, float)) and abs(val) > seuil_coloration:
                    fill_to_apply = fill_HZ
            if col_pm:
                val = row[col_pm - 1].value
                if isinstance(val, (int, float)) and abs(val) > seuil_coloration:
                    fill_to_apply = fill_PM

            if fill_to_apply:
                for cell in row:
                    cell.fill = fill_to_apply

wb.save(fichier_excel)
