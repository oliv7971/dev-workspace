import os
import shutil
import unicodedata

# Dossier de base contenant toutes les galeries
DOSSIER_BASE = r"C:\Temp\activites-par-galerie"

# Liste des catégories à trier
CATEGORIES = {
    "IMPLANTATION": ["implant", "imp", "implantation"],
    "AUSCULTATION": ["aus", "auscult"],
    "LEVE": ["levé", "leve", "lev", "lv"],
    "POLYGO": ["poly", "polygo", "refs"],
    "THEORIQUES": ["theoriques", "theo", "prepa"],
    "METRES": ["metres", "métrés", "metrés"],
    "ETUDE": ["etude"],
    "RECOLEMENT": ["recol", "rec", "doe"]
}

DOSSIER_A_CLASSER = "_a_classer"
DOSSIER_CLASSE = "_classé"
DOSSIER_DIVERS = "DIVERS"

def normaliser(texte):
    return ''.join(c for c in unicodedata.normalize('NFD', texte)
                   if unicodedata.category(c) != 'Mn').lower()

def detecter_categorie_nom_dossier(nom_dossier):
    nom_norm = normaliser(nom_dossier)
    for categorie, mots_cles in CATEGORIES.items():
        for mot in mots_cles:
            if normaliser(mot) in nom_norm:
                return categorie
    return DOSSIER_DIVERS

# Parcours des galeries dans le dossier de base
for galerie in os.listdir(DOSSIER_BASE):
    chemin_galerie = os.path.join(DOSSIER_BASE, galerie)
    if not os.path.isdir(chemin_galerie):
        continue

    source = os.path.join(chemin_galerie, DOSSIER_A_CLASSER)
    destination_base = os.path.join(chemin_galerie, DOSSIER_CLASSE)

    if not os.path.exists(source):
        print(f"[IGNORÉ] Pas de '{DOSSIER_A_CLASSER}' dans {galerie}")
        continue

    print(f"🔄 Traitement de : {galerie}")

    # Crée les sous-dossiers de destination (par catégorie)
    for categorie in list(CATEGORIES.keys()) + [DOSSIER_DIVERS]:
        os.makedirs(os.path.join(destination_base, categorie), exist_ok=True)

    # Classement des sous-dossiers de _a_classer
    for nom_dossier in os.listdir(source):
        chemin_dossier = os.path.join(source, nom_dossier)
        if not os.path.isdir(chemin_dossier):
            continue

        categorie = detecter_categorie_nom_dossier(nom_dossier)
        dossier_cible = os.path.join(destination_base, categorie, nom_dossier)

        if not os.path.exists(dossier_cible):
            try:
                shutil.move(chemin_dossier, dossier_cible)
                print(f"   [OK] {nom_dossier} → {categorie}")
            except Exception as e:
                print(f"   [ERREUR] Impossible de déplacer {nom_dossier} : {e}")
        else:
            # Le dossier existe déjà, on supprime celui de _a_classer pour éviter les doublons
            try:
                shutil.rmtree(chemin_dossier)
                print(f"   [INFO] {nom_dossier} déjà présent → {categorie} (supprimé de _a_classer)")
            except Exception as e:
                print(f"   [ERREUR] Impossible de supprimer {nom_dossier} : {e}")
