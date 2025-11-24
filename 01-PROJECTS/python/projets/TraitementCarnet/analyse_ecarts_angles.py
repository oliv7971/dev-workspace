import re
from collections import defaultdict
import math

def analyser_ecarts(fichier_geo):
    """
    Analyse les écarts d'angles pour chaque point
    pour détecter les mesures aberrantes
    """
    
    with open(fichier_geo, 'r', encoding='latin-1') as f:
        lignes = f.readlines()
    
    # Extraire les mesures
    mesures_par_point = defaultdict(list)
    
    for i, ligne in enumerate(lignes, 1):
        match = re.match(r'(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', ligne)
        if match:
            nom = match.group(1)
            hz = float(match.group(2))
            v = float(match.group(3))
            dist = float(match.group(4))
            
            mesures_par_point[nom].append({
                'ligne': i,
                'hz': hz,
                'v': v,
                'distance': dist
            })
    
    # Analyser les écarts pour chaque point
    points_avec_ecarts = []
    
    for nom, mesures in mesures_par_point.items():
        if len(mesures) < 2:
            continue
        
        # Calculer les statistiques
        hz_values = [m['hz'] for m in mesures]
        v_values = [m['v'] for m in mesures]
        d_values = [m['distance'] for m in mesures]
        
        # Écarts max/min (en valeur absolue, sans tenir compte des 200 gons)
        hz_min, hz_max = min(hz_values), max(hz_values)
        v_min, v_max = min(v_values), max(v_values)
        d_min, d_max = min(d_values), max(d_values)
        
        # Écart brut
        ecart_hz_brut = hz_max - hz_min
        ecart_v_brut = v_max - v_min
        ecart_d = d_max - d_min
        
        # Détecter si on a des mesures en Face I et Face II (différence ~200 gons)
        # Si oui, regrouper par face et analyser séparément
        tolerance_face = 190  # Pour détecter les faces I/II (différence ~200 gons)
        
        # Tenter de regrouper par face
        faces = []
        for m in mesures:
            trouve = False
            for face in faces:
                # Si Hz est proche (< 10 gons) d'une mesure de cette face
                if any(abs(m['hz'] - mf['hz']) < 10 or abs(abs(m['hz'] - mf['hz']) - 200) < 10 for mf in face):
                    face.append(m)
                    trouve = True
                    break
            if not trouve:
                faces.append([m])
        
        # Si on a plusieurs faces distinctes, analyser chaque face séparément
        if len(faces) > 1:
            # Analyser les écarts dans chaque face
            ecarts_par_face = []
            for i, face in enumerate(faces):
                if len(face) < 2:
                    continue
                hz_face = [m['hz'] for m in face]
                v_face = [m['v'] for m in face]
                d_face = [m['distance'] for m in face]
                
                ecart_hz_face = max(hz_face) - min(hz_face)
                ecart_v_face = max(v_face) - min(v_face)
                ecart_d_face = max(d_face) - min(d_face)
                
                ecarts_par_face.append({
                    'face': i + 1,
                    'nb_mesures': len(face),
                    'ecart_hz': ecart_hz_face,
                    'ecart_v': ecart_v_face,
                    'ecart_d': ecart_d_face
                })
            
            # Prendre le max des écarts par face
            ecart_hz = max(f['ecart_hz'] for f in ecarts_par_face)
            ecart_v = max(f['ecart_v'] for f in ecarts_par_face)
        else:
            ecart_hz = ecart_hz_brut
            ecart_v = ecart_v_brut
        
        # Moyenne et écart-type
        hz_moy = sum(hz_values) / len(hz_values)
        v_moy = sum(v_values) / len(v_values)
        d_moy = sum(d_values) / len(d_values)
        
        # Écart-type
        if len(mesures) > 1:
            hz_std = math.sqrt(sum((x - hz_moy)**2 for x in hz_values) / len(hz_values))
            v_std = math.sqrt(sum((x - v_moy)**2 for x in v_values) / len(v_values))
            d_std = math.sqrt(sum((x - d_moy)**2 for x in d_values) / len(d_values))
        else:
            hz_std = 0
            v_std = 0
            d_std = 0
        
        # Détecter les mesures aberrantes (> 2 écart-types)
        mesures_aberrantes = []
        for m in mesures:
            ecart_hz_sigma = abs(m['hz'] - hz_moy) / hz_std if hz_std > 0 else 0
            ecart_v_sigma = abs(m['v'] - v_moy) / v_std if v_std > 0 else 0
            ecart_d_sigma = abs(m['distance'] - d_moy) / d_std if d_std > 0 else 0
            
            if ecart_hz_sigma > 2 or ecart_v_sigma > 2 or ecart_d_sigma > 2:
                mesures_aberrantes.append({
                    'mesure': m,
                    'ecart_hz_sigma': ecart_hz_sigma,
                    'ecart_v_sigma': ecart_v_sigma,
                    'ecart_d_sigma': ecart_d_sigma
                })
        
        # Seuil d'alerte : écart Hz ou V > 0.003 gon (= 0.003 grade) ou distance > 3mm
        seuil_hz = 0.003  # gon
        seuil_v = 0.003   # gon
        seuil_d = 0.003   # m
        
        if ecart_hz > seuil_hz or ecart_v > seuil_v or ecart_d > seuil_d or mesures_aberrantes:
            points_avec_ecarts.append({
                'nom': nom,
                'nb_mesures': len(mesures),
                'ecart_hz': ecart_hz,
                'ecart_v': ecart_v,
                'ecart_d': ecart_d,
                'hz_moy': hz_moy,
                'v_moy': v_moy,
                'd_moy': d_moy,
                'hz_std': hz_std,
                'v_std': v_std,
                'd_std': d_std,
                'mesures': mesures,
                'mesures_aberrantes': mesures_aberrantes
            })
    
    return points_avec_ecarts

def afficher_ecarts(points_avec_ecarts):
    """
    Affiche les points avec écarts significatifs
    """
    
    # Trier par écart Hz décroissant
    points_avec_ecarts.sort(key=lambda x: x['ecart_hz'], reverse=True)
    
    print("=" * 100)
    print("ANALYSE DES ÉCARTS D'ANGLES PAR POINT")
    print("=" * 100)
    print(f"\n{len(points_avec_ecarts)} points avec écarts détectés\n")
    
    # Seuils d'alerte
    seuil_alerte_hz = 0.003  # gon
    seuil_alerte_v = 0.003   # gon
    seuil_alerte_d = 0.003   # m
    
    points_critiques = []
    
    for point in points_avec_ecarts:
        # Déterminer le niveau de criticité
        critique = False
        if point['ecart_hz'] > seuil_alerte_hz or point['ecart_v'] > seuil_alerte_v or point['ecart_d'] > seuil_alerte_d:
            critique = True
            points_critiques.append(point)
        
        if critique or point['mesures_aberrantes']:
            print(f"\n{'⚠️  ' if critique else ''}Point: {point['nom']}")
            print(f"  Nombre de mesures: {point['nb_mesures']}")
            print(f"  Écarts: Hz=±{point['ecart_hz']:.4f}° V=±{point['ecart_v']:.4f}° D=±{point['ecart_d']:.3f}m")
            print(f"  Moyennes: Hz={point['hz_moy']:.4f}° V={point['v_moy']:.4f}° D={point['d_moy']:.3f}m")
            print(f"  Écart-type: Hz=±{point['hz_std']:.4f}° V=±{point['v_std']:.4f}° D=±{point['d_std']:.3f}m")
            
            if point['mesures_aberrantes']:
                print(f"\n  ⚠️  {len(point['mesures_aberrantes'])} mesure(s) aberrante(s) détectée(s):")
                for ab in point['mesures_aberrantes']:
                    m = ab['mesure']
                    print(f"    Ligne {m['ligne']:4d}: Hz={m['hz']:.4f}° V={m['v']:.4f}° D={m['distance']:.3f}m")
                    print(f"      → Écarts: {ab['ecart_hz_sigma']:.1f}σ (Hz), {ab['ecart_v_sigma']:.1f}σ (V), {ab['ecart_d_sigma']:.1f}σ (D)")
            
            print(f"\n  Détail des mesures:")
            for m in point['mesures']:
                ecart_hz = m['hz'] - point['hz_moy']
                ecart_v = m['v'] - point['v_moy']
                ecart_d = m['distance'] - point['d_moy']
                print(f"    Ligne {m['ligne']:4d}: Hz={m['hz']:.4f}° (Δ{ecart_hz:+.4f}°) V={m['v']:.4f}° (Δ{ecart_v:+.4f}°) D={m['distance']:.3f}m (Δ{ecart_d:+.3f}m)")
    
    print("\n" + "=" * 100)
    print(f"RÉSUMÉ:")
    print(f"  Points analysés: {len(points_avec_ecarts)}")
    print(f"  Points critiques (écarts > seuils): {len(points_critiques)}")
    print(f"  Seuils: Hz=±{seuil_alerte_hz}° V=±{seuil_alerte_v}° D=±{seuil_alerte_d}m")
    print("=" * 100)

if __name__ == "__main__":
    fichier = "POLYGCR-251121-L.geo"
    
    print(f"Analyse des écarts d'angles dans {fichier}...\n")
    points_avec_ecarts = analyser_ecarts(fichier)
    afficher_ecarts(points_avec_ecarts)
