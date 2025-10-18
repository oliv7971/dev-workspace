"""
Module batch - Calculs par lots sur un axe
"""

import pandas as pd
import numpy as np
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.geometrie import Point
from core.axe import AxeEnPlan, ProfilEnLong
from core.calculs_perpendiculaire import ModeCalcul


class CalculsBatch:
    """Calculs par lots sur un axe défini"""
    
    def __init__(self, axe_plan=None, profil_long=None):
        self.axe_plan = axe_plan
        self.profil_long = profil_long
        
    def projeter_points_excel(self, fichier_excel, mode='perpendiculaire', mode_calcul=None):
        """
        Projette une liste de points depuis Excel vers PM/Déport
        
        Args:
            fichier_excel: Fichier Excel avec colonnes 'ID', 'X', 'Y', 'Z'
            mode: 'perpendiculaire' ou 'vertical' (ancien système)
            mode_calcul: ModeCalcul (nouveau système) - prioritaire si défini
            
        Returns:
            DataFrame avec PM, Déport selon le mode choisi
        """
        if self.axe_plan is None:
            raise ValueError("Axe en plan non défini")
            
        df = pd.read_excel(fichier_excel)
        resultats = []
        
        for idx, row in df.iterrows():
            point = Point(row['X'], row['Y'], row.get('Z', 0))
            
            try:
                # Projection horizontale (PM + déport horizontal)
                pm, deport_h = self.axe_plan.projeter_point(point, mode='perpendiculaire')
                
                # Déport vertical si profil défini
                deport_v = 0.0
                if self.profil_long is not None:
                    z_axe = self.profil_long.altitude_at_pm(pm)
                    deport_v = point.z - z_axe
                
                resultats.append({
                    'ID': row['ID'],
                    'X': row['X'],
                    'Y': row['Y'],
                    'Z': row.get('Z', 0),
                    'PM': pm,
                    'Deport_H': deport_h,
                    'Deport_V': deport_v,
                    'Distance_H': abs(deport_h),
                    'Distance_3D': point.distance_2d(self.axe_plan.point_at_pm(pm))
                })
                
            except Exception as e:
                # Point non projetable
                resultats.append({
                    'ID': row['ID'],
                    'X': row['X'],
                    'Y': row['Y'],
                    'Z': row.get('Z', 0),
                    'PM': None,
                    'Deport_H': None,
                    'Deport_V': None,
                    'Distance_H': None,
                    'Distance_3D': None,
                    'Erreur': str(e)
                })
                print(f"⚠️ Erreur projection {row['ID']}: {e}")
            
        return pd.DataFrame(resultats)
    
    def projeter_points_excel_modes(self, fichier_excel, mode_calcul=ModeCalcul.HORIZONTAL_2D):
        """
        Projette une liste de points avec le nouveau système de modes
        
        Args:
            fichier_excel: Fichier Excel avec colonnes 'ID', 'X', 'Y', 'Z'
            mode_calcul: ModeCalcul (PERPENDICULAIRE_PROFIL, VERTICAL_ABSOLU, HORIZONTAL_2D)
            
        Returns:
            DataFrame avec PM, Déport selon le mode choisi + comparaison
        """
        if self.axe_plan is None:
            raise ValueError("Axe en plan non défini")
        
        # Vérifier si calculateur perpendiculaire disponible
        if (mode_calcul != ModeCalcul.HORIZONTAL_2D and 
            self.axe_plan.calculateur_perpendiculaire is None):
            raise ValueError("Profil en long requis pour modes perpendiculaire/vertical - utiliser associer_profil_long()")
            
        df = pd.read_excel(fichier_excel)
        resultats = []
        
        for idx, row in df.iterrows():
            point = Point(row['X'], row['Y'], row.get('Z', 0))
            
            try:
                # Projection avec le mode choisi
                pm, deport = self.axe_plan.projeter_point_avec_mode(point, mode_calcul)
                
                # Ajout informations complémentaires
                resultat = {
                    'ID': row['ID'],
                    'X': row['X'],
                    'Y': row['Y'],
                    'Z': row.get('Z', 0),
                    'PM': pm,
                    'Deport': deport,
                    'Mode': mode_calcul.value,
                    'Distance_absolue': abs(deport)
                }
                
                # Comparaison des modes si calculateur disponible
                if self.axe_plan.calculateur_perpendiculaire is not None:
                    comparaison = self.axe_plan.comparaison_modes_projection(point)
                    
                    resultat['Deport_Horizontal'] = comparaison[ModeCalcul.HORIZONTAL_2D]['deport']
                    resultat['Deport_Perpendiculaire'] = comparaison[ModeCalcul.PERPENDICULAIRE_PROFIL]['deport']
                    resultat['Deport_Vertical'] = comparaison[ModeCalcul.VERTICAL_ABSOLU]['deport']
                    
                    # Différences entre modes
                    deport_h = comparaison[ModeCalcul.HORIZONTAL_2D]['deport']
                    deport_p = comparaison[ModeCalcul.PERPENDICULAIRE_PROFIL]['deport']
                    deport_v = comparaison[ModeCalcul.VERTICAL_ABSOLU]['deport']
                    
                    resultat['Diff_H_P'] = abs(deport_h - deport_p)
                    resultat['Diff_H_V'] = abs(deport_h - deport_v)
                    resultat['Diff_P_V'] = abs(deport_p - deport_v)
                
                resultats.append(resultat)
                
            except Exception as e:
                # Point non projetable
                resultats.append({
                    'ID': row['ID'],
                    'X': row['X'],
                    'Y': row['Y'],
                    'Z': row.get('Z', 0),
                    'PM': None,
                    'Deport': None,
                    'Mode': mode_calcul.value,
                    'Erreur': str(e)
                })
                print(f"⚠️ Erreur projection {row['ID']} (nouveau mode): {e}")
            
        return pd.DataFrame(resultats)
    
    def calculer_points_depuis_pm(self, fichier_excel):
        """
        Calcule XYZ depuis liste PM/Déport
        
        Args:
            fichier_excel: Fichier Excel avec colonnes 'ID', 'PM', 'Deport_H', 'Deport_V'
            
        Returns:
            DataFrame avec coordonnées XYZ calculées
        """
        if self.axe_plan is None:
            raise ValueError("Axe en plan non défini")
            
        df = pd.read_excel(fichier_excel)
        resultats = []
        
        for idx, row in df.iterrows():
            try:
                pm = row['PM']
                deport_h = row.get('Deport_H', 0.0)
                deport_v = row.get('Deport_V', 0.0)
                
                # Point sur l'axe avec déport horizontal
                point = self.axe_plan.point_at_pm(pm, deport_h, mode_deport='perpendiculaire')
                
                # Altitude finale
                z_final = point.z
                if self.profil_long is not None:
                    z_axe = self.profil_long.altitude_at_pm(pm)
                    z_final = z_axe + deport_v
                else:
                    z_final += deport_v
                
                resultats.append({
                    'ID': row['ID'],
                    'PM': pm,
                    'Deport_H': deport_h,
                    'Deport_V': deport_v,
                    'X': point.x,
                    'Y': point.y,
                    'Z': z_final
                })
                
            except Exception as e:
                resultats.append({
                    'ID': row['ID'],
                    'PM': row['PM'],
                    'Deport_H': row.get('Deport_H', 0),
                    'Deport_V': row.get('Deport_V', 0),
                    'X': None,
                    'Y': None,
                    'Z': None,
                    'Erreur': str(e)
                })
                print(f"⚠️ Erreur calcul {row['ID']}: {e}")
                
        return pd.DataFrame(resultats)
    
    def tabuler_axe_excel(self, pm_debut, pm_fin, intervalle, fichier_sortie=None):
        """
        Génère une tabulation de l'axe vers Excel
        
        Args:
            pm_debut, pm_fin: Limites de tabulation
            intervalle: Pas de tabulation en mètres
            fichier_sortie: Fichier Excel de sortie (optionnel)
            
        Returns:
            DataFrame avec tabulation complète
        """
        if self.axe_plan is None:
            raise ValueError("Axe en plan non défini")
        
        # Générer la tabulation de base
        tabulation = self.axe_plan.tabuler(pm_debut, pm_fin, intervalle)
        
        # Enrichir avec le profil en long
        for item in tabulation:
            if self.profil_long is not None:
                item['Z_Axe'] = self.profil_long.altitude_at_pm(item['PM'])
                item['Pente_%'] = self.profil_long.pente_at_pm(item['PM'])
            else:
                item['Z_Axe'] = item['Z']
                item['Pente_%'] = 0.0
        
        df = pd.DataFrame(tabulation)
        
        # Export Excel si demandé
        if fichier_sortie:
            df.to_excel(fichier_sortie, index=False)
            print(f"✓ Tabulation exportée vers {fichier_sortie}")
            
        return df
    
    def analyser_ecarts(self, fichier_points_leves, tolerance_h=0.05, tolerance_v=0.02):
        """
        Analyse les écarts entre points levés et axe théorique
        
        Args:
            fichier_points_leves: Fichier Excel avec points de contrôle
            tolerance_h, tolerance_v: Tolérances en mètres
            
        Returns:
            DataFrame avec analyse des écarts
        """
        df_proj = self.projeter_points_excel(fichier_points_leves)
        
        # Analyse statistique des écarts
        ecarts_h = df_proj['Distance_H'].dropna()
        ecarts_v = df_proj['Deport_V'].dropna().abs()
        
        # Statistiques
        stats = {
            'Nombre_points': len(df_proj),
            'Points_valides': len(ecarts_h),
            'Ecart_H_moyen': ecarts_h.mean() if len(ecarts_h) > 0 else 0,
            'Ecart_H_max': ecarts_h.max() if len(ecarts_h) > 0 else 0,
            'Ecart_H_RMS': np.sqrt((ecarts_h**2).mean()) if len(ecarts_h) > 0 else 0,
            'Ecart_V_moyen': ecarts_v.mean() if len(ecarts_v) > 0 else 0,
            'Ecart_V_max': ecarts_v.max() if len(ecarts_v) > 0 else 0,
            'Ecart_V_RMS': np.sqrt((ecarts_v**2).mean()) if len(ecarts_v) > 0 else 0,
            'Hors_tolerance_H': (ecarts_h > tolerance_h).sum() if len(ecarts_h) > 0 else 0,
            'Hors_tolerance_V': (ecarts_v > tolerance_v).sum() if len(ecarts_v) > 0 else 0
        }
        
        # Ajouter colonnes d'analyse
        df_proj['Hors_Tol_H'] = df_proj['Distance_H'] > tolerance_h
        df_proj['Hors_Tol_V'] = df_proj['Deport_V'].abs() > tolerance_v
        
        return df_proj, stats
    
    def generer_rapport_calculs(self, repertoire_sortie="./"):
        """
        Génère un rapport complet des calculs effectués
        """
        rapport = {
            'Axe': {
                'Nom': self.axe_plan.nom if self.axe_plan else "Non défini",
                'Longueur_totale': self.axe_plan.longueur_totale() if self.axe_plan else 0,
                'Nb_elements': len(self.axe_plan.elements) if self.axe_plan else 0
            },
            'Projection': self.axe_plan.gestionnaire_projection.rapport_alteration() if self.axe_plan else {},
            'Profil': {
                'Nom': self.profil_long.nom if self.profil_long else "Non défini",
                'Nb_points': len(self.profil_long.points) if self.profil_long else 0
            }
        }
        
        return rapport