#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour séparer les dossiers GRD4 de GRD6
"""

import os
import shutil
import sys

# Chemins
GALERIE_GRD6 = r"C:\data\11-CHANTIERS\BURE\11-GALERIES\GALERIE GRD6"
GALERIE_GRD4 = r"C:\data\11-CHANTIERS\BURE\11-GALERIES\GALERIE GRD4"

def separer_grd4(simulation=True):
    """
    Déplace tous les dossiers contenant GRD4 de GRD6 vers GRD4
    """
    print(f"Mode: {'SIMULATION' if simulation else 'EXECUTION'}")
    print()
    
    # Créer GALERIE GRD4 si elle n'existe pas
    if not os.path.exists(GALERIE_GRD4):
        if not simulation:
            os.makedirs(GALERIE_GRD4)
            print(f"[CREE] {GALERIE_GRD4}")
        else:
            print(f"[A CREER] {GALERIE_GRD4}")
    
    deplacements = []
    
    # Parcourir les catégories dans GRD6
    for categorie in os.listdir(GALERIE_GRD6):
        chemin_categorie_src = os.path.join(GALERIE_GRD6, categorie)
        
        if not os.path.isdir(chemin_categorie_src):
            continue
        
        # Parcourir les dossiers dans chaque catégorie
        for dossier in os.listdir(chemin_categorie_src):
            # Si le nom contient GRD4
            if "GRD4" in dossier.upper():
                src = os.path.join(chemin_categorie_src, dossier)
                
                if not os.path.isdir(src):
                    continue
                
                # Créer la catégorie dans GRD4 si nécessaire
                chemin_categorie_dst = os.path.join(GALERIE_GRD4, categorie)
                dst = os.path.join(chemin_categorie_dst, dossier)
                
                # Vérifier si un dossier avec le même nom existe déjà dans GRD4
                if os.path.exists(dst):
                    print(f"[DOUBLON] {categorie}\\{dossier}")
                    print(f"  Existe déjà dans GALERIE GRD4")
                    if not simulation:
                        # En cas de doublon, on supprime celui de GRD6
                        shutil.rmtree(src)
                        print(f"  Supprimé de GRD6")
                else:
                    deplacements.append((src, dst, categorie, dossier))
    
    # Afficher et exécuter les déplacements
    if deplacements:
        print(f"\n{len(deplacements)} dossiers à déplacer:")
        print()
        
        # Grouper par catégorie
        categories_dict = {}
        for src, dst, categorie, dossier in deplacements:
            if categorie not in categories_dict:
                categories_dict[categorie] = []
            categories_dict[categorie].append((src, dst, dossier))
        
        for categorie in sorted(categories_dict.keys()):
            print(f"{categorie}:")
            for src, dst, dossier in categories_dict[categorie]:
                print(f"  - {dossier}")
            print()
        
        if not simulation:
            print("Déplacement en cours...")
            deplacements_ok = 0
            erreurs = 0
            
            for src, dst, categorie, dossier in deplacements:
                try:
                    # Créer la catégorie dans GRD4 si nécessaire
                    chemin_categorie_dst = os.path.dirname(dst)
                    if not os.path.exists(chemin_categorie_dst):
                        os.makedirs(chemin_categorie_dst)
                    
                    # Déplacer le dossier
                    shutil.move(src, dst)
                    deplacements_ok += 1
                    print(f"[OK] {categorie}\\{dossier}")
                except Exception as e:
                    erreurs += 1
                    print(f"[ERREUR] {categorie}\\{dossier}: {e}")
            
            print()
            print(f"RÉSUMÉ: {deplacements_ok} déplacés, {erreurs} erreurs")
    else:
        print("Aucun dossier GRD4 trouvé dans GALERIE GRD6")

if __name__ == "__main__":
    # Mode simulation par défaut
    simulation = True
    
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        simulation = False
    
    separer_grd4(simulation)
    
    if simulation:
        print()
        print("Pour exécuter les déplacements, lancez:")
        print("py src\\separer_grd4_grd6.py --execute")
