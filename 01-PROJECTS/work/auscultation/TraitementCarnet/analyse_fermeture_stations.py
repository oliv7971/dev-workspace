import re
from collections import defaultdict
import math

def analyser_fermeture_stations(fichier_geo):
    """
    Analyse la fermeture des stations et les écarts sur chaque cible
    """
    
    with open(fichier_geo, 'r', encoding='latin-1') as f:
        lignes = f.readlines()
    
    # Extraire les stations et leurs mesures
    station_courante = None
    stations = defaultdict(lambda: {'nom': None, 'timestamp': None, 'mesures': defaultdict(list)})
    station_index = 0
    
    for i, ligne in enumerate(lignes, 1):
        # Détecter une nouvelle station
        match_station = re.search(r'Station\s+(\S+)', ligne)
        if match_station:
            station_index += 1
            station_courante = station_index
            stations[station_courante]['nom'] = match_station.group(1)
            stations[station_courante]['ligne_debut'] = i
            continue
        
        # Extraire les mesures (nom cible + 3 ou 4 valeurs numériques)
        if station_courante:
            match_mesure = re.match(r'\S+\s+Mesure\s+(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', ligne)
            if match_mesure:
                nom = match_mesure.group(1)
                hz = float(match_mesure.group(3))
                v = float(match_mesure.group(4))
                dist = float(match_mesure.group(5))
                
                stations[station_courante]['mesures'][nom].append({
                    'ligne': i,
                    'hz': hz,
                    'v': v,
                    'distance': dist
                })
    
    return stations

def calculer_fermeture(mesures):
    """
    Calcule la fermeture angulaire entre première et dernière mesure
    """
    if len(mesures) < 2:
        return None
    
    premiere = mesures[0]
    derniere = mesures[-1]
    
    # Écarts angulaires (en tenant compte des 400 gons)
    ecart_hz = derniere['hz'] - premiere['hz']
    ecart_v = derniere['v'] - premiere['v']
    ecart_d = derniere['distance'] - premiere['distance']
    
    # Normaliser les écarts Hz entre -200 et +200 gons
    while ecart_hz > 200:
        ecart_hz -= 400
    while ecart_hz < -200:
        ecart_hz += 400
    
    return {
        'ecart_hz': ecart_hz,
        'ecart_v': ecart_v,
        'ecart_d': ecart_d,
        'premiere_ligne': premiere['ligne'],
        'derniere_ligne': derniere['ligne'],
        'nb_mesures': len(mesures)
    }

def calculer_statistiques_cible(mesures):
    """
    Calcule les statistiques (min, max, moyenne, écart-type) pour une cible
    """
    if len(mesures) < 2:
        return None
    
    hz_values = [m['hz'] for m in mesures]
    v_values = [m['v'] for m in mesures]
    d_values = [m['distance'] for m in mesures]
    
    # Statistiques de base
    stats = {
        'nb_mesures': len(mesures),
        'hz_min': min(hz_values),
        'hz_max': max(hz_values),
        'hz_moy': sum(hz_values) / len(hz_values),
        'v_min': min(v_values),
        'v_max': max(v_values),
        'v_moy': sum(v_values) / len(v_values),
        'd_min': min(d_values),
        'd_max': max(d_values),
        'd_moy': sum(d_values) / len(d_values),
    }
    
    # Écarts
    stats['ecart_hz'] = stats['hz_max'] - stats['hz_min']
    stats['ecart_v'] = stats['v_max'] - stats['v_min']
    stats['ecart_d'] = stats['d_max'] - stats['d_min']
    
    # Écart-type
    if len(mesures) > 1:
        stats['hz_std'] = math.sqrt(sum((x - stats['hz_moy'])**2 for x in hz_values) / len(hz_values))
        stats['v_std'] = math.sqrt(sum((x - stats['v_moy'])**2 for x in v_values) / len(v_values))
        stats['d_std'] = math.sqrt(sum((x - stats['d_moy'])**2 for x in d_values) / len(d_values))
    else:
        stats['hz_std'] = 0
        stats['v_std'] = 0
        stats['d_std'] = 0
    
    # Détecter les mesures aberrantes (> 2 sigma)
    stats['mesures_aberrantes'] = []
    for m in mesures:
        ecart_hz_sigma = abs(m['hz'] - stats['hz_moy']) / stats['hz_std'] if stats['hz_std'] > 0 else 0
        ecart_v_sigma = abs(m['v'] - stats['v_moy']) / stats['v_std'] if stats['v_std'] > 0 else 0
        ecart_d_sigma = abs(m['distance'] - stats['d_moy']) / stats['d_std'] if stats['d_std'] > 0 else 0
        
        if ecart_hz_sigma > 2 or ecart_v_sigma > 2 or ecart_d_sigma > 2:
            stats['mesures_aberrantes'].append({
                'ligne': m['ligne'],
                'hz': m['hz'],
                'v': m['v'],
                'd': m['distance'],
                'ecart_hz_sigma': ecart_hz_sigma,
                'ecart_v_sigma': ecart_v_sigma,
                'ecart_d_sigma': ecart_d_sigma
            })
    
    return stats

def afficher_rapport(stations):
    """
    Affiche le rapport complet d'analyse
    """
    
    print("=" * 100)
    print("RAPPORT D'ANALYSE DE FERMETURE DES STATIONS")
    print("=" * 100)
    
    seuil_fermeture_hz = 0.005  # gon
    seuil_fermeture_v = 0.005   # gon
    seuil_fermeture_d = 0.005   # m
    
    seuil_ecart_hz = 0.003  # gon
    seuil_ecart_v = 0.003   # gon
    seuil_ecart_d = 0.003   # m
    
    for station_id, station_data in sorted(stations.items()):
        print(f"\n{'=' * 100}")
        print(f"STATION {station_id} - {station_data['nom']}")
        print(f"{'=' * 100}")
        
        nb_cibles = len(station_data['mesures'])
        nb_mesures_total = sum(len(mesures) for mesures in station_data['mesures'].values())
        
        print(f"\nNombre de cibles : {nb_cibles}")
        print(f"Nombre total de mesures : {nb_mesures_total}")
        
        # 1. Analyse de fermeture
        print(f"\n{'-' * 100}")
        print("1. FERMETURE ANGULAIRE (première vs dernière mesure)")
        print(f"{'-' * 100}")
        
        fermetures_critiques = []
        
        for cible, mesures in sorted(station_data['mesures'].items()):
            fermeture = calculer_fermeture(mesures)
            if fermeture and fermeture['nb_mesures'] >= 2:
                critique = (abs(fermeture['ecart_hz']) > seuil_fermeture_hz or 
                           abs(fermeture['ecart_v']) > seuil_fermeture_v or 
                           abs(fermeture['ecart_d']) > seuil_fermeture_d)
                
                if critique:
                    fermetures_critiques.append((cible, fermeture))
        
        if fermetures_critiques:
            print(f"\n⚠️  {len(fermetures_critiques)} cible(s) avec fermeture > seuils :")
            for cible, fermeture in fermetures_critiques:
                print(f"\n  {cible} ({fermeture['nb_mesures']} mesures)")
                print(f"    Lignes {fermeture['premiere_ligne']} → {fermeture['derniere_ligne']}")
                print(f"    Écarts : Hz={fermeture['ecart_hz']:+.4f}° V={fermeture['ecart_v']:+.4f}° D={fermeture['ecart_d']:+.4f}m")
        else:
            print(f"\n✓ Toutes les fermetures sont dans les seuils (Hz≤{seuil_fermeture_hz}° V≤{seuil_fermeture_v}° D≤{seuil_fermeture_d}m)")
        
        # 2. Analyse des écarts par cible
        print(f"\n{'-' * 100}")
        print("2. ÉCARTS PAR CIBLE (statistiques sur l'ensemble des mesures)")
        print(f"{'-' * 100}")
        
        cibles_avec_ecarts = []
        cibles_avec_aberrations = []
        
        for cible, mesures in sorted(station_data['mesures'].items()):
            stats = calculer_statistiques_cible(mesures)
            if stats:
                critique = (stats['ecart_hz'] > seuil_ecart_hz or 
                           stats['ecart_v'] > seuil_ecart_v or 
                           stats['ecart_d'] > seuil_ecart_d)
                
                if critique or stats['mesures_aberrantes']:
                    cibles_avec_ecarts.append((cible, stats))
                    if stats['mesures_aberrantes']:
                        cibles_avec_aberrations.append((cible, stats))
        
        if cibles_avec_ecarts:
            print(f"\n⚠️  {len(cibles_avec_ecarts)} cible(s) avec écarts significatifs :")
            for cible, stats in cibles_avec_ecarts:
                print(f"\n  {cible} ({stats['nb_mesures']} mesures)")
                print(f"    Écarts : Hz=±{stats['ecart_hz']:.4f}° V=±{stats['ecart_v']:.4f}° D=±{stats['ecart_d']:.3f}m")
                print(f"    Moyennes : Hz={stats['hz_moy']:.4f}° V={stats['v_moy']:.4f}° D={stats['d_moy']:.3f}m")
                print(f"    Écart-type : Hz=±{stats['hz_std']:.4f}° V=±{stats['v_std']:.4f}° D=±{stats['d_std']:.3f}m")
                
                if stats['mesures_aberrantes']:
                    print(f"\n    ⚠️  {len(stats['mesures_aberrantes'])} mesure(s) aberrante(s) (> 2σ) :")
                    for ab in stats['mesures_aberrantes']:
                        print(f"      Ligne {ab['ligne']}: Hz={ab['hz']:.4f}° V={ab['v']:.4f}° D={ab['d']:.3f}m")
                        print(f"        → Écarts: {ab['ecart_hz_sigma']:.1f}σ (Hz), {ab['ecart_v_sigma']:.1f}σ (V), {ab['ecart_d_sigma']:.1f}σ (D)")
        else:
            print(f"\n✓ Tous les écarts sont dans les seuils (Hz≤{seuil_ecart_hz}° V≤{seuil_ecart_v}° D≤{seuil_ecart_d}m)")
        
        # Résumé de la station
        print(f"\n{'-' * 100}")
        print(f"RÉSUMÉ STATION {station_id}:")
        print(f"  Fermetures critiques : {len(fermetures_critiques)}/{nb_cibles}")
        print(f"  Cibles avec écarts : {len(cibles_avec_ecarts)}/{nb_cibles}")
        print(f"  Cibles avec aberrations : {len(cibles_avec_aberrations)}/{nb_cibles}")
        print(f"{'-' * 100}")
    
    print("\n" + "=" * 100)
    print("FIN DU RAPPORT")
    print("=" * 100)

if __name__ == "__main__":
    fichier = "POLYGCR-251121-V.geo"
    
    print(f"Analyse du fichier {fichier}...\n")
    stations = analyser_fermeture_stations(fichier)
    afficher_rapport(stations)
