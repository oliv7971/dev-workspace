#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script spécifique pour le traitement des données d'implantation GMA
Ajoute les colonnes : Côté, th_X, th_Y

Fonctionnalités :
- Détermine le côté (Gauche/Droite) basé sur Coordonnée X/L
- Calcule th_X et th_Y selon les spécifications du projet
- Traite les données d'analyse d'implantation

Usage :
    python process_implantation_gma.py -i "analyse_complete.csv" -o "analyse_finale.csv"
"""

import pandas as pd
import argparse
import math

def process_implantation_data(input_file, output_file, encoding='iso-8859-1', separator=';'):
    """Traite les données d'implantation avec colonnes spécifiques GMA"""
    
    try:
        # Lire le fichier CSV
        print(f"Lecture du fichier : {input_file}")
        df = pd.read_csv(input_file, encoding=encoding, sep=separator)
        
        print(f"Données lues : {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Vérifier les colonnes nécessaires
        required_cols = ['Coordonnée X/L', 'Coordonnée Y/H ', 'PM Tunnel']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Erreur : Colonnes manquantes : {missing_cols}")
            return False
        
        # 1. Ajouter la colonne Côté
        def determine_side(value):
            try:
                val = float(value)
                if val < 0:
                    return "Gauche"
                elif val > 0:
                    return "Droite"
                else:
                    return "Centre"
            except (ValueError, TypeError):
                return "Indéterminé"
        
        df['Côté'] = df['Coordonnée X/L'].apply(determine_side)
        
        # 2. Ajouter les colonnes th_X et th_Y avec valeurs calculées
        # th_X est une valeur absolue : +1.903 pour côté Droite, -1.903 pour côté Gauche
        df['th_X'] = df['Côté'].apply(lambda cote: 1.903 if cote == 'Droite' else -1.903 if cote == 'Gauche' else 0)
        df['th_Y'] = -0.997  # Valeur théorique constante
        
        # 3. Ajouter les colonnes de comparaison (écarts)
        df['Écart_X'] = df['Coordonnée X/L'] - df['th_X']
        df['Écart_Y'] = df['Coordonnée Y/H '] - df['th_Y']
        
        print("Colonnes th_X et th_Y ajoutées avec valeurs calculées :")
        print(f"  th_X = +1.903 (côté Droite), -1.903 (côté Gauche)")
        print(f"  th_Y = -0.997 (pour tous les points)")
        print("Colonnes de comparaison ajoutées :")
        print(f"  Écart_X = Coordonnée X/L - th_X")
        print(f"  Écart_Y = Coordonnée Y/H - th_Y")
        
        # Statistiques
        side_counts = df['Côté'].value_counts()
        print(f"\nRépartition par côté :")
        for side, count in side_counts.items():
            print(f"  {side}: {count} points")
        
        # Afficher quelques exemples
        print(f"\nStructure des données :")
        sample_rows = df.head(3)
        for idx, row in sample_rows.iterrows():
            if idx > 0:  # Ignorer l'en-tête si présent
                print(f"  Point {row['#Nom du point']}: "
                      f"X/L={row['Coordonnée X/L']:.3f}, "
                      f"Y/H={row['Coordonnée Y/H ']:.3f}, "
                      f"Côté={row['Côté']}, "
                      f"th_X={row['th_X']}, th_Y={row['th_Y']}, "
                      f"Écart_X={row['Écart_X']:.3f}, Écart_Y={row['Écart_Y']:.3f}")
        
        # Sauvegarder
        df.to_csv(output_file, index=False, encoding=encoding, sep=separator)
        print(f"\nFichier sauvegardé : {output_file}")
        print(f"Structure finale : {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"Nouvelles colonnes ajoutées : Côté, th_X, th_Y, Écart_X, Écart_Y")
        
        return True
        
    except Exception as e:
        print(f"Erreur : {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Traitement spécifique des données d'implantation GMA")
    
    parser.add_argument("--input", "-i", required=True, 
                       help="Fichier CSV d'entrée (données d'analyse)")
    parser.add_argument("--output", "-o", required=True, 
                       help="Fichier CSV de sortie avec colonnes ajoutées")
    parser.add_argument("--encoding", default="iso-8859-1", 
                       help="Encodage du fichier (défaut: iso-8859-1)")
    parser.add_argument("--separator", "-s", default=";", 
                       help="Séparateur CSV (défaut: ;)")
    
    args = parser.parse_args()
    
    print("=== Traitement des données d'implantation GMA ===")
    print(f"Fichier d'entrée : {args.input}")
    print(f"Fichier de sortie : {args.output}")
    print()
    
    success = process_implantation_data(args.input, args.output, args.encoding, args.separator)
    
    if success:
        print("\n✓ Traitement terminé avec succès")
        print("\nNOTE: Vérifiez les formules de calcul de th_X et th_Y")
        print("      et adaptez-les selon vos spécifications techniques.")
    else:
        print("\n✗ Échec du traitement")

if __name__ == "__main__":
    main()