"""
Calculateur d'Axes - Application principale
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configuration et logging
from config import get_config
from logging_utils import get_logger, log_function

# Imports absolus
from core.geometrie import Point, Vecteur
from core.axe import AxeEnPlan, ProfilEnLong
from core.projections import ModeProjection
from calculs.batch import CalculsBatch
from data_io.excel import ExcelIO
from data_io.dxf import DxfExport


class CalculateurAxes:
    """Application principale de calcul d'axes"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("CalculateurAxes")
        
        self.axe_plan = None
        self.profil_long = None
        self.calculateur = None
        self.io_excel = ExcelIO()
        self.io_dxf = DxfExport()
        
        # Initialiser les répertoires
        self.config.initialiser_repertoires()
        self.logger.info(f"Initialisation {self.config.APP_NAME} v{self.config.VERSION}")
    
    @log_function("Création axe exemple")
    def creer_axe_exemple(self):
        """Crée un axe d'exemple pour démonstration"""
        try:
            print("🏗️ Création d'un axe d'exemple...")
            self.logger.info("Début création axe d'exemple")
            
            # Créer l'axe
            self.axe_plan = AxeEnPlan("Axe Exemple")
            
            # Points de départ avec validation
            coords = [(823000, 1234000, 230), (823100, 1234100, 232), (823200, 1234150, 234)]
            
            # Validation des coordonnées
            for i, (x, y, z) in enumerate(coords):
                if not (self.config.valider_coordonnee(x) and self.config.valider_coordonnee(y)):
                    raise ValueError(f"Point {i+1}: {self.config.MSG_ERREUR_COORDONNEES}")
            
            p1, p2, p3 = [Point(x, y, z) for x, y, z in coords]
            
            # Ajouter des éléments
            # Alignement droit de 100m
            self.axe_plan.ajouter_alignement(p1, p2)
            
            # Arc de rayon 200m avec validation
            centre = Point(823200, 1234000, 233)
            rayon = 200
            if not self.config.valider_rayon(rayon):
                raise ValueError(self.config.MSG_ERREUR_RAYON)
            self.axe_plan.ajouter_arc(centre, rayon, 45, 76.831)  # 45g à 76.831g
            
            # Profil en long simple
            self.profil_long = ProfilEnLong("Profil Exemple")
            self.profil_long.ajouter_point(0, 230)
            self.profil_long.ajouter_point(100, 232)
            self.profil_long.ajouter_point(200, 234)
            self.profil_long.ajouter_point(300, 235)
            
            # Calculateur
            self.calculateur = CalculsBatch(self.axe_plan, self.profil_long)
            
            longueur = self.axe_plan.longueur_totale()
            print(f"✅ Axe créé - Longueur: {longueur:.1f}m")
            self.logger.log_operation("Création axe exemple", f"Longueur: {longueur:.1f}m", succes=True)
            return True
            
        except Exception as e:
            print(f"❌ Erreur création axe: {e}")
            self.logger.log_operation("Création axe exemple", str(e), succes=False)
            return False
    
    def demo_calculs_batch(self):
        """Démonstration des calculs par lots"""
        print("\n📊 Démonstration calculs par lots...")
        
        if self.axe_plan is None:
            self.creer_axe_exemple()
        
        # 1. Tabulation de l'axe
        print("\n1️⃣ Tabulation de l'axe...")
        tabulation = self.calculateur.tabuler_axe_excel(0, 300, 20)
        print(f"   {len(tabulation)} points tabulés")
        
        # Afficher les 5 premiers points
        print("   Aperçu:")
        for i in range(min(5, len(tabulation))):
            row = tabulation.iloc[i]
            print(f"   PM {row['PM']:6.0f}: X={row['X']:9.2f} Y={row['Y']:9.2f} Z={row['Z']:6.2f} Gis={row['Gisement']:7.3f}g")
        
        # 2. Créer des points d'exemple à projeter
        print("\n2️⃣ Projection de points...")
        points_test = [
            Point(823050, 1234060, 231.5),  # Près de l'axe
            Point(823150, 1234110, 233.0),  # Sur l'arc
            Point(823080, 1234080, 232.2),  # Avec déport
        ]
        
        for i, pt in enumerate(points_test):
            pm, deport = self.axe_plan.projeter_point(pt)
            print(f"   Point {i+1}: PM={pm:7.2f} Déport={deport:+6.3f}m")
        
        # 3. Calcul de points depuis PM/Déport
        print("\n3️⃣ Calcul XYZ depuis PM/Déport...")
        pm_deports = [
            (50, 0, 0.5),    # PM 50, axe, +0.5m en Z
            (150, -3, -0.2), # PM 150, -3m à gauche, -0.2m en Z  
            (250, 2.5, 0),   # PM 250, +2.5m à droite
        ]
        
        for pm, dh, dv in pm_deports:
            try:
                pt = self.axe_plan.point_at_pm(pm, dh)
                z_final = pt.z
                if self.profil_long:
                    z_axe = self.profil_long.altitude_at_pm(pm)
                    z_final = z_axe + dv
                
                print(f"   PM {pm:3.0f} D={dh:+5.1f}: X={pt.x:9.2f} Y={pt.y:9.2f} Z={z_final:6.2f}")
            except ValueError as e:
                print(f"   PM {pm:3.0f}: Erreur - {e}")
    
    def demo_projections(self):
        """Démonstration des modes de projection"""
        print("\n🌍 Démonstration gestion projections...")
        
        if self.axe_plan is None:
            self.creer_axe_exemple()
        
        # Test des différents modes
        modes = [
            ModeProjection.AUCUNE,
            ModeProjection.MANUELLE,
            ModeProjection.IGN
        ]
        
        for mode in modes:
            print(f"\n📐 Mode: {mode.value}")
            
            if mode == ModeProjection.MANUELLE:
                self.axe_plan.configurer_projection(mode, alteration_ppm=-140)
            elif mode == ModeProjection.IGN:
                self.axe_plan.configurer_projection(mode, altitude=250)
            else:
                self.axe_plan.configurer_projection(mode)
            
            # Info sur la configuration
            info = self.axe_plan.gestionnaire_projection.get_info_alteration()
            print(f"   {info}")
            
            # Test conversion distance
            distances_test = [100, 1000, 5000]
            for dist in distances_test:
                dist_corr = self.axe_plan.gestionnaire_projection.convertir_distance(dist)
                ecart = dist_corr - dist
                print(f"   {dist:4.0f}m → {dist_corr:8.3f}m (écart: {ecart*1000:+5.1f}mm)")
    
    def demo_export(self):
        """Démonstration des exports"""
        print("\n💾 Démonstration exports...")
        
        if self.axe_plan is None:
            self.creer_axe_exemple()
        
        # 1. Export Excel
        print("\n📊 Export Excel...")
        try:
            # Tabulation
            tabulation = self.calculateur.tabuler_axe_excel(0, 300, 10, "exemples/tabulation_axe.xlsx")
            print("   ✅ Tabulation Excel exportée")
            
            # Génération modèles
            self.io_excel.generer_modele_excel('points', 'exemples/modele_points.xlsx')
            self.io_excel.generer_modele_excel('elements', 'exemples/modele_elements.xlsx')
            print("   ✅ Modèles Excel générés")
            
        except Exception as e:
            print(f"   ⚠️ Erreur Excel: {e}")
        
        # 2. Export DXF
        print("\n🎨 Export DXF...")
        try:
            # Points d'exemple
            points = [
                Point(823025, 1234025, 230.5),
                Point(823075, 1234075, 231.8),
                Point(823125, 1234125, 233.2),
            ]
            points[0].id = "PT001"
            points[1].id = "PT002" 
            points[2].id = "PT003"
            
            # Export complet
            succes = self.io_dxf.exporter_axe_complet(
                self.axe_plan, 
                self.profil_long, 
                points,
                "exemples/axe_complet.dxf",
                titre="Axe d'Exemple",
                auteur="Calculateur d'Axes",
                inclure_tabulation=True,
                inclure_profil=True
            )
            
            if succes:
                print("   ✅ Export DXF réussi")
            else:
                print("   ⚠️ Export DXF échoué (ezdxf non disponible?)")
                
        except Exception as e:
            print(f"   ⚠️ Erreur DXF: {e}")
    
    def menu_principal(self):
        """Menu principal de l'application"""
        # Détecter si on est en mode interactif
        mode_interactif = sys.stdin.isatty()
        if not mode_interactif:
            print("🤖 Mode non-interactif détecté - Démonstration automatique")
            self.creer_axe_exemple()
            return
            
        while True:
            print("\n" + "="*50)
            print("🧮 CALCULATEUR D'AXES - Menu Principal")
            print("="*50)
            print("1. Créer axe d'exemple")
            print("2. Démonstration calculs par lots")
            print("3. Démonstration projections")
            print("4. Démonstration exports")
            print("5. Informations sur l'axe actuel")
            print("6. 🆕 Test perpendiculaire vs vertical")
            print("7. 📊 Import/Export Excel")
            print("0. Quitter")
            print("-"*50)
            
            try:
                choix = input("Votre choix (0-7): ").strip()
            except EOFError:
                print("\n⚠️ Pas d'entrée disponible - Création d'axe automatique")
                choix = '1'  # Créer un axe exemple par défaut
            except KeyboardInterrupt:
                print("\n👋 Interruption utilisateur - Au revoir !")
                break
            
            try:
                if choix == '0':
                    print("👋 Au revoir !")
                    break
                elif choix == '1':
                    self.creer_axe_exemple()
                elif choix == '2':
                    self.demo_calculs_batch()
                elif choix == '3':
                    self.demo_projections()
                elif choix == '4':
                    self.demo_export()
                elif choix == '5':
                    self.afficher_info_axe()
                elif choix == '6':
                    self.demo_perpendiculaire_vertical()
                elif choix == '7':
                    self.demo_import_export_excel()
                else:
                    print("❌ Choix invalide")
                    
            except KeyboardInterrupt:
                print("\n👋 Interruption utilisateur - Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
            
            try:
                input("\n⏸️  Appuyez sur Entrée pour continuer...")
            except EOFError:
                print("⏸️  Continuons...")
                # En mode non-interactif, on continue automatiquement
                if choix == '1':  # Si on vient de créer un axe exemple
                    break  # Sortir après création d'exemple en mode non-interactif
            except KeyboardInterrupt:
                print("\n👋 Interruption utilisateur - Au revoir !")
                break
    
    def afficher_info_axe(self):
        """Affiche les informations sur l'axe actuel"""
        print("\n📋 Informations axe actuel...")
        
        if self.axe_plan is None:
            print("❌ Aucun axe défini")
            return
        
        print(f"📏 Nom: {self.axe_plan.nom}")
        print(f"📏 Longueur totale: {self.axe_plan.longueur_totale():.2f}m")
        print(f"📏 Nombre d'éléments: {len(self.axe_plan.elements)}")
        
        # Détail des éléments
        print("\n🧩 Éléments:")
        pm_cumul = 0
        for i, elem in enumerate(self.axe_plan.elements):
            longueur = elem.longueur()
            type_elem = elem.__class__.__name__
            print(f"   {i+1}. {type_elem:15} PM {pm_cumul:7.2f} → {pm_cumul+longueur:7.2f} (L={longueur:6.2f}m)")
            pm_cumul += longueur
        
        # Projection
        print(f"\n🌍 Projection: {self.axe_plan.gestionnaire_projection.get_info_alteration()}")
        
        # Profil
        if self.profil_long:
            print(f"📈 Profil: {self.profil_long.nom} ({len(self.profil_long.points)} points)")
        else:
            print("📈 Profil: Non défini")
    
    def demo_perpendiculaire_vertical(self):
        """Démonstration de la distinction perpendiculaire/vertical"""
        print("\n🧮 Distinction Perpendiculaire vs Vertical...")
        
        from core.calculs_perpendiculaire import ModeCalcul
        import math
        
        # Créer un axe avec pente si pas déjà fait
        if self.axe_plan is None:
            self.creer_axe_exemple()
        
        # Créer un profil avec pente significative
        from core.axe import ProfilEnLong
        profil = ProfilEnLong("Profil Test Pente")
        profil.ajouter_point(0, 100)    # PM=0, Z=100m
        profil.ajouter_point(200, 110)  # PM=200, Z=110m (5% de pente)
        profil.ajouter_pente(0, 200, 5.0)  # 5% de pente constante
        
        # Associer le profil
        calculateur = self.axe_plan.associer_profil_long(profil)
        self.profil_long = profil
        
        print("   ✅ Axe avec profil en pente (5%) créé")
        
        # Point test : 2m à droite, 1m au-dessus de l'axe au PM 100
        point_test = Point(1102, 2002, 106)
        pm_test = 100
        
        print(f"\n📍 Point test: X={point_test.x}, Y={point_test.y}, Z={point_test.z}")
        print(f"   Position: 2m à droite, PM≈{pm_test}, altitude 106m")
        
        # Altitude théorique axe
        alt_axe = profil.altitude_at_pm(pm_test)
        print(f"   Altitude axe au PM {pm_test}: {alt_axe}m")
        
        # Comparaison des modes
        print("\n📐 Comparaison des modes de calcul:")
        print("-" * 60)
        
        comparaison = self.axe_plan.comparaison_modes_projection(point_test)
        
        for mode, resultats in comparaison.items():
            print(f"\n🔹 {mode.replace('_', ' ').title()}:")
            print(f"   {resultats['description']}")
            print(f"   Déport: {resultats.get('deport', 'N/A'):.3f}m")
            if 'distance' in resultats:
                print(f"   Distance: {resultats['distance']:.3f}m")
        
        # Test calculs inverses
        print(f"\n🔄 Calcul inverse - Point au PM {pm_test} + 2m déport:")
        print("-" * 60)
        
        modes_test = [
            (ModeCalcul.HORIZONTAL_2D, "Horizontal 2D"),
            (ModeCalcul.PERPENDICULAIRE_PROFIL, "Perpendiculaire profil"),
            (ModeCalcul.VERTICAL_ABSOLU, "Vertical absolu")
        ]
        
        for mode, nom in modes_test:
            try:
                pt = self.axe_plan.point_at_pm_avec_mode(pm_test, 2.0, mode)
                print(f"   {nom:20}: X={pt.x:.2f}, Y={pt.y:.2f}, Z={pt.z:.2f}")
            except Exception as e:
                print(f"   {nom:20}: Erreur - {e}")
        
        print("\n💡 Interprétation:")
        print("   📏 Horizontal 2D: Projection plane classique")
        print("   📐 Perpendiculaire: Tient compte de la pente (niveau)")  
        print("   🪃 Vertical: Selon la pesanteur (fil à plomb)")
        print("   📐 Différences visibles avec pentes importantes !")
        print("   ⚖️ Différences visibles avec pentes importantes !")

    def demo_import_export_excel(self):
        """Démonstration Import/Export Excel"""
        print("\n📊 DÉMONSTRATION IMPORT/EXPORT EXCEL")
        print("="*50)
        
        print("\n1. 📁 Vérification des modèles Excel...")
        exemples_dir = Path("exemples")
        
        modeles_requis = [
            "modele_saisie_elements.xlsx",
            "modele_points_a_traiter.xlsx",
            "GUIDE_SAISIE_EXCEL.md"
        ]
        
        modeles_existants = []
        for modele in modeles_requis:
            fichier = exemples_dir / modele
            if fichier.exists():
                modeles_existants.append(modele)
                print(f"   ✅ {modele}")
            else:
                print(f"   ❌ {modele} - Manquant")
        
        if len(modeles_existants) < len(modeles_requis):
            print("\n🔄 Création des modèles manquants...")
            try:
                import subprocess
                subprocess.run([sys.executable, "demo_saisie_excel.py"], check=True)
                print("   ✅ Modèles créés avec succès")
            except Exception as e:
                print(f"   ❌ Erreur création modèles: {e}")
                return
        
        print("\n2. 📋 Test d'import de définition d'axe...")
        try:
            fichier_elements = exemples_dir / "modele_saisie_elements.xlsx"
            if fichier_elements.exists():
                elements_def = self.io_excel.charger_definition_axe(str(fichier_elements))
                print(f"   ✅ {len(elements_def)} éléments chargés depuis Excel")
                
                for i, elem in enumerate(elements_def[:3], 1):
                    print(f"      {i}. {elem['type']}: {elem}")
            else:
                print("   ❌ Fichier modèle non trouvé")
                
        except Exception as e:
            print(f"   ❌ Erreur import: {e}")
        
        print("\n3. 📍 Test d'import de points...")
        try:
            fichier_points = exemples_dir / "modele_points_a_traiter.xlsx" 
            if fichier_points.exists():
                points = self.io_excel.charger_points(str(fichier_points))
                print(f"   ✅ {len(points)} points chargés")
                
                for i, point in enumerate(points[:3], 1):
                    id_point = getattr(point, 'id', f'P{i}')
                    print(f"      {i}. {id_point}: ({point.x}, {point.y}, {point.z:.1f})")
            else:
                print("   ❌ Fichier points non trouvé")
                
        except Exception as e:
            print(f"   ❌ Erreur import points: {e}")
        
        print("\n4. 💾 Test d'export...")
        if self.axe_plan is not None:
            try:
                # Générer quelques points de l'axe
                points_axe = []
                longueur_totale = self.axe_plan.longueur_totale()
                
                for i in range(0, int(longueur_totale), 50):
                    pm = self.axe_plan.pm_debut + i
                    point = self.axe_plan.point_at_pm(pm)
                    point.id = f"AXE_{i:03d}"
                    point.pm = pm
                    points_axe.append(point)
                
                fichier_export = exemples_dir / "export_points_axe.xlsx"
                self.io_excel.exporter_points(points_axe, str(fichier_export), 'complet')
                print(f"   ✅ {len(points_axe)} points exportés vers {fichier_export.name}")
                
            except Exception as e:
                print(f"   ❌ Erreur export: {e}")
        else:
            print("   ⚠️ Aucun axe chargé - créez d'abord un axe (option 1)")
        
        print(f"\n📁 Fichiers disponibles dans {exemples_dir}:")
        try:
            for fichier in exemples_dir.glob("*"):
                if fichier.is_file():
                    taille = fichier.stat().st_size
                    print(f"   📄 {fichier.name} ({taille} octets)")
        except Exception:
            print("   ❌ Erreur lecture répertoire")
        
        print("\n💡 UTILISATION:")
        print("   1. Modifiez les modèles Excel avec vos données")
        print("   2. Utilisez l'option 1 pour créer un axe exemple")
        print("   3. Les fichiers sont dans le dossier 'exemples/'")
        print("   4. Consultez GUIDE_SAISIE_EXCEL.md pour les détails")


def main():
    """Point d'entrée principal"""


def main():
    """Fonction principale"""  
    config = get_config()
    logger = get_logger("Main")
    
    print(f"🚀 Lancement du {config.APP_NAME}")
    print(f"   Version {config.VERSION} - Calculs topographiques d'axes")
    
    logger.info(f"Démarrage application {config.APP_NAME} v{config.VERSION}")
    
    # Gérer les arguments en ligne de commande
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            print("🤖 Mode démonstration automatique")
            try:
                app = CalculateurAxes()
                app.creer_axe_exemple()
                return 0
            except Exception as e:
                logger.critical(f"Erreur en mode démo: {e}", exc_info=True)
                print(f"💥 Erreur en mode démo: {e}")
                return 1
        elif sys.argv[1] == "--help":
            print("\nOptions disponibles:")
            print("  --demo    : Exécute une démonstration automatique")
            print("  --help    : Affiche cette aide")
            return 0
    
    try:
        # Créer l'application
        app = CalculateurAxes()
        
        # Vérification des dépendances
        print("\n🔧 Vérification des modules...")
        dependances_ok = True
        
        modules_requis = [
            ("pandas", "pip install pandas", True),
            ("numpy", "pip install numpy", True),
            ("openpyxl", "pip install openpyxl (pour Excel)", False),
            ("ezdxf", "pip install ezdxf (pour DXF)", False)
        ]
        
        for module, install_cmd, critique in modules_requis:
            try:
                __import__(module)
                print(f"   ✅ {module} disponible")
                logger.debug(f"Module {module} OK")
            except ImportError:
                if critique:
                    print(f"   ❌ {module} manquant - {install_cmd}")
                    logger.error(f"Module critique {module} manquant")
                    dependances_ok = False
                else:
                    print(f"   ⚠️ {module} manquant - {install_cmd}")
                    logger.warning(f"Module optionnel {module} manquant")
        
        if not dependances_ok:
            logger.critical("Dépendances critiques manquantes - arrêt de l'application")
            print("\n❌ Impossible de continuer sans les modules requis")
            return 1
        
        # Lancer le menu
        logger.info("Lancement interface utilisateur")
        app.menu_principal()
        logger.info("Fermeture normale de l'application")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interruption utilisateur (Ctrl+C)")
        print("\n👋 Interruption utilisateur - Au revoir !")
        return 0
    except Exception as e:
        logger.critical(f"Erreur fatale: {e}", exc_info=True)
        print(f"\n💥 Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    main()