#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour calculer les angles de profils de tunnel
Utilisation rapide pour les fichiers Amberg

Usage:
    python calcul_angle_simple.py fichier_amberg.csv
"""

import sys
import os
from calculateur_angles_tunnel import CalculateurAnglesTunnel

def main():
    if len(sys.argv) != 2:
        print("Usage: python calcul_angle_simple.py fichier_amberg.csv")
        print("Exemple: python calcul_angle_simple.py AnalysisData_PM_13.408m.csv")
        return
    
    fichier_entree = sys.argv[1]
    
    if not os.path.exists(fichier_entree):
        print(f"Erreur: Le fichier '{fichier_entree}' n'existe pas.")
        return
    
    print(f"Traitement du fichier: {fichier_entree}")
    print("=" * 50)
    
    # Créer le calculateur
    calc = CalculateurAnglesTunnel()
    
    # Charger le fichier
    if not calc.charger_fichier_amberg(fichier_entree):
        return
    
    # Calculer les angles
    if not calc.calculer_angles(unite_angle='degres'):
        return
    
    # Afficher les statistiques
    calc.afficher_statistiques()
    
    # Générer le nom de fichier de sortie
    nom_base = os.path.splitext(fichier_entree)[0]
    fichier_sortie = f"{nom_base}_avec_angles.csv"
    
    # Sauvegarder
    calc.sauvegarder_resultats(fichier_sortie)
    
    print(f"\n✓ Traitement terminé!")
    print(f"✓ Fichier de sortie: {fichier_sortie}")

if __name__ == "__main__":
    main()