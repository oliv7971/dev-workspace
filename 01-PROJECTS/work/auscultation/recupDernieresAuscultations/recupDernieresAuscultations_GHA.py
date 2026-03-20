#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Recuperation des dernieres auscultations GHA.

Ce script parcourt les repertoires d'auscultation GHA et recupere les 10 dernieres lignes
des colonnes AB, AC, AD, AE, AF, AG de l'onglet DATABASE de chaque fichier Excel (.xlsm).
Les donnees sont exportees en format CSV.

Repertoires traites :
- 01-GVA105-106
- 02-GHA-04-05  
- 03-GHA-T15
- 04-GHA-T28
- 05-GHA-T41

Colonnes recuperees : AB, AC, AD, AE, AF, AG (10 dernieres lignes)
Format de sortie : CSV
"""

from __future__ import annotations
import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import pandas as pd
except ImportError:
    print("ERREUR: Le module pandas est requis. Installez-le avec : pip install pandas openpyxl")
    sys.exit(1)

# Configuration
BASE_AUSCULTATION = Path(r"C:\data\11-CHANTIERS\BURE\22-AUSCULTATION\GHA")
REPERTOIRES_GHA = [
    "01-GVA105-106",
    "02-GHA-04-05", 
    "03-GHA-T15",
    "04-GHA-T28",
    "05-GHA-T41"
]
COLONNES_CIBLES = ['AB', 'AC', 'AD', 'AE', 'AF', 'AG']
ONGLET_CIBLE = 'DATABASE'
NB_LIGNES_MAX = 10

# Configuration du logging
LOG_FORMAT = "%(levelname)s - %(message)s"

def trouver_fichier_xlsm(repertoire: Path) -> Optional[Path]:
    """
    Trouve le fichier .xlsm dans le repertoire donne.
    Selectionne le dernier fichier par ordre alphabetique (le plus recent chronologiquement).
    
    Args:
        repertoire: Chemin vers le repertoire a analyser
        
    Returns:
        Chemin vers le fichier .xlsm trouve, ou None si aucun trouve
    """
    if not repertoire.exists():
        logging.warning(f"Repertoire inexistant : {repertoire}")
        return None
        
    # Filtrer les fichiers .xlsm en excluant les fichiers temporaires Excel (commencant par ~$)
    fichiers_xlsm = [f for f in repertoire.glob("*.xlsm") if not f.name.startswith("~$")]
    
    if not fichiers_xlsm:
        logging.warning(f"Aucun fichier .xlsm trouve dans : {repertoire}")
        return None
    
    # Trier par ordre alphabetique et prendre le dernier
    fichiers_xlsm_tries = sorted(fichiers_xlsm, key=lambda x: x.name)
    fichier_selectionne = fichiers_xlsm_tries[-1]
    
    if len(fichiers_xlsm) > 1:
        logging.warning(f"Plusieurs fichiers .xlsm trouves dans {repertoire}, utilisation du dernier alphabetiquement : {fichier_selectionne.name}")
    
    return fichier_selectionne

def lire_dernieres_lignes_excel(fichier_excel: Path, onglet: str, colonnes: List[str], nb_lignes: int) -> Optional[pd.DataFrame]:
    """
    Lit les dernieres lignes des colonnes specifiees d'un fichier Excel.
    
    Args:
        fichier_excel: Chemin vers le fichier Excel
        onglet: Nom de l'onglet a lire
        colonnes: Liste des colonnes a recuperer (ex: ['AB', 'AC', 'AD', 'AE', 'AF', 'AG'])
        nb_lignes: Nombre de lignes a recuperer depuis la fin
        
    Returns:
        DataFrame avec les donnees recuperees, ou None si erreur
    """
    try:
        logging.info(f"Lecture de {fichier_excel.name}, onglet '{onglet}'")
        
        # Lecture de tout l'onglet d'abord
        df = pd.read_excel(fichier_excel, sheet_name=onglet, engine='openpyxl')
        
        if df.empty:
            logging.warning(f"Onglet '{onglet}' vide dans {fichier_excel.name}")
            return None
            
        # Conversion des noms de colonnes pour correspondre a la notation Excel
        # Les colonnes Excel sont nommees differemment dans pandas
        # Nous devons identifier les colonnes par leur position
        colonnes_indices = []
        for col in colonnes:
            # Conversion de la notation Excel (AD, AE, etc.) en index numerique
            index = excel_col_to_index(col)
            if index < len(df.columns):
                colonnes_indices.append(index)
            else:
                logging.warning(f"Colonne {col} (index {index}) non trouvee dans {fichier_excel.name}")
        
        if not colonnes_indices:
            logging.error(f"Aucune colonne cible trouvee dans {fichier_excel.name}")
            return None
            
        # Selection des colonnes par index
        df_selection = df.iloc[:, colonnes_indices]
        
        # Renommage des colonnes avec les noms Excel originaux
        noms_colonnes = [colonnes[i] for i in range(len(colonnes_indices))]
        df_selection.columns = noms_colonnes
        
        # Suppression des lignes entierement vides
        df_selection = df_selection.dropna(how='all')
        
        if df_selection.empty:
            logging.warning(f"Aucune donnee trouvee dans les colonnes {colonnes} de {fichier_excel.name}")
            return None
            
        # Recuperation des dernieres lignes
        dernieres_lignes = df_selection.tail(nb_lignes)
        
        logging.info(f"  -> {len(dernieres_lignes)} lignes recuperees sur {len(df_selection)} disponibles")
        
        return dernieres_lignes
        
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {fichier_excel.name}: {e}")
        return None

def excel_col_to_index(col_name: str) -> int:
    """
    Convertit un nom de colonne Excel (ex: 'AD') en index numerique (base 0).
    
    Args:
        col_name: Nom de la colonne Excel (ex: 'A', 'Z', 'AA', 'AD')
        
    Returns:
        Index numerique de la colonne (base 0)
    """
    result = 0
    for char in col_name:
        result = result * 26 + (ord(char.upper()) - ord('A') + 1)
    return result - 1

def exporter_vers_csv(donnees: List[Tuple[str, pd.DataFrame]], fichier_sortie: Path):
    """
    Exporte les donnees vers un fichier CSV.
    
    Args:
        donnees: Liste de tuples (nom_repertoire, dataframe)
        fichier_sortie: Chemin vers le fichier CSV de sortie
    """
    try:
        with open(fichier_sortie, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            
            # En-tete principal
            writer.writerow(['Repertoire', 'Ligne', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG'])
            
            for nom_repertoire, df in donnees:
                if df is not None and not df.empty:
                    for idx, row in df.iterrows():
                        ligne_csv = [nom_repertoire, str(idx)]
                        
                        # Ajout des valeurs des colonnes
                        for col in COLONNES_CIBLES:
                            if col in df.columns:
                                valeur = row[col]
                                # Formatage des valeurs numeriques
                                if pd.isna(valeur):
                                    ligne_csv.append('')
                                elif isinstance(valeur, (int, float)):
                                    ligne_csv.append(f"{valeur:.3f}" if isinstance(valeur, float) else str(valeur))
                                else:
                                    ligne_csv.append(str(valeur))
                            else:
                                ligne_csv.append('')
                        
                        writer.writerow(ligne_csv)
                    
                    # Ligne de separation entre les repertoires
                    writer.writerow([''] * 8)
        
        logging.info(f"Export CSV reussi : {fichier_sortie}")
        
    except Exception as e:
        logging.error(f"Erreur lors de l'export CSV : {e}")

def main():
    parser = argparse.ArgumentParser(description="Recupere les dernieres auscultations GHA depuis les fichiers Excel.")
    parser.add_argument("--output", "-o", type=Path, 
                       default=Path("dernieres_auscultations_GHA.csv"),
                       help="Fichier CSV de sortie (defaut: dernieres_auscultations_GHA.csv)")
    parser.add_argument("--lignes", "-n", type=int, default=NB_LIGNES_MAX,
                       help=f"Nombre de dernieres lignes a recuperer (defaut: {NB_LIGNES_MAX})")
    parser.add_argument("--verbose", "-v", action="count", default=0,
                       help="Niveau de verbosite (-v, -vv)")
    parser.add_argument("--base", type=Path, default=BASE_AUSCULTATION,
                       help="Repertoire de base des auscultations")
    
    args = parser.parse_args()
    
    # Configuration du logging
    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format=LOG_FORMAT)
    
    logging.info(f"Recherche des auscultations dans : {args.base}")
    logging.info(f"Colonnes cibles : {', '.join(COLONNES_CIBLES)}")
    logging.info(f"Nombre de lignes par fichier : {args.lignes}")
    
    if not args.base.exists():
        logging.error(f"Repertoire de base inexistant : {args.base}")
        return 1
    
    donnees_recuperees = []
    
    for nom_repertoire in REPERTOIRES_GHA:
        repertoire = args.base / nom_repertoire
        logging.info(f"\n--- Traitement de {nom_repertoire} ---")
        
        fichier_xlsm = trouver_fichier_xlsm(repertoire)
        if fichier_xlsm is None:
            continue
            
        donnees = lire_dernieres_lignes_excel(
            fichier_xlsm, 
            ONGLET_CIBLE, 
            COLONNES_CIBLES, 
            args.lignes
        )
        
        donnees_recuperees.append((nom_repertoire, donnees))
    
    # Export des donnees
    if donnees_recuperees:
        exporter_vers_csv(donnees_recuperees, args.output)
        
        # Statistiques finales
        nb_fichiers_traites = sum(1 for _, df in donnees_recuperees if df is not None)
        nb_lignes_total = sum(len(df) for _, df in donnees_recuperees if df is not None)
        
        print(f"\n=== RESUME ===")
        print(f"Fichiers traites avec succes : {nb_fichiers_traites}/{len(REPERTOIRES_GHA)}")
        print(f"Lignes totales recuperees : {nb_lignes_total}")
        print(f"Fichier de sortie : {args.output.absolute()}")
        
        return 0
    else:
        logging.error("Aucune donnee recuperee")
        return 1

if __name__ == "__main__":
    sys.exit(main())
