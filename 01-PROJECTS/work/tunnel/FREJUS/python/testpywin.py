import win32com.client
excel = win32com.client.Dispatch("Excel.Application")
print("Excel a été lancé avec succès !")
excel.Quit()
