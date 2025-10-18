"""
Module DXF - Export vers format DXF
"""

try:
    import ezdxf
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False

import math
import sys
import os

# Ajouter le répertoire parent au path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from core.geometrie import Point
from core.elements import AlignementDroit, Arc


class DxfExport:
    """Gestionnaire d'export DXF pour les axes et points"""
    
    def __init__(self):
        if not EZDXF_AVAILABLE:
            print("⚠️ Module ezdxf non disponible - export DXF impossible")
            print("   Installer avec: pip install ezdxf")
        
        self.doc = None
        self.msp = None
    
    def creer_document(self, version='R2010'):
        """Crée un nouveau document DXF"""
        if not EZDXF_AVAILABLE:
            raise ImportError("Module ezdxf non disponible")
        
        self.doc = ezdxf.new(version)
        self.msp = self.doc.modelspace()
        
        # Créer les calques standards
        self.doc.layers.new('AXES', dxfattribs={'color': 1})  # Rouge
        self.doc.layers.new('POINTS', dxfattribs={'color': 2})  # Jaune
        self.doc.layers.new('TEXTES', dxfattribs={'color': 3})  # Vert
        self.doc.layers.new('CONSTRUCTION', dxfattribs={'color': 8})  # Gris
    
    def exporter_axe(self, axe, calque='AXES', nb_points=100):
        """
        Exporte un axe vers DXF sous forme de polyline
        
        Args:
            axe: AxeEnPlan à exporter
            calque: Nom du calque DXF
            nb_points: Nombre de points pour discrétiser les courbes
        """
        if not EZDXF_AVAILABLE or self.doc is None:
            return
        
        points_polyline = []
        
        for element in axe.elements:
            if isinstance(element, AlignementDroit):
                # Alignement droit - 2 points suffisent
                if not points_polyline:  # Premier élément
                    points_polyline.append((element.debut.x, element.debut.y))
                points_polyline.append((element.fin.x, element.fin.y))
                
            elif isinstance(element, Arc):
                # Arc - discrétiser en plusieurs points
                longueur = element.longueur()
                pas = longueur / nb_points if longueur > 0 else 0
                
                for i in range(nb_points + 1):
                    distance = i * pas
                    if distance > longueur:
                        distance = longueur
                    
                    try:
                        point = element.point_at_distance(distance)
                        points_polyline.append((point.x, point.y))
                    except ValueError:
                        break
        
        # Créer la polyline
        if len(points_polyline) > 1:
            self.msp.add_lwpolyline(points_polyline, dxfattribs={'layer': calque})
    
    def exporter_points(self, points, calque='POINTS', taille_texte=2.5):
        """
        Exporte une liste de points avec leurs étiquettes
        """
        if not EZDXF_AVAILABLE or self.doc is None:
            return
        
        for point in points:
            # Point (cercle)
            self.msp.add_circle(
                center=(point.x, point.y), 
                radius=taille_texte/4,
                dxfattribs={'layer': calque}
            )
            
            # Étiquette
            nom_point = getattr(point, 'id', f'P{hash(point) % 1000:03d}')
            self.msp.add_text(
                nom_point,
                dxfattribs={
                    'layer': 'TEXTES',
                    'height': taille_texte,
                    'style': 'Standard'
                }
            ).set_pos((point.x + taille_texte, point.y + taille_texte))
    
    def exporter_tabulation(self, tabulation, calque='CONSTRUCTION', intervalle_etiquettes=50):
        """
        Exporte une tabulation d'axe avec points et PM
        """
        if not EZDXF_AVAILABLE or self.doc is None:
            return
        
        for i, item in enumerate(tabulation):
            x, y = item['X'], item['Y']
            pm = item['PM']
            
            # Point de construction
            self.msp.add_point(
                (x, y),
                dxfattribs={'layer': calque}
            )
            
            # Étiquette PM tous les X mètres
            if pm % intervalle_etiquettes == 0:
                self.msp.add_text(
                    f"PM {pm:.0f}",
                    dxfattribs={
                        'layer': 'TEXTES',
                        'height': 2.0,
                        'style': 'Standard'
                    }
                ).set_pos((x, y + 3))
    
    def exporter_profil_long(self, profil, axe=None, echelle_h=1000, echelle_v=100):
        """
        Exporte un profil en long (vue de côté)
        
        Args:
            profil: ProfilEnLong
            axe: AxeEnPlan pour les PM de référence
            echelle_h, echelle_v: Échelles horizontale et verticale
        """
        if not EZDXF_AVAILABLE or self.doc is None or not profil.points:
            return
        
        # Points du profil
        points_profil = []
        for pm, z in profil.points:
            x_profil = pm / echelle_h * 1000  # Conversion pour échelle
            y_profil = z / echelle_v * 100
            points_profil.append((x_profil, y_profil))
        
        # Ligne de profil
        if len(points_profil) > 1:
            self.msp.add_lwpolyline(points_profil, dxfattribs={'layer': 'AXES'})
        
        # Annotations
        for pm, z in profil.points[::5]:  # Une étiquette sur 5
            x_profil = pm / echelle_h * 1000
            y_profil = z / echelle_v * 100
            
            self.msp.add_text(
                f"PM{pm:.0f}\nZ{z:.2f}",
                dxfattribs={
                    'layer': 'TEXTES',
                    'height': 1.0
                }
            ).set_pos((x_profil, y_profil + 5))
    
    def ajouter_cartouche(self, titre="Calculateur d'Axes", auteur="", date=""):
        """Ajoute un cartouche au dessin"""
        if not EZDXF_AVAILABLE or self.doc is None:
            return
        
        # Position du cartouche (coin bas-droit)
        x_base = 200
        y_base = 10
        
        # Rectangle du cartouche
        points_cartouche = [
            (x_base, y_base),
            (x_base + 100, y_base),
            (x_base + 100, y_base + 30),
            (x_base, y_base + 30),
            (x_base, y_base)
        ]
        self.msp.add_lwpolyline(points_cartouche, dxfattribs={'layer': 'CONSTRUCTION'})
        
        # Textes
        self.msp.add_text(titre, dxfattribs={'height': 3.0}).set_pos((x_base + 5, y_base + 20))
        self.msp.add_text(f"Auteur: {auteur}", dxfattribs={'height': 2.0}).set_pos((x_base + 5, y_base + 15))
        self.msp.add_text(f"Date: {date}", dxfattribs={'height': 2.0}).set_pos((x_base + 5, y_base + 10))
    
    def sauvegarder(self, fichier_sortie):
        """Sauvegarde le document DXF"""
        if not EZDXF_AVAILABLE or self.doc is None:
            return False
        
        try:
            self.doc.saveas(fichier_sortie)
            print(f"✓ DXF exporté vers {fichier_sortie}")
            return True
        except Exception as e:
            print(f"⚠️ Erreur export DXF: {e}")
            return False
    
    def exporter_axe_complet(self, axe, profil=None, points=None, 
                           fichier_sortie="axe_export.dxf", **options):
        """
        Export complet d'un projet vers DXF
        
        Args:
            axe: AxeEnPlan
            profil: ProfilEnLong optionnel
            points: Liste de points optionnelle
            fichier_sortie: Nom du fichier DXF
            options: Options d'export
        """
        if not EZDXF_AVAILABLE:
            print("⚠️ Export DXF impossible - ezdxf non disponible")
            return False
        
        # Créer le document
        self.creer_document()
        
        # Export de l'axe
        if axe:
            self.exporter_axe(axe)
            
            # Tabulation de l'axe
            if options.get('inclure_tabulation', True):
                longueur = axe.longueur_totale()
                intervalle = options.get('intervalle_tabulation', 20)
                tabulation = axe.tabuler(0, longueur, intervalle)
                self.exporter_tabulation(tabulation)
        
        # Export du profil en long
        if profil and options.get('inclure_profil', True):
            self.exporter_profil_long(profil, axe)
        
        # Export des points
        if points and options.get('inclure_points', True):
            self.exporter_points(points)
        
        # Cartouche
        if options.get('inclure_cartouche', True):
            self.ajouter_cartouche(
                titre=options.get('titre', "Calculateur d'Axes"),
                auteur=options.get('auteur', ""),
                date=options.get('date', "")
            )
        
        # Sauvegarde
        return self.sauvegarder(fichier_sortie)