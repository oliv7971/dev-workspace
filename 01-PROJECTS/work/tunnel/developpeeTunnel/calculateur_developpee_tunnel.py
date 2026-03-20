#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculateur de développée de tunnel
Transforme un profil circulaire de tunnel en développée plane
pour cartographier les écarts le long de la voûte déroulée

Auteur: Assistant IA
Date: Octobre 2025
"""

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import os
from pathlib import Path

class DeveloppeeTunnel:
    """
    Classe pour calculer la développée d'un tunnel à partir de profils Amberg
    """
    
    def __init__(self):
        self.donnees = None
        self.resultats = None
        self.rayon_moyen = None
        self.angles = None
        self.longueurs_developpees = None
        self.ecarts = None
    
    def charger_fichier_amberg(self, chemin_fichier):
        """
        Charge un fichier CSV généré par Amberg
        
        Args:
            chemin_fichier (str): Chemin vers le fichier CSV
            
        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        try:
            self.donnees = pd.read_csv(
                chemin_fichier, 
                sep=';', 
                encoding='latin-1',
                na_values=['', ' ', 'N/A', 'NULL']
            )
            
            print(f"Fichier chargé avec succès: {chemin_fichier}")
            print(f"Nombre de points: {len(self.donnees)}")
            
            return True
            
        except FileNotFoundError:
            print(f"Erreur: Fichier non trouvé: {chemin_fichier}")
            return False
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
    
    def estimer_rayon_moyen(self, methode='distance_moyenne'):
        """
        Estime le rayon moyen du tunnel
        
        Args:
            methode (str): 'distance_moyenne', 'mediane', 'ajustement_cercle'
            
        Returns:
            float: Rayon moyen estimé
        """
        if self.donnees is None:
            print("Erreur: Aucun fichier chargé")
            return None
        
        # Coordonnées X,Y (colonnes G et H)
        x_coords = self.donnees.iloc[:, 6].values  # Colonne G
        y_coords = self.donnees.iloc[:, 7].values  # Colonne H
        
        # Calculer les distances depuis l'origine
        distances = np.sqrt(x_coords**2 + y_coords**2)
        
        if methode == 'distance_moyenne':
            self.rayon_moyen = np.mean(distances)
        elif methode == 'mediane':
            self.rayon_moyen = np.median(distances)
        elif methode == 'ajustement_cercle':
            # Méthode plus sophistiquée (approximation)
            self.rayon_moyen = np.mean(distances)
        
        print(f"\n=== ESTIMATION DU RAYON ===")
        print(f"Méthode: {methode}")
        print(f"Distance min: {distances.min():.3f} m")
        print(f"Distance max: {distances.max():.3f} m")
        print(f"Distance moyenne: {distances.mean():.3f} m")
        print(f"Écart-type: {distances.std():.3f} m")
        print(f"Rayon moyen retenu: {self.rayon_moyen:.3f} m")
        
        # Évaluer la qualité de l'approximation circulaire
        ecart_relatif = (distances.std() / distances.mean()) * 100
        print(f"Écart relatif: {ecart_relatif:.2f}% (< 5% = bon profil circulaire)")
        
        return self.rayon_moyen
    
    def calculer_angles(self):
        """
        Calcule les angles de chaque point par rapport à l'axe X
        
        Returns:
            bool: True si le calcul a réussi
        """
        if self.donnees is None:
            print("Erreur: Aucun fichier chargé")
            return False
        
        # Coordonnées X,Y (colonnes G et H)
        x_coords = self.donnees.iloc[:, 6].values
        y_coords = self.donnees.iloc[:, 7].values
        
        # Calculer les angles (référence axe X)
        self.angles = np.arctan2(y_coords, x_coords)  # En radians
        
        print(f"\n=== CALCUL DES ANGLES ===")
        print(f"Angle min: {np.degrees(self.angles.min()):.3f}°")
        print(f"Angle max: {np.degrees(self.angles.max()):.3f}°")
        print(f"Étendue angulaire: {np.degrees(self.angles.max() - self.angles.min()):.3f}°")
        
        return True
    
    def calculer_developpee(self):
        """
        Calcule la développée du tunnel avec référence à l'axe (0,0)
        et direction de référence Y (vers l'avant du tunnel)
        
        Returns:
            bool: True si le calcul a réussi
        """
        if self.rayon_moyen is None:
            print("Erreur: Rayon moyen non calculé")
            return False
        
        if self.angles is None:
            print("Erreur: Angles non calculés")
            return False
        
        # Corriger la discontinuité à ±180° pour un dépliage continu
        angles_corriges = self._corriger_discontinuite(self.angles)
        
        # Référence : direction Y (90°) = 0 de développée
        angle_reference = np.pi/2  # 90° en radians
        
        # Calculer les angles relatifs par rapport à la direction Y
        angles_relatifs = angles_corriges - angle_reference
        
        # Longueur développée = Rayon × angle_relatif
        # Côté droit (X>0) : développée positive
        # Côté gauche (X<0) : développée négative
        self.longueurs_developpees = self.rayon_moyen * angles_relatifs
        
        # Trier les points par longueur développée pour progression continue
        indices_tries = np.argsort(self.longueurs_developpees)
        self.longueurs_developpees = self.longueurs_developpees[indices_tries]
        
        # Récupérer les écarts correspondants (colonne I)
        ecarts_complets = self.donnees.iloc[:, 8].values  # Colonne I
        self.ecarts = ecarts_complets[indices_tries]
        
        # Créer le dataframe des résultats
        self.resultats = pd.DataFrame({
            'Point_Original': self.donnees.iloc[indices_tries, 0].values,  # Nom du point
            'Angle_deg': np.degrees(angles_corriges[indices_tries]),
            'Longueur_Developpee_m': self.longueurs_developpees,
            'Ecart_mm': self.ecarts * 1000,  # Conversion en mm
            'X_original': self.donnees.iloc[indices_tries, 6].values,
            'Y_original': self.donnees.iloc[indices_tries, 7].values
        })
        
        print(f"\n=== DÉVELOPPÉE CALCULÉE ===")
        print(f"Référence: Direction Y (vers l'avant du tunnel) = 0 m")
        print(f"Dépliage: Côté droit (+), côté gauche (-)")
        print(f"Longueur développée min: {self.longueurs_developpees.min():.3f} m (extrême gauche)")
        print(f"Longueur développée max: {self.longueurs_developpees.max():.3f} m (extrême droite)")
        print(f"Étendue totale: {self.longueurs_developpees.max() - self.longueurs_developpees.min():.3f} m")
        print(f"Écart min: {self.ecarts.min()*1000:.2f} mm")
        print(f"Écart max: {self.ecarts.max()*1000:.2f} mm")
        print(f"Écart moyen: {np.mean(self.ecarts)*1000:.2f} mm")
        
        return True
    
    def _corriger_discontinuite(self, angles):
        """
        Corrige la discontinuité à ±180° pour avoir un dépliage continu
        Convertit les angles de [-180°, +180°] vers une progression continue
        """
        angles_corriges = angles.copy()
        
        # Coordonnées pour identifier les positions
        x_coords = self.donnees.iloc[:, 6].values
        y_coords = self.donnees.iloc[:, 7].values
        
        # Pour chaque point, vérifier s'il faut corriger l'angle
        for i in range(len(angles)):
            angle_deg = np.degrees(angles[i])
            
            # Si le point est près de -180°, le ramener vers +180° pour continuité
            if angle_deg < -90:  # Points dans les quadrants 3 et 4 (X<0)
                if angle_deg < -90:
                    # Convertir -180° → +180° pour continuité
                    angles_corriges[i] = angles[i] + 2*np.pi
        
        return angles_corriges
    
    def afficher_statistiques(self):
        """
        Affiche des statistiques détaillées sur la développée
        """
        if self.resultats is None:
            print("Erreur: Aucun résultat disponible")
            return
        
        print(f"\n=== STATISTIQUES DE LA DÉVELOPPÉE ===")
        print(f"Nombre de points: {len(self.resultats)}")
        print(f"Rayon moyen utilisé: {self.rayon_moyen:.3f} m")
        print(f"Référence 0 m: Direction Y (vers l'avant du tunnel)")
        print(f"Dépliage: Côté droit (+), côté gauche (-)")
        print(f"Longueur développée min: {self.longueurs_developpees.min():.3f} m (extrême gauche)")
        print(f"Longueur développée max: {self.longueurs_developpees.max():.3f} m (extrême droite)")
        print(f"Étendue totale: {self.longueurs_developpees.max() - self.longueurs_developpees.min():.3f} m")
        print(f"Étendue angulaire: {np.degrees(self.angles.max() - self.angles.min()):.1f}°")
        
        print(f"\nÉcarts (en mm):")
        print(f"  Min: {self.ecarts.min()*1000:.2f}")
        print(f"  Max: {self.ecarts.max()*1000:.2f}")
        print(f"  Moyenne: {np.mean(self.ecarts)*1000:.2f}")
        print(f"  Écart-type: {np.std(self.ecarts)*1000:.2f}")
        
        print(f"\n=== PREMIERS POINTS DE LA DÉVELOPPÉE ===")
        print(self.resultats.head(10).to_string(index=False))
    
    def creer_graphique(self, sauvegarder=True):
        """
        Crée un graphique de la développée
        
        Args:
            sauvegarder (bool): Si True, sauvegarde le graphique
        """
        if self.resultats is None:
            print("Erreur: Aucun résultat disponible")
            return
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # Graphique 1: Développée du tunnel (vue de profil déroulé)
        ax1.plot(self.longueurs_developpees, self.ecarts * 1000, 'b-o', markersize=4)
        ax1.set_xlabel('Longueur développée depuis l\'avant du tunnel (m)')
        ax1.set_ylabel('Écart par rapport au profil théorique (mm)')
        ax1.set_title('Développée du tunnel - Cartographie des écarts (Référence: Direction Y = 0 m)')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Profil théorique')
        ax1.axvline(x=0, color='g', linestyle='--', alpha=0.7, label='Direction Y (0 m)')
        ax1.legend()
        
        # Graphique 2: Angles correspondants (pour référence terrain)
        angles_deg_resultats = self.resultats['Angle_deg'].values
        ax2.plot(self.longueurs_developpees, angles_deg_resultats, 'r-s', markersize=3)
        ax2.set_xlabel('Longueur développée depuis l\'avant du tunnel (m)')
        ax2.set_ylabel('Angle par rapport à l\'axe X (degrés)')
        ax2.set_title('Correspondance terrain - Angles pour repérage (Réf. développée: Direction Y = 0°)')
        ax2.grid(True, alpha=0.3)
        
        # Lignes de référence corrigées selon votre logique
        ax2.axhline(y=90, color='g', linestyle='--', alpha=0.7, label='90° = Direction Y+ (Réf. développée 0°)')
        ax2.axhline(y=0, color='b', linestyle='--', alpha=0.7, label='0° = Direction X+ (90° développée)')
        ax2.axhline(y=180, color='orange', linestyle='--', alpha=0.7, label='180° = Direction X- (180° développée)')
        ax2.axhline(y=-90, color='purple', linestyle='--', alpha=0.7, label='-90° = Direction Y- (270° développée)')
        ax2.axvline(x=0, color='g', linestyle='--', alpha=0.7, label='Référence développée (0 m)')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Ajouter des annotations corrigées pour les directions principales
        # Correspondance : angle polaire → angle développée
        directions_mapping = [
            (90, '90° polaire = 0° développée (Y+)'),
            (0, '0° polaire = 90° développée (X+)'),
            (180, '180° polaire = 180° développée (X-)'),
            (-90, '-90° polaire = 270° développée (Y-)')
        ]
        
        for angle_polaire, nom_direction in directions_mapping:
            # Trouver le point le plus proche de cet angle polaire
            idx_proche = np.argmin(np.abs(angles_deg_resultats - angle_polaire))
            if np.abs(angles_deg_resultats[idx_proche] - angle_polaire) < 15:  # Si proche à 15° près
                ax2.annotate(nom_direction, 
                           xy=(self.longueurs_developpees[idx_proche], angles_deg_resultats[idx_proche]),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
                           fontsize=9)

        # Graphique 3: Vue polaire (profil original)
        angles_deg = np.degrees(self.angles[np.argsort(self.angles)])
        ecarts_tries = self.ecarts
        
        scatter = ax3.scatter(self.resultats['X_original'], self.resultats['Y_original'], 
                   c=self.resultats['Ecart_mm'], cmap='RdYlBu_r', s=50)
        ax3.set_xlabel('X (m)')
        ax3.set_ylabel('Y (m)')
        ax3.set_title('Profil original du tunnel (coloré par écart)')
        ax3.set_aspect('equal')
        ax3.grid(True, alpha=0.3)
        
        # Ajouter des flèches pour indiquer les directions principales
        ax3.arrow(0, 0, 2, 0, head_width=0.2, head_length=0.3, fc='blue', ec='blue', alpha=0.7)
        ax3.text(2.5, 0, '0° polaire = 90° développée (X+)', fontsize=9, ha='left', va='center', color='blue')
        ax3.arrow(0, 0, 0, 2, head_width=0.2, head_length=0.3, fc='green', ec='green', alpha=0.7)
        ax3.text(0, 2.5, '90° polaire = 0° développée (Y+)\nRéférence développée', fontsize=9, ha='center', va='bottom', color='green')
        
        # Ajouter une barre de couleur
        cbar = plt.colorbar(scatter, ax=ax3)
        cbar.set_label('Écart (mm)')
        
        plt.tight_layout()
        
        if sauvegarder:
            nom_fichier = f"developpee_tunnel_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(nom_fichier, dpi=300, bbox_inches='tight')
            print(f"Graphique sauvegardé: {nom_fichier}")
        
        plt.show()
    
    def sauvegarder_resultats(self, chemin_sortie=None):
        """
        Sauvegarde les résultats de la développée
        
        Args:
            chemin_sortie (str): Chemin du fichier de sortie
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        if self.resultats is None:
            print("Erreur: Aucun résultat à sauvegarder")
            return None
        
        if chemin_sortie is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            chemin_sortie = f"developpee_tunnel_{timestamp}.csv"
        
        try:
            self.resultats.to_csv(
                chemin_sortie, 
                sep=';', 
                index=False, 
                encoding='latin-1'
            )
            print(f"Développée sauvegardée dans: {chemin_sortie}")
            return chemin_sortie
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return None


def main():
    """
    Fonction principale pour tester la développée
    """
    print("=== CALCULATEUR DE DÉVELOPPÉE DE TUNNEL ===")
    print("Transformation du profil circulaire en développée plane\n")
    
    # Créer une instance du calculateur
    dev = DeveloppeeTunnel()
    
    # Chemin du fichier exemple
    fichier_exemple = "AnalysisData_PM_13.408m.csv"
    
    if not os.path.exists(fichier_exemple):
        print(f"Fichier exemple non trouvé: {fichier_exemple}")
        return
    
    # Charger le fichier
    if not dev.charger_fichier_amberg(fichier_exemple):
        return
    
    # Estimer le rayon moyen
    dev.estimer_rayon_moyen('distance_moyenne')
    
    # Calculer les angles
    if not dev.calculer_angles():
        return
    
    # Calculer la développée
    if not dev.calculer_developpee():
        return
    
    # Afficher les statistiques
    dev.afficher_statistiques()
    
    # Créer le graphique
    dev.creer_graphique()
    
    # Sauvegarder les résultats
    dev.sauvegarder_resultats()
    
    print("\n=== TRAITEMENT TERMINÉ ===")


if __name__ == "__main__":
    main()