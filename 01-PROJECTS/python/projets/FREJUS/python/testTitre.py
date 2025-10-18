import win32com.client as win32

excel = win32.gencache.EnsureDispatch('Excel.Application')
excel.Visible = False

fichier = r"C:\data\11-CHANTIERS\FREJUS\2025-07-14-traitement FRejus 2025\02-conversion xlsx\01-PARTIE FRANCE\graphique pm010_Nv280824-26jan25.xlsx"
wb = excel.Workbooks.Open(fichier)

for feuille in wb.Sheets:
    print(f"🧾 Onglet : {feuille.Name}")
    print("  LeftHeader   :", feuille.PageSetup.LeftHeader)
    print("  CenterHeader :", feuille.PageSetup.CenterHeader)
    print("  RightHeader  :", feuille.PageSetup.RightHeader)
    print("  LeftFooter   :", feuille.PageSetup.LeftFooter)
    print("  CenterFooter :", feuille.PageSetup.CenterFooter)
    print("  RightFooter  :", feuille.PageSetup.RightFooter)
    print("-" * 40)

wb.Close(False)
excel.Quit()
