"""
Supprime les dossiers vides (récursivement) dans un chemin donné.
Traite d'abord les plus profonds (bottom-up) pour vider les parents.
"""
import os
import sys

TARGET = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS\38-TUNNEL DE SIAIX\_atrier"
DRY_RUN = "--execute" not in sys.argv

def is_empty(path):
    """Retourne True si le dossier ne contient aucun fichier ni sous-dossier."""
    try:
        return len(os.listdir(path)) == 0
    except PermissionError:
        return False

def find_and_remove_empty(root, dry):
    removed = []
    # os.walk bottom-up : on traite les feuilles avant les parents
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if dirpath == root:
            continue  # ne jamais supprimer le dossier racine lui-même
        if is_empty(dirpath):
            rel = os.path.relpath(dirpath, root)
            if dry:
                print(f"  [DRY]  {rel}")
            else:
                try:
                    os.rmdir(dirpath)
                    print(f"  [DEL]  {rel}")
                    removed.append(dirpath)
                except Exception as e:
                    print(f"  [ERR]  {rel} — {e}")
    return removed

if __name__ == "__main__":
    mode = "DRY-RUN" if DRY_RUN else "EXÉCUTION"
    print(f"=== {mode} — dossiers vides dans _atrier ===\n")
    result = find_and_remove_empty(TARGET, DRY_RUN)
    print(f"\nTotal : {len(result)} dossier(s) {'à supprimer' if DRY_RUN else 'supprimé(s)'}.")
    if DRY_RUN:
        print("Relancer avec --execute pour supprimer.")
