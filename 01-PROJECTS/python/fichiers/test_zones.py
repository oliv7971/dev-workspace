import win32com.client as win32
import os

file_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250708-rapport mensuel juin\1-tableaux\Radiers\GER1-S4\GER1-RADIER-PLOT1-069-073-NIVELLEMENT-25-06-30.xlsm"  # <--- à adapter
pdf_output = r"C:\temp\test.pdf"

excel = win32.gencache.EnsureDispatch("Excel.Application")
excel.Visible = True
excel.DisplayAlerts = False

print("Ouverture du fichier Excel...")
wb = excel.Workbooks.Open(file_path, UpdateLinks=0)
print("Classeur ouvert.")

try:
    print("Accès à la feuille 'ALTIMETRIE'...")
    sheet = wb.Sheets("ALTIMETRIE")
    print("Feuille trouvée.")

    print("Sélection de la feuille...")
    sheet.Select()

    print("Détection de la zone d'impression...")
    last_cell = sheet.Cells.SpecialCells(11)  # xlCellTypeLastCell
    zone = f"A1:{last_cell.Address}"
    print(f"Zone trouvée : {zone}")
    sheet.PageSetup.PrintArea = zone

    print("Réglage de la mise en page...")
    ps = sheet.PageSetup
    ps.Orientation = 2
    ps.Zoom = False
    ps.FitToPagesWide = 1
    ps.FitToPagesTall = False
    sheet.ResetAllPageBreaks()

    print("Export PDF...")
    sheet.ExportAsFixedFormat(0, pdf_output)
    print(f"✅ PDF exporté : {pdf_output}")

except Exception as e:
    print(f"💥 Erreur pendant le traitement : {e}")

finally:
    print("Fermeture du classeur...")
    try:
        wb.Close(SaveChanges=False)
    except Exception as e:
        print(f"⚠️ Erreur à la fermeture : {e}")
    excel.Quit()
