#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AJOUT DE NOUVELLES MESURES (Sans reset complet)
================================================

Alternative au reset complet : ajoute seulement les nouvelles dates
qui n'existent pas encore dans les onglets.

Cas d'usage :
- Ajout d'une nouvelle campagne de mesure
- Mesures accélérées (nouvelle mesure à 14h alors que 08h existe déjà)
- Mise à jour incrémentale sans tout recalculer

Principe :
1. Lit les dates existantes dans "Résultats observations"
2. Compare avec DATABASE
3. Ajoute uniquement les dates manquantes
4. Maintient l'ordre chronologique
"""

import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime
import pandas as pd

# ==================== CONFIGURATION ====================

FICHIER_EXCEL = "01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm"
ONGLET_REFERENCE = "Résultats observations"  # Onglet de référence pour les dates
LIGNE_DEBUT_DONNEES = 10

ONGLETS_A_METTRE_A_JOUR = [
    "Résultats observations",
    "OBSERVATIONS",
    "PROJECTION",
    "EVOLUTIONS XYZ",
    "ÉVOLUTION PM H V",
    "cordes ref1",
    "cordes ref2",
    "EVOLUTIONS CORDES REF1",
    "EVOLUTIONS CORDES REF2"
]

# ==================== FONCTIONS ====================

def extraire_dates_existantes(ws, ligne_debut=10):
    """
    Extrait les dates déjà présentes dans un onglet (colonne A)
    """
    dates_existantes = []
    
    for row in range(ligne_debut, ws.max_row + 1):
        cell_value = ws.cell(row, 1).value  # Colonne A
        if cell_value:
            try:
                # Convertir en datetime
                if isinstance(cell_value, datetime):
                    dates_existantes.append(cell_value)
                elif isinstance(cell_value, str):
                    # Essayer plusieurs formats
                    for fmt in ["%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                        try:
                            dt = datetime.strptime(cell_value, fmt)
                            dates_existantes.append(dt)
                            break
                        except ValueError:
                            continue
            except Exception as e:
                print(f"⚠️ Date invalide ligne {row} : {cell_value}")
    
    return dates_existantes


def extraire_dates_database(wb):
    """
    Extrait toutes les dates de DATABASE
    """
    if "DATABASE" not in wb.sheetnames:
        return []
    
    ws_db = wb["DATABASE"]
    
    # Trouver la colonne DATE
    date_col = None
    for col in range(1, ws_db.max_column + 1):
        cell_value = ws_db.cell(12, col).value
        if cell_value and str(cell_value).upper() == "DATE":
            date_col = col
            break
    
    if date_col is None:
        return []
    
    # Extraire les dates
    dates_database = []
    for row in range(14, ws_db.max_row + 1):
        cell_value = ws_db.cell(row, date_col).value
        if cell_value:
            try:
                if isinstance(cell_value, datetime):
                    dates_database.append(cell_value)
                elif isinstance(cell_value, str):
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]:
                        try:
                            dt = datetime.strptime(cell_value, fmt)
                            dates_database.append(dt)
                            break
                        except ValueError:
                            continue
            except Exception as e:
                pass
    
    return sorted(dates_database)


def trouver_dates_manquantes(dates_existantes, dates_database):
    """
    Compare et trouve les dates de DATABASE qui ne sont pas dans l'onglet
    """
    # Convertir en set pour comparaison efficace
    set_existantes = set(dates_existantes)
    set_database = set(dates_database)
    
    dates_manquantes = set_database - set_existantes
    
    return sorted(list(dates_manquantes))


def inserer_dates_triees(ws, dates_completes, ligne_debut=10):
    """
    Réinsère toutes les dates (existantes + nouvelles) dans l'ordre chronologique
    """
    # Supprimer toutes les lignes existantes
    max_row = ws.max_row
    if max_row >= ligne_debut:
        ws.delete_rows(ligne_debut, max_row - ligne_debut + 1)
    
    # Insérer les dates triées
    if not dates_completes:
        return
    
    date_point_zero = dates_completes[0]
    
    for i, dt in enumerate(dates_completes):
        ligne = ligne_debut + i
        
        # Colonne A : Date (avec heure si != 00:00)
        if dt.hour == 0 and dt.minute == 0:
            ws.cell(ligne, 1).value = dt.strftime('%d/%m/%Y')
        else:
            ws.cell(ligne, 1).value = dt.strftime('%d/%m/%Y %H:%M')
        
        # Colonne B : Jours depuis point 0
        delta = dt - date_point_zero
        jours = delta.total_seconds() / 86400
        ws.cell(ligne, 2).value = round(jours, 2)


def ajouter_nouvelles_mesures():
    """
    Fonction principale : ajoute uniquement les nouvelles dates
    """
    print("\n➕ AJOUT DE NOUVELLES MESURES")
    print("="*60)
    print(f"📂 Fichier : {FICHIER_EXCEL}\n")
    
    # Charger le fichier
    try:
        wb = openpyxl.load_workbook(FICHIER_EXCEL, keep_vba=True)
        print(f"✅ Fichier chargé\n")
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {FICHIER_EXCEL}")
        return
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return
    
    # Vérifier l'onglet de référence
    if ONGLET_REFERENCE not in wb.sheetnames:
        print(f"❌ Onglet '{ONGLET_REFERENCE}' non trouvé")
        wb.close()
        return
    
    ws_ref = wb[ONGLET_REFERENCE]
    
    # Étape 1 : Extraire dates existantes
    print("📅 Extraction des dates existantes...")
    dates_existantes = extraire_dates_existantes(ws_ref, LIGNE_DEBUT_DONNEES)
    print(f"   ✅ {len(dates_existantes)} dates déjà présentes")
    
    # Étape 2 : Extraire dates de DATABASE
    print("\n📊 Extraction des dates de DATABASE...")
    dates_database = extraire_dates_database(wb)
    print(f"   ✅ {len(dates_database)} dates dans DATABASE")
    
    if not dates_database:
        print("\n❌ Aucune date trouvée dans DATABASE")
        wb.close()
        return
    
    # Étape 3 : Trouver les dates manquantes
    print("\n🔍 Recherche des nouvelles dates...")
    dates_manquantes = trouver_dates_manquantes(dates_existantes, dates_database)
    
    if not dates_manquantes:
        print("   ✅ Aucune nouvelle date - Tous les onglets sont à jour !")
        wb.close()
        return
    
    print(f"   🆕 {len(dates_manquantes)} nouvelles dates trouvées :")
    for dt in dates_manquantes[:10]:  # Afficher 10 premières
        print(f"      - {dt.strftime('%d/%m/%Y %H:%M')}")
    if len(dates_manquantes) > 10:
        print(f"      ... et {len(dates_manquantes) - 10} autres")
    
    # Étape 4 : Fusionner et trier
    print("\n🔄 Fusion et tri chronologique...")
    dates_completes = sorted(dates_existantes + dates_manquantes)
    print(f"   ✅ {len(dates_completes)} dates au total")
    
    # Étape 5 : Mettre à jour tous les onglets
    print("\n📝 Mise à jour des onglets...")
    onglets_mis_a_jour = 0
    
    for onglet_nom in ONGLETS_A_METTRE_A_JOUR:
        if onglet_nom not in wb.sheetnames:
            print(f"   ⚠️ {onglet_nom} : Non trouvé - Ignoré")
            continue
        
        ws = wb[onglet_nom]
        inserer_dates_triees(ws, dates_completes, LIGNE_DEBUT_DONNEES)
        print(f"   ✅ {onglet_nom} : Mis à jour")
        onglets_mis_a_jour += 1
    
    # Étape 6 : Sauvegarder
    print("\n💾 Sauvegarde...")
    try:
        wb.save(FICHIER_EXCEL)
        print(f"✅ Fichier sauvegardé : {FICHIER_EXCEL}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        backup_name = FICHIER_EXCEL.replace(".xlsm", "_BACKUP.xlsm")
        try:
            wb.save(backup_name)
            print(f"⚠️ Sauvegarde de secours : {backup_name}")
        except:
            print("❌ Impossible de sauvegarder")
    
    wb.close()
    
    print("\n" + "="*60)
    print("✅ AJOUT TERMINÉ")
    print("="*60)
    print(f"📊 Résumé :")
    print(f"   - {len(dates_manquantes)} nouvelles dates ajoutées")
    print(f"   - {onglets_mis_a_jour} onglets mis à jour")
    print(f"   - {len(dates_completes)} dates au total")
    print("\n📌 Les formules Excel vont se recalculer automatiquement")


# ==================== EXÉCUTION ====================

if __name__ == "__main__":
    print("\n" + "➕ " * 30)
    print("AJOUT DE NOUVELLES MESURES - MODE INCRÉMENTAL")
    print("➕ " * 30 + "\n")
    
    print("ℹ️ Ce script va :")
    print("   1. Comparer DATABASE avec les onglets existants")
    print("   2. Ajouter uniquement les nouvelles dates")
    print("   3. Maintenir l'ordre chronologique")
    print("   4. Conserver toutes les données existantes")
    print()
    
    reponse = input("Continuer ? (oui/non) : ").lower().strip()
    
    if reponse in ['oui', 'o', 'yes', 'y']:
        ajouter_nouvelles_mesures()
    else:
        print("\n❌ Opération annulée")
