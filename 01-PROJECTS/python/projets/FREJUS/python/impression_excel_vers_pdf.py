import os
import re
import win32com.client as win32
from PyPDF2 import PdfMerger

# 📁 Dossier contenant les fichiers Excel convertis
#excel_folder = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\01-PARTIE FRANCE"
excel_folder = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\02-PARTIE ITALIE"
pdf_output_folder = os.path.join(excel_folder, "PDFs")
os.makedirs(pdf_output_folder, exist_ok=True)

# Démarrage d'Excel
excel = win32.gencache.EnsureDispatch("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

for filename in os.listdir(excel_folder):
    if filename.lower().endswith(".xlsx") and not filename.startswith("~$"):
        xlsx_path = os.path.join(excel_folder, filename)
        pdf_path = os.path.join(pdf_output_folder, filename.replace(".xlsx", ".pdf"))
        print(f"Traitement de : {filename}")

        # Ouverture du fichier SANS mise à jour des liens externes
        wb = excel.Workbooks.Open(
            Filename=xlsx_path,
            UpdateLinks=0  # ← Empêche les popups sur liens cassés
        )

        temp_pdf_paths = []

        try:
            # === 1. Feuille "tableau"
            try:
                sheet = wb.Sheets("tableau")
                sheet.Select()
                temp_path = os.path.join(pdf_output_folder, "~tableau.pdf")
                sheet.ExportAsFixedFormat(0, temp_path)
                temp_pdf_paths.append(temp_path)
            except Exception:
                print(" ⚠️ Feuille 'tableau' absente")

            # === 2. Feuille "zoom"
            try:
                sheet = wb.Sheets("zoom")
                chart_objects = sheet.ChartObjects()
                if chart_objects.Count > 0:
                    chart_objects.Item(1).Activate()
                    temp_path = os.path.join(pdf_output_folder, "~zoom.pdf")
                    sheet.ExportAsFixedFormat(0, temp_path)
                    temp_pdf_paths.append(temp_path)
            except Exception:
                print(" ⚠️ Feuille 'zoom' absente ou sans graphique")

            # === 3. Feuilles "graph.*mois" dynamiques
            for sheet in wb.Sheets:
                name = sheet.Name.strip().lower()
                if re.match(r"^graph.*mois$", name):
                    try:
                        chart_objects = sheet.ChartObjects()
                        if chart_objects.Count > 0:
                            chart_objects.Item(1).Activate()
                            temp_path = os.path.join(pdf_output_folder, f"~{name}.pdf")
                            sheet.ExportAsFixedFormat(0, temp_path)
                            temp_pdf_paths.append(temp_path)
                    except Exception:
                        print(f" ⚠️ Problème graphique sur '{name}'")

            # === Fusion PDF
            if temp_pdf_paths:
                merger = PdfMerger()
                for temp_path in temp_pdf_paths:
                    merger.append(temp_path)
                merger.write(pdf_path)
                merger.close()

                for temp_path in temp_pdf_paths:
                    os.remove(temp_path)

                print(f" ✅ PDF généré : {pdf_path}")
            else:
                print(" ❌ Rien à exporter pour ce fichier")

        except Exception as e:
            print(f"💥 Erreur sur {filename} : {e}")

        finally:
            wb.Close(SaveChanges=False)

excel.Quit()
print("🎉 Terminé ! Tous les fichiers ont été imprimés en PDF.")
