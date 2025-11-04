#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple pour calculer la développée d'un tunnel
Usage: python developpee_simple.py fichier_amberg.csv
"""

import sys
import os
from calculateur_developpee_tunnel import DeveloppeeTunnel

def main():
    if len(sys.argv) != 2:
        print("Usage: python developpee_simple.py fichier_amberg.csv")
        print("Exemple: python developpee_simple.py AnalysisData_PM_13.408m.csv")
        return
    
    fichier_entree = sys.argv[1]
    
    if not os.path.exists(fichier_entree):
        print(f"Erreur: Le fichier '{fichier_entree}' n'existe pas.")
        return
    
    print("🚇 === DÉVELOPPÉE DE TUNNEL ===")
    print(f"📁 Traitement du fichier: {fichier_entree}")
    print("=" * 50)
    
    # Créer le calculateur
    dev = DeveloppeeTunnel()
    
    # Traitement complet
    if not dev.charger_fichier_amberg(fichier_entree):
        return
    
    # Estimation automatique du rayon
    rayon = dev.estimer_rayon_moyen('distance_moyenne')
    if rayon is None:
        return
    
    # Calculs
    if not dev.calculer_angles():
        return
    
    if not dev.calculer_developpee():
        return
    
    # Résultats
    dev.afficher_statistiques()
    
    # Génération des fichiers de sortie
    nom_base = os.path.splitext(fichier_entree)[0]
    fichier_csv = f"{nom_base}_developpee.csv"
    
    dev.sauvegarder_resultats(fichier_csv)
    dev.creer_graphique(sauvegarder=True)
    
    print(f"\n✅ === TRAITEMENT TERMINÉ ===")
    print(f"📊 Fichier CSV: {fichier_csv}")
    print(f"📈 Graphique: developpee_tunnel_*.png")
    print(f"📏 Étendue développée: {dev.longueurs_developpees.min():.2f} m à {dev.longueurs_developpees.max():.2f} m")
    print(f"📐 Rayon moyen utilisé: {rayon:.3f} m")
    print(f"🎯 Référence 0 m: Direction Y (vers l'avant du tunnel)")
    print(f"📍 Dépliage continu: droite (+), gauche (-)")

if __name__ == "__main__":
    main()