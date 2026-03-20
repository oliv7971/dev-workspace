import re
from collections import defaultdict
import math

# Lire le fichier
with open('carnet/GHA-auscultation 251201-E.geo', 'r', encoding='latin-1') as f:
    lignes = f.readlines()

# Extraire les mesures par station
mesures_par_station = defaultdict(lambda: defaultdict(list))
station_actuelle = None

for ligne in lignes:
    # Détecter changement de station
    if 'Station' in ligne and not 'Mesure' in ligne:
        match = re.match(r'\d+\s+Station\s+(\S+)', ligne)
        if match:
            station_actuelle = match.group(1)
    
    # Extraire les mesures
    if 'Mesure' in ligne and station_actuelle:
        match = re.match(r'\S+\s+Mesure\s+(\S+)\s+\S+\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', ligne)
        if match:
            point = match.group(1)
            hz = float(match.group(2))
            v = float(match.group(3))
            dist = float(match.group(4))
            
            mesures_par_station[station_actuelle][point].append({
                'hz': hz,
                'v': v,
                'dist': dist
            })

# Analyser les incohérences
print("=" * 100)
print("ANALYSE DES INCOHÉRENCES PAR STATION")
print("=" * 100)

seuil_hz_gon = 0.005  # 5 mgon
seuil_v_gon = 0.005   # 5 mgon
seuil_dist_m = 0.005  # 5mm

for station in sorted(mesures_par_station.keys()):
    print(f"\n{'='*100}")
    print(f"STATION {station}")
    print(f"{'='*100}")
    
    points_avec_problemes = []
    points_ok = []
    
    for point, mesures in sorted(mesures_par_station[station].items()):
        if len(mesures) < 2:
            continue
        
        # Calculer moyennes et écarts
        hz_moy = sum(m['hz'] for m in mesures) / len(mesures)
        v_moy = sum(m['v'] for m in mesures) / len(mesures)
        dist_moy = sum(m['dist'] for m in mesures) / len(mesures)
        
        # Calculer écarts max
        hz_ecart_max = max(abs(m['hz'] - hz_moy) for m in mesures)
        v_ecart_max = max(abs(m['v'] - v_moy) for m in mesures)
        dist_ecart_max = max(abs(m['dist'] - dist_moy) for m in mesures)
        
        # Vérifier si problème
        probleme = False
        messages = []
        
        if hz_ecart_max > seuil_hz_gon:
            probleme = True
            messages.append(f"Hz: ±{hz_ecart_max:.4f} gon")
        
        if v_ecart_max > seuil_v_gon:
            probleme = True
            messages.append(f"V: ±{v_ecart_max:.4f} gon")
        
        if dist_ecart_max > seuil_dist_m:
            probleme = True
            messages.append(f"D: ±{dist_ecart_max*1000:.1f} mm")
        
        if probleme:
            points_avec_problemes.append((point, mesures, hz_ecart_max, v_ecart_max, dist_ecart_max, messages))
        else:
            points_ok.append(point)
    
    # Afficher les points avec problèmes
    if points_avec_problemes:
        print(f"\n⚠️  {len(points_avec_problemes)} POINT(S) AVEC ÉCARTS SIGNIFICATIFS :")
        print("-" * 100)
        
        for point, mesures, hz_ecart, v_ecart, dist_ecart, messages in points_avec_problemes:
            print(f"\n  {point} ({len(mesures)} mesures) - Écarts : {' | '.join(messages)}")
            
            hz_moy = sum(m['hz'] for m in mesures) / len(mesures)
            v_moy = sum(m['v'] for m in mesures) / len(mesures)
            dist_moy = sum(m['dist'] for m in mesures) / len(mesures)
            
            print(f"    Moyennes : Hz={hz_moy:10.4f} gon  V={v_moy:9.4f} gon  D={dist_moy:8.3f} m")
            
            for i, m in enumerate(mesures, 1):
                dhz = m['hz'] - hz_moy
                dv = m['v'] - v_moy
                dd = m['dist'] - dist_moy
                
                symbole = "⚠️ " if abs(dhz) > seuil_hz_gon or abs(dv) > seuil_v_gon or abs(dd) > seuil_dist_m else "  "
                print(f"      {symbole}Mes.{i}: Hz={m['hz']:10.4f} ({dhz:+7.4f})  "
                      f"V={m['v']:9.4f} ({dv:+7.4f})  D={m['dist']:8.3f} ({dd*1000:+6.1f}mm)")
    
    # Résumé
    if points_ok:
        print(f"\n✓ {len(points_ok)} point(s) cohérent(s) (écarts < seuils)")
    
    nb_total = len(points_avec_problemes) + len(points_ok)
    if nb_total > 0:
        print(f"\nRésumé station {station}: {len(points_avec_problemes)} problème(s) / {nb_total} points multi-mesurés")

print(f"\n{'='*100}")
print(f"Seuils utilisés : Hz ±{seuil_hz_gon*1000:.0f} mgon | V ±{seuil_v_gon*1000:.0f} mgon | D ±{seuil_dist_m*1000:.0f} mm")
print(f"{'='*100}")
