import os
import shutil
import unicodedata
import json

# Chargement de la configuration principale (config/config.json)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.json')

def _charger_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding='utf-8') as f:
            return json.load(f)
    # Valeurs par défaut si pas de config
    return {
        'chemins': {
            'source_base': r"C:\\data\\11-CHANTIERS\\BURE\\10-ACTIVITES",
            'destination_temp': r"C:\\Temp\\activites-par-galerie"
        }
    }

cfg = _charger_config()
source_base = cfg['chemins'].get('source_base')
destination_base = cfg['chemins'].get('destination_temp')

# Chargement des correspondances depuis config/correspondances.json
CORRESP_PATH = os.path.join(BASE_DIR, 'config', 'correspondances.json')
if not os.path.exists(CORRESP_PATH):
    raise FileNotFoundError(f"Fichier de correspondances introuvable: {CORRESP_PATH}")

with open(CORRESP_PATH, encoding='utf-8') as f:
    correspondances = json.load(f)

def normaliser(txt):
    return ''.join(c for c in unicodedata.normalize('NFD', txt)
                   if unicodedata.category(c) != 'Mn').lower()

# Parcours des répertoires année/mois
for annee in os.listdir(source_base):
    chemin_annee = os.path.join(source_base, annee)
    if not os.path.isdir(chemin_annee):
        continue

    for mois in os.listdir(chemin_annee):
        chemin_mois = os.path.join(chemin_annee, mois)
        if not os.path.isdir(chemin_mois):
            continue

        for dossier in os.listdir(chemin_mois):
            chemin_dossier = os.path.join(chemin_mois, dossier)
            if not os.path.isdir(chemin_dossier):
                continue
            if dossier.lower() in ["_a_classer", "_classé"]:
                continue

            match = None
            for identifiant, cible in correspondances.items():
                if normaliser(identifiant) in normaliser(dossier):
                    match = cible
                    break

            # Cas 1 : correspondance trouvée
            if match:
                cible_a_classer = os.path.join(destination_base, match, "_a_classer")
                os.makedirs(cible_a_classer, exist_ok=True)

                destination = os.path.join(cible_a_classer, dossier)
                if os.path.exists(destination):
                    shutil.rmtree(destination)

                shutil.copytree(chemin_dossier, destination)
                print(f"[OK] {dossier} → {match}")

            # Cas 2 : pas de correspondance → __NON_RECONNUS
            else:
                dossier_non_reconnu = os.path.join(destination_base, "__NON_RECONNUS", "_a_classer", dossier)
                os.makedirs(os.path.dirname(dossier_non_reconnu), exist_ok=True)

                if os.path.exists(dossier_non_reconnu):
                    shutil.rmtree(dossier_non_reconnu)

                shutil.copytree(chemin_dossier, dossier_non_reconnu)
                print(f"[NON RECONNU] {dossier} → __NON_RECONNUS")
