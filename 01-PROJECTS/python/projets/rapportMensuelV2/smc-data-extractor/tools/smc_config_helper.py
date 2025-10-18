#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration rapide pour l'interface SMC GUI
Permet de modifier facilement les valeurs par défaut
"""

import os
from datetime import datetime

class SMCConfig:
    """Configuration pour l'interface SMC"""

    # Chemins par défaut
    BASE_CHANTIER_PATH = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité"
    DEFAULT_OUTPUT_PATH = r"C:\temp\smc_output"

    @staticmethod
    def get_current_month():
        """Retourne le mois actuel au format YYYY-MM"""
        return datetime.now().strftime("%Y-%m")

    @staticmethod
    def get_previous_month():
        """Retourne le mois précédent au format YYYY-MM"""
        current = datetime.now()
        if current.month == 1:
            return f"{current.year - 1}-12"
        else:
            return f"{current.year}-{current.month - 1:02d}"

    @staticmethod
    def build_monthly_path(year, month):
        """Construit le chemin complet pour un mois donné"""
        month_names = {
            1: "janvier", 2: "février", 3: "mars", 4: "avril",
            5: "mai", 6: "juin", 7: "juillet", 8: "août",
            9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
        }

        month_num = int(month)
        month_name = month_names[month_num]

        # Format: 250901-rapport mensuel septembre
        folder_name = f"{year}{month:02d}01-rapport mensuel {month_name}"

        return os.path.join(
            SMCConfig.BASE_CHANTIER_PATH,
            str(year),
            folder_name,
            "1-tableaux"
        )

    @staticmethod
    def suggest_paths():
        """Suggère les chemins les plus probables"""
        current_month = SMCConfig.get_current_month()
        previous_month = SMCConfig.get_previous_month()

        year, month = current_month.split('-')
        prev_year, prev_month = previous_month.split('-')

        current_path = SMCConfig.build_monthly_path(int(year), int(month))
        previous_path = SMCConfig.build_monthly_path(int(prev_year), int(prev_month))

        print("📁 CHEMINS SUGGÉRÉS POUR SMC")
        print("=" * 50)
        print(f"📅 Mois actuel ({current_month}):")
        print(f"   {current_path}")
        print(f"   Existe: {'✅' if os.path.exists(current_path) else '❌'}")
        print()
        print(f"📅 Mois précédent ({previous_month}):")
        print(f"   {previous_path}")
        print(f"   Existe: {'✅' if os.path.exists(previous_path) else '❌'}")
        print()
        print(f"💾 Sortie par défaut:")
        print(f"   {SMCConfig.DEFAULT_OUTPUT_PATH}")

if __name__ == "__main__":
    SMCConfig.suggest_paths()
