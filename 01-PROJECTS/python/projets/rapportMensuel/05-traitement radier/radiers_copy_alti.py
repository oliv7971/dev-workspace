import os
import pandas as pd
import openpyxl

def copy_altimetrie_sheets_with_values(root_dir, output_file):
    # Utiliser pandas avec openpyxl pour écrire le fichier Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        sheet_added = False

        for subdir, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(('.xlsx', '.xlsm')):
                    file_path = os.path.join(subdir, file)
                    try:
                        # Utiliser openpyxl pour charger le fichier et pandas pour lire les données
                        xlsx = pd.ExcelFile(file_path, engine='openpyxl')

                        # Vérifier si l'onglet "ALTIMETRIE" existe
                        if 'ALTIMETRIE' in xlsx.sheet_names:
                            # Lire l'onglet "ALTIMETRIE" avec pandas
                            df = pd.read_excel(file_path, sheet_name='ALTIMETRIE', engine='openpyxl')
                            sheet_name = f"ALTIMETRIE_{os.path.splitext(file)[0]}"
                            # Écrire dans le fichier de sortie
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            sheet_added = True

                    except Exception as e:
                        print(f"Erreur lors du traitement du fichier {file_path}: {e}")

        if not sheet_added:
            print("Aucune feuille 'ALTIMETRIE' trouvée dans les fichiers Excel.")

# Exemple d'utilisation
root_directory = 'C:/Temp/radiers/radiers'  # Remplacez par le chemin de votre répertoire
output_file_path = 'grouped_altimetrie.xlsx'
copy_altimetrie_sheets_with_values(root_directory, output_file_path)
