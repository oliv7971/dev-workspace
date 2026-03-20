"""
Script de recherche personnalisé dans les galeries
Recherche rapide et fiable dans tous les dossiers, sans dépendre de l'indexation Windows
"""

import os
import sys

# Base des galeries
GALERIES_BASE = r"C:\data\11-CHANTIERS\BURE\11-GALERIES"

def rechercher(texte, galerie=None):
    """
    Recherche un texte dans les noms de dossiers
    
    Args:
        texte: Texte à rechercher (insensible à la casse)
        galerie: Nom de la galerie spécifique (optionnel)
    """
    
    texte_lower = texte.lower()
    resultats = []
    
    # Définir le chemin de recherche
    if galerie:
        chemin_base = os.path.join(GALERIES_BASE, galerie)
        if not os.path.exists(chemin_base):
            print(f"[ERREUR] La galerie '{galerie}' n'existe pas")
            return
    else:
        chemin_base = GALERIES_BASE
    
    print(f"\nRecherche de '{texte}' dans {chemin_base}...")
    print("=" * 80)
    
    # Parcourir tous les dossiers
    for racine, dossiers, fichiers in os.walk(chemin_base):
        # Chercher dans les noms de dossiers
        for dossier in dossiers:
            if texte_lower in dossier.lower():
                chemin_complet = os.path.join(racine, dossier)
                chemin_relatif = chemin_complet.replace(GALERIES_BASE + "\\", "")
                resultats.append(chemin_relatif)
        
        # Chercher dans les noms de fichiers si demandé
        for fichier in fichiers:
            if texte_lower in fichier.lower():
                chemin_complet = os.path.join(racine, fichier)
                chemin_relatif = chemin_complet.replace(GALERIES_BASE + "\\", "")
                resultats.append(chemin_relatif)
    
    # Afficher les résultats
    if resultats:
        print(f"\n{len(resultats)} résultat(s) trouvé(s):\n")
        for i, resultat in enumerate(sorted(resultats), 1):
            print(f"{i:4d}. {resultat}")
    else:
        print("\nAucun résultat trouvé.")
    
    print("=" * 80)

def main():
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  py src\\rechercher.py <TEXTE>")
        print("  py src\\rechercher.py <TEXTE> <GALERIE>")
        print("\nExemples:")
        print("  py src\\rechercher.py auscultation")
        print("  py src\\rechercher.py \"SMC 31\"")
        print('  py src\\rechercher.py polygo "GALERIE GGS"')
        return
    
    texte = sys.argv[1]
    galerie = sys.argv[2] if len(sys.argv) > 2 else None
    
    rechercher(texte, galerie)

if __name__ == "__main__":
    main()
