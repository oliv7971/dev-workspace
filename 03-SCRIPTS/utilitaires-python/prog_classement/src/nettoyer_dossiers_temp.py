"""
Script de nettoyage des dossiers et fichiers temporaires/anciens
dans l'arborescence des galeries.

Supprime :
- Dossiers _ancien*, _ANCIENS, .backup, .temp, .bak
- Fichiers temporaires Excel (~$*.xlsx, ~$*.xls)
- Dossiers tmp/temp vides
- Fichiers .gsi vides (0 bytes)

NE SUPPRIME PAS les fichiers .txt (peuvent contenir des notes)
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple
import argparse


def trouver_dossiers_a_supprimer(racine: str) -> List[Path]:
    """
    Trouve tous les dossiers à supprimer.
    
    Critères :
    - Noms : _ancien*, _ANCIENS, .backup, .temp, *.bak, tmp (vide), temp (vide)
    """
    racine_path = Path(racine)
    dossiers_a_supprimer = []
    
    print("Recherche des dossiers à supprimer...")
    
    for dossier in racine_path.rglob("*"):
        if not dossier.is_dir():
            continue
            
        nom = dossier.name
        
        # Dossiers à supprimer par nom
        if (nom.startswith("_ancien") or 
            nom == "_ANCIENS" or 
            nom == ".backup" or 
            nom == ".temp" or 
            nom.endswith(".bak") or
            nom == "Data.anc"):
            dossiers_a_supprimer.append(dossier)
            continue
        
        # Dossiers tmp/temp vides uniquement
        if nom in ["tmp", "temp", "Tmp", "Temp"]:
            try:
                if not any(dossier.iterdir()):  # Vide
                    dossiers_a_supprimer.append(dossier)
            except PermissionError:
                continue
    
    return dossiers_a_supprimer


def trouver_fichiers_a_supprimer(racine: str) -> List[Path]:
    """
    Trouve tous les fichiers à supprimer.
    
    Critères :
    - Fichiers temporaires Excel : ~$*.xlsx, ~$*.xls, ~$*.xlsm
    - Fichiers .gsi vides (0 bytes)
    """
    racine_path = Path(racine)
    fichiers_a_supprimer = []
    
    print("Recherche des fichiers à supprimer...")
    
    for fichier in racine_path.rglob("*"):
        if not fichier.is_file():
            continue
            
        nom = fichier.name
        
        # Fichiers temporaires Excel
        if nom.startswith("~$") and fichier.suffix in [".xlsx", ".xls", ".xlsm"]:
            fichiers_a_supprimer.append(fichier)
            continue
        
        # Fichiers .gsi vides
        if fichier.suffix == ".gsi":
            try:
                if fichier.stat().st_size == 0:
                    fichiers_a_supprimer.append(fichier)
            except (PermissionError, OSError):
                continue
    
    return fichiers_a_supprimer


def afficher_rapport(dossiers: List[Path], fichiers: List[Path]):
    """Affiche un rapport des éléments à supprimer."""
    print("\n" + "="*80)
    print("RAPPORT DE NETTOYAGE")
    print("="*80)
    
    print(f"\n📁 DOSSIERS À SUPPRIMER : {len(dossiers)}")
    if dossiers:
        # Regrouper par type
        types = {}
        for d in dossiers:
            nom = d.name
            if nom.startswith("_ancien"):
                cle = "_ancien*"
            elif nom == "_ANCIENS":
                cle = "_ANCIENS"
            elif nom == ".backup":
                cle = ".backup"
            elif nom == ".temp":
                cle = ".temp"
            elif nom.endswith(".bak"):
                cle = "*.bak"
            elif nom == "Data.anc":
                cle = "Data.anc"
            elif nom.lower() in ["tmp", "temp"]:
                cle = "tmp/temp (vides)"
            else:
                cle = "autres"
            
            types[cle] = types.get(cle, 0) + 1
        
        for type_nom, count in sorted(types.items()):
            print(f"  - {type_nom}: {count}")
        
        print("\nPremiers exemples:")
        for d in dossiers[:10]:
            print(f"  {d}")
        if len(dossiers) > 10:
            print(f"  ... et {len(dossiers) - 10} autres")
    
    print(f"\n📄 FICHIERS À SUPPRIMER : {len(fichiers)}")
    if fichiers:
        # Regrouper par type
        types = {}
        for f in fichiers:
            nom = f.name
            if nom.startswith("~$"):
                cle = "~$ (Excel temporaires)"
            elif f.suffix == ".gsi" and f.stat().st_size == 0:
                cle = ".gsi vides"
            else:
                cle = "autres"
            
            types[cle] = types.get(cle, 0) + 1
        
        for type_nom, count in sorted(types.items()):
            print(f"  - {type_nom}: {count}")
        
        print("\nPremiers exemples:")
        for f in fichiers[:10]:
            print(f"  {f}")
        if len(fichiers) > 10:
            print(f"  ... et {len(fichiers) - 10} autres")
    
    print("\n" + "="*80)


def supprimer_elements(dossiers: List[Path], fichiers: List[Path]) -> Tuple[int, int, List[str]]:
    """
    Supprime les dossiers et fichiers.
    
    Returns:
        (nb_dossiers_supprimés, nb_fichiers_supprimés, liste_erreurs)
    """
    nb_dossiers = 0
    nb_fichiers = 0
    erreurs = []
    
    # Supprimer les fichiers
    print("\nSuppression des fichiers...")
    for fichier in fichiers:
        try:
            fichier.unlink()
            nb_fichiers += 1
            if nb_fichiers % 50 == 0:
                print(f"  {nb_fichiers} fichiers supprimés...")
        except Exception as e:
            erreurs.append(f"Fichier {fichier}: {e}")
    
    # Supprimer les dossiers
    print("\nSuppression des dossiers...")
    for dossier in dossiers:
        try:
            shutil.rmtree(dossier)
            nb_dossiers += 1
            if nb_dossiers % 20 == 0:
                print(f"  {nb_dossiers} dossiers supprimés...")
        except Exception as e:
            erreurs.append(f"Dossier {dossier}: {e}")
    
    return nb_dossiers, nb_fichiers, erreurs


def main():
    parser = argparse.ArgumentParser(
        description="Nettoie les dossiers et fichiers temporaires/anciens"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Exécute réellement la suppression (sinon mode simulation)"
    )
    parser.add_argument(
        "--racine",
        type=str,
        default=r"C:\data\11-CHANTIERS\BURE\11-GALERIES",
        help="Chemin racine à analyser"
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("NETTOYAGE DES FICHIERS TEMPORAIRES ET ANCIENS")
    print("="*80)
    print(f"\nRacine : {args.racine}")
    print(f"Mode : {'EXÉCUTION' if args.execute else 'SIMULATION'}")
    print("\nÉléments ciblés :")
    print("  - Dossiers : _ancien*, _ANCIENS, .backup, .temp, *.bak, Data.anc, tmp/temp vides")
    print("  - Fichiers : ~$*.xlsx/xls (Excel temp), .gsi vides")
    print("  - PRÉSERVÉS : tous les fichiers .txt")
    
    # Vérifier que le chemin existe
    if not os.path.exists(args.racine):
        print(f"\n❌ ERREUR : Le chemin {args.racine} n'existe pas")
        return 1
    
    # Rechercher les éléments
    dossiers = trouver_dossiers_a_supprimer(args.racine)
    fichiers = trouver_fichiers_a_supprimer(args.racine)
    
    # Afficher le rapport
    afficher_rapport(dossiers, fichiers)
    
    if not args.execute:
        print("\n⚠️  MODE SIMULATION - Aucune suppression effectuée")
        print("   Ajoutez --execute pour supprimer réellement ces éléments")
        return 0
    
    # Confirmation
    print("\n⚠️  ATTENTION : Cette opération est IRRÉVERSIBLE !")
    reponse = input("Voulez-vous vraiment supprimer ces éléments ? (oui/non) : ")
    
    if reponse.lower() != "oui":
        print("❌ Opération annulée")
        return 0
    
    # Exécution
    print("\n" + "="*80)
    print("EXÉCUTION DE LA SUPPRESSION")
    print("="*80)
    
    nb_dossiers, nb_fichiers, erreurs = supprimer_elements(dossiers, fichiers)
    
    print("\n" + "="*80)
    print("RÉSULTAT")
    print("="*80)
    print(f"\n✅ {nb_fichiers} fichiers supprimés")
    print(f"✅ {nb_dossiers} dossiers supprimés")
    
    if erreurs:
        print(f"\n⚠️  {len(erreurs)} erreurs rencontrées :")
        for erreur in erreurs[:20]:
            print(f"  - {erreur}")
        if len(erreurs) > 20:
            print(f"  ... et {len(erreurs) - 20} autres erreurs")
    else:
        print("\n✅ Aucune erreur")
    
    print("\n✅ Nettoyage terminé avec succès")
    return 0


if __name__ == "__main__":
    exit(main())
