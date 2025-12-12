"""
Consolidation des coordonnées de cibles extraites
Regroupe tous les fichiers CSV en un seul fichier condensé
"""

import pandas as pd
from pathlib import Path

def consolider_cibles():
    """Consolide tous les CSV de cibles en un seul fichier"""
    
    # Chercher tous les fichiers CSV extraits
    dossier = Path('.')
    fichiers_csv = list(dossier.glob('*_cibles_extraites.csv'))
    
    if not fichiers_csv:
        print("Aucun fichier CSV trouvé")
        return
    
    print("=" * 80)
    print("CONSOLIDATION DES COORDONNÉES DE CIBLES")
    print("=" * 80)
    print(f"Fichiers CSV trouvés: {len(fichiers_csv)}\n")
    
    # Liste pour stocker toutes les données
    donnees_consolidees = []
    
    # Lire chaque fichier CSV
    for fichier_csv in sorted(fichiers_csv):
        # Extraire le nom du fichier source (sans _cibles_extraites.csv)
        nom_fichier = fichier_csv.stem.replace('_cibles_extraites', '')
        
        # Lire le CSV
        df = pd.read_csv(fichier_csv, sep=';', encoding='utf-8-sig')
        
        # Ajouter la colonne Fichier
        df.insert(0, 'Fichier', nom_fichier)
        
        # Ajouter au consolidé
        donnees_consolidees.append(df)
        
        print(f"✓ {nom_fichier}: {len(df)} cibles")
    
    # Concaténer tous les DataFrames
    df_consolide = pd.concat(donnees_consolidees, ignore_index=True)
    
    # Sauvegarder le fichier consolidé
    fichier_sortie = 'coordonnees_cibles_consolidees.csv'
    df_consolide.to_csv(fichier_sortie, sep=';', index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Total de cibles consolidées: {len(df_consolide)}")
    print(f"Fichier créé: {fichier_sortie}")
    print("=" * 80)
    
    # Afficher un aperçu
    print("\nAPERÇU DES DONNÉES CONSOLIDÉES:")
    print("=" * 80)
    print(df_consolide.to_string(index=False))
    
    return df_consolide

if __name__ == '__main__':
    consolider_cibles()
