#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour séparer les alvéoles HA21-E1, HA21-E2 et HA21-E3
"""

import os
import shutil
import sys
from collections import defaultdict

BASE_PATH = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

ALVEOLES = {
    'HA21': 'ALVEOLE HA21',
    'E1': 'ALVEOLE HA21-E1',
    'E2': 'ALVEOLE HA21-E2',
    'E3': 'ALVEOLE HA21-E3'
}

def detecter_alveole(nom_dossier):
    """
    Détecte à quelle alvéole appartient un dossier selon son nom
    Retourne: 'E1', 'E2', 'E3', ou None (reste dans HA21 générique)
    
    Règles:
    - Si multi-alvéoles (1_2_3, E1_E2, etc.) -> None (reste dans HA21)
    - Si spécifique à une alvéole -> E1/E2/E3
    - Si ambigu ou générique HA21 -> None (reste dans HA21)
    """
    nom_upper = nom_dossier.upper()
    
    # Si multi-alvéoles, laisser dans HA21 générique
    if any(p in nom_upper for p in ['1_2_3', 'E1_E2', 'E2_E3', 'E1_E3', '1_2', '2_3', '1_3']):
        return None
    
    # Compter les mentions d'alvéoles
    mentions = {
        'E1': 0,
        'E2': 0,
        'E3': 0
    }
    
    # Patterns pour E3
    if any(p in nom_upper for p in ['HA21-E3', 'HA213', 'HA21-3', 'HA21E3']):
        mentions['E3'] += 1
    
    # Patterns pour E2
    if any(p in nom_upper for p in ['HA21-E2', 'HA212', 'HA21-2', 'HA21E2']):
        mentions['E2'] += 1
    
    # Patterns pour E1
    if any(p in nom_upper for p in ['HA21-E1', 'HA211', 'HA21-1', 'HA21E1']):
        mentions['E1'] += 1
    
    # Si une seule alvéole mentionnée, c'est clair
    total_mentions = sum(mentions.values())
    if total_mentions == 1:
        for alv, count in mentions.items():
            if count == 1:
                return alv
    
    # Si plusieurs alvéoles ou aucune, laisser dans HA21
    return None

def separer_ha21(simulation=True):
    """
    Sépare les dossiers HA21-E1, HA21-E2, HA21-E3
    """
    print(f"Mode: {'SIMULATION' if simulation else 'EXECUTION'}")
    print()
    
    deplacements = defaultdict(list)  # {alveole_src: [(src, dst, alveole_dst, nom_dossier)]}
    doublons = []
    incertains = []
    
    # Parcourir chaque alvéole source
    for alv_src_key, alv_src_nom in ALVEOLES.items():
        chemin_src = os.path.join(BASE_PATH, alv_src_nom)
        
        if not os.path.exists(chemin_src):
            print(f"[!] {alv_src_nom} n'existe pas")
            continue
        
        # Parcourir tous les sous-dossiers (catégories et leurs contenus)
        for root, dirs, files in os.walk(chemin_src):
            for d in dirs:
                alv_dst = detecter_alveole(d)
                
                # Si aucune alvéole détectée ou c'est multi-alvéoles, on laisse
                if alv_dst is None:
                    continue
                
                # Si c'est déjà dans la bonne alvéole, on ne fait rien
                if alv_dst == alv_src_key:
                    continue
                
                src_path = os.path.join(root, d)
                
                # Construire le chemin de destination (même structure de dossiers)
                # Exemple: ALVEOLE HA21\AUSCULTATION\dossier -> ALVEOLE HA21-E1\AUSCULTATION\dossier
                chemin_relatif = os.path.relpath(root, chemin_src)
                chemin_dst_parent = os.path.join(BASE_PATH, ALVEOLES[alv_dst], chemin_relatif)
                dst_path = os.path.join(chemin_dst_parent, d)
                
                # Vérifier si doublon
                if os.path.exists(dst_path):
                    doublons.append((alv_src_nom, ALVEOLES[alv_dst], d))
                else:
                    deplacements[alv_src_nom].append((src_path, dst_path, ALVEOLES[alv_dst], d, chemin_relatif))
    
    # Afficher les doublons
    if doublons:
        print(f"=== {len(doublons)} DOUBLONS DÉTECTÉS ===")
        for src, dst, nom in doublons:
            print(f"[DOUBLON] {nom}")
            print(f"  Existe dans {src} ET {dst}")
        print()
    
    # Afficher les déplacements
    if deplacements:
        total = sum(len(v) for v in deplacements.values())
        print(f"=== {total} DOSSIERS À DÉPLACER ===")
        print()
        
        for alv_src in sorted(deplacements.keys()):
            print(f"Depuis {alv_src}:")
            
            # Grouper par destination
            par_dest = defaultdict(list)
            for src, dst, alv_dst, nom, rel in deplacements[alv_src]:
                par_dest[alv_dst].append((src, dst, nom, rel))
            
            for alv_dst in sorted(par_dest.keys()):
                print(f"  -> {alv_dst}: {len(par_dest[alv_dst])} dossiers")
                
                # Afficher quelques exemples
                for src, dst, nom, rel in par_dest[alv_dst][:3]:
                    cat = rel if rel != '.' else '(racine)'
                    print(f"     - {cat}\\{nom}")
                if len(par_dest[alv_dst]) > 3:
                    print(f"     ... et {len(par_dest[alv_dst]) - 3} autres")
            print()
        
        if not simulation:
            print("Déplacement en cours...")
            deplacements_ok = 0
            erreurs = 0
            
            for alv_src, items in deplacements.items():
                for src, dst, alv_dst, nom, rel in items:
                    try:
                        # Créer le dossier parent si nécessaire
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        
                        # Déplacer
                        shutil.move(src, dst)
                        deplacements_ok += 1
                        print(f"[OK] {nom} -> {alv_dst}")
                    except Exception as e:
                        erreurs += 1
                        print(f"[ERREUR] {nom}: {e}")
            
            # Supprimer les doublons de la source
            if doublons and erreurs == 0:
                print()
                print("Suppression des doublons dans les sources...")
                for alv_src, alv_dst, nom in doublons:
                    for root, dirs, files in os.walk(os.path.join(BASE_PATH, alv_src)):
                        if nom in dirs:
                            chemin = os.path.join(root, nom)
                            try:
                                shutil.rmtree(chemin)
                                print(f"[SUPPRIMÉ] {nom} de {alv_src}")
                            except Exception as e:
                                print(f"[ERREUR] Suppression de {nom}: {e}")
            
            print()
            print(f"RÉSUMÉ: {deplacements_ok} déplacés, {len(doublons)} doublons traités, {erreurs} erreurs")
    else:
        print("Aucun dossier à déplacer")
    
    # Rappel
    if simulation:
        print()
        print("Note: Les dossiers multi-alvéoles (ex: HA21-1_2_3) restent dans ALVEOLE HA21")
        print()
        print("Pour exécuter les déplacements, lancez:")
        print("py src\\separer_ha21.py --execute")

if __name__ == "__main__":
    simulation = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        simulation = False
    
    separer_ha21(simulation)
