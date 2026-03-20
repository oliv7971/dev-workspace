import os
import win32com.client as win32

# Dossier contenant tes fichiers .xls
#source_folder = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\01-PARTIE FRANCE"
source_folder = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\02-PARTIE ITALIE"

destination_folder = os.path.join(source_folder, "converted")

# Crée un dossier "converted" s'il n'existe pas
os.makedirs(destination_folder, exist_ok=True)

excel = win32.gencache.EnsureDispatch('Excel.Application')
excel.Visible = False

for filename in os.listdir(source_folder):
    if filename.lower().endswith(".xls") and not filename.startswith("~$"):
        full_path = os.path.join(source_folder, filename)
        print(f"Conversion de : {filename}")
        
        wb = excel.Workbooks.Open(full_path)
        new_filename = os.path.splitext(filename)[0] + ".xlsx"
        wb.SaveAs(os.path.join(destination_folder, new_filename), FileFormat=51)  # 51 = .xlsx
        wb.Close(SaveChanges=False)

excel.Quit()
print("Conversion terminée !")
