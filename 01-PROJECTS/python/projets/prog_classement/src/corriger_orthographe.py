"""
Script pour corriger les erreurs d'orthographe dans les noms de dossiers
Déplace les dossiers mal orthographiés vers les bonnes catégories
"""

import os
import shutil

# Configuration
GALERIE_BASE = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

def corriger_auscultation_gtb():
    """Corrige les dossiers 'ltation' (auscultation mal orthographié) dans GTB"""
    
    galerie_path = os.path.join(GALERIE_BASE, "GALERIE GTB")
    divers_path = os.path.join(galerie_path, "DIVERS")
    auscultation_path = os.path.join(galerie_path, "AUSCULTATION")
    
    # Vérifier que les chemins existent
    if not os.path.exists(divers_path):
        print(f"[ERREUR] Le dossier DIVERS n'existe pas: {divers_path}")
        return
    
    # Créer le dossier AUSCULTATION s'il n'existe pas
    if not os.path.exists(auscultation_path):
        os.makedirs(auscultation_path)
        print(f"[CRÉÉ] {auscultation_path}")
    
    # Parcourir les dossiers dans DIVERS
    dossiers_deplaces = 0
    dossiers_erreurs = 0
    
    print(f"\nRecherche des dossiers contenant 'ltation' dans DIVERS...")
    print("=" * 80)
    
    try:
        for dossier in os.listdir(divers_path):
            dossier_path = os.path.join(divers_path, dossier)
            
            # Vérifier si c'est un dossier et s'il contient "ltation"
            if os.path.isdir(dossier_path) and "ltation" in dossier.lower():
                destination = os.path.join(auscultation_path, dossier)
                
                # Vérifier si le dossier existe déjà dans la destination
                if os.path.exists(destination):
                    try:
                        shutil.rmtree(dossier_path)
                        print(f"[DOUBLON SUPPRIMÉ] {dossier}")
                        dossiers_deplaces += 1
                    except Exception as e:
                        print(f"[ERREUR SUPPRESSION] {dossier}: {e}")
                        dossiers_erreurs += 1
                    continue
                
                try:
                    shutil.move(dossier_path, destination)
                    print(f"[DÉPLACÉ] {dossier}")
                    dossiers_deplaces += 1
                except Exception as e:
                    print(f"[ERREUR] {dossier}: {e}")
                    dossiers_erreurs += 1
    
    except PermissionError as e:
        print(f"[ERREUR] Permission refusée: {e}")
        return
    
    # Résumé
    print("=" * 80)
    print(f"\nRÉSUMÉ:")
    print(f"  Dossiers déplacés  : {dossiers_deplaces}")
    print(f"  Erreurs            : {dossiers_erreurs}")
    print(f"\nSource     : {divers_path}")
    print(f"Destination: {auscultation_path}")

def main():
    print("\n" + "=" * 80)
    print("CORRECTION DES ERREURS D'ORTHOGRAPHE - GALERIE GTB")
    print("=" * 80)
    
    corriger_auscultation_gtb()
    
    print("\n[TERMINÉ]")

if __name__ == "__main__":
    main()
