#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTÈME DE RESET ET MISE À JOUR COMPLÈTE
=========================================

Problème résolu :
- Anciennes valeurs qui restent dans les cellules
- Dates manquantes de DATABASE
- PLUSIEURS MESURES PAR JOUR (mesure accélérée 6h/12h)

Principe :
1. Vide toutes les données des onglets (garde structure)
2. Extrait TOUTES les dates+heures de DATABASE
3. Les insère dans colonne A de "Résultats observations"
4. Les formules Excel se recalculent automatiquement

Gestion multi-mesures :
- 26/11/2025 08:00 → Ligne 10
- 26/11/2025 14:00 → Ligne 11
- 26/11/2025 20:00 → Ligne 12
"""

import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime
import pandas as pd
from collections import defaultdict

# ==================== CONFIGURATION ====================

FICHIER_EXCEL = "01_51-B-GER-HA21_3-PM_135-25-05-21.xlsm"

# Onglets à traiter (vider et mettre à jour avec dates)
ONGLETS_A_TRAITER = [
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

# Ligne de début des données (après en-têtes)
LIGNE_DEBUT_DONNEES = 10

# Colonnes à conserver (Date, Jours)
COLONNES_DATES = ['A', 'B']

# ==================== FONCTIONS ====================

def extraire_dates_database(wb):
    """
    Extrait toutes les dates uniques de DATABASE avec horodatage
    Gère plusieurs mesures le même jour
    """
    print("\n📅 EXTRACTION DES DATES DE DATABASE")
    print("="*60)
    
    if "DATABASE" not in wb.sheetnames:
        print("❌ Onglet DATABASE non trouvé !")
        return []
    
    ws_db = wb["DATABASE"]
    
    # Trouver la colonne DATE dans DATABASE
    date_col = None
    for col in range(1, ws_db.max_column + 1):
        cell_value = ws_db.cell(12, col).value  # Ligne d'en-tête DATABASE
        if cell_value and str(cell_value).upper() == "DATE":
            date_col = col
            break
    
    if date_col is None:
        print("❌ Colonne DATE non trouvée dans DATABASE")
        return []
    
    print(f"✅ Colonne DATE trouvée : {get_column_letter(date_col)}")
    
    # Extraire toutes les dates
    dates_brutes = []
    for row in range(14, ws_db.max_row + 1):  # Données DATABASE commencent ligne 14
        cell_value = ws_db.cell(row, date_col).value
        if cell_value:
            dates_brutes.append(cell_value)
    
    print(f"📊 {len(dates_brutes)} mesures trouvées dans DATABASE")
    
    # Convertir en datetime et gérer les formats
    dates_datetime = []
    for date_val in dates_brutes:
        try:
            if isinstance(date_val, datetime):
                dates_datetime.append(date_val)
            elif isinstance(date_val, str):
                # Essayer plusieurs formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]:
                    try:
                        dt = datetime.strptime(date_val, fmt)
                        dates_datetime.append(dt)
                        break
                    except ValueError:
                        continue
        except Exception as e:
            print(f"⚠️ Date ignorée : {date_val} ({e})")
    
    # Trier chronologiquement
    dates_datetime.sort()
    
    # Détecter mesures multiples par jour
    compteur_par_jour = defaultdict(int)
    for dt in dates_datetime:
        jour = dt.date()
        compteur_par_jour[jour] += 1
    
    jours_multiples = {jour: count for jour, count in compteur_par_jour.items() if count > 1}
    
    if jours_multiples:
        print(f"\n🔄 MESURES MULTIPLES DÉTECTÉES :")
        for jour, count in sorted(jours_multiples.items())[:5]:  # Afficher 5 premiers
            print(f"   {jour.strftime('%d/%m/%Y')}: {count} mesures")
        if len(jours_multiples) > 5:
            print(f"   ... et {len(jours_multiples) - 5} autres jours")
    
    print(f"\n✅ {len(dates_datetime)} dates extraites et triées")
    if dates_datetime:
        print(f"   📅 Première : {dates_datetime[0].strftime('%d/%m/%Y %H:%M')}")
        print(f"   📅 Dernière : {dates_datetime[-1].strftime('%d/%m/%Y %H:%M')}")
    
    return dates_datetime


def vider_donnees_onglet(ws, ligne_debut=10):
    """
    Vide toutes les données d'un onglet à partir de ligne_debut
    Conserve les en-têtes et la structure
    """
    max_row = ws.max_row
    
    if max_row >= ligne_debut:
        # Supprimer toutes les lignes de données
        ws.delete_rows(ligne_debut, max_row - ligne_debut + 1)
        return max_row - ligne_debut + 1
    return 0


def inserer_dates_dans_onglet(ws, dates_datetime, ligne_debut=10):
    """
    Insère les dates dans la colonne A d'un onglet
    Calcule automatiquement les jours depuis le point 0 (colonne B)
    """
    if not dates_datetime:
        print("   ⚠️ Aucune date à insérer")
        return
    
    date_point_zero = dates_datetime[0]  # Première date = point 0
    
    for i, dt in enumerate(dates_datetime):
        ligne = ligne_debut + i
        
        # Colonne A : Date + Heure
        # Format selon si c'est minuit (00:00) ou pas
        if dt.hour == 0 and dt.minute == 0:
            # Juste la date si minuit
            ws.cell(ligne, 1).value = dt.strftime('%d/%m/%Y')
        else:
            # Date + heure si mesure en cours de journée
            ws.cell(ligne, 1).value = dt.strftime('%d/%m/%Y %H:%M')
        
        # Colonne B : Jours depuis point 0
        delta = dt - date_point_zero
        jours_depuis_point_zero = delta.total_seconds() / 86400  # Convertir en jours (avec décimales)
        ws.cell(ligne, 2).value = round(jours_depuis_point_zero, 2)
    
    print(f"   ✅ {len(dates_datetime)} dates insérées (lignes {ligne_debut}-{ligne_debut + len(dates_datetime) - 1})")


def reset_et_mise_a_jour_complete():
    """
    Fonction principale : Reset complet et mise à jour avec toutes les dates
    """
    print("🔄 RESET ET MISE À JOUR COMPLÈTE")
    print("="*60)
    print(f"📂 Fichier : {FICHIER_EXCEL}\n")
    
    # Charger le fichier
    try:
        wb = openpyxl.load_workbook(FICHIER_EXCEL, keep_vba=True)
        print(f"✅ Fichier chargé : {len(wb.sheetnames)} onglets\n")
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé : {FICHIER_EXCEL}")
        return
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return
    
    # Étape 1 : Extraire toutes les dates de DATABASE
    dates_datetime = extraire_dates_database(wb)
    
    if not dates_datetime:
        print("\n❌ Aucune date trouvée dans DATABASE - Abandon")
        wb.close()
        return
    
    # Étape 2 : Traiter chaque onglet
    print("\n🔧 TRAITEMENT DES ONGLETS")
    print("="*60)
    
    for onglet_nom in ONGLETS_A_TRAITER:
        if onglet_nom not in wb.sheetnames:
            print(f"⚠️ {onglet_nom}: Onglet non trouvé - Ignoré")
            continue
        
        print(f"\n📋 {onglet_nom}:")
        ws = wb[onglet_nom]
        
        # Vider les données
        lignes_supprimees = vider_donnees_onglet(ws, LIGNE_DEBUT_DONNEES)
        if lignes_supprimees > 0:
            print(f"   🗑️ {lignes_supprimees} lignes supprimées")
        else:
            print(f"   ℹ️ Onglet déjà vide")
        
        # Insérer les nouvelles dates
        inserer_dates_dans_onglet(ws, dates_datetime, LIGNE_DEBUT_DONNEES)
    
    # Étape 3 : Sauvegarder
    print("\n💾 SAUVEGARDE")
    print("="*60)
    
    try:
        wb.save(FICHIER_EXCEL)
        print(f"✅ Fichier sauvegardé : {FICHIER_EXCEL}")
        print(f"✅ {len(dates_datetime)} dates insérées dans {len([o for o in ONGLETS_A_TRAITER if o in wb.sheetnames])} onglets")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde : {e}")
        
        # Tentative de sauvegarde de secours
        backup_name = FICHIER_EXCEL.replace(".xlsm", "_BACKUP.xlsm")
        try:
            wb.save(backup_name)
            print(f"⚠️ Sauvegarde de secours : {backup_name}")
        except:
            print("❌ Impossible de sauvegarder même en backup")
    
    wb.close()
    
    print("\n" + "="*60)
    print("✅ TRAITEMENT TERMINÉ")
    print("="*60)
    print("\n📌 IMPORTANT :")
    print("   - Les anciennes données ont été supprimées")
    print("   - Les nouvelles dates sont insérées")
    print("   - Les formules Excel vont se recalculer automatiquement")
    print("   - Vérifiez les calculs dans Excel après ouverture")
    
    if any(jour_count > 1 for jour_count in [sum(1 for d in dates_datetime if d.date() == jour) for jour in set(d.date() for d in dates_datetime)]):
        print("\n⚠️ ATTENTION : Plusieurs mesures par jour détectées")
        print("   Les lignes incluent maintenant l'heure (ex: 26/11/2025 14:00)")


# ==================== EXÉCUTION ====================

if __name__ == "__main__":
    print("\n" + "🚀 " * 30)
    print("SYSTÈME DE RESET ET MISE À JOUR COMPLÈTE - AUSCULTATION")
    print("🚀 " * 30 + "\n")
    
    # Demander confirmation
    print("⚠️ Ce script va :")
    print("   1. VIDER toutes les données des onglets (garde structure)")
    print("   2. Extraire toutes les dates de DATABASE")
    print("   3. Réinsérer les dates triées chronologiquement")
    print("   4. Gérer les mesures multiples par jour (6h/12h/18h)")
    print()
    
    reponse = input("Voulez-vous continuer ? (oui/non) : ").lower().strip()
    
    if reponse in ['oui', 'o', 'yes', 'y']:
        reset_et_mise_a_jour_complete()
    else:
        print("\n❌ Opération annulée par l'utilisateur")
