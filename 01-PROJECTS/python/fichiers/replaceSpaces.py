import os

def replace_spaces_and_tabs(input_file, output_file):
    # Lire le fichier d'entrée
    with open(input_file, 'r') as file:
        content = file.read()

    # Remplacer les espaces et les tabulations par des points-virgules
    content = content.replace(' ', ';').replace('\t', ';')

    # Écrire le contenu modifié dans le fichier de sortie
    with open(output_file, 'w') as file:
        file.write(content)

    print(f"Fichier '{output_file}' généré avec succès.")

# Chemin vers le fichier d'entrée
input_file = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/2025/02/2025-02-08-e-GET2-leve instrumentation cablages front/3-traitements/GET2-leveCables.txt"
# Chemin vers le fichier de sortie
output_file = "C:/data/11-CHANTIERS/BURE/10-ACTIVITES/2025/02/2025-02-08-e-GET2-leve instrumentation cablages front/3-traitements/GET2-leveCables2.txt"

# Appeler la fonction pour remplacer les espaces et les tabulations
replace_spaces_and_tabs(input_file, output_file)
