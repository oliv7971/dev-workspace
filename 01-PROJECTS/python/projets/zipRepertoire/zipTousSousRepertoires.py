import os
import zipfile

# Chemin du dossier contenant les répertoires à zipper
dossier_source = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES"

# Parcours de tous les éléments dans le dossier
for nom_sous_dossier in os.listdir(dossier_source):
    chemin_complet = os.path.join(dossier_source, nom_sous_dossier)

    if os.path.isdir(chemin_complet):
        zip_path = os.path.join(dossier_source, nom_sous_dossier + ".zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(chemin_complet):
                for file in files:
                    chemin_fichier = os.path.join(root, file)
                    chemin_relatif = os.path.relpath(chemin_fichier, start=chemin_complet)
                    zipf.write(chemin_fichier, arcname=os.path.join(nom_sous_dossier, chemin_relatif))

        print(f"{zip_path} créé avec succès.")
