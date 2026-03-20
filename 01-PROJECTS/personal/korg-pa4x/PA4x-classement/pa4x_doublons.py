"""
Script pour identifier et déplacer les répertoires en doublon pour Korg PA4X
Compare les répertoires du NAS avec le répertoire principal et déplace les doublons.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Configuration des chemins
NAS_SOURCE = r"\\Nas_louhans_2\01-ds420-data\20-MUSIQUE STUDIO\01-SYNTHES HW\pa4x_a_classer"
LOCAL_MAIN = r"D:\01-MUSIQUE\02-KORG PA4X"
DOUBLONS_DIR = os.path.join(NAS_SOURCE, "_doublons")

# Fichier de log
LOG_FILE = os.path.join(os.path.dirname(__file__), f"doublons_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")


def get_all_directory_names(path: str, recursive: bool = True) -> set:
    """
    Récupère tous les noms de répertoires (uniquement les noms, pas les chemins complets)
    
    Args:
        path: Chemin racine à scanner
        recursive: Si True, parcourt récursivement tous les sous-répertoires
        
    Returns:
        Set contenant tous les noms de répertoires (en minuscules pour comparaison insensible à la casse)
    """
    dir_names = set()
    
    try:
        if recursive:
            for root, dirs, files in os.walk(path):
                for d in dirs:
                    # On garde le nom en minuscules pour comparaison insensible à la casse
                    dir_names.add(d.lower())
        else:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    dir_names.add(item.lower())
    except Exception as e:
        print(f"Erreur lors du scan de {path}: {e}")
    
    return dir_names


def find_duplicate_directories(source_path: str, reference_path: str, log_file) -> list:
    """
    Trouve les répertoires dans source_path qui existent déjà dans reference_path
    
    Args:
        source_path: Chemin des répertoires à vérifier (NAS)
        reference_path: Chemin de référence (répertoire principal)
        log_file: Fichier de log ouvert
        
    Returns:
        Liste des chemins complets des répertoires en doublon
    """
    duplicates = []
    
    print("Scan du répertoire de référence (local)...")
    log_file.write("=" * 60 + "\n")
    log_file.write(f"Scan du répertoire de référence: {reference_path}\n")
    
    # Récupère tous les noms de répertoires du répertoire principal (récursivement)
    reference_dirs = get_all_directory_names(reference_path, recursive=True)
    print(f"  -> {len(reference_dirs)} répertoires trouvés dans le répertoire principal")
    log_file.write(f"  -> {len(reference_dirs)} répertoires trouvés\n\n")
    
    print("\nScan du répertoire source (NAS)...")
    log_file.write(f"Scan du répertoire source: {source_path}\n")
    
    # Parcourt tous les répertoires du NAS récursivement
    try:
        for root, dirs, files in os.walk(source_path):
            # Ignore le dossier des doublons lui-même
            if "_doublons" in root:
                continue
                
            for d in dirs:
                if d.lower() == "_doublons":
                    continue
                    
                # Vérifie si ce répertoire existe dans la référence
                if d.lower() in reference_dirs:
                    full_path = os.path.join(root, d)
                    duplicates.append(full_path)
                    print(f"  [DOUBLON] {d}")
                    log_file.write(f"  [DOUBLON] {full_path}\n")
    except Exception as e:
        print(f"Erreur lors du scan du NAS: {e}")
        log_file.write(f"Erreur lors du scan du NAS: {e}\n")
    
    return duplicates


def move_duplicates(duplicates: list, doublons_dir: str, log_file, dry_run: bool = True) -> tuple:
    """
    Déplace les répertoires en doublon vers le dossier des doublons
    
    Args:
        duplicates: Liste des chemins des répertoires à déplacer
        doublons_dir: Répertoire de destination pour les doublons
        log_file: Fichier de log ouvert
        dry_run: Si True, simule seulement sans déplacer
        
    Returns:
        Tuple (nombre de succès, nombre d'erreurs)
    """
    success = 0
    errors = 0
    
    if not duplicates:
        print("\nAucun doublon à déplacer.")
        log_file.write("\nAucun doublon à déplacer.\n")
        return success, errors
    
    mode = "SIMULATION" if dry_run else "DÉPLACEMENT"
    print(f"\n{'=' * 60}")
    print(f"Mode: {mode}")
    print(f"{'=' * 60}")
    log_file.write(f"\n{'=' * 60}\n")
    log_file.write(f"Mode: {mode}\n")
    log_file.write(f"{'=' * 60}\n")
    
    if not dry_run:
        # Crée le répertoire des doublons s'il n'existe pas
        os.makedirs(doublons_dir, exist_ok=True)
        print(f"Répertoire des doublons: {doublons_dir}")
        log_file.write(f"Répertoire des doublons: {doublons_dir}\n\n")
    
    for dup_path in duplicates:
        dir_name = os.path.basename(dup_path)
        # Préserve la structure relative
        rel_path = os.path.relpath(os.path.dirname(dup_path), NAS_SOURCE)
        
        if rel_path == ".":
            dest_path = os.path.join(doublons_dir, dir_name)
        else:
            dest_path = os.path.join(doublons_dir, rel_path, dir_name)
        
        try:
            if dry_run:
                print(f"  [SIMULATION] {dir_name}")
                print(f"              -> {dest_path}")
                log_file.write(f"  [SIMULATION] {dup_path}\n")
                log_file.write(f"              -> {dest_path}\n")
            else:
                # Crée le répertoire parent si nécessaire
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Vérifie si la destination existe déjà
                if os.path.exists(dest_path):
                    # Ajoute un suffixe timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    dest_path = f"{dest_path}_{timestamp}"
                
                shutil.move(dup_path, dest_path)
                print(f"  [OK] {dir_name} -> {dest_path}")
                log_file.write(f"  [OK] {dup_path}\n")
                log_file.write(f"      -> {dest_path}\n")
            
            success += 1
            
        except Exception as e:
            print(f"  [ERREUR] {dir_name}: {e}")
            log_file.write(f"  [ERREUR] {dup_path}: {e}\n")
            errors += 1
    
    return success, errors


def main():
    """Fonction principale"""
    print("=" * 60)
    print("Détection des doublons PA4X")
    print("=" * 60)
    print(f"\nSource (NAS)  : {NAS_SOURCE}")
    print(f"Référence     : {LOCAL_MAIN}")
    print(f"Doublons vers : {DOUBLONS_DIR}")
    print(f"Log           : {LOG_FILE}")
    print()
    
    with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
        log_file.write("=" * 60 + "\n")
        log_file.write("Détection des doublons PA4X\n")
        log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("=" * 60 + "\n")
        log_file.write(f"\nSource (NAS)  : {NAS_SOURCE}\n")
        log_file.write(f"Référence     : {LOCAL_MAIN}\n")
        log_file.write(f"Doublons vers : {DOUBLONS_DIR}\n\n")
        
        # Étape 1: Trouver les doublons
        duplicates = find_duplicate_directories(NAS_SOURCE, LOCAL_MAIN, log_file)
        
        print(f"\n{'=' * 60}")
        print(f"Résumé: {len(duplicates)} répertoire(s) en doublon trouvé(s)")
        print(f"{'=' * 60}")
        log_file.write(f"\n{'=' * 60}\n")
        log_file.write(f"Résumé: {len(duplicates)} répertoire(s) en doublon trouvé(s)\n")
        log_file.write(f"{'=' * 60}\n")
        
        if not duplicates:
            print("\nAucun doublon trouvé. Fin du programme.")
            log_file.write("\nAucun doublon trouvé.\n")
            return
        
        # Étape 2: Simulation d'abord
        print("\n--- SIMULATION (pas de déplacement réel) ---")
        log_file.write("\n--- SIMULATION ---\n")
        success, errors = move_duplicates(duplicates, DOUBLONS_DIR, log_file, dry_run=True)
        
        # Demander confirmation
        print(f"\n{'=' * 60}")
        response = input(f"\nVoulez-vous déplacer ces {len(duplicates)} répertoire(s) vers le dossier doublons? (oui/non): ")
        
        if response.lower() in ['oui', 'o', 'yes', 'y']:
            print("\n--- DÉPLACEMENT RÉEL ---")
            log_file.write("\n--- DÉPLACEMENT RÉEL ---\n")
            success, errors = move_duplicates(duplicates, DOUBLONS_DIR, log_file, dry_run=False)
            
            print(f"\n{'=' * 60}")
            print(f"Terminé: {success} succès, {errors} erreur(s)")
            log_file.write(f"\nTerminé: {success} succès, {errors} erreur(s)\n")
        else:
            print("\nOpération annulée.")
            log_file.write("\nOpération annulée par l'utilisateur.\n")
    
    print(f"\nLog sauvegardé dans: {LOG_FILE}")


if __name__ == "__main__":
    main()
