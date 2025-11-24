import re

def analyser_suffixes(fichier_geo):
    """
    Analyse les points avec des suffixes numériques auto-incrémentés
    pour identifier ceux qui ont les mêmes angles (duplicatas à nettoyer)
    """
    
    with open(fichier_geo, 'r', encoding='latin-1') as f:
        lignes = f.readlines()
    
    # Extraire les mesures
    mesures = []
    for i, ligne in enumerate(lignes, 1):
        match = re.match(r'(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', ligne)
        if match:
            nom = match.group(1)
            hz = float(match.group(2))
            v = float(match.group(3))
            dist = float(match.group(4))
            mesures.append({
                'ligne': i,
                'nom': nom,
                'hz': hz,
                'v': v,
                'distance': dist
            })
    
    # Grouper par angles identiques
    groupes_angles = {}
    tolerance_angle = 0.5  # gon
    tolerance_dist = 0.3   # m
    precision = 0.1
    
    for mesure in mesures:
        hz_round = round(mesure['hz'] / precision) * precision
        v_round = round(mesure['v'] / precision) * precision
        d_round = round(mesure['distance'] / precision) * precision
        
        cle = (hz_round, v_round, d_round)
        
        if cle not in groupes_angles:
            groupes_angles[cle] = []
        groupes_angles[cle].append(mesure)
    
    # Identifier les séries avec suffixes numériques
    series_suffixes = {}
    pattern_suffixe = re.compile(r'^(.+?)\.(\d+)$')
    
    for cle, groupe in groupes_angles.items():
        if len(groupe) >= 2:
            noms = set(m['nom'] for m in groupe)
            
            # Chercher des patterns avec suffixes numériques (pas forcément consécutifs)
            noms_base = {}
            for nom in noms:
                match = pattern_suffixe.match(nom)
                if match:
                    base = match.group(1)
                    suffixe = int(match.group(2))
                    if base not in noms_base:
                        noms_base[base] = []
                    noms_base[base].append((suffixe, nom))
            
            # Si on a au moins 2 noms avec la même base, c'est une série
            for base, suffixes in noms_base.items():
                if len(suffixes) >= 2:
                    suffixes.sort()
                    
                    if base not in series_suffixes:
                        series_suffixes[base] = []
                    
                    series_suffixes[base].append({
                        'hz': cle[0],
                        'v': cle[1],
                        'd': cle[2],
                        'noms': [s[1] for s in suffixes],
                        'mesures': [m for m in groupe if m['nom'] in [s[1] for s in suffixes]]
                    })
    
    return series_suffixes, groupes_angles

def afficher_series(series_suffixes):
    """
    Affiche les séries de points avec suffixes à nettoyer
    """
    print("=" * 80)
    print("POINTS AVEC SUFFIXES AUTO-INCRÉMENTÉS À NETTOYER")
    print("=" * 80)
    print()
    
    if not series_suffixes:
        print("Aucune série de suffixes détectée.")
        return
    
    compteur_total = 0
    
    for base in sorted(series_suffixes.keys()):
        series = series_suffixes[base]
        print(f"\n{'=' * 80}")
        print(f"BASE: {base}")
        print(f"{'=' * 80}")
        
        for i, serie in enumerate(series, 1):
            noms = serie['noms']
            mesures = serie['mesures']
            
            print(f"\nSérie {i}: {len(noms)} variantes avec {len(mesures)} mesures")
            print(f"  Angles: Hz≈{serie['hz']:.2f}° V≈{serie['v']:.2f}° D≈{serie['d']:.2f}m")
            print(f"  Noms trouvés: {', '.join(sorted(noms))}")
            print(f"  → Suggestion: Renommer tous en '{base}'")
            
            print(f"\n  Détail des mesures:")
            for m in sorted(mesures, key=lambda x: x['ligne']):
                print(f"    Ligne {m['ligne']:4d}: {m['nom']:20s} Hz={m['hz']:.4f}° V={m['v']:.4f}° D={m['distance']:.3f}m")
            
            compteur_total += len([n for n in noms if '.' in n])
    
    print("\n" + "=" * 80)
    print(f"RÉSUMÉ: {len(series_suffixes)} bases de noms avec suffixes")
    print(f"Nombre total de noms avec suffixes à renommer: {compteur_total}")
    print("=" * 80)

def generer_script_renommage(series_suffixes, fichier_source, fichier_cible):
    """
    Génère un script de renommage pour supprimer les suffixes
    """
    
    # Construire le dictionnaire de renommage
    renommages = {}
    for base, series in series_suffixes.items():
        for serie in series:
            for nom in serie['noms']:
                if '.' in nom:  # Si c'est un nom avec suffixe
                    renommages[nom] = base
    
    if not renommages:
        print("Aucun renommage nécessaire.")
        return
    
    # Générer le script
    script = f"""import re

def renommer_suffixes(fichier_source, fichier_cible):
    \"\"\"
    Supprime les suffixes auto-incrémentés des noms de points
    \"\"\"
    
    # Dictionnaire de renommage
    renommages = {{
"""
    
    for ancien, nouveau in sorted(renommages.items()):
        script += f"        '{ancien}': '{nouveau}',\n"
    
    script += """    }
    
    with open(fichier_source, 'r', encoding='latin-1') as f:
        contenu = f.read()
    
    # Compteur de remplacements
    compteurs = {nom: 0 for nom in renommages.keys()}
    
    # Effectuer les remplacements
    for ancien, nouveau in renommages.items():
        pattern = r'\\b' + re.escape(ancien) + r'\\b'
        occurrences = len(re.findall(pattern, contenu))
        if occurrences > 0:
            contenu = re.sub(pattern, nouveau, contenu)
            compteurs[ancien] = occurrences
            print(f"{ancien:20s} → {nouveau:20s} : {occurrences:3d} remplacements")
    
    # Sauvegarder
    with open(fichier_cible, 'w', encoding='latin-1') as f:
        f.write(contenu)
    
    total = sum(compteurs.values())
    nb_points = len([c for c in compteurs.values() if c > 0])
    print(f"\\nTotal: {nb_points} points renommés, {total} remplacements effectués")
    print(f"Fichier sauvegardé: {fichier_cible}")

if __name__ == "__main__":
    renommer_suffixes('""" + fichier_source + """', '""" + fichier_cible + """')
"""
    
    with open('renommer_suffixes.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"\nScript généré: renommer_suffixes.py")
    print(f"  {len(renommages)} points à renommer")
    print(f"  Source: {fichier_source}")
    print(f"  Cible: {fichier_cible}")

if __name__ == "__main__":
    fichier = "POLYGCR-251121-E.geo"
    
    print("Analyse des suffixes auto-incrémentés...")
    series_suffixes, groupes_angles = analyser_suffixes(fichier)
    
    afficher_series(series_suffixes)
    
    # Générer le script de renommage
    fichier_cible = fichier.replace('-E.geo', '-F.geo')
    generer_script_renommage(series_suffixes, fichier, fichier_cible)
