#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour extraire les cibles de tous les fichiers Excel
Usage: python extraction_simple.py
"""

import sys
import os
from pathlib import Path
from extracteur_cibles import ExtracteurCibles

def traiter_fichier(chemin_fichier):
    """
    Traite un seul fichier Excel
    
    Args:
        chemin_fichier (str): Chemin vers le fichier
        
    Returns:
        bool: True si succès
    """
    print(f"\n{'='*80}")
    print(f"Traitement: {os.path.basename(chemin_fichier)}")
    print(f"{'='*80}")
    
    extracteur = ExtracteurCibles()
    
    if not extracteur.charger_fichier(chemin_fichier):
        print(f"✗ Échec du chargement")
        return False
    
    if not extracteur.extraire_coordonnees():
        print(f"✗ Échec de l'extraction")
        return False
    
    extracteur.afficher_resultats()
    
    # Sauvegarder avec nom automatique
    nom_sortie = Path(chemin_fichier).stem + "_cibles_extraites.csv"
    extracteur.sauvegarder_csv(nom_sortie)
    
    print(f"✓ Traitement réussi")
    return True

def main():
    """
    Traite tous les fichiers Excel du répertoire courant
    """
    print("="*80)
    print("EXTRACTEUR DE CIBLES - TRAITEMENT BATCH")
    print("="*80)
    
    # Si un argument est fourni, traiter ce fichier spécifique
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
        if os.path.exists(fichier):
            traiter_fichier(fichier)
        else:
            print(f"Fichier non trouvé: {fichier}")
        return
    
    # Sinon, traiter tous les fichiers .xlsx du répertoire
    fichiers_excel = list(Path('.').glob('*.xlsx'))
    
    if not fichiers_excel:
        print("Aucun fichier Excel (.xlsx) trouvé dans le répertoire courant")
        return
    
    print(f"Fichiers trouvés: {len(fichiers_excel)}")
    
    succes = 0
    echecs = 0
    
    for fichier in fichiers_excel:
        try:
            if traiter_fichier(str(fichier)):
                succes += 1
            else:
                echecs += 1
        except Exception as e:
            print(f"✗ Erreur: {e}")
            echecs += 1
    
    print(f"\n{'='*80}")
    print(f"RÉSUMÉ")
    print(f"{'='*80}")
    print(f"Total: {len(fichiers_excel)} fichiers")
    print(f"✓ Succès: {succes}")
    print(f"✗ Échecs: {echecs}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
