"""
Script pour comparer les dossiers entre C:\Temp\activites-par-galerie et C:\data\11-CHANTIERS\BURE\11-GALERIES
Identifie les dossiers présents dans Temp mais absents dans le répertoire final
"""

import os
from collections import defaultdict

# Chemins source et destination
TEMP_BASE = r"C:\Temp\activites-par-galerie"
DESTINATION_BASE = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

def lister_dossiers_temp(galerie_path):
    """Liste tous les dossiers d'activité dans _classé d'une galerie du temp (indépendamment de la catégorie)"""
    dossiers = set()
    classe_path = os.path.join(galerie_path, "_classé")
    
    if not os.path.exists(classe_path):
        return dossiers
    
    # Parcourir toutes les catégories
    try:
        for categorie in os.listdir(classe_path):
            categorie_path = os.path.join(classe_path, categorie)
            if os.path.isdir(categorie_path):
                # Lister les dossiers d'activité dans cette catégorie
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
    """Liste tous les dossiers d'activité dans une galerie de destination (indépendamment de la catégorie)"""
    dossiers = set()
    
    if not os.path.exists(galerie_path):
        return dossiers
    
    # Parcourir TOUS les sous-dossiers, quelle que soit la catégorie
    try:
        for item in os.listdir(galerie_path):
            item_path = os.path.join(galerie_path, item)
            if os.path.isdir(item_path):
                # Lister le contenu de ce sous-dossier (catégorie)
                try:
                    for dossier in os.listdir(item_path):
                        dossier_path = os.path.join(item_path, dossier)
                        if os.path.isdir(dossier_path):
                            dossiers.add(dossier)
                except PermissionError:
                    continue
    except PermissionError:
        pass
    
    return dossiers

def main():
    """Compare les dossiers et affiche les différences par galerie"""
    
    print("=" * 80)
    print("COMPARAISON DES DOSSIERS")
    print("Source: C:\\Temp\\activites-par-galerie")
    print("Destination: C:\\data\\11-CHANTIERS\\BURE\\11-GALERIES")
    print("=" * 80)
    print()
    
    # Statistiques globales
    total_temp = 0
    total_destination = 0
    total_manquants = 0
    
    resultats = {}
    
    # Parcourir toutes les galeries du temp
    for galerie in sorted(os.listdir(TEMP_BASE)):
        galerie_temp_path = os.path.join(TEMP_BASE, galerie)
        
        if not os.path.isdir(galerie_temp_path):
            continue
        
        # Lister les dossiers dans temp
        dossiers_temp = lister_dossiers_temp(galerie_temp_path)
        
        # Trouver le chemin de destination correspondant
        galerie_dest_path = os.path.join(DESTINATION_BASE, galerie)
        
        # Lister les dossiers dans destination
        dossiers_destination = lister_dossiers_destination(galerie_dest_path)
        
        # Identifier les dossiers manquants
        manquants = dossiers_temp - dossiers_destination
        
        if dossiers_temp:  # Seulement si la galerie a des dossiers
            resultats[galerie] = {
                'temp': len(dossiers_temp),
                'destination': len(dossiers_destination),
                'manquants': len(manquants),
                'liste_manquants': sorted(manquants)
            }
            
            total_temp += len(dossiers_temp)
            total_destination += len(dossiers_destination)
            total_manquants += len(manquants)
    
    # Afficher les résultats
    print("\n=== RÉSUMÉ PAR GALERIE ===")
    print("-" * 80)
    print(f"{'GALERIE':<25} {'TEMP':<10} {'DESTINATION':<15} {'MANQUANTS':<10}")
    print("-" * 80)
    
    for galerie, stats in sorted(resultats.items()):
        print(f"{galerie:<25} {stats['temp']:<10} {stats['destination']:<15} {stats['manquants']:<10}")
    
    print("-" * 80)
    print(f"{'TOTAL':<25} {total_temp:<10} {total_destination:<15} {total_manquants:<10}")
    print()
    
    # Afficher le détail des dossiers manquants
    print("\n=== DÉTAIL DES DOSSIERS MANQUANTS ===")
    print("=" * 80)
    
    for galerie, stats in sorted(resultats.items()):
        if stats['manquants'] > 0:
            print(f"\n- {galerie} ({stats['manquants']} dossiers manquants)")
            print("-" * 80)
            for dossier in stats['liste_manquants']:
                print(f"   - {dossier}")
    
    if total_manquants == 0:
        print("\n[OK] Tous les dossiers du temp sont présents dans la destination !")
    else:
        print(f"\n[!] Il reste {total_manquants} dossiers à transférer")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
