#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des points targets (prisme 000344)
Les points avec constante de prisme 000344 sont des targets, pas des références.
Renommage : XX.GGS.YD/G → TXX{D/G}
"""

import re

def corriger_targets():
    """Corrige les noms des points targets avec prisme 000344"""
    
    fichier_entree = "carnet/POLYGGS-251204-K.geo"
    fichier_sortie = "carnet/POLYGGS-251204-L.geo"
    
    # Pattern pour détecter les lignes avec prisme 000344
    # et nom du type XX.GGS.YD ou XX.GGS.YG
    pattern_target = re.compile(
        r'^(000344\s+Mesure\s+)(\d+)\.GGS\.(\d+)([DG])(\s+.*)$'
    )
    
    modifications = {}
    lignes_modifiees = 0
    
    with open(fichier_entree, 'r', encoding='utf-8') as f_in:
        lignes = f_in.readlines()
    
    with open(fichier_sortie, 'w', encoding='utf-8') as f_out:
        for ligne in lignes:
            match = pattern_target.match(ligne)
            if match:
                debut = match.group(1)
                num1 = match.group(2)
                num2 = match.group(3)
                suffixe = match.group(4)
                fin = match.group(5)
                
                ancien_nom = f"{num1}.GGS.{num2}{suffixe}"
                nouveau_nom = f"T{num1}{suffixe}"
                
                nouvelle_ligne = f"{debut}{nouveau_nom}{fin}\n"
                f_out.write(nouvelle_ligne)
                
                # Comptabiliser les modifications
                if ancien_nom not in modifications:
                    modifications[ancien_nom] = nouveau_nom
                lignes_modifiees += 1
            else:
                f_out.write(ligne)
    
    # Affichage du résumé
    print("=" * 80)
    print("CORRECTION DES TARGETS - PRISME 000344")
    print("=" * 80)
    print(f"\nFichier d'entrée  : {fichier_entree}")
    print(f"Fichier de sortie : {fichier_sortie}")
    print(f"\nNombre de modifications : {lignes_modifiees} lignes")
    print(f"Nombre de points uniques : {len(modifications)}")
    
    if modifications:
        print("\nCORRESPONDANCES APPLIQUÉES:")
        print("-" * 80)
        for ancien, nouveau in sorted(modifications.items()):
            print(f"  {ancien:30s} → {nouveau}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    corriger_targets()
