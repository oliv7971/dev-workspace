#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour ajouter une colonne "Côté" basée sur la colonne G (Coordonnée X/L)

Règle :
- Si Coordonnée X/L < 0 : Gauche
- Si Coordonnée X/L > 0 : Droite
- Si Coordonnée X/L = 0 : Centre
"""

import pandas as pd
import argparse
import logging

def add_side_column(input_file, output_file, encoding='iso-8859-1', separator=';'):
    """Ajoute une colonne Côté basée sur la colonne G"""
    
    try:
        # Lire le fichier CSV
        print(f"Lecture du fichier : {input_file}")
        df = pd.read_csv(input_file, encoding=encoding, sep=separator)
        
        print(f"Données lues : {len(df)} lignes, {len(df.columns)} colonnes")
        print(f"Colonnes : {list(df.columns)}")
        
        # Identifier la colonne Coordonnée X/L (colonne G)
        coord_col = 'Coordonnée X/L'
        
        if coord_col not in df.columns:
            print(f"Erreur : La colonne '{coord_col}' n'existe pas")
            print(f"Colonnes disponibles : {list(df.columns)}")
            return False
        
        # Ajouter la colonne Côté
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
        
        df['Côté'] = df[coord_col].apply(determine_side)
        
        # Compter les côtés
        side_counts = df['Côté'].value_counts()
        print(f"\nRépartition par côté :")
        for side, count in side_counts.items():
            print(f"  {side}: {count} points")
        
        # Sauvegarder
        df.to_csv(output_file, index=False, encoding=encoding, sep=separator)
        print(f"\nFichier sauvegardé : {output_file}")
        print(f"Nouvelle structure : {len(df)} lignes, {len(df.columns)} colonnes")
        
        return True
        
    except Exception as e:
        print(f"Erreur : {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Ajouter une colonne Côté basée sur Coordonnée X/L")
    
    parser.add_argument("--input", "-i", required=True, help="Fichier CSV d'entrée")
    parser.add_argument("--output", "-o", required=True, help="Fichier CSV de sortie")
    parser.add_argument("--encoding", default="iso-8859-1", help="Encodage (défaut: iso-8859-1)")
    parser.add_argument("--separator", "-s", default=";", help="Séparateur (défaut: ;)")
    
    args = parser.parse_args()
    
    success = add_side_column(args.input, args.output, args.encoding, args.separator)
    
    if success:
        print("✓ Traitement réussi")
    else:
        print("✗ Échec du traitement")

if __name__ == "__main__":
    main()