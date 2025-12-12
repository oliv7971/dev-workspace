#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute une colonne "Nb_cibles" au CSV des deplacements
"""

import pandas as pd
import os

# Chemin du fichier CSV
csv_path = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\2-extractions\smc_output\Deplacements_Ligne_SMC_2025_11.csv"

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

# Fonction pour determiner le nombre de cibles d'une ligne
def compter_cibles_ligne(row):
    """
    Determine le nombre de cibles en fonction de la presence de donnees
    dans les colonnes IG (Inter Gauche) et ID (Inter Droit)
    """
    # Verifier si les colonnes "inter" ont des donnees (non NaN)
    has_ig = pd.notna(row.get('DPM IG', None)) or pd.notna(row.get('DH IG', None)) or pd.notna(row.get('DZ IG', None))
    has_id = pd.notna(row.get('DPM ID', None)) or pd.notna(row.get('DH ID', None)) or pd.notna(row.get('DZ ID', None))
    
    return has_ig or has_id

# NOUVELLE LOGIQUE: Detecter au niveau de la SECTION (pas ligne par ligne)
# Pour chaque section, si SOIT periodique SOIT cumule a des donnees Inter -> 7 cibles
# Cela corrige le cas des nouvelles sections sans donnees periodiques (comme C060)

print("Detection du nombre de cibles par SECTION (periodique + cumule):")
print("-" * 60)

# Creer un dictionnaire section -> nb_cibles
section_nb_cibles = {}

for (galerie, section), group in df.groupby(['galerie', 'section']):
    # Verifier si au moins une ligne du groupe a des donnees Inter
    has_inter = False
    for idx, row in group.iterrows():
        if compter_cibles_ligne(row):
            has_inter = True
            break
    
    nb_cibles = 7 if has_inter else 5
    section_nb_cibles[(galerie, section)] = nb_cibles
    
    # Afficher avec detail si detection basee sur cumule seulement
    periodique_row = group[group['mode'] == 'périodique']
    cumule_row = group[group['mode'] == 'cumulé']
    
    has_inter_period = False
    has_inter_cumule = False
    
    if len(periodique_row) > 0:
        has_inter_period = compter_cibles_ligne(periodique_row.iloc[0])
    if len(cumule_row) > 0:
        has_inter_cumule = compter_cibles_ligne(cumule_row.iloc[0])
    
    note = ""
    if has_inter_cumule and not has_inter_period:
        note = " (detecte via cumule - nouvelles donnees periodiques vides)"
    
    print(f"{galerie:<6} {section:<8} -> {nb_cibles} cibles{note}")

# Appliquer le nombre de cibles au niveau de la section
def get_nb_cibles_section(row):
    return section_nb_cibles.get((row['galerie'], row['section']), 5)

df['Nb_cibles'] = df.apply(get_nb_cibles_section, axis=1)

print()
print("Verification - Nb_cibles applique a chaque ligne:")
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
df.to_csv(output_path, index=False, sep=';')

print()
print("="*70)
print(f"SUCCES ! Fichier sauvegarde :")
print(f"{output_path}")
print("="*70)

# Afficher aussi les premieres lignes pour verification
print()
print("Apercu des premieres lignes :")
print(df[['galerie', 'section', 'Nb_cibles', 'type', 'mode']].head(10))
