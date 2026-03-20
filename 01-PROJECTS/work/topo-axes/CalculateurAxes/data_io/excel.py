"""
Module Excel - Import/Export de données Excel
"""

import pandas as pd
import os
import sys

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.geometrie import Point
from core.axe import AxeEnPlan, ProfilEnLong
from config import get_config
from logging_utils import get_logger, log_function
from validation import get_validateur


class ExcelIO:
    """Gestionnaire d'import/export Excel pour les calculs d'axes"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("ExcelIO")
        self.validateur = get_validateur()
        
        self.formats_reconnus = {
            'points': ['ID', 'X', 'Y', 'Z'],
            'pm_deports': ['ID', 'PM', 'Deport_H', 'Deport_V'],
            'sommets': ['Sommet', 'X', 'Y', 'Z', 'PM', 'Rayon'],
            'elements': ['Element', 'Type', 'Param1', 'Param2', 'Param3'],
            'profil': ['PM', 'Z', 'Pente']
        }
    
    def detecter_format(self, fichier_excel, feuille=0):
        """
        Détecte automatiquement le format d'un fichier Excel
        
        Returns:
            Tuple (format_detecte, DataFrame)
        """
        try:
            df = pd.read_excel(fichier_excel, sheet_name=feuille)
            colonnes = set(df.columns.str.upper())
            
            # Test des différents formats
            for format_nom, colonnes_requises in self.formats_reconnus.items():
                colonnes_req_upper = set(col.upper() for col in colonnes_requises)
                if colonnes_req_upper.issubset(colonnes):
                    return format_nom, df
            
            return 'inconnu', df
            
        except Exception as e:
            print(f"Erreur lecture Excel: {e}")
            return None, None
    
    @log_function("Chargement points Excel")
    def charger_points(self, fichier_excel, feuille=0):
        """
        Charge une liste de points depuis Excel avec validation
        
        Returns:
            Liste d'objets Point
        """
        # Validation préalable du fichier
        erreurs_fichier = self.validateur.valider_fichier_excel(fichier_excel)
        if erreurs_fichier:
            raise ValueError(f"Fichier invalide: {'; '.join(erreurs_fichier)}")
        
        self.logger.info(f"Chargement points depuis {fichier_excel}")
        
        try:
            df = pd.read_excel(fichier_excel, sheet_name=feuille)
        except Exception as e:
            self.logger.error(f"Erreur lecture Excel: {e}")
            raise
        
        # Validation des données
        erreurs_donnees = self.validateur.valider_donnees_points_excel(df)
        if erreurs_donnees:
            self.logger.error(f"Données invalides: {len(erreurs_donnees)} erreur(s)")
            for erreur in erreurs_donnees[:5]:  # Afficher max 5 erreurs
                self.logger.error(f"  - {erreur}")
            raise ValueError(f"Données invalides: {erreurs_donnees[0]}")
        
        points = []
        
        # Normaliser les noms de colonnes
        colonnes_map = {}
        for col in df.columns:
            col_upper = col.upper()
            if col_upper in ['ID', 'NOM', 'NAME', 'POINT']:
                colonnes_map['id'] = col
            elif col_upper in ['X', 'EAST', 'E']:
                colonnes_map['x'] = col
            elif col_upper in ['Y', 'NORTH', 'N']:
                colonnes_map['y'] = col
            elif col_upper in ['Z', 'H', 'ALT', 'ALTITUDE']:
                colonnes_map['z'] = col
            elif col_upper in ['PM', 'PK']:
                colonnes_map['pm'] = col
        
        for idx, row in df.iterrows():
            try:
                point = Point(
                    x=float(row[colonnes_map['x']]),
                    y=float(row[colonnes_map['y']]),
                    z=float(row[colonnes_map.get('z', 0)]) if 'z' in colonnes_map else 0.0,
                    pm=float(row[colonnes_map['pm']]) if 'pm' in colonnes_map and pd.notna(row[colonnes_map['pm']]) else None
                )
                
                # Ajouter l'ID comme attribut
                if 'id' in colonnes_map:
                    point.id = row[colonnes_map['id']]
                
                points.append(point)
                
            except (ValueError, KeyError) as e:
                print(f"Erreur ligne {idx+2}: {e}")
                continue
        
        return points
    
    def charger_definition_axe(self, fichier_excel, feuille='Elements'):
        """
        Charge une définition d'axe depuis Excel
        
        Format attendu:
        - Element | Type | Param1 | Param2 | Param3
        - 1 | AD | 50.0000 | 100.00 |
        - 2 | C | 200 | 31.831 |
        """
        df = pd.read_excel(fichier_excel, sheet_name=feuille)
        elements_def = []
        
        for idx, row in df.iterrows():
            try:
                type_elem = str(row['Type']).upper()
                
                if type_elem == 'AD':  # Alignement droit
                    elements_def.append({
                        'type': 'AD',
                        'gisement': float(row['Param1']),
                        'longueur': float(row['Param2'])
                    })
                
                elif type_elem == 'C':  # Arc circulaire
                    elem_def = {
                        'type': 'C',
                        'rayon': float(row['Param1'])
                    }
                    
                    # Param2 peut être déviation ou longueur
                    param2 = float(row['Param2'])
                    if abs(param2) < 100:  # Probablement une déviation en grades
                        elem_def['deviation'] = param2
                    else:  # Probablement une longueur
                        elem_def['longueur'] = param2
                    
                    elements_def.append(elem_def)
                
                elif type_elem == 'CL':  # Clothoïde
                    elements_def.append({
                        'type': 'CL',
                        'rayon_debut': float(row['Param1']) if pd.notna(row['Param1']) else float('inf'),
                        'rayon_fin': float(row['Param2']) if pd.notna(row['Param2']) else float('inf'),
                        'longueur': float(row['Param3'])
                    })
                
            except (ValueError, KeyError) as e:
                print(f"Erreur élément ligne {idx+2}: {e}")
                continue
        
        return elements_def
    
    def charger_profil_long(self, fichier_excel, feuille='Profil'):
        """
        Charge un profil en long depuis Excel
        """
        df = pd.read_excel(fichier_excel, sheet_name=feuille)
        profil = ProfilEnLong()
        
        for idx, row in df.iterrows():
            try:
                pm = float(row['PM'])
                z = float(row['Z'])
                profil.ajouter_point(pm, z)
                
                # Pente si disponible
                if 'Pente' in row and pd.notna(row['Pente']):
                    pente = float(row['Pente'])
                    # Ajouter la pente (à améliorer)
                    
            except (ValueError, KeyError) as e:
                print(f"Erreur profil ligne {idx+2}: {e}")
                continue
        
        return profil
    
    def exporter_points(self, points, fichier_sortie, format_export='complet'):
        """
        Exporte une liste de points vers Excel
        
        Args:
            points: Liste d'objets Point
            fichier_sortie: Chemin du fichier Excel
            format_export: 'complet', 'xy', 'xyz', 'pm_deport'
        """
        donnees = []
        
        for i, point in enumerate(points):
            ligne = {}
            
            # ID
            if hasattr(point, 'id'):
                ligne['ID'] = point.id
            else:
                ligne['ID'] = f"P{i+1:03d}"
            
            # Coordonnées de base
            if format_export in ['complet', 'xy', 'xyz']:
                ligne['X'] = round(point.x, 3)
                ligne['Y'] = round(point.y, 3)
                
                if format_export in ['complet', 'xyz']:
                    ligne['Z'] = round(point.z, 3)
            
            # PM si disponible
            if format_export in ['complet', 'pm_deport'] and point.pm is not None:
                ligne['PM'] = round(point.pm, 3)
            
            # Attributs supplémentaires
            if format_export == 'complet':
                if hasattr(point, 'deport_h'):
                    ligne['Deport_H'] = round(point.deport_h, 3)
                if hasattr(point, 'deport_v'):
                    ligne['Deport_V'] = round(point.deport_v, 3)
                if hasattr(point, 'distance'):
                    ligne['Distance'] = round(point.distance, 3)
            
            donnees.append(ligne)
        
        df = pd.DataFrame(donnees)
        
        # Créer le répertoire si nécessaire
        os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
        
        df.to_excel(fichier_sortie, index=False)
        print(f"✓ {len(points)} points exportés vers {fichier_sortie}")
    
    def exporter_tabulation(self, tabulation, fichier_sortie):
        """
        Exporte une tabulation d'axe vers Excel
        """
        df = pd.DataFrame(tabulation)
        
        # Arrondir les valeurs numériques
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                df[col] = df[col].round(3)
        
        os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
        df.to_excel(fichier_sortie, index=False)
        print(f"✓ Tabulation exportée vers {fichier_sortie}")
    
    def generer_modele_excel(self, type_modele, fichier_sortie):
        """
        Génère un fichier Excel modèle avec les colonnes appropriées
        
        Args:
            type_modele: 'points', 'elements', 'profil', 'pm_deports'
        """
        if type_modele == 'points':
            donnees_exemple = [
                {'ID': 'P001', 'X': 823000.000, 'Y': 1234000.000, 'Z': 250.000},
                {'ID': 'P002', 'X': 823100.000, 'Y': 1234100.000, 'Z': 252.000},
            ]
        
        elif type_modele == 'elements':
            donnees_exemple = [
                {'Element': 1, 'Type': 'AD', 'Param1': 50.0000, 'Param2': 100.00, 'Param3': '', 'Commentaire': 'Gisement (g), Longueur (m)'},
                {'Element': 2, 'Type': 'C', 'Param1': 200, 'Param2': 31.831, 'Param3': '', 'Commentaire': 'Rayon (m), Déviation (g)'},
                {'Element': 3, 'Type': 'CL', 'Param1': 1000000, 'Param2': 200, 'Param3': 60, 'Commentaire': 'R_début, R_fin, Longueur'},
            ]
        
        elif type_modele == 'profil':
            donnees_exemple = [
                {'PM': 0.000, 'Z': 250.000, 'Pente': 2.0},
                {'PM': 100.000, 'Z': 252.000, 'Pente': 1.5},
                {'PM': 200.000, 'Z': 253.500, 'Pente': 0.0},
            ]
        
        elif type_modele == 'pm_deports':
            donnees_exemple = [
                {'ID': 'PT001', 'PM': 50.000, 'Deport_H': 0.000, 'Deport_V': 0.000},
                {'ID': 'PT002', 'PM': 150.000, 'Deport_H': -2.500, 'Deport_V': 0.500},
            ]
        
        else:
            raise ValueError(f"Type de modèle non reconnu: {type_modele}")
        
        df = pd.DataFrame(donnees_exemple)
        os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
        df.to_excel(fichier_sortie, index=False)
        print(f"✓ Modèle {type_modele} généré: {fichier_sortie}")