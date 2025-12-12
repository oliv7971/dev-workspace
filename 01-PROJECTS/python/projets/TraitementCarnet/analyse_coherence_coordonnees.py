import re
from collections import defaultdict
import math

def lire_coordonnees_geo(fichier_geo):
    """
    Lit les coordonnées depuis un fichier .geo Covadis
    Format: 000XXX  Point  NOM  3  X  Y  Z
    """
    
    coordonnees = defaultdict(list)
    
    with open(fichier_geo, 'r', encoding='latin-1') as f:
        for i, ligne in enumerate(f, 1):
            # Format Point avec coordonnées
            match = re.match(r'\S+\s+Point\s+(\S+)\s+3\s+([\d.-]+)\s+([\d.-]+)\s+([\d.-]+)', ligne)
            if match:
                nom = match.group(1)
                x = float(match.group(2))
                y = float(match.group(3))
                z = float(match.group(4))
                
                coordonnees[nom].append({
                    'ligne': i,
                    'x': x,
                    'y': y,
                    'z': z
                })
    
    return coordonnees

def lire_coordonnees_txt(fichier_txt):
    """
    Lit les coordonnées depuis un fichier texte
    Format: NOM X Y Z (séparés par espaces ou tabulations)
    """
    
    coordonnees = defaultdict(list)
    
    with open(fichier_txt, 'r', encoding='utf-8') as f:
        for i, ligne in enumerate(f, 1):
            ligne = ligne.strip()
            if not ligne or ligne.startswith('#'):
                continue
            
            # Essayer de parser: NOM X Y Z
            parties = ligne.split()
            if len(parties) >= 4:
                try:
                    nom = parties[0]
                    x = float(parties[1])
                    y = float(parties[2])
                    z = float(parties[3])
                    
                    coordonnees[nom].append({
                        'ligne': i,
                        'x': x,
                        'y': y,
                        'z': z
                    })
                except ValueError:
                    continue
    
    return coordonnees

def calculer_statistiques_point(coords):
    """
    Calcule les statistiques pour un point
    """
    
    if len(coords) == 0:
        return None
    
    if len(coords) == 1:
        return {
            'nb_obs': 1,
            'x_moy': coords[0]['x'],
            'y_moy': coords[0]['y'],
            'z_moy': coords[0]['z'],
            'x_std': 0,
            'y_std': 0,
            'z_std': 0,
            'ecart_3d_max': 0,
            'ecarts': []
        }
    
    # Moyennes
    x_moy = sum(c['x'] for c in coords) / len(coords)
    y_moy = sum(c['y'] for c in coords) / len(coords)
    z_moy = sum(c['z'] for c in coords) / len(coords)
    
    # Écarts-types
    x_std = math.sqrt(sum((c['x'] - x_moy)**2 for c in coords) / len(coords))
    y_std = math.sqrt(sum((c['y'] - y_moy)**2 for c in coords) / len(coords))
    z_std = math.sqrt(sum((c['z'] - z_moy)**2 for c in coords) / len(coords))
    
    # Écarts individuels
    ecarts = []
    ecart_3d_max = 0
    
    for c in coords:
        dx = c['x'] - x_moy
        dy = c['y'] - y_moy
        dz = c['z'] - z_moy
        ecart_3d = math.sqrt(dx**2 + dy**2 + dz**2)
        ecart_plani = math.sqrt(dx**2 + dy**2)
        
        ecarts.append({
            'ligne': c['ligne'],
            'dx': dx,
            'dy': dy,
            'dz': dz,
            'ecart_plani': ecart_plani,
            'ecart_3d': ecart_3d
        })
        
        ecart_3d_max = max(ecart_3d_max, ecart_3d)
    
    return {
        'nb_obs': len(coords),
        'x_moy': x_moy,
        'y_moy': y_moy,
        'z_moy': z_moy,
        'x_std': x_std,
        'y_std': y_std,
        'z_std': z_std,
        'ecart_3d_max': ecart_3d_max,
        'ecarts': ecarts
    }

def generer_rapport(coordonnees, seuil_plani_mm=3.0, seuil_alti_mm=3.0):
    """
    Génère un rapport d'analyse des coordonnées
    """
    
    seuil_plani = seuil_plani_mm / 1000.0  # Conversion mm -> m
    seuil_alti = seuil_alti_mm / 1000.0
    
    print("=" * 120)
    print("RAPPORT D'ANALYSE DE COHÉRENCE DES COORDONNÉES")
    print("=" * 120)
    print(f"\nSeuils d'alerte : Planimétrie ±{seuil_plani_mm:.1f}mm  |  Altimétrie ±{seuil_alti_mm:.1f}mm")
    print(f"\nNombre total de points : {len(coordonnees)}")
    
    points_avec_ecarts = []
    points_ok = []
    
    for nom, coords in sorted(coordonnees.items()):
        stats = calculer_statistiques_point(coords)
        
        if stats['nb_obs'] == 1:
            points_ok.append(nom)
            continue
        
        # Vérifier si des écarts dépassent les seuils
        critique = False
        for ecart in stats['ecarts']:
            if ecart['ecart_plani'] > seuil_plani or abs(ecart['dz']) > seuil_alti:
                critique = True
                break
        
        if critique or stats['ecart_3d_max'] > seuil_plani:
            points_avec_ecarts.append((nom, stats))
        else:
            points_ok.append(nom)
    
    # Afficher les points avec écarts
    if points_avec_ecarts:
        print(f"\n{'=' * 120}")
        print(f"⚠️  {len(points_avec_ecarts)} POINT(S) AVEC ÉCARTS SIGNIFICATIFS")
        print(f"{'=' * 120}")
        
        for nom, stats in points_avec_ecarts:
            print(f"\n{nom} - {stats['nb_obs']} observations")
            print(f"  Coordonnées moyennes : X={stats['x_moy']:.4f}m  Y={stats['y_moy']:.4f}m  Z={stats['z_moy']:.4f}m")
            print(f"  Écart-type : σX=±{stats['x_std']*1000:.2f}mm  σY=±{stats['y_std']*1000:.2f}mm  σZ=±{stats['z_std']*1000:.2f}mm")
            print(f"  Écart 3D max : {stats['ecart_3d_max']*1000:.2f}mm")
            
            print(f"\n  Détail des écarts à la moyenne :")
            for ecart in stats['ecarts']:
                symbole = "⚠️ " if ecart['ecart_plani'] > seuil_plani or abs(ecart['dz']) > seuil_alti else "  "
                print(f"    {symbole}Ligne {ecart['ligne']:4d}: "
                      f"ΔX={ecart['dx']*1000:+6.2f}mm  ΔY={ecart['dy']*1000:+6.2f}mm  ΔZ={ecart['dz']*1000:+6.2f}mm  "
                      f"Δplani={ecart['ecart_plani']*1000:5.2f}mm  Δ3D={ecart['ecart_3d']*1000:5.2f}mm")
    
    # Résumé des points OK
    if points_ok:
        print(f"\n{'=' * 120}")
        print(f"✓ {len(points_ok)} POINT(S) AVEC COORDONNÉES COHÉRENTES")
        print(f"{'=' * 120}")
        
        # Afficher les statistiques pour ces points aussi
        for nom in points_ok:
            stats = calculer_statistiques_point(coordonnees[nom])
            if stats['nb_obs'] > 1:
                print(f"\n{nom} - {stats['nb_obs']} observations")
                print(f"  Moyennes : X={stats['x_moy']:.4f}m  Y={stats['y_moy']:.4f}m  Z={stats['z_moy']:.4f}m")
                print(f"  Écart-type : σX=±{stats['x_std']*1000:.2f}mm  σY=±{stats['y_std']*1000:.2f}mm  σZ=±{stats['z_std']*1000:.2f}mm")
                print(f"  Écart 3D max : {stats['ecart_3d_max']*1000:.2f}mm")
    
    # Résumé global
    print(f"\n{'=' * 120}")
    print("RÉSUMÉ GLOBAL")
    print(f"{'=' * 120}")
    print(f"  Total points analysés : {len(coordonnees)}")
    print(f"  Points avec écarts > seuils : {len(points_avec_ecarts)}")
    print(f"  Points cohérents : {len(points_ok)}")
    print(f"{'=' * 120}")

def generer_fichier_moyennes(coordonnees, fichier_sortie):
    """
    Génère un fichier avec les coordonnées moyennes
    """
    
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        f.write("# Coordonnées moyennes\n")
        f.write("# Format: NOM X Y Z NB_OBS ECART_3D_MAX(mm)\n")
        f.write("#\n")
        
        for nom, coords in sorted(coordonnees.items()):
            stats = calculer_statistiques_point(coords)
            f.write(f"{nom:20s} {stats['x_moy']:12.4f} {stats['y_moy']:12.4f} {stats['z_moy']:10.4f} "
                   f"{stats['nb_obs']:3d} {stats['ecart_3d_max']*1000:6.2f}\n")
    
    print(f"\n✓ Fichier de coordonnées moyennes généré : {fichier_sortie}")

if __name__ == "__main__":
    # Configuration
    fichier_entree = "dat/20251124_GCR.xyz"  # Ou chemin vers fichier .txt/.xyz/.geo
    fichier_sortie = "dat/coordonnees_moyennes.txt"
    
    # Déterminer le type de fichier
    if fichier_entree.endswith('.geo'):
        print(f"Lecture du fichier GEO : {fichier_entree}")
        coordonnees = lire_coordonnees_geo(fichier_entree)
    else:
        print(f"Lecture du fichier XYZ/TXT : {fichier_entree}")
        coordonnees = lire_coordonnees_txt(fichier_entree)
    
    if not coordonnees:
        print("Aucune coordonnée trouvée dans le fichier")
    else:
        # Générer le rapport
        generer_rapport(coordonnees, seuil_plani_mm=3.0, seuil_alti_mm=3.0)
        
        # Générer le fichier de moyennes
        generer_fichier_moyennes(coordonnees, fichier_sortie)
