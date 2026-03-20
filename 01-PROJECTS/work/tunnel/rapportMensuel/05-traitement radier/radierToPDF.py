import os
import win32com.client

def convert_sheet_to_pdf(excel_path, sheet_name, pdf_path):
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False

    try:
        workbook = excel.Workbooks.Open(excel_path)
        # Sélectionner la feuille spécifique
        workbook.Worksheets(sheet_name).Select()
        # Exporter la feuille sélectionnée en PDF
        workbook.ActiveSheet.ExportAsFixedFormat(0, pdf_path)
    except Exception as e:
        print(f"Erreur lors de la conversion du fichier {excel_path}: {e}")
    finally:
        workbook.Close(False)
        excel.Quit()

def process_excel_files(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(('.xlsx', '.xlsm')):
                file_path = os.path.join(subdir, file)
                try:
                    # Vérifier si l'onglet "Graphiques" existe
                    excel = win32com.client.Dispatch("Excel.Application")
                    workbook = excel.Workbooks.Open(file_path)
                    if 'Graphiques' in [sheet.Name for sheet in workbook.Sheets]:
                        # Chemin pour le fichier PDF de sortie
                        pdf_file_path = file_path.replace('.xlsx', '.pdf').replace('.xlsm', '.pdf')
                        convert_sheet_to_pdf(file_path, 'Graphiques', pdf_file_path)
                    workbook.Close(False)
                except Exception as e:
                    print(f"Erreur lors du traitement du fichier {file_path}: {e}")
                finally:
                    excel.Quit()

# Exemple d'utilisation
root_directory = 'C:/Temp/radiers/Radiers'  # Remplacez par le chemin de votre répertoire
process_excel_files(root_directory)
