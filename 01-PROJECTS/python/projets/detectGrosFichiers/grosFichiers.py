#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour détecter les fichiers les plus volumineux dans un répertoire et ses sous-répertoires.
Auteur: GitHub Copilot
Date: 6 septembre 2025
"""

import os
import sys
from pathlib import Path
import argparse


def format_size(size_bytes):
    """Convertit la taille en bytes en format lisible (KB, MB, GB, TB)"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def scan_directory(directory, min_size=0):
    """
    Scanne un répertoire et ses sous-répertoires pour trouver tous les fichiers.
    
    Args:
        directory (str): Chemin du répertoire à scanner
        min_size (int): Taille minimale en bytes pour inclure un fichier
    
    Returns:
        list: Liste de tuples (taille, chemin_fichier)
    """
    files_info = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Obtenir la taille du fichier
                    size = os.path.getsize(file_path)
                    
                    # Filtrer par taille minimale si spécifiée
                    if size >= min_size:
                        files_info.append((size, file_path))
                        
                except (OSError, IOError) as e:
                    # Ignorer les fichiers inaccessibles (permissions, liens brisés, etc.)
                    print(f"Erreur d'accès au fichier {file_path}: {e}", file=sys.stderr)
                    continue
                    
    except (OSError, IOError) as e:
        print(f"Erreur d'accès au répertoire {directory}: {e}", file=sys.stderr)
        return []
    
    return files_info


def main():
    parser = argparse.ArgumentParser(
        description="Trouve les fichiers les plus volumineux dans un répertoire et ses sous-répertoires"
    )
    parser.add_argument(
        "directory", 
        nargs='?', 
        default=".", 
        help="Répertoire à scanner (par défaut: répertoire courant)"
    )
    parser.add_argument(
        "-n", "--number", 
        type=int, 
        default=10, 
        help="Nombre de fichiers à afficher (par défaut: 10)"
    )
    parser.add_argument(
        "-m", "--min-size", 
        type=str, 
        default="0", 
        help="Taille minimale des fichiers (ex: 1MB, 500KB, 2GB)"
    )
    parser.add_argument(
        "-s", "--sort", 
        choices=['size', 'name'], 
        default='size', 
        help="Critère de tri: 'size' par taille (défaut) ou 'name' par nom"
    )
    
    args = parser.parse_args()
    
    # Convertir la taille minimale en bytes
    min_size_bytes = parse_size(args.min_size)
    
    # Vérifier que le répertoire existe
    if not os.path.isdir(args.directory):
        print(f"Erreur: '{args.directory}' n'est pas un répertoire valide.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scan du répertoire: {os.path.abspath(args.directory)}")
    print(f"Taille minimale: {format_size(min_size_bytes)}")
    print("Recherche en cours...")
    
    # Scanner le répertoire
    files_info = scan_directory(args.directory, min_size_bytes)
    
    if not files_info:
        print("Aucun fichier trouvé correspondant aux critères.")
        return
    
    # Trier par taille (décroissant) ou par nom
    if args.sort == 'size':
        files_info.sort(key=lambda x: x[0], reverse=True)
    else:
        files_info.sort(key=lambda x: x[1])
    
    # Afficher les résultats
    print(f"\n{len(files_info)} fichier(s) trouvé(s). Voici les {min(args.number, len(files_info))} plus volumineux:\n")
    print(f"{'Taille':<12} {'Chemin'}")
    print("-" * 80)
    
    for i, (size, path) in enumerate(files_info[:args.number]):
        formatted_size = format_size(size)
        print(f"{formatted_size:<12} {path}")
    
    # Statistiques
    if files_info:
        total_size = sum(size for size, _ in files_info)
        print(f"\nStatistiques:")
        print(f"Nombre total de fichiers: {len(files_info)}")
        print(f"Taille totale: {format_size(total_size)}")
        print(f"Taille moyenne: {format_size(total_size // len(files_info))}")


def parse_size(size_str):
    """
    Convertit une chaîne de taille (ex: '1MB', '500KB') en bytes.
    
    Args:
        size_str (str): Taille sous forme de chaîne
    
    Returns:
        int: Taille en bytes
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith('B'):
        size_str = size_str[:-1]
    
    multipliers = {
        'K': 1024,
        'KB': 1024,
        'M': 1024**2,
        'MB': 1024**2,
        'G': 1024**3,
        'GB': 1024**3,
        'T': 1024**4,
        'TB': 1024**4,
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            try:
                number = float(size_str[:-len(suffix)])
                return int(number * multiplier)
            except ValueError:
                break
    
    try:
        return int(float(size_str))
    except ValueError:
        print(f"Erreur: Format de taille invalide '{size_str}'. Utilisez des formats comme '1MB', '500KB', etc.")
        sys.exit(1)


if __name__ == "__main__":
    main()