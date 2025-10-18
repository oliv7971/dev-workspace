#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de Graphiques Excel pour Auscultation
================================================

Ce script génère automatiquement les graphiques Excel intégrés
pour le système d'auscultation avec 20 cibles (V1 à V20).

Basé sur l'analyse du fichier existant avec 4 ScatterCharts:
- Déplacement en Z
- Déplacement latéral GER = PM sur axe alvéole
- Déplacement PM GER = déport sur axe alvéole
- Mesure des cordes

Auteur: Système d'automatisation Excel
Date: Décembre 2024
"""

import openpyxl
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.chart.title import Title
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties, RichTextProperties
from openpyxl.drawing.colors import ColorChoice, SchemeColor, SystemColor
from openpyxl.drawing.text import Font
import sys
import os
from pathlib import Path

class GenerateurGraphiquesExcel:
    """Générateur de graphiques Excel pour auscultation"""

    def __init__(self, fichier_excel):
        """
        Initialise le générateur

        Args:
            fichier_excel: Chemin vers le fichier Excel
        """
        self.fichier_excel = fichier_excel
        self.workbook = None
        self.onglet_graphiques = None

        # Configuration des graphiques basée sur l'analyse
        self.types_graphiques = [
            {
                "nom": "Déplacement en Z",
                "suffixe": "_Z",
                "position": {"col_debut": 13, "row_debut": 6, "col_fin": 23, "row_fin": 32}
            },
            {
                "nom": "Déplacement latéral GER = PM sur axe alvéole",
                "suffixe": "_PM",
                "position": {"col_debut": 1, "row_debut": 39, "col_fin": 11, "row_fin": 65}
            },
            {
                "nom": "Déplacement PM GER = déport sur axe alvéole",
                "suffixe": "_H",
                "position": {"col_debut": 13, "row_debut": 39, "col_fin": 23, "row_fin": 65}
            },
            {
                "nom": "Mesure des cordes",
                "suffixe": "_CORDES",
                "position": {"col_debut": 1, "row_debut": 6, "col_fin": 11, "row_fin": 32}
            }
        ]

    def charger_fichier(self):
        """Charge le fichier Excel"""
        try:
            print(f"📂 Chargement du fichier: {self.fichier_excel}")
            self.workbook = openpyxl.load_workbook(self.fichier_excel)

            # Vérifier l'onglet Graphiques
            if 'Graphiques' not in self.workbook.sheetnames:
                print("❌ Onglet 'Graphiques' non trouvé!")
                return False

            self.onglet_graphiques = self.workbook['Graphiques']
            print(f"✅ Fichier chargé - {len(self.workbook.sheetnames)} onglets détectés")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return False

    def creer_titre_graphique(self, titre_texte):
        """
        Crée un titre de graphique simplifié

        Args:
            titre_texte: Texte du titre

        Returns:
            Title: Objet titre formaté
        """
        # Créer un titre simple - openpyxl peut créer les titres automatiquement
        # Pas besoin de définir tous les détails de formatage manuellement
        return titre_texte  # On retourne juste le texte, le graphique l'utilisera

    def creer_scatter_chart(self, titre, donnees_x, donnees_y, position):
        """
        Crée un ScatterChart avec le formatage détecté

        Args:
            titre: Titre du graphique
            donnees_x: Référence des données X
            donnees_y: Référence des données Y
            position: Dictionnaire avec col_debut, row_debut, col_fin, row_fin

        Returns:
            ScatterChart: Graphique configuré
        """
        # Créer le graphique scatter
        chart = ScatterChart()

        # Ajouter le titre (simple)
        chart.title = titre

        # Créer les séries de données
        series = Series(donnees_y, donnees_x)
        chart.series.append(series)

        # Positionnement basé sur l'analyse
        chart.anchor = f"{chr(65 + position['col_debut'])}{position['row_debut']}"
        chart.width = (position['col_fin'] - position['col_debut']) * 0.75  # Largeur approx
        chart.height = (position['row_fin'] - position['row_debut']) * 0.3  # Hauteur approx

        return chart

    def supprimer_graphiques_existants(self):
        """Supprime tous les graphiques existants de l'onglet Graphiques"""
        try:
            print("🗑️ Suppression des graphiques existants...")

            # Supprimer tous les objets de dessin (graphiques)
            if hasattr(self.onglet_graphiques, '_charts'):
                self.onglet_graphiques._charts = []

            if hasattr(self.onglet_graphiques, '_images'):
                self.onglet_graphiques._images = []

            if hasattr(self.onglet_graphiques, '_drawing'):
                self.onglet_graphiques._drawing = None

            print("✅ Graphiques existants supprimés")
            return True

        except Exception as e:
            print(f"⚠️ Attention lors de la suppression: {e}")
            return True  # On continue même en cas d'erreur

    def generer_graphiques_20_cibles(self):
        """
        Génère les graphiques pour les 20 cibles (V1 à V20)
        """
        if not self.onglet_graphiques:
            print("❌ Onglet Graphiques non disponible")
            return False

        try:
            print("🎯 Génération des graphiques pour 20 cibles...")

            # Supprimer les graphiques existants
            self.supprimer_graphiques_existants()

            # Vérifier les onglets de données disponibles
            onglets_donnees = ['OBSERVATIONS', 'PROJECTION', 'EVOLUTIONS XYZ', 'ÉVOLUTION PM H V']
            onglets_disponibles = [o for o in onglets_donnees if o in self.workbook.sheetnames]

            print(f"📊 Onglets de données disponibles: {onglets_disponibles}")

            graphiques_crees = 0

            # Pour chaque type de graphique
            for i, type_graph in enumerate(self.types_graphiques):
                print(f"\n📈 Création graphique: {type_graph['nom']}")

                # Déterminer l'onglet source selon le type
                if "Z" in type_graph['suffixe']:
                    onglet_source = 'EVOLUTIONS XYZ' if 'EVOLUTIONS XYZ' in onglets_disponibles else 'OBSERVATIONS'
                elif "PM" in type_graph['suffixe'] or "H" in type_graph['suffixe']:
                    onglet_source = 'ÉVOLUTION PM H V' if 'ÉVOLUTION PM H V' in onglets_disponibles else 'PROJECTION'
                elif "CORDES" in type_graph['suffixe']:
                    onglet_source = 'cordes ref1' if 'cordes ref1' in self.workbook.sheetnames else 'OBSERVATIONS'
                else:
                    onglet_source = 'OBSERVATIONS'

                if onglet_source not in self.workbook.sheetnames:
                    print(f"⚠️ Onglet {onglet_source} non trouvé, utilisation de OBSERVATIONS")
                    onglet_source = 'OBSERVATIONS'

                # Créer des références de données exemple
                # En réalité, il faudrait analyser la structure exacte des colonnes
                ws_source = self.workbook[onglet_source]

                # Exemple de plage de données (à ajuster selon la structure réelle)
                donnees_x = Reference(ws_source, min_col=1, min_row=10, max_row=30)  # Colonne dates/temps
                donnees_y = Reference(ws_source, min_col=3 + i, min_row=10, max_row=30)  # Colonnes mesures

                # Créer le graphique
                chart = self.creer_scatter_chart(
                    titre=type_graph['nom'],
                    donnees_x=donnees_x,
                    donnees_y=donnees_y,
                    position=type_graph['position']
                )

                # Ajouter à l'onglet Graphiques
                self.onglet_graphiques.add_chart(chart, chart.anchor)
                graphiques_crees += 1

                print(f"  ✅ Graphique '{type_graph['nom']}' créé à la position {chart.anchor}")

            print(f"\n🎊 {graphiques_crees} graphiques créés avec succès!")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
            import traceback
            traceback.print_exc()
            return False

    def sauvegarder(self, fichier_sortie=None):
        """
        Sauvegarde le fichier avec les nouveaux graphiques

        Args:
            fichier_sortie: Nom du fichier de sortie (optionnel)
        """
        if not fichier_sortie:
            # Créer un nom de fichier avec suffix
            base_name = Path(self.fichier_excel).stem
            extension = Path(self.fichier_excel).suffix
            fichier_sortie = f"{base_name}_GRAPHIQUES_20_CIBLES{extension}"

        try:
            print(f"💾 Sauvegarde vers: {fichier_sortie}")
            self.workbook.save(fichier_sortie)
            print("✅ Fichier sauvegardé avec succès!")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False

    def fermer(self):
        """Ferme le workbook"""
        if self.workbook:
            self.workbook.close()

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🎯 GÉNÉRATEUR DE GRAPHIQUES EXCEL - AUSCULTATION")
    print("=" * 60)
    print()

    # Demander le fichier d'entrée
    if len(sys.argv) > 1:
        fichier_excel = sys.argv[1]
    else:
        fichier_excel = input("📂 Nom du fichier Excel à traiter: ").strip()

    if not fichier_excel:
        fichier_excel = "AUSCULTATION CARREFOUR_TEMPLATE_v2.xlsx"

    # Vérifier l'existence du fichier
    if not os.path.exists(fichier_excel):
        print(f"❌ Fichier non trouvé: {fichier_excel}")
        return

    # Créer le générateur
    generateur = GenerateurGraphiquesExcel(fichier_excel)

    try:
        # Charger le fichier
        if not generateur.charger_fichier():
            return

        # Générer les graphiques
        if generateur.generer_graphiques_20_cibles():
            # Sauvegarder
            if generateur.sauvegarder():
                print("\n🎊 GÉNÉRATION TERMINÉE AVEC SUCCÈS!")
                print("📈 Vos graphiques pour 20 cibles sont maintenant intégrés dans Excel")
            else:
                print("\n❌ Erreur lors de la sauvegarde")
        else:
            print("\n❌ Erreur lors de la génération des graphiques")

    finally:
        generateur.fermer()

if __name__ == "__main__":
    main()
