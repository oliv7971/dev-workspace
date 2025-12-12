"""
Script pour comparer une galerie spécifique entre Temp et Destination
Affiche les dossiers manquants un par un pour vérification manuelle
"""

import os
import sys

# Chemins source et destination
TEMP_BASE = r"C:\Temp\activites-par-galerie"
DESTINATION_BASE = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

def lister_dossiers_temp(galerie_path):
    """Liste tous les dossiers d'activité dans _classé d'une galerie du temp"""
    dossiers = set()
    classe_path = os.path.join(galerie_path, "_classé")
    
    if not os.path.exists(classe_path):
        return dossiers
    
    # Parcourir toutes les catégories
    try:
        for categorie in os.listdir(classe_path):
            categorie_path = os.path.join(classe_path, categorie)
            if os.path.isdir(categorie_path):
                try:
                    for dossier in os.listdir(categorie_path):
                        dossier_path = os.path.join(categorie_path, dossier)
                        if os.path.isdir(dossier_path):
                            dossiers.add(dossier)
                except PermissionError:
                    continue
    except PermissionError:
        pass
    
    return dossiers

def lister_dossiers_destination(galerie_path):
    """Liste tous les dossiers d'activité dans une galerie de destination"""
    dossiers = set()
    
    if not os.path.exists(galerie_path):
        return dossiers
    
    try:
        for item in os.listdir(galerie_path):
            item_path = os.path.join(galerie_path, item)
            if os.path.isdir(item_path):
                # Si c'est un dossier de catégorie, lister son contenu
                try:
                    for dossier in os.listdir(item_path):
                        dossier_path = os.path.join(item_path, dossier)
                        if os.path.isdir(dossier_path):
                            dossiers.add(dossier)
                except:
                    # Sinon c'est peut-être directement un dossier d'activité
                    dossiers.add(item)
    except PermissionError:
        pass
    
    return dossiers

def comparer_galerie(nom_galerie):
    """Compare une galerie spécifique entre temp et destination"""
    
    # Chemins de la galerie
    temp_galerie = os.path.join(TEMP_BASE, nom_galerie)
    dest_galerie = os.path.join(DESTINATION_BASE, nom_galerie)
    
    # Vérifier que la galerie existe dans temp
    if not os.path.exists(temp_galerie):
        print(f"[ERREUR] La galerie '{nom_galerie}' n'existe pas dans {TEMP_BASE}")
        return
    
    # Lister les dossiers
    dossiers_temp = lister_dossiers_temp(temp_galerie)
    dossiers_dest = lister_dossiers_destination(dest_galerie)
    
    # Trouver les dossiers manquants
    manquants = sorted(dossiers_temp - dossiers_dest)
    
    # Afficher les résultats
    print(f"\n{'='*80}")
    print(f"GALERIE: {nom_galerie}")
    print(f"{'='*80}")
    print(f"Dossiers dans Temp     : {len(dossiers_temp)}")
    print(f"Dossiers dans Destination: {len(dossiers_dest)}")
    print(f"Dossiers manquants    : {len(manquants)}")
    print(f"{'='*80}")
    
    if manquants:
        print(f"\n--- DOSSIERS A TRANSFERER ({len(manquants)}) ---\n")
        for i, dossier in enumerate(manquants, 1):
            print(f"{i:4d}. {dossier}")
    else:
        print("\n[OK] Tous les dossiers sont déjà présents dans la destination!")

def main():
    # Lister toutes les galeries disponibles
    if len(sys.argv) < 2:
        print("\nUsage: py src\\comparer_galerie.py <NOM_GALERIE>")
        print("\nGaleries disponibles:")
        print("-" * 40)
        
        try:
            galeries = sorted([g for g in os.listdir(TEMP_BASE) 
                             if os.path.isdir(os.path.join(TEMP_BASE, g)) 
                             and not g.startswith('_')])
            for galerie in galeries:
                print(f"  - {galerie}")
        except:
            pass
        
        print("\nExemple: py src\\comparer_galerie.py GGS")
        return
    
    nom_galerie = sys.argv[1]
    comparer_galerie(nom_galerie)

if __name__ == "__main__":
    main()
