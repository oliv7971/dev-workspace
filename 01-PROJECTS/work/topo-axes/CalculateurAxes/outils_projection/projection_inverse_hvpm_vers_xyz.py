"""
Script de projection inverse: H,V,PM → X,Y,Z
Reconstitue les coordonnées XYZ à partir des coordonnées sur axe

Usage: 
  python projection_inverse_hvpm_vers_xyz.py fichier_hvpm.csv [fichier_sortie.csv] [mode] [--axe fichier_axe.txt]
  
  Mode: vertical (défaut) ou perpendiculaire
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
            while premiere_ligne.startswith('#') or not premiere_ligne[0].isdigit():
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
    
    return origine, direction, gisement, pente


def convertir_hvpm_vers_xyz(points_hvpm, origine, direction, mode='vertical'):
    """
    Convertit des coordonnées H,V,PM en X,Y,Z.
    Calcul vectorisé avec numpy pour performance maximale.
    
    Args:
        points_hvpm: array (N, 3) avec colonnes [H, V, PM]
        origine: point origine de la droite (X, Y, Z)
        direction: vecteur directeur unitaire (dx, dy, dz)
        mode: 'perpendiculaire' ou 'vertical'
    
    Returns:
        points_xyz: array (N, 3) avec colonnes [X, Y, Z]
    """
    h = points_hvpm[:, 0]
    v = points_hvpm[:, 1]
    pm = points_hvpm[:, 2]
    
    if mode == 'perpendiculaire':
        # PROJECTION PERPENDICULAIRE 3D
        # Point sur l'axe au PM donné
        points_sur_axe = origine + pm[:, np.newaxis] * direction
        
        # Vecteur perpendiculaire horizontal (dans le plan XY)
        # Perpendiculaire à la direction en plan, tourné de 90° à droite
        direction_2d = direction[:2]
        perp_2d = np.array([direction_2d[1], -direction_2d[0]])  # Rotation 90° droite
        perp_2d = perp_2d / np.linalg.norm(perp_2d)
        
        # Vecteur perpendiculaire 3D pour le déport H
        vecteur_h = np.zeros((len(h), 3))
        vecteur_h[:, :2] = h[:, np.newaxis] * perp_2d
        
        # Vecteur vertical pour le déport V
        vecteur_v = np.zeros((len(v), 3))
        vecteur_v[:, 2] = v
        
        # Position finale
        points_xyz = points_sur_axe + vecteur_h + vecteur_v
        
    else:  # mode == 'vertical'
        # PROJECTION VERTICALE
        # Direction 2D normalisée
        direction_2d = direction[:2] / np.linalg.norm(direction[:2])
        
        # Point sur l'axe en plan au PM donné
        points_plan = origine[:2] + pm[:, np.newaxis] * direction_2d
        
        # Vecteur perpendiculaire horizontal (à droite de la direction)
        perp_2d = np.array([direction_2d[1], -direction_2d[0]])
        
        # Position XY
        xy = points_plan + h[:, np.newaxis] * perp_2d
        
        # Altitude de l'axe au PM
        pente_z = direction[2] / np.linalg.norm(direction[:2])  # dZ par mètre en plan
        z_axe = origine[2] + pente_z * pm
        
        # Altitude finale
        z = z_axe + v
        
        # Assemblage
        points_xyz = np.column_stack([xy, z])
    
    return points_xyz


def traiter_fichier(fichier_entree, fichier_sortie, points_axe, mode='vertical', chunk_size=500000):
    """
    Traite un fichier de points par blocs pour économiser la RAM.
    
    Args:
        fichier_entree: chemin du fichier H,V,PM
        fichier_sortie: chemin du fichier de sortie X,Y,Z
        points_axe: array (N, 4) définissant la droite
        mode: 'perpendiculaire' ou 'vertical'
        chunk_size: nombre de lignes à traiter par bloc
    """
    print(f"\n{'='*60}")
    print(f"PROJECTION INVERSE: H,V,PM → X,Y,Z")
    print(f"{'='*60}")
    
    # Définir la droite
    print("\n1. Définition de la droite de référence...")
    origine, direction, gisement, pente = definir_droite_depuis_points(points_axe)
    
    print(f"   Origine (PM=0) : X={origine[0]:.3f}, Y={origine[1]:.3f}, Z={origine[2]:.3f}")
    print(f"   Gisement : {gisement:.4f} grades")
    print(f"   Pente : {pente:.2f} %")
    print(f"   Mode : {mode.upper()}")
    
    # Compter le nombre de lignes et détecter le séparateur
    print(f"\n2. Lecture du fichier : {fichier_entree}")
    
    # Détecter le séparateur en lisant la première ligne (après l'en-tête éventuel)
    with open(fichier_entree, 'r') as f:
        premiere_ligne = f.readline().strip()
        deuxieme_ligne = f.readline().strip()
        
        # Utiliser la 2ème ligne si la 1ère est un en-tête
        ligne_test = deuxieme_ligne if premiere_ligne.replace(',', '').replace(';', '').replace('\t', '').replace('.', '').replace('-', '').replace(' ', '').isalpha() else premiere_ligne
        
        if ';' in ligne_test:
            separateur = ';'
        elif '\t' in ligne_test:
            separateur = '\t'
        elif ',' in ligne_test:
            separateur = ','
        else:
            separateur = r'\s+'  # Regex pour un ou plusieurs espaces
    
    sep_name = {';': 'POINT-VIRGULE', '\t': 'TAB', ',': 'VIRGULE'}.get(separateur, 'ESPACE')
    print(f"   Séparateur détecté : {sep_name}")
    
    with open(fichier_entree, 'r') as f:
        nb_lignes = sum(1 for _ in f) - 1  # -1 pour l'en-tête
    
    print(f"   Nombre de points : {nb_lignes:,}")
    taille_mo = Path(fichier_entree).stat().st_size / (1024 * 1024)
    print(f"   Taille fichier : {taille_mo:.1f} Mo")
    
    # Traitement par blocs
    print(f"\n3. Conversion des points (par blocs de {chunk_size:,})...")
    
    nb_blocks = (nb_lignes + chunk_size - 1) // chunk_size
    
    with open(fichier_sortie, 'w') as f_out:
        # En-tête
        f_out.write("X,Y,Z\n")
        
        # Traiter par blocs
        for i, chunk in enumerate(pd.read_csv(fichier_entree, 
                                               sep=separateur, 
                                               chunksize=chunk_size,
                                               dtype=float,
                                               skipinitialspace=True,
                                               on_bad_lines='skip',
                                               engine='python' if separateur == r'\s+' else 'c')):
            
            # S'assurer que les colonnes sont dans le bon ordre
            if 'H' in chunk.columns:
                points_hvpm = chunk[['H', 'V', 'PM']].values
            else:
                # Pas d'en-tête, prendre les 3 premières colonnes
                points_hvpm = chunk.iloc[:, :3].values
            
            # Filtrer les NaN
            mask = ~np.isnan(points_hvpm).any(axis=1)
            points_hvpm = points_hvpm[mask]
            
            if len(points_hvpm) == 0:
                continue
                
            points_xyz = convertir_hvpm_vers_xyz(points_hvpm, origine, direction, mode)
            
            # Écrire les résultats
            for j in range(len(points_xyz)):
                f_out.write(f"{points_xyz[j, 0]:.6f},{points_xyz[j, 1]:.6f},{points_xyz[j, 2]:.6f}\n")
            
            # Afficher progression
            progress = (i + 1) / nb_blocks * 100
            points_traites = min((i + 1) * chunk_size, nb_lignes)
            print(f"   [{progress:5.1f}%] {points_traites:,} / {nb_lignes:,} points traités", end='\r')
    
    print(f"\n\n4. ✓ Terminé !")
    print(f"   Fichier de sortie : {fichier_sortie}")
    taille_sortie_mo = Path(fichier_sortie).stat().st_size / (1024 * 1024)
    print(f"   Taille : {taille_sortie_mo:.1f} Mo")
    print(f"\n{'='*60}\n")


def main():
    """Point d'entrée principal"""
    
    # Arguments de ligne de commande
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("PROJECTION INVERSE: H,V,PM → X,Y,Z")
        print("="*70)
        print("\nUsage:")
        print("  python projection_inverse_hvpm_vers_xyz.py fichier_hvpm.csv [sortie.csv] [mode] [--axe axe.txt]")
        print("\nMode de projection:")
        print("  vertical        - Projection verticale (classique) [DÉFAUT]")
        print("  perpendiculaire - Projection perpendiculaire 3D")
        print("\nDéfinition de l'axe:")
        print("  --axe fichier   - Fichier texte avec points PM,X,Y,Z")
        print("  (par défaut)    - Utilise l'axe BURE GRE codé dans le script")
        print("\nExemples:")
        print('  python projection_inverse_hvpm_vers_xyz.py points_hvpm.csv')
        print('  python projection_inverse_hvpm_vers_xyz.py points_hvpm.csv resultat.csv')
        print('  python projection_inverse_hvpm_vers_xyz.py points_hvpm.csv resultat.csv vertical --axe mon_axe.txt\n')
        sys.exit(1)
    
    fichier_entree = sys.argv[1]
    fichier_sortie = None
    mode = 'vertical'  # Mode par défaut
    fichier_axe = None
    
    # Parser les arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--axe':
            if i + 1 < len(sys.argv):
                fichier_axe = sys.argv[i + 1]
                i += 2
            else:
                print("ERREUR: --axe nécessite un nom de fichier")
                sys.exit(1)
        elif arg.lower() in ['vertical', 'perpendiculaire']:
            mode = arg.lower()
            i += 1
        elif fichier_sortie is None and not arg.startswith('--'):
            fichier_sortie = arg
            i += 1
        else:
            print(f"ERREUR: Argument inconnu '{arg}'")
            sys.exit(1)
    
    # Fichier de sortie par défaut
    if fichier_sortie is None:
        path_entree = Path(fichier_entree)
        fichier_sortie = path_entree.parent / f"{path_entree.stem}_XYZ.csv"
    
    # Vérifier que le fichier d'entrée existe
    if not Path(fichier_entree).exists():
        print(f"\nERREUR: Le fichier '{fichier_entree}' n'existe pas!")
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
        
        # Charger les points de l'axe
        points_axe = charger_points_axe(fichier_axe)
        
        traiter_fichier(fichier_entree, fichier_sortie, points_axe, mode)
        
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
