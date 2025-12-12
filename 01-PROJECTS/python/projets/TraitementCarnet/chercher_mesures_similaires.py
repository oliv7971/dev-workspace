import re

def trouver_mesures_similaires(fichier_geo, cible, tolerance_hz=2.0, tolerance_v=2.0, tolerance_d=0.5):
    """
    Trouve les mesures similaires à une cible donnée
    """
    
    with open(fichier_geo, 'r', encoding='latin-1') as f:
        lignes = f.readlines()
    
    # Trouver la mesure de la cible recherchée
    mesure_cible = None
    
    for i, ligne in enumerate(lignes, 1):
        match = re.match(r'\S+\s+Mesure\s+(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', ligne)
        if match:
            nom = match.group(1)
            if nom == cible:
                mesure_cible = {
                    'ligne': i,
                    'nom': nom,
                    'hz': float(match.group(3)),
                    'v': float(match.group(4)),
                    'distance': float(match.group(5))
                }
                break
    
    if not mesure_cible:
        print(f"Cible {cible} non trouvée dans le fichier")
        return
    
    print(f"Cible recherchée : {cible}")
    print(f"  Ligne {mesure_cible['ligne']}")
    print(f"  Hz={mesure_cible['hz']:.4f}° V={mesure_cible['v']:.4f}° D={mesure_cible['distance']:.3f}m")
    print(f"\nRecherche de mesures similaires (tolérance: Hz±{tolerance_hz}° V±{tolerance_v}° D±{tolerance_d}m)...\n")
    
    # Chercher toutes les mesures similaires
    mesures_similaires = []
    
    for i, ligne in enumerate(lignes, 1):
        match = re.match(r'\S+\s+Mesure\s+(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', ligne)
        if match:
            nom = match.group(1)
            hz = float(match.group(3))
            v = float(match.group(4))
            distance = float(match.group(5))
            
            # Calculer les écarts
            ecart_hz = abs(hz - mesure_cible['hz'])
            ecart_v = abs(v - mesure_cible['v'])
            ecart_d = abs(distance - mesure_cible['distance'])
            
            # Gérer les écarts Hz avec modulo 200 gons (face I/II)
            ecart_hz_face = min(ecart_hz, abs(ecart_hz - 200), abs(ecart_hz + 200))
            
            # Si dans les tolérances
            if ecart_hz_face <= tolerance_hz and ecart_v <= tolerance_v and ecart_d <= tolerance_d:
                mesures_similaires.append({
                    'ligne': i,
                    'nom': nom,
                    'hz': hz,
                    'v': v,
                    'distance': distance,
                    'ecart_hz': ecart_hz_face,
                    'ecart_v': ecart_v,
                    'ecart_d': ecart_d
                })
    
    # Afficher les résultats
    if len(mesures_similaires) <= 1:
        print("Aucune mesure similaire trouvée (à part la cible elle-même)")
    else:
        print(f"✓ {len(mesures_similaires)} mesure(s) similaire(s) trouvée(s) :\n")
        
        for m in mesures_similaires:
            if m['nom'] != cible:
                print(f"  {m['nom']:20s} (ligne {m['ligne']:4d})")
                print(f"    Hz={m['hz']:.4f}° V={m['v']:.4f}° D={m['distance']:.3f}m")
                print(f"    Écarts: ΔHz={m['ecart_hz']:.4f}° ΔV={m['ecart_v']:.4f}° ΔD={m['ecart_d']:.3f}m\n")

if __name__ == "__main__":
    fichier = "POLYGCR-251121-V.geo"
    cible = "A.LB.C056"
    
    trouver_mesures_similaires(fichier, cible, tolerance_hz=2.0, tolerance_v=2.0, tolerance_d=0.5)
