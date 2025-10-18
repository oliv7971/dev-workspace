import os
import shutil
import unicodedata
import json

# Chemin de base à adapter
base_dir = r"C:\Temp\activites-par-galerie"

json_path = os.path.join(os.path.dirname(__file__), "categories.json")


# Chargement du fichier JSON de catégories
with open(json_path, encoding="utf-8") as f:
    categories = json.load(f)

DOSSIER_A_CLASSER = "_a_classer"
DOSSIER_CLASSE = "_classé"
DOSSIER_DIVERS = "DIVERS"

def normaliser(texte):
    return ''.join(c for c in unicodedata.normalize('NFD', texte)
                   if unicodedata.category(c) != 'Mn').lower()

def detecter_categorie(nom):
    nom_norm = normaliser(nom)
    print(f"🔎 Analyse : {nom} → {nom_norm}")
    for categorie, mots_cles in categories.items():
        for mot in mots_cles:
            if normaliser(mot) in nom_norm:
                print(f"✅ Catégorie détectée : {categorie} via mot-clé '{mot}'")
                return categorie
    print("❌ Aucune correspondance")
    return DOSSIER_DIVERS


log = []

# Parcours des galeries ou alvéoles
for nom_site in os.listdir(base_dir):
    print(f"📂 Traitement de : {nom_site}")
    chemin_site = os.path.join(base_dir, nom_site)
    if not os.path.isdir(chemin_site):
        continue

    chemin_a_classer = os.path.join(chemin_site, DOSSIER_A_CLASSER)
    chemin_classe = os.path.join(chemin_site, DOSSIER_CLASSE)
    print(f"   ↪ _a_classer trouvé : {chemin_a_classer}")


    if not os.path.exists(chemin_a_classer):
        continue

    os.makedirs(chemin_classe, exist_ok=True)

    for dossier in os.listdir(chemin_a_classer):
        chemin_dossier = os.path.join(chemin_a_classer, dossier)
        print(f"   🔍 Dossier détecté dans _a_classer : {dossier}")

        if not os.path.isdir(chemin_dossier):
            continue

        categorie = detecter_categorie(dossier)
        destination = os.path.join(chemin_classe, categorie, dossier)
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        if os.path.exists(destination):
            shutil.rmtree(destination)

        shutil.move(chemin_dossier, destination)
        print(f"[OK] {dossier} → {nom_site}\\{categorie}")
