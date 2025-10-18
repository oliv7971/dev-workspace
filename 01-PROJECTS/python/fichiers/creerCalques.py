import csv
import os

# Chemin vers le fichier CSV d'entrée
input_csv = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/2025/02/2025-02-08-e-GET2-leve instrumentation cablages front/3-traitements/GET2-leveCables2.csv"
# Répertoire où les fichiers de sortie seront enregistrés
output_directory = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/2025/02/2025-02-08-e-GET2-leve instrumentation cablages front/4-calques"

# Créer le répertoire de sortie s'il n'existe pas
os.makedirs(output_directory, exist_ok=True)

# Dictionnaire pour stocker les lignes par calque
calques = {}

# Lire le fichier CSV
with open(input_csv, mode='r', newline='') as infile:
    reader = csv.DictReader(infile, delimiter=';')
    for row in reader:
        calque = row['Calque']
        if calque not in calques:
            calques[calque] = []
        calques[calque].append(row)

# Écrire les fichiers de sortie pour chaque calque
for calque, rows in calques.items():
    output_file = os.path.join(output_directory, f"{calque}.txt")
    with open(output_file, mode='w', newline='') as outfile:
        # Écrire l'en-tête
        outfile.write("N;X;Y;Z;Calque\n")
        # Écrire les lignes
        for row in rows:
            outfile.write(f"{row['N']};{row['X']};{row['Y']};{row['Z']};{row['Calque']}\n")

print("Fichiers générés avec succès pour chaque calque.")
