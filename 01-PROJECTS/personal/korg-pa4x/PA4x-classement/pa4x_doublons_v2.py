"""
Script pour identifier et déplacer les répertoires en doublon pour Korg PA4X
Version 2 - Optimisée avec progression et scan limité

Compare les répertoires du NAS avec le répertoire principal et déplace les doublons.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Configuration des chemins
NAS_SOURCE = r"\\Nas_louhans_2\01-ds420-data\20-MUSIQUE STUDIO\01-SYNTHES HW\pa4x_a_classer"
LOCAL_MAIN = r"D:\01-MUSIQUE\02-KORG PA4X"
DOUBLONS_DIR = os.path.join(NAS_SOURCE, "_doublons")

# Configuration du scan
# Profondeur max pour le scan (None = illimité, 1 = premier niveau seulement, 2 = 2 niveaux, etc.)
MAX_DEPTH_NAS = None    # Pour le NAS: scan complet pour approche granulaire
MAX_DEPTH_LOCAL = None  # Pour le local: scan complet (c'est rapide)

# Fichier de log
LOG_FILE = os.path.join(os.path.dirname(__file__), f"doublons_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")


def print_progress(message, end='\n'):
    """Affiche un message avec timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}", end=end)
    sys.stdout.flush()


def get_directories_with_depth(path: str, max_depth: int = None) -> dict:
    """
    Récupère les répertoires avec contrôle de profondeur
    
    Args:
        path: Chemin racine à scanner
        max_depth: Profondeur maximale (None = illimité)
        
    Returns:
        Dict {nom_lowercase: chemin_complet}
    """
    dirs_found = {}
    count = 0
    
    try:
        # Utiliser une approche itérative avec contrôle de profondeur
        dirs_to_process = [(path, 0)]  # (chemin, profondeur)
        
        while dirs_to_process:
            current_path, depth = dirs_to_process.pop(0)
            
            try:
                items = os.listdir(current_path)
            except PermissionError as e:
                print_progress(f"  [SKIP] Accès refusé: {current_path}")
                continue
            except Exception as e:
                print_progress(f"  [ERREUR] {current_path}: {e}")
                continue
            
            for item in items:
                item_path = os.path.join(current_path, item)
                
                try:
                    if os.path.isdir(item_path):
                        # Ignore le dossier des doublons
                        if item.lower() == "_doublons":
                            continue
                        
                        # Enregistre ce répertoire
                        dirs_found[item.lower()] = item_path
                        count += 1
                        
                        # Affiche progression tous les 100 répertoires
                        if count % 100 == 0:
                            print_progress(f"  ... {count} répertoires scannés")
                        
                        # Ajouter à la liste à traiter si on n'a pas atteint la profondeur max
                        if max_depth is None or depth < max_depth:
                            dirs_to_process.append((item_path, depth + 1))
                            
                except Exception as e:
                    print_progress(f"  [ERREUR] {item_path}: {e}")
                    continue
                    
    except Exception as e:
        print_progress(f"Erreur lors du scan de {path}: {e}")
    
    return dirs_found


def get_immediate_subdirs(path: str) -> list:
    """
    Récupère uniquement les sous-répertoires directs (premier niveau)
    Très rapide même sur le réseau.
    
    Returns:
        Liste de tuples (nom, chemin_complet)
    """
    subdirs = []
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and item.lower() != "_doublons":
                subdirs.append((item, item_path))
    except Exception as e:
        print_progress(f"Erreur: {e}")
    return subdirs


def main():
    """Fonction principale"""
    print("=" * 70)
    print("Détection des doublons PA4X - Version 2 (Optimisée)")
    print("=" * 70)
    print(f"\nSource (NAS)  : {NAS_SOURCE}")
    print(f"Référence     : {LOCAL_MAIN}")
    print(f"Doublons vers : {DOUBLONS_DIR}")
    print(f"Log           : {LOG_FILE}")
    print()
    
    with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
        log_file.write("=" * 70 + "\n")
        log_file.write("Détection des doublons PA4X - Version 2\n")
        log_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("=" * 70 + "\n\n")
        
        # ============================================================
        # ÉTAPE 1: Scanner le répertoire LOCAL (rapide)
        # ============================================================
        print_progress("ÉTAPE 1: Scan du répertoire LOCAL (référence)...")
        print_progress(f"  Chemin: {LOCAL_MAIN}")
        print_progress(f"  Profondeur: {'illimitée' if MAX_DEPTH_LOCAL is None else MAX_DEPTH_LOCAL}")
        
        start_time = datetime.now()
        local_dirs = get_directories_with_depth(LOCAL_MAIN, MAX_DEPTH_LOCAL)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print_progress(f"  Terminé: {len(local_dirs)} répertoires en {elapsed:.1f}s")
        log_file.write(f"Répertoire local: {len(local_dirs)} répertoires trouvés\n\n")
        
        # ============================================================
        # ÉTAPE 2: Scanner les sous-répertoires du NAS (premier niveau uniquement)
        # ============================================================
        print_progress("")
        print_progress("ÉTAPE 2: Scan du NAS (répertoires à classer)...")
        print_progress(f"  Chemin: {NAS_SOURCE}")
        print_progress(f"  Profondeur: {MAX_DEPTH_NAS}")
        
        start_time = datetime.now()
        nas_dirs = get_directories_with_depth(NAS_SOURCE, MAX_DEPTH_NAS)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print_progress(f"  Terminé: {len(nas_dirs)} répertoires en {elapsed:.1f}s")
        log_file.write(f"Répertoire NAS: {len(nas_dirs)} répertoires trouvés\n\n")
        
        # ============================================================
        # ÉTAPE 3: Trouver les doublons
        # ============================================================
        print_progress("")
        print_progress("ÉTAPE 3: Recherche des doublons...")
        
        all_duplicates = []
        for dir_name_lower, nas_path in nas_dirs.items():
            if dir_name_lower in local_dirs:
                all_duplicates.append({
                    'name': os.path.basename(nas_path),
                    'nas_path': nas_path,
                    'local_path': local_dirs[dir_name_lower]
                })
        
        print_progress(f"  {len(all_duplicates)} doublon(s) bruts trouvés")
        
        # ============================================================
        # ÉTAPE 3b: Filtrer pour ne garder que les feuilles
        # (ne pas déplacer un parent si un de ses enfants est aussi un doublon)
        # On veut déplacer uniquement les répertoires les plus profonds
        # ============================================================
        print_progress("")
        print_progress("ÉTAPE 3b: Filtrage des doublons (approche granulaire - feuilles uniquement)...")
        
        # Trier par longueur de chemin décroissante (les plus profonds = les enfants d'abord)
        all_duplicates.sort(key=lambda x: len(x['nas_path']), reverse=True)
        
        duplicates = []
        processed_paths = set()  # Chemins déjà traités (pour éviter de traiter un parent si enfant déjà traité)
        
        for dup in all_duplicates:
            nas_path = dup['nas_path']
            
            # Vérifier si ce chemin est un ancêtre d'un chemin déjà traité
            # Si oui, on ne le déplace pas car on a déjà prévu de déplacer ses enfants
            is_ancestor = False
            for child_path in processed_paths:
                if child_path.lower().startswith(nas_path.lower() + os.sep):
                    is_ancestor = True
                    break
            
            if not is_ancestor:
                duplicates.append(dup)
            
            processed_paths.add(nas_path)
        
        print_progress(f"  {len(duplicates)} doublon(s) feuille(s) à déplacer")
        
        # ============================================================
        # ÉTAPE 4: Afficher les résultats
        # ============================================================
        print("\n" + "=" * 70)
        print(f"RÉSULTATS: {len(duplicates)} répertoire(s) en doublon")
        print("=" * 70)
        
        log_file.write("=" * 70 + "\n")
        log_file.write("DOUBLONS TROUVÉS\n")
        log_file.write("=" * 70 + "\n\n")
        
        if not duplicates:
            print("\nAucun doublon trouvé!")
            log_file.write("Aucun doublon trouvé.\n")
            return
        
        for i, dup in enumerate(duplicates, 1):
            print(f"\n{i}. {dup['name']}")
            print(f"   NAS   : {dup['nas_path']}")
            print(f"   Local : {dup['local_path']}")
            log_file.write(f"{i}. {dup['name']}\n")
            log_file.write(f"   NAS   : {dup['nas_path']}\n")
            log_file.write(f"   Local : {dup['local_path']}\n\n")
        
        # ============================================================
        # ÉTAPE 5: Demander confirmation pour déplacer
        # ============================================================
        print("\n" + "=" * 70)
        response = input(f"\nDéplacer ces {len(duplicates)} répertoire(s) vers '_doublons'? (oui/non): ")
        
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            print("\nOpération annulée.")
            log_file.write("\nOpération annulée par l'utilisateur.\n")
            return
        
        # Créer le dossier doublons
        os.makedirs(DOUBLONS_DIR, exist_ok=True)
        print_progress(f"\nDossier doublons créé: {DOUBLONS_DIR}")
        
        success = 0
        errors = 0
        
        for dup in duplicates:
            src = dup['nas_path']
            
            # Calculer le chemin relatif depuis NAS_SOURCE pour préserver l'arborescence
            rel_path = os.path.relpath(src, NAS_SOURCE)
            dst = os.path.join(DOUBLONS_DIR, rel_path)
            
            # Si destination existe déjà, ajouter timestamp
            if os.path.exists(dst):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dst = f"{dst}_{timestamp}"
            
            try:
                # Créer les répertoires parents si nécessaire
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                print_progress(f"  Déplacement: {rel_path}...")
                shutil.move(src, dst)
                print_progress(f"    -> OK")
                log_file.write(f"[OK] {src} -> {dst}\n")
                success += 1
            except Exception as e:
                print_progress(f"    -> ERREUR: {e}")
                log_file.write(f"[ERREUR] {src}: {e}\n")
                errors += 1
        
        print("\n" + "=" * 70)
        print(f"TERMINÉ: {success} déplacé(s), {errors} erreur(s)")
        print("=" * 70)
        log_file.write(f"\nTerminé: {success} déplacé(s), {errors} erreur(s)\n")
    
    print(f"\nLog sauvegardé: {LOG_FILE}")


if __name__ == "__main__":
    main()
