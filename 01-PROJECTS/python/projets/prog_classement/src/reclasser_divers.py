"""
Script pour reclasser les dossiers mal placés dans DIVERS
Détecte les dossiers qui auraient dû être classés dans d'autres catégories
"""

import os
import shutil
import json
import unicodedata

# Configuration
GALERIES_BASE = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"
CONFIG_FILE = r"config\categories.json"

def normaliser(texte):
    """Normalise le texte (supprime accents, met en minuscules)"""
    return ''.join(c for c in unicodedata.normalize('NFD', texte)
                   if unicodedata.category(c) != 'Mn').lower()

def charger_categories():
    """Charge les catégories depuis le fichier JSON"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def detecter_categorie(nom_dossier, categories):
    """Détecte la catégorie d'un dossier selon les mots-clés"""
    nom_norm = normaliser(nom_dossier)
    
    # Parcourir toutes les catégories sauf DIVERS
    for categorie, mots_cles in categories.items():
        if categorie == "DIVERS":
            continue
        for mot_cle in mots_cles:
            mot_cle_norm = normaliser(mot_cle)
            if mot_cle_norm in nom_norm:
                return categorie
    
    return "DIVERS"

def reclasser_galerie(nom_galerie, categories, dry_run=True):
    """Reclasse les dossiers mal placés dans DIVERS d'une galerie"""
    
    galerie_path = os.path.join(GALERIES_BASE, nom_galerie)
    divers_path = os.path.join(galerie_path, "DIVERS")
    
    if not os.path.exists(divers_path):
        print(f"[INFO] Pas de dossier DIVERS dans {nom_galerie}")
        return
    
    print(f"\n{'='*80}")
    print(f"GALERIE: {nom_galerie}")
    print(f"{'='*80}")
    
    dossiers_a_deplacer = {}
    
    # Analyser les dossiers dans DIVERS
    try:
        for dossier in os.listdir(divers_path):
            dossier_path = os.path.join(divers_path, dossier)
            
            if not os.path.isdir(dossier_path):
                continue
            
            # Détecter la bonne catégorie
            categorie = detecter_categorie(dossier, categories)
            
            if categorie != "DIVERS":
                if categorie not in dossiers_a_deplacer:
                    dossiers_a_deplacer[categorie] = []
                dossiers_a_deplacer[categorie].append(dossier)
    
    except PermissionError as e:
        print(f"[ERREUR] Permission refusée: {e}")
        return
    
    # Afficher ce qui sera fait
    if not dossiers_a_deplacer:
        print("[OK] Tous les dossiers sont correctement classés dans DIVERS")
        return
    
    total = sum(len(dossiers) for dossiers in dossiers_a_deplacer.values())
    print(f"\n{total} dossier(s) à reclasser:")
    
    for categorie in sorted(dossiers_a_deplacer.keys()):
        dossiers = dossiers_a_deplacer[categorie]
        print(f"\n  → {categorie} ({len(dossiers)} dossiers)")
        for dossier in sorted(dossiers):
            print(f"      - {dossier}")
    
    # Déplacer les dossiers
    if not dry_run:
        print(f"\n{'='*80}")
        print("DÉPLACEMENT EN COURS...")
        print(f"{'='*80}")
        
        deplaces = 0
        erreurs = 0
        
        for categorie, dossiers in dossiers_a_deplacer.items():
            categorie_path = os.path.join(galerie_path, categorie)
            
            # Créer le dossier de catégorie s'il n'existe pas
            if not os.path.exists(categorie_path):
                os.makedirs(categorie_path)
                print(f"[CRÉÉ] {categorie}")
            
            for dossier in dossiers:
                source = os.path.join(divers_path, dossier)
                destination = os.path.join(categorie_path, dossier)
                
                try:
                    if os.path.exists(destination):
                        # Supprimer le doublon dans DIVERS
                        shutil.rmtree(source)
                        print(f"[DOUBLON SUPPRIMÉ] {dossier} → {categorie}")
                    else:
                        # Déplacer
                        shutil.move(source, destination)
                        print(f"[DÉPLACÉ] {dossier} → {categorie}")
                    deplaces += 1
                except Exception as e:
                    print(f"[ERREUR] {dossier}: {e}")
                    erreurs += 1
        
        print(f"\n{'='*80}")
        print(f"RÉSUMÉ: {deplaces} déplacés, {erreurs} erreurs")
        print(f"{'='*80}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  py src\\reclasser_divers.py <GALERIE> [--execute]")
        print("\nExemples:")
        print('  py src\\reclasser_divers.py "GALERIE GTB"         # Mode simulation')
        print('  py src\\reclasser_divers.py "GALERIE GTB" --execute  # Exécution réelle')
        print("\nMode simulation par défaut (aucun fichier déplacé)")
        return
    
    nom_galerie = sys.argv[1]
    dry_run = "--execute" not in sys.argv
    
    if dry_run:
        print("\n[MODE SIMULATION] Aucun fichier ne sera déplacé")
        print("Ajoutez --execute pour effectuer les déplacements")
    else:
        print("\n[MODE EXÉCUTION] Les fichiers seront déplacés")
    
    # Charger les catégories
    categories = charger_categories()
    
    # Reclasser
    reclasser_galerie(nom_galerie, categories, dry_run)

if __name__ == "__main__":
    main()
