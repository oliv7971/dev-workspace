"""
Script de tabulation d'axe 3D
Génère des points régulièrement espacés le long d'un axe

Usage: 
  python tabuler_axe.py [--axe fichier_axe.txt] [--pas 0.5] [--sortie tabulation.csv]
  
  --axe: fichier définissant l'axe (PM,X,Y,Z)
  --pas: espacement entre points en mètres (défaut: 1.0m)
  --sortie: fichier de sortie (défaut: axe_tabule.csv)
"""

import numpy as np
import sys
from pathlib import Path


def charger_points_axe(fichier_axe=None):
    """
    Charge les points définissant l'axe.
    
    Args:
        fichier_axe: chemin vers fichier texte avec PM,X,Y,Z (séparateur auto-détecté)
                    Si None, utilise l'axe par défaut codé en dur
    
    Returns:
        array (N, 4) avec colonnes [PM, X, Y, Z]
    """
    if fichier_axe is None:
        # Axe par défaut (BURE GRE)
        print("   Utilisation de l'axe par défaut (BURE GRE)")
        return np.array([
            [0.000, 823241.141, 1091511.231, -123.794],
            [9.721, 823245.250, 1091502.421, -123.697],
            [56.601, 823265.062, 1091459.933, -123.228],
            [156.601, 823307.323, 1091369.302, -122.228]
        ])
    else:
        # Charger depuis fichier
        print(f"   Chargement de l'axe depuis : {fichier_axe}")
        
        # Détecter le séparateur
        with open(fichier_axe, 'r') as f:
            premiere_ligne = f.readline().strip()
            # Ignorer les lignes de commentaires ou d'en-tête
            while premiere_ligne.startswith('#') or (premiere_ligne and not premiere_ligne[0].replace('-', '').replace('.', '').isdigit()):
                premiere_ligne = f.readline().strip()
                
            if ';' in premiere_ligne:
                sep = ';'
            elif '\t' in premiere_ligne:
                sep = '\t'
            elif ',' in premiere_ligne:
                sep = ','
            else:
                sep = None  # Whitespace
        
        # Charger avec pandas
        import pandas as pd
        df = pd.read_csv(fichier_axe, sep=sep, header=None, 
                        names=['PM', 'X', 'Y', 'Z'],
                        comment='#', skipinitialspace=True,
                        engine='python' if sep is None else 'c')
        
        points = df[['PM', 'X', 'Y', 'Z']].values
        print(f"   → {len(points)} points chargés")
        return points


def definir_droite_depuis_points(points_axe):
    """
    Définit une droite 3D à partir de points de référence.
    Utilise une régression linéaire 3D pour avoir la meilleure droite moyenne.
    
    Args:
        points_axe: array (N, 4) avec colonnes [PM, X, Y, Z]
    
    Returns:
        origine: point (X, Y, Z) à PM=0
        direction: vecteur unitaire (dx, dy, dz) de la droite
        gisement: en grades
        pente: en pourcentage
        pm_min: PM minimum des points d'entrée
        pm_max: PM maximum des points d'entrée
    """
    pm = points_axe[:, 0]
    x = points_axe[:, 1]
    y = points_axe[:, 2]
    z = points_axe[:, 3]
    
    # Régression linéaire pour chaque coordonnée en fonction du PM
    # X = a_x * PM + b_x
    a_x = np.polyfit(pm, x, 1)[0]
    b_x = np.polyfit(pm, x, 1)[1]
    
    a_y = np.polyfit(pm, y, 1)[0]
    b_y = np.polyfit(pm, y, 1)[1]
    
    a_z = np.polyfit(pm, z, 1)[0]
    b_z = np.polyfit(pm, z, 1)[1]
    
    # Point origine (PM = 0)
    origine = np.array([b_x, b_y, b_z])
    
    # Vecteur direction pour PM = 1m
    direction_brut = np.array([a_x, a_y, a_z])
    
    # Normaliser pour avoir un vecteur unitaire
    direction = direction_brut / np.linalg.norm(direction_brut)
    
    # Calcul du gisement (en grades)
    gis_rad = np.arctan2(a_x, a_y)
    gisement = gis_rad * 200 / np.pi
    if gisement < 0:
        gisement += 400
    
    # Calcul de la pente
    dist_2d = np.sqrt(a_x**2 + a_y**2)
    pente = (a_z / dist_2d) * 100
    
    # Limites PM
    pm_min = np.min(pm)
    pm_max = np.max(pm)
    
    return origine, direction, gisement, pente, pm_min, pm_max


def tabuler_axe(points_axe, pas=1.0, pm_debut=None, pm_fin=None):
    """
    Génère des points régulièrement espacés le long de l'axe.
    
    Args:
        points_axe: array (N, 4) définissant l'axe
        pas: espacement entre points en mètres
        pm_debut: PM de début (None = min des points d'entrée)
        pm_fin: PM de fin (None = max des points d'entrée)
    
    Returns:
        array (M, 4) avec colonnes [PM, X, Y, Z]
    """
    # Définir la droite
    origine, direction, gisement, pente, pm_min, pm_max = definir_droite_depuis_points(points_axe)
    
    # Limites PM
    if pm_debut is None:
        pm_debut = pm_min
    if pm_fin is None:
        pm_fin = pm_max
    
    # Générer les PM tabulés
    nb_points = int((pm_fin - pm_debut) / pas) + 1
    pm_tabule = np.linspace(pm_debut, pm_fin, nb_points)
    
    # Calculer X, Y, Z pour chaque PM
    # Point = origine + PM * direction
    points_tabules = origine + pm_tabule[:, np.newaxis] * direction
    
    # Assembler avec PM
    resultat = np.column_stack([pm_tabule, points_tabules])
    
    return resultat, gisement, pente


def main():
    """Point d'entrée principal"""
    
    # Valeurs par défaut
    fichier_axe = None
    pas = 1.0
    fichier_sortie = "axe_tabule.csv"
    pm_debut = None
    pm_fin = None
    
    # Arguments de ligne de commande
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        print("\n" + "="*70)
        print("TABULATION D'AXE 3D")
        print("="*70)
        print("\nUsage:")
        print("  python tabuler_axe.py [--axe fichier] [--pas 0.5] [--sortie fichier]")
        print("                        [--debut 0] [--fin 100]")
        print("\nOptions:")
        print("  --axe fichier    Fichier définissant l'axe (PM,X,Y,Z)")
        print("                   Par défaut: axe BURE GRE codé dans le script")
        print("  --pas valeur     Espacement entre points en mètres (défaut: 1.0)")
        print("  --sortie fichier Fichier de sortie CSV (défaut: axe_tabule.csv)")
        print("  --debut PM       PM de début (défaut: min de l'axe)")
        print("  --fin PM         PM de fin (défaut: max de l'axe)")
        print("\nExemples:")
        print("  python tabuler_axe.py")
        print("  python tabuler_axe.py --pas 0.5")
        print("  python tabuler_axe.py --axe mon_axe.txt --pas 0.25 --sortie tabulation.csv")
        print("  python tabuler_axe.py --debut 10 --fin 50 --pas 0.1")
        print("\nFormat du fichier de sortie:")
        print("  PM,X,Y,Z")
        print("  0.000,823241.141,1091511.231,-123.794")
        print("  1.000,823241.547,1091510.377,-123.784")
        print("  ...\n")
        sys.exit(0 if '--help' in sys.argv or '-h' in sys.argv else 1)
    
    # Parser les arguments
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--axe':
            if i + 1 < len(sys.argv):
                fichier_axe = sys.argv[i + 1]
                i += 2
            else:
                print("ERREUR: --axe nécessite un nom de fichier")
                sys.exit(1)
        elif arg == '--pas':
            if i + 1 < len(sys.argv):
                try:
                    pas = float(sys.argv[i + 1])
                    if pas <= 0:
                        print("ERREUR: le pas doit être > 0")
                        sys.exit(1)
                    i += 2
                except ValueError:
                    print(f"ERREUR: valeur invalide pour --pas: '{sys.argv[i + 1]}'")
                    sys.exit(1)
            else:
                print("ERREUR: --pas nécessite une valeur")
                sys.exit(1)
        elif arg == '--sortie':
            if i + 1 < len(sys.argv):
                fichier_sortie = sys.argv[i + 1]
                i += 2
            else:
                print("ERREUR: --sortie nécessite un nom de fichier")
                sys.exit(1)
        elif arg == '--debut':
            if i + 1 < len(sys.argv):
                try:
                    pm_debut = float(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print(f"ERREUR: valeur invalide pour --debut: '{sys.argv[i + 1]}'")
                    sys.exit(1)
            else:
                print("ERREUR: --debut nécessite une valeur")
                sys.exit(1)
        elif arg == '--fin':
            if i + 1 < len(sys.argv):
                try:
                    pm_fin = float(sys.argv[i + 1])
                    i += 2
                except ValueError:
                    print(f"ERREUR: valeur invalide pour --fin: '{sys.argv[i + 1]}'")
                    sys.exit(1)
            else:
                print("ERREUR: --fin nécessite une valeur")
                sys.exit(1)
        else:
            print(f"ERREUR: Argument inconnu '{arg}'")
            print("Utilisez --help pour l'aide")
            sys.exit(1)
    
    # Vérifier que le fichier axe existe si spécifié
    if fichier_axe is not None and not Path(fichier_axe).exists():
        print(f"\nERREUR: Le fichier axe '{fichier_axe}' n'existe pas!")
        sys.exit(1)
    
    # Traiter
    try:
        # Import pandas ici pour message d'erreur clair si manquant
        global pd
        import pandas as pd
        
        print("\n" + "="*60)
        print("TABULATION D'AXE 3D")
        print("="*60)
        
        # Charger les points de l'axe
        print("\n1. Chargement de l'axe...")
        points_axe = charger_points_axe(fichier_axe)
        
        # Tabuler
        print("\n2. Tabulation de l'axe...")
        print(f"   Pas: {pas} m ({pas*100:.1f} cm)")
        if pm_debut is not None:
            print(f"   PM début: {pm_debut:.3f} m")
        if pm_fin is not None:
            print(f"   PM fin: {pm_fin:.3f} m")
        
        points_tabules, gisement, pente = tabuler_axe(points_axe, pas, pm_debut, pm_fin)
        
        print(f"\n   → {len(points_tabules)} points générés")
        print(f"   Gisement: {gisement:.4f} grades")
        print(f"   Pente: {pente:.2f} %")
        print(f"   PM: {points_tabules[0, 0]:.3f} → {points_tabules[-1, 0]:.3f} m")
        
        # Écrire le résultat
        print(f"\n3. Écriture du fichier: {fichier_sortie}")
        with open(fichier_sortie, 'w') as f:
            f.write("PM,X,Y,Z\n")
            for i in range(len(points_tabules)):
                f.write(f"{points_tabules[i, 0]:.6f},{points_tabules[i, 1]:.6f},"
                       f"{points_tabules[i, 2]:.6f},{points_tabules[i, 3]:.6f}\n")
        
        taille_ko = Path(fichier_sortie).stat().st_size / 1024
        print(f"   Taille: {taille_ko:.1f} Ko")
        
        print("\n✓ Terminé !")
        print("="*60 + "\n")
        
    except ImportError:
        print("\nERREUR: pandas n'est pas installé!")
        print("Installation: pip install pandas")
        sys.exit(1)
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
