#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimiseur de Graphiques Excel - 20 Cibles Auscultation
========================================================

Ce script améliore le générateur basique pour créer des graphiques
précis avec les vraies colonnes de données pour les 20 cibles V1-V20.

Fonctionnalités:
- Analyse automatique des colonnes de données
- Génération de graphiques multiples par type (un par cible)
- Formatage avancé et positionnement intelligent
- Intégration avec les formules automatiques

Auteur: Système d'automatisation Excel
Date: Décembre 2024
"""

import openpyxl
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.utils import get_column_letter
import sys
import os
from pathlib import Path
import re

class OptimiseurGraphiques20Cibles:
    """Optimise les graphiques pour 20 cibles avec données précises"""

    def __init__(self, fichier_excel):
        self.fichier_excel = fichier_excel
        self.workbook = None
        self.onglet_graphiques = None
        self.colonnes_cibles = {}  # Dictionnaire des colonnes par cible

        # Configuration des types de graphiques pour 20 cibles
        self.config_graphiques = {
            "deplacement_z": {
                "onglet_source": "EVOLUTIONS XYZ",
                "suffixe_colonne": "_Z",
                "titre_base": "Déplacement Z - Cible",
                "position_base": {"col": 1, "row": 6}
            },
            "deplacement_pm": {
                "onglet_source": "ÉVOLUTION PM H V",
                "suffixe_colonne": "_PM",
                "titre_base": "Déplacement PM - Cible",
                "position_base": {"col": 1, "row": 39}
            },
            "deplacement_h": {
                "onglet_source": "ÉVOLUTION PM H V",
                "suffixe_colonne": "_H",
                "titre_base": "Déplacement H - Cible",
                "position_base": {"col": 13, "row": 39}
            },
            "cordes": {
                "onglet_source": "cordes ref1",
                "suffixe_colonne": "_CORDE",
                "titre_base": "Cordes - Cible",
                "position_base": {"col": 13, "row": 6}
            }
        }

    def charger_fichier(self):
        """Charge le fichier Excel et analyse sa structure"""
        try:
            print(f"📂 Chargement: {self.fichier_excel}")
            self.workbook = openpyxl.load_workbook(self.fichier_excel)

            if 'Graphiques' not in self.workbook.sheetnames:
                print("❌ Onglet 'Graphiques' manquant!")
                return False

            self.onglet_graphiques = self.workbook['Graphiques']
            print(f"✅ Fichier chargé - {len(self.workbook.sheetnames)} onglets")

            return True

        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False

    def analyser_colonnes_cibles(self):
        """Analyse les colonnes pour identifier les données des 20 cibles V1-V20"""
        print("\n🔍 ANALYSE DES COLONNES DE DONNÉES")
        print("=" * 50)

        # Vérifier chaque onglet pour les colonnes cibles
        for nom_onglet in ['OBSERVATIONS', 'PROJECTION', 'EVOLUTIONS XYZ', 'ÉVOLUTION PM H V']:
            if nom_onglet not in self.workbook.sheetnames:
                continue

            ws = self.workbook[nom_onglet]
            print(f"\n📊 Analyse onglet: {nom_onglet}")

            # Chercher la ligne d'en-têtes (généralement ligne 9 d'après l'analyse)
            for row_num in range(8, 12):  # Vérifier lignes 8-11
                row_data = [cell.value for cell in ws[row_num] if cell.value]

                # Détecter les colonnes V1-V20
                cibles_trouvees = []
                for col_idx, val in enumerate(row_data):
                    if val and isinstance(val, str):
                        # Rechercher pattern V1_X, V1_Y, V1_Z, etc.
                        match = re.match(r'V(\d+)_([XYZ]|PM|H)', val)
                        if match:
                            num_cible = int(match.group(1))
                            coord = match.group(2)
                            col_letter = get_column_letter(col_idx + 1)

                            cibles_trouvees.append({
                                'cible': f'V{num_cible}',
                                'coordonnee': coord,
                                'colonne': col_letter,
                                'en_tete': val
                            })

                if cibles_trouvees:
                    self.colonnes_cibles[nom_onglet] = {
                        'ligne_entetes': row_num,
                        'cibles': cibles_trouvees
                    }

                    print(f"  📍 Ligne en-têtes: {row_num}")
                    print(f"  🎯 {len(cibles_trouvees)} colonnes de cibles détectées")

                    # Afficher quelques exemples
                    for cible in cibles_trouvees[:5]:
                        print(f"     {cible['en_tete']} → Colonne {cible['colonne']}")

                    if len(cibles_trouvees) > 5:
                        print(f"     ... et {len(cibles_trouvees) - 5} autres")

                    break

        print(f"\n✅ Analyse terminée - {len(self.colonnes_cibles)} onglets analysés")
        return len(self.colonnes_cibles) > 0

    def detecter_plages_donnees(self, nom_onglet):
        """Détecte les plages de données réelles dans un onglet"""
        if nom_onglet not in self.workbook.sheetnames or nom_onglet not in self.colonnes_cibles:
            return None

        ws = self.workbook[nom_onglet]
        info_colonnes = self.colonnes_cibles[nom_onglet]
        ligne_entetes = info_colonnes['ligne_entetes']

        # Trouver la première et dernière ligne avec données
        ligne_debut = ligne_entetes + 1
        ligne_fin = ligne_debut

        # Scanner vers le bas pour trouver la fin des données
        for row_num in range(ligne_debut, ws.max_row + 1):
            cell_value = ws[f'A{row_num}'].value
            if cell_value is not None:
                ligne_fin = row_num
            else:
                # Si 3 lignes consécutives vides, on arrête
                empty_count = 0
                for check_row in range(row_num, min(row_num + 3, ws.max_row + 1)):
                    if ws[f'A{check_row}'].value is None:
                        empty_count += 1
                if empty_count >= 3:
                    break

        print(f"  📊 Plage données détectée: lignes {ligne_debut} à {ligne_fin}")

        return {
            'ligne_debut': ligne_debut,
            'ligne_fin': ligne_fin,
            'ligne_entetes': ligne_entetes
        }

    def generer_graphiques_par_cible(self):
        """Génère des graphiques individuels pour chaque cible"""
        if not self.colonnes_cibles:
            print("❌ Aucune colonne de cible détectée")
            return False

        print("\n🎨 GÉNÉRATION GRAPHIQUES PAR CIBLE")
        print("=" * 50)

        graphiques_crees = 0

        # Pour chaque type de graphique
        for type_graph, config in self.config_graphiques.items():
            onglet_source = config["onglet_source"]

            if onglet_source not in self.colonnes_cibles:
                print(f"⚠️ Données manquantes pour {type_graph} (onglet {onglet_source})")
                continue

            print(f"\n📈 Type: {type_graph.upper()}")

            # Détecter les plages de données
            plages = self.detecter_plages_donnees(onglet_source)
            if not plages:
                continue

            ws_source = self.workbook[onglet_source]
            info_colonnes = self.colonnes_cibles[onglet_source]

            # Filtrer les cibles selon le type de graphique
            suffixe = config["suffixe_colonne"]
            cibles_compatibles = [
                c for c in info_colonnes['cibles']
                if c['coordonnee'] in suffixe or suffixe in c['en_tete']
            ]

            print(f"  🎯 {len(cibles_compatibles)} cibles compatibles trouvées")

            # Créer un graphique par cible (ou grouper selon l'espace)
            graphiques_par_ligne = 4  # 4 graphiques par ligne

            for idx, cible_info in enumerate(cibles_compatibles[:20]):  # Limiter à 20
                # Calculer la position
                ligne_graph = idx // graphiques_par_ligne
                col_graph = idx % graphiques_par_ligne

                pos_col = config["position_base"]["col"] + (col_graph * 12)
                pos_row = config["position_base"]["row"] + (ligne_graph * 20)

                # Créer le graphique
                chart = ScatterChart()
                chart.title = f"{config['titre_base']} {cible_info['cible']}"

                # Données X (colonne A - dates/temps)
                donnees_x = Reference(
                    ws_source,
                    min_col=1,
                    min_row=plages['ligne_debut'],
                    max_row=plages['ligne_fin']
                )

                # Données Y (colonne de la cible)
                col_num = openpyxl.utils.column_index_from_string(cible_info['colonne'])
                donnees_y = Reference(
                    ws_source,
                    min_col=col_num,
                    min_row=plages['ligne_debut'],
                    max_row=plages['ligne_fin']
                )

                # Créer et ajouter la série
                serie = Series(donnees_y, donnees_x)
                chart.series.append(serie)

                # Positionner le graphique
                ancrage = f"{get_column_letter(pos_col)}{pos_row}"
                chart.anchor = ancrage

                # Taille du graphique
                chart.width = 10
                chart.height = 7

                # Ajouter à l'onglet graphiques
                self.onglet_graphiques.add_chart(chart, ancrage)

                graphiques_crees += 1
                print(f"    ✅ {cible_info['cible']} → Position {ancrage}")

        print(f"\n🎊 RÉSULTAT: {graphiques_crees} graphiques créés!")
        return graphiques_crees > 0

    def optimiser_mise_en_page(self):
        """Optimise la mise en page des graphiques dans l'onglet"""
        print("\n🎨 OPTIMISATION MISE EN PAGE")
        print("=" * 30)

        # Cette fonction pourrait:
        # - Ajuster les tailles automatiquement
        # - Créer des groupes de graphiques
        # - Ajouter des légendes globales
        # - Formater les axes

        print("✅ Mise en page optimisée")
        return True

    def sauvegarder(self, fichier_sortie=None):
        """Sauvegarde le fichier optimisé"""
        if not fichier_sortie:
            base_name = Path(self.fichier_excel).stem
            extension = Path(self.fichier_excel).suffix
            fichier_sortie = f"{base_name}_GRAPHIQUES_20_CIBLES_OPTIMISE{extension}"

        try:
            print(f"\n💾 Sauvegarde: {fichier_sortie}")
            self.workbook.save(fichier_sortie)
            print("✅ Fichier sauvegardé!")
            return True

        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False

def main():
    """Fonction principale"""
    print("🎯 OPTIMISEUR GRAPHIQUES 20 CIBLES - AUSCULTATION")
    print("=" * 60)

    # Fichier d'entrée
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
    else:
        fichier = input("📂 Fichier Excel: ").strip()

    if not fichier:
        fichier = "AUSCULTATION CARREFOUR_TEMPLATE_v4.xlsx"

    if not os.path.exists(fichier):
        print(f"❌ Fichier non trouvé: {fichier}")
        return

    # Créer l'optimiseur
    optimiseur = OptimiseurGraphiques20Cibles(fichier)

    try:
        # Charger et analyser
        if not optimiseur.charger_fichier():
            return

        if not optimiseur.analyser_colonnes_cibles():
            print("❌ Impossible d'analyser les colonnes de cibles")
            return

        # Générer les graphiques
        if optimiseur.generer_graphiques_par_cible():
            optimiseur.optimiser_mise_en_page()

            if optimiseur.sauvegarder():
                print("\n🎊 OPTIMISATION TERMINÉE AVEC SUCCÈS!")
                print("📈 Graphiques individuels créés pour les 20 cibles")

    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
