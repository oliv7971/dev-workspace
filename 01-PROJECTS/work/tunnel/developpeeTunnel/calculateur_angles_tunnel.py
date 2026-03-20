#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculateur d'angles pour profils de tunnel
Calcule l'angle de chaque point par rapport à l'axe du tunnel
À partir des données générées par le logiciel Amberg

Auteur: Assistant IA
Date: Octobre 2025
"""

import pandas as pd
import numpy as np
import math
import os
from pathlib import Path

class CalculateurAnglesTunnel:
    """
    Classe pour calculer les angles des points de profil de tunnel
    par rapport à l'axe principal
    """
    
    def __init__(self):
        self.donnees = None
        self.resultats = None
    
    def charger_fichier_amberg(self, chemin_fichier):
        """
        Charge un fichier CSV généré par Amberg
        
        Args:
            chemin_fichier (str): Chemin vers le fichier CSV
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        try:
            # Lire le fichier CSV avec le séparateur point-virgule
            # et gérer l'encodage pour les caractères spéciaux
            self.donnees = pd.read_csv(
                chemin_fichier, 
                sep=';', 
                encoding='latin-1',  # Pour gérer les caractères accentués
                na_values=['', ' ', 'N/A', 'NULL']
            )
            
            print(f"Fichier chargé avec succès: {chemin_fichier}")
            print(f"Nombre de points: {len(self.donnees)}")
            print("\nColonnes disponibles:")
            for i, col in enumerate(self.donnees.columns):
                print(f"  {chr(65+i)}: {col}")
            
            return True
            
        except FileNotFoundError:
            print(f"Erreur: Fichier non trouvé: {chemin_fichier}")
            return False
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
    
    def calculer_angles(self, unite_angle='degres'):
        """
        Calcule l'angle de chaque point par rapport à l'axe
        
        Args:
            unite_angle (str): 'degres' ou 'radians'
            
        Returns:
            bool: True si le calcul a réussi, False sinon
        """
        if self.donnees is None:
            print("Erreur: Aucun fichier chargé")
            return False
        
        try:
            # Identifier les colonnes X et Y (coordonnées par rapport à l'axe)
            # Colonnes G et H selon la demande
            col_x = self.donnees.columns[6]  # Colonne G (index 6)
            col_y = self.donnees.columns[7]  # Colonne H (index 7)
            
            print(f"\nCalcul des angles à partir des colonnes:")
            print(f"  X (transversale): {col_x}")
            print(f"  Y (longitudinale): {col_y}")
            print(f"  Référence: axe X (0° = direction transversale)")
            print(f"  Convention: 90° = vers l'avant du tunnel, -90° = vers l'arrière")
            
            # Copier les données pour les résultats
            self.resultats = self.donnees.copy()
            
            # Calculer l'angle pour chaque point
            angles = []
            
            for index, row in self.donnees.iterrows():
                x = float(row[col_x])  # Coordonnée transversale
                y = float(row[col_y])  # Coordonnée longitudinale
                
                # Calculer l'angle avec atan2 (prend en compte le quadrant)
                # atan2(y, x) donne l'angle depuis l'axe X positif
                # Pour des profils de tunnel, on veut l'angle depuis l'axe X (transversal)
                angle_rad = math.atan2(y, x)  # Angle depuis l'axe X
                
                # Convertir en degrés si demandé
                if unite_angle == 'degres':
                    angle = math.degrees(angle_rad)
                else:
                    angle = angle_rad
                
                angles.append(angle)
            
            # Ajouter la colonne des angles
            nom_colonne_angle = f"Angle ({unite_angle})"
            self.resultats[nom_colonne_angle] = angles
            
            print(f"\nCalcul terminé! Colonne '{nom_colonne_angle}' ajoutée.")
            print(f"Angles calculés: min={min(angles):.3f}, max={max(angles):.3f}")
            
            return True
            
        except Exception as e:
            print(f"Erreur lors du calcul des angles: {e}")
            return False
    
    def afficher_statistiques(self):
        """
        Affiche des statistiques sur les angles calculés
        """
        if self.resultats is None:
            print("Erreur: Aucun résultat disponible")
            return
        
        # Trouver la colonne des angles
        col_angle = None
        for col in self.resultats.columns:
            if 'Angle' in col:
                col_angle = col
                break
        
        if col_angle is None:
            print("Erreur: Colonne des angles non trouvée")
            return
        
        angles = self.resultats[col_angle]
        
        print(f"\n=== STATISTIQUES DES ANGLES ===")
        print(f"Nombre de points: {len(angles)}")
        print(f"Angle minimum: {angles.min():.3f}°")
        print(f"Angle maximum: {angles.max():.3f}°")
        print(f"Angle moyen: {angles.mean():.3f}°")
        print(f"Écart-type: {angles.std():.3f}°")
        
        # Quelques exemples
        print(f"\n=== PREMIERS POINTS ===")
        colonnes_importantes = ['#Nom du point', 'Coordonnée X/L', 'Coordonnée Y/H ', col_angle]
        for col in colonnes_importantes:
            if col not in self.resultats.columns:
                # Chercher une colonne similaire
                for c in self.resultats.columns:
                    if col.replace(' ', '').replace('é', 'e') in c.replace(' ', '').replace('é', 'e'):
                        colonnes_importantes[colonnes_importantes.index(col)] = c
                        break
        
        print(self.resultats[colonnes_importantes].head(10).to_string(index=False))
    
    def sauvegarder_resultats(self, chemin_sortie=None):
        """
        Sauvegarde les résultats dans un nouveau fichier CSV
        
        Args:
            chemin_sortie (str): Chemin du fichier de sortie. Si None, génère automatiquement
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        if self.resultats is None:
            print("Erreur: Aucun résultat à sauvegarder")
            return None
        
        if chemin_sortie is None:
            # Générer un nom de fichier automatique
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            chemin_sortie = f"resultats_angles_tunnel_{timestamp}.csv"
        
        try:
            self.resultats.to_csv(
                chemin_sortie, 
                sep=';', 
                index=False, 
                encoding='latin-1'
            )
            print(f"\nRésultats sauvegardés dans: {chemin_sortie}")
            return chemin_sortie
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return None


def main():
    """
    Fonction principale pour tester le calculateur
    """
    print("=== CALCULATEUR D'ANGLES POUR PROFILS DE TUNNEL ===")
    print("Calcul des angles à partir des données Amberg\n")
    
    # Créer une instance du calculateur
    calc = CalculateurAnglesTunnel()
    
    # Chemin du fichier exemple
    fichier_exemple = "AnalysisData_PM_13.408m.csv"
    
    if not os.path.exists(fichier_exemple):
        print(f"Fichier exemple non trouvé: {fichier_exemple}")
        print("Veuillez placer un fichier CSV d'Amberg dans le même répertoire.")
        return
    
    # Charger le fichier
    if not calc.charger_fichier_amberg(fichier_exemple):
        return
    
    # Calculer les angles
    if not calc.calculer_angles(unite_angle='degres'):
        return
    
    # Afficher les statistiques
    calc.afficher_statistiques()
    
    # Sauvegarder les résultats
    calc.sauvegarder_resultats()
    
    print("\n=== TRAITEMENT TERMINÉ ===")


if __name__ == "__main__":
    main()