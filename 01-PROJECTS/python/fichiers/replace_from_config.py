import os
import tkinter as tk
from tkinter import filedialog

def replace_from_config(file_to_process, config_file, output_file):
    """
    Remplace toutes les occurrences des clés dans un fichier en utilisant un fichier de configuration clé-valeur.

    :param file_to_process: Chemin du fichier à traiter.
    :param config_file: Chemin du fichier de configuration (clé-valeur).
    :param output_file: Chemin du fichier de sortie.
    """
    try:
        # Lecture du fichier de configuration pour construire le dictionnaire de remplacement
        replacements = {}
        with open(config_file, 'r', encoding='utf-8') as config:
            for line in config:
                # Suppression des espaces et gestion des lignes vides ou des commentaires
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    #key, value = line.split(None, 1)  # Séparation clé-valeur avec un espace
                    key, value = line.split("\t", 1)  # Séparer par tabulation

                    replacements[key] = value
                except ValueError:
                    print(f"Ligne ignorée dans le fichier de configuration : {line}")

        # Lecture et traitement du fichier à modifier
        with open(file_to_process, 'r', encoding='utf-8') as input_file:
            content = input_file.read()

        # Remplacement des clés par leurs valeurs
        for key, value in replacements.items():
            content = content.replace(key, value)

        # Écriture du fichier modifié
        with open(output_file, 'w', encoding='utf-8') as output:
            output.write(content)

        print(f"Remplacements terminés. Résultat écrit dans {output_file}")

    except FileNotFoundError as e:
        print(f"Erreur : Fichier introuvable - {e.filename}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")


def select_file(title):
    """
    Ouvre une boîte de dialogue pour sélectionner un fichier.

    :param title: Titre de la boîte de dialogue.
    :return: Chemin du fichier sélectionné.
    """
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    file_path = filedialog.askopenfilename(title=title)
    return file_path


def save_file(title):
    """
    Ouvre une boîte de dialogue pour sélectionner un fichier de sortie.

    :param title: Titre de la boîte de dialogue.
    :return: Chemin du fichier de sortie.
    """
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale
    file_path = filedialog.asksaveasfilename(title=title, defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    return file_path


# Programme principal
print("Sélectionnez le fichier à traiter.")
file_to_process = select_file("Choisissez le fichier à modifier")

# Si l'utilisateur annule une sélection, on arrête tout de suite.
if not file_to_process:
    print("Sélection du fichier à traiter annulée. Le programme va s'arrêter.")
    exit()

print("Sélectionnez le fichier de configuration (clé-valeur).")
config_file = select_file("Choisissez le fichier de configuration")

# Vérifie si le fichier de configuration est annulé.
if not config_file:
    print("Sélection du fichier de configuration annulée. Le programme va s'arrêter.")
    exit()

print("Sélectionnez le fichier de sortie.")
output_file = save_file("Choisissez le fichier de sortie")

# Vérifie si le fichier de sortie est annulé.
if not output_file:
    print("Sélection du fichier de sortie annulée. Le programme va s'arrêter.")
    exit()

# Si tous les fichiers sont sélectionnés, on lance le traitement
replace_from_config(file_to_process, config_file, output_file)
