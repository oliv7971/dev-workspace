import os
import time
import win32com.client as win32
from PyPDF2 import PdfMerger

# === Fonctions utilitaires ===

def num_to_col_letter(n):
    result = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result

def get_last_column_letter_from_merged_cell_line_5(sheet):
    try:
        for cell in sheet.Range("5:5"):
            if cell.MergeCells:
                merged = cell.MergeArea
                last_col_num = merged.Columns.Count + merged.Column - 1
                return num_to_col_letter(last_col_num)
    except Exception as e:
        print(f"  ⚠️ Erreur cellule fusionnée ligne 5 : {e}")
    return None

def get_last_used_column_letter(sheet, max_rows=20):
    last_col = 1
    try:
        for row in range(1, max_rows + 1):
            for col in range(1, sheet.Columns.Count + 1):
                val = sheet.Cells(row, col).Value
                if val not in (None, ""):
                    last_col = max(last_col, col)
    except Exception as e:
        print(f"  ⚠️ Erreur recherche colonne : {e}")
    return num_to_col_letter(last_col)

def get_best_last_column_letter(sheet):
    col = get_last_column_letter_from_merged_cell_line_5(sheet)
    if col:
        print(f"  📏 Colonne max via fusion ligne 5 : {col}")
        return col
    else:
        col = get_last_used_column_letter(sheet)
        print(f"  📏 Colonne max via contenu : {col}")
        return col

def get_last_used_row(sheet):
    try:
        cell = sheet.Cells.Find("*", SearchOrder=1, SearchDirection=2)  # xlByRows=1, xlPrevious=2
        if cell:
            return cell.Row
    except Exception as e:
        print(f"  ⚠️ Erreur dans Find() pour la dernière ligne : {e}")
    return 1

# === Dossier racine ===

base_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\250708-rapport mensuel juin\1-tableaux\Radiers"

for subdir in os.listdir(base_folder):
    sub_path = os.path.join(base_folder, subdir)
    if not os.path.isdir(sub_path):
        continue

    print(f"\n📁 Dossier : {sub_path}")
    pdf_output_folder = os.path.join(sub_path, "PDFs")
    os.makedirs(pdf_output_folder, exist_ok=True)

    for filename in os.listdir(sub_path):
        if filename.lower().endswith((".xlsx", ".xlsm")) and not filename.startswith("~$"):
            xlsx_path = os.path.join(sub_path, filename)
            pdf_path = os.path.join(pdf_output_folder, filename.rsplit(".", 1)[0] + ".pdf")
            print(f"\n📄 Traitement : {filename}")

            excel = win32.gencache.EnsureDispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            try:
                print("  ➤ Ouverture du classeur...")
                wb = excel.Workbooks.Open(Filename=xlsx_path, UpdateLinks=0)
                temp_pdf_paths = []

                try:
                    print("  🔎 Feuille 'ALTIMETRIE'...")
                    sheet_alt = wb.Sheets("ALTIMETRIE")
                    print("  ✅ Feuille trouvée.")

                    print("  🛠️ Détection zone d'impression...")
                    last_col = get_best_last_column_letter(sheet_alt)
                    last_row = get_last_used_row(sheet_alt) + 2
                    zone = f"A1:{last_col}{last_row}"
                    print(f"  🖨️ Zone d'impression visée : {zone}")

                    try:
                        sheet_alt.PageSetup.PrintArea = zone
                        print("  ✅ Zone définie.")
                    except Exception as e:
                        print(f"  ⚠️ Erreur définition PrintArea : {e}")

                    try:
                        ps = sheet_alt.PageSetup
                        print("  📐 Orientation...")
                        ps.Orientation = 2
                        print("  📐 Zoom off...")
                        ps.Zoom = False
                        print("  📐 FitToPagesWide...")
                        ps.FitToPagesWide = 1
                        print("  📐 FitToPagesTall...")
                        ps.FitToPagesTall = False
                        print("  📐 ResetAllPageBreaks...")
                        sheet_alt.ResetAllPageBreaks()
                        print("  ✅ Mise en page OK.")
                    except Exception as e:
                        print(f"  ⚠️ Erreur mise en page : {e}")

                    # Export
                    try:
                        temp_path = os.path.join(pdf_output_folder, f"~{filename}_tableau.pdf")
                        print("  📤 Export ALTIMETRIE...")
                        sheet_alt.ExportAsFixedFormat(0, temp_path)
                        temp_pdf_paths.append(temp_path)
                        print("  ✅ Export 'ALTIMETRIE' terminé.")
                    except Exception as e:
                        print(f"  ⚠️ Erreur export ALTIMETRIE : {e}")
                except Exception as e:
                    print(f"  ⚠️ Erreur feuille 'ALTIMETRIE' : {e}")

                # Feuille Graphiques
                try:
                    print("  🔎 Feuille 'Graphiques'...")
                    sheet_graph = wb.Sheets("Graphiques")
                    chart_objects = sheet_graph.ChartObjects()
                    if chart_objects.Count > 0:
                        print("  📊 Graphique trouvé.")
                        chart = chart_objects.Item(1).Chart
                        temp_path = os.path.join(pdf_output_folder, f"~{filename}_zoom.pdf")
                        chart.ExportAsFixedFormat(0, temp_path)
                        temp_pdf_paths.append(temp_path)
                        print("  ✅ Export 'Graphiques' terminé.")
                    else:
                        print("  ⚠️ Aucun graphique trouvé.")
                except Exception as e:
                    print(f"  ⚠️ Erreur feuille 'Graphiques' : {e}")

                # Fusion PDF
                if temp_pdf_paths:
                    try:
                        print("  🔗 Fusion des PDF...")
                        merger = PdfMerger()
                        for temp in temp_pdf_paths:
                            merger.append(temp)
                        merger.write(pdf_path)
                        merger.close()
                        print(f"  ✅ PDF final : {pdf_path}")
                    except Exception as e:
                        print(f"  💥 Erreur fusion PDF : {e}")
                    finally:
                        for temp in temp_pdf_paths:
                            if os.path.exists(temp):
                                os.remove(temp)
                else:
                    print("  ❌ Aucun contenu exporté pour ce fichier.")

                time.sleep(0.2)

            except Exception as e:
                print(f"  💥 Erreur générale sur {filename} : {e}")

            finally:
                print("  🧹 Fermeture du classeur...")
                try:
                    wb.Close(SaveChanges=False)
                except Exception as e:
                    print(f"  ⚠️ Erreur fermeture classeur : {e}")
                excel.Quit()
                del excel
                time.sleep(0.2)

print("\n🎉 Terminé ! Tous les dossiers ont été traités.")
