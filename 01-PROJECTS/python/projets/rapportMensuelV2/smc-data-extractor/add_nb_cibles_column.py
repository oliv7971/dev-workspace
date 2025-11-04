#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute une colonne "Nb_cibles" au CSV des deplacements
"""

import pandas as pd
import os

# Chemin du fichier CSV
csv_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\2-extractions\smc_output\Deplacements_Ligne_SMC_2025_10.csv"

print("="*70)
print("AJOUT COLONNE 'Nb_cibles' AU CSV")
print("="*70)
print(f"Fichier : {csv_path}")
print()

# Lire le CSV
df = pd.read_csv(csv_path)

print(f"Lignes chargees : {len(df)}")
print(f"Colonnes : {list(df.columns[:5])}...")
print()

# Fonction pour determiner le nombre de cibles
def compter_cibles(row):
    """
    Determine le nombre de cibles en fonction de la presence de donnees
    dans les colonnes IG (Inter Gauche) et ID (Inter Droit)
    """
    # Verifier si les colonnes "inter" ont des donnees (non NaN)
    has_ig = pd.notna(row.get('DPM IG', None)) or pd.notna(row.get('DH IG', None)) or pd.notna(row.get('DZ IG', None))
    has_id = pd.notna(row.get('DPM ID', None)) or pd.notna(row.get('DH ID', None)) or pd.notna(row.get('DZ ID', None))
    
    # Si au moins une des positions "inter" a des donnees
    if has_ig or has_id:
        return 7  # Bas, Inter, Haut, Voute (gauche et droit) + Voute = 7
    else:
        return 5  # Bas, Haut, Voute (gauche et droit) + Voute = 5

# Appliquer la fonction a chaque ligne
df['Nb_cibles'] = df.apply(compter_cibles, axis=1)

print("Nombre de cibles par section :")
print("-" * 40)
for idx, row in df.iterrows():
    if row['mode'] == 'périodique':  # Afficher seulement les lignes periodiques pour lisibilite
        print(f"{row['galerie']:<6} {row['section']:<8} -> {row['Nb_cibles']} cibles")

# Reordonner les colonnes pour mettre Nb_cibles apres section
cols = df.columns.tolist()
# Retirer Nb_cibles de sa position actuelle
cols.remove('Nb_cibles')
# Trouver l'index de 'section'
section_idx = cols.index('section')
# Inserer Nb_cibles juste apres section
cols.insert(section_idx + 1, 'Nb_cibles')
# Reordonner le DataFrame
df = df[cols]

# Sauvegarder le fichier modifie
output_path = csv_path.replace('.csv', '_avec_nb_cibles.csv')
df.to_csv(output_path, index=False)

print()
print("="*70)
print(f"SUCCES ! Fichier sauvegarde :")
print(f"{output_path}")
print("="*70)

# Afficher aussi les premieres lignes pour verification
print()
print("Apercu des premieres lignes :")
print(df[['galerie', 'section', 'Nb_cibles', 'type', 'mode']].head(10))
