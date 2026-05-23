import os
import sys
import yaml
import datetime
from nas_admin.inventory import init_db, scan_directory

# Chemin racine des dossiers à inventorier
BASE_PATH = r"\\Nas_travail\01-ds414-data\31-GGC-DOSSIERS"

# Dossier où stocker les bases SQLite (peut être modifié)
DB_DIR = os.path.abspath("inventaires")

# Fichier log
LOG_PATH = os.path.abspath("inventaire_log.txt")

# Charger la config globale si besoin
CONFIG_PATH = os.path.abspath("config.yaml")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
else:
    config = {}

os.makedirs(DB_DIR, exist_ok=True)

def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def main():
    if not os.path.exists(BASE_PATH):
        print(f"Chemin introuvable: {BASE_PATH}")
        log(f"ERREUR: Chemin introuvable: {BASE_PATH}")
        sys.exit(1)

    dossiers = [d for d in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, d))]
    print(f"{len(dossiers)} dossiers trouvés à inventorier.")
    log(f"{len(dossiers)} dossiers trouvés à inventorier dans {BASE_PATH}")

    for dossier in dossiers:
        dossier_path = os.path.join(BASE_PATH, dossier)
        db_path = os.path.join(DB_DIR, f"inventaire_{dossier}.db")
        print(f"\n=== Traitement du dossier: {dossier} ===")
        log(f"Début inventaire: {dossier}")
        conn = init_db(db_path)
        try:
            scan_directory(dossier_path, config, conn, compute_hashes=True)
        except Exception as e:
            log(f"ERREUR dans {dossier}: {e}")
            print(f"Erreur dans {dossier}: {e}")
        finally:
            conn.close()
        print(f"Inventaire terminé pour: {dossier}")
        log(f"Fin inventaire: {dossier}")

if __name__ == "__main__":
    main()
