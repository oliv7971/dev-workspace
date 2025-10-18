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
        with open(config_file, 'r', encoding='utf-8-sig') as config:
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
        with open(file_to_process, 'r', encoding='utf-8-sig') as input_file:
            content = input_file.read()

        # Remplacement des clés par leurs valeurs (clés triées par longueur desc)
        total = 0
        for key in sorted(replacements.keys(), key=len, reverse=True):
            value = replacements[key]
            occ = content.count(key)
            if occ:
                content = content.replace(key, value)
                print(f'Remplacement: "{key}" -> "{value}" ({occ} occurrence(s))')
                total += occ
        print(f"Total remplacements: {total}")

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


def main():
    root = tk.Tk()
    root.withdraw()

    print("Sélectionnez le fichier à traiter.")
    file_to_process = filedialog.askopenfilename(title="Choisissez le fichier à modifier")
    if not file_to_process:
        print("Sélection du fichier à traiter annulée.")
        root.destroy()
        sys.exit(0)

    print("Sélectionnez le fichier de configuration (clé-valeur).")
    config_file = filedialog.askopenfilename(title="Choisissez le fichier de configuration")
    if not config_file:
        print("Sélection du fichier de configuration annulée.")
        root.destroy()
        sys.exit(0)

    print("Sélectionnez le fichier de sortie.")
    output_file = filedialog.asksaveasfilename(title="Choisissez le fichier de sortie",
                                               defaultextension=".txt",
                                               filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not output_file:
        print("Sélection du fichier de sortie annulée.")
        root.destroy()
        sys.exit(0)

    root.destroy()
    replace_from_config(file_to_process, config_file, output_file)

if __name__ == "__main__":
    import sys
    main()
