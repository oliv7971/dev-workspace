#!/usr/bin/env python3
"""
Calculs de déports par rapport à l'axe de référence
"""

import math
import openpyxl
from openpyxl.utils import get_column_letter

class AxeReference:
    def __init__(self):
        # Définition de l'axe à partir des données fournies
        self.pk_debut = 0.0
        self.pk_fin = 100.0
        self.x_debut = 823216.6581
        self.y_debut = 1091503.0821
        self.x_fin = 823258.9200
        self.y_fin = 1091412.4514
        self.azimut_gr = 172.2222  # en grades
        self.z_ref = -123.621  # altitude de référence
        self.pente = 0.0  # pente en %

        # Conversion azimut en radians
        self.azimut_rad = self.azimut_gr * (math.pi / 200)  # grades vers radians

        # Calcul des composantes directionnelles
        self.dx = self.x_fin - self.x_debut
        self.dy = self.y_fin - self.y_debut
        self.longueur_axe = math.sqrt(self.dx**2 + self.dy**2)

    def calculer_deports(self, x_mesure, y_mesure, z_mesure):
        """Calcule les déports par rapport à l'axe"""

        # Vecteur du point de départ vers le point mesuré
        dx_mesure = x_mesure - self.x_debut
        dy_mesure = y_mesure - self.y_debut

        # Projection sur l'axe (déport longitudinal)
        projection_long = (dx_mesure * self.dx + dy_mesure * self.dy) / self.longueur_axe
        pk_projete = self.pk_debut + projection_long

        # Point projeté sur l'axe
        ratio = projection_long / self.longueur_axe
        x_projete = self.x_debut + ratio * self.dx
        y_projete = self.y_debut + ratio * self.dy

        # Déport transversal (distance perpendiculaire à l'axe)
        dx_transversal = x_mesure - x_projete
        dy_transversal = y_mesure - y_projete
        deport_transversal = math.sqrt(dx_transversal**2 + dy_transversal**2)

        # Signe du déport transversal (gauche/droite)
        # Produit vectoriel pour déterminer le côté
        produit_vectoriel = self.dx * dy_transversal - self.dy * dx_transversal
        if produit_vectoriel < 0:
            deport_transversal = -deport_transversal

        # Déport vertical
        z_theorique = self.z_ref + (projection_long * self.pente / 100)
        deport_vertical = z_mesure - z_theorique

        return {
            'pk': pk_projete,
            'deport_transversal': deport_transversal,
            'deport_longitudinal': projection_long,
            'deport_vertical': deport_vertical,
            'x_projete': x_projete,
            'y_projete': y_projete,
            'z_projete': z_theorique
        }

def creer_systeme_avec_deports():
    """Crée un système Excel avec calculs de déports par rapport à l'axe"""

    print("🎯 Création du système avec déports par rapport à l'axe...")

    # Test des calculs
    axe = AxeReference()

    # Exemple de calcul
    x_test, y_test, z_test = 823230.0, 1091480.0, -123.5
    deports = axe.calculer_deports(x_test, y_test, z_test)

    print(f"📊 Test des calculs de déports:")
    print(f"   Point test: X={x_test}, Y={y_test}, Z={z_test}")
    print(f"   PK projeté: {deports['pk']:.3f}")
    print(f"   Déport transversal: {deports['deport_transversal']:.3f} m")
    print(f"   Déport longitudinal: {deports['deport_longitudinal']:.3f} m")
    print(f"   Déport vertical: {deports['deport_vertical']:.3f} m")

    return axe

def generer_formules_deports():
    """Génère les formules Excel pour les calculs de déports"""

    print("📝 Génération des formules Excel pour les déports...")

    # Paramètres de l'axe
    axe_info = {
        'X_DEBUT': 823216.6581,
        'Y_DEBUT': 1091503.0821,
        'X_FIN': 823258.9200,
        'Y_FIN': 1091412.4514,
        'Z_REF': -123.621,
        'PK_DEBUT': 0.0,
        'PK_FIN': 100.0
    }

    # Formules Excel (à adapter selon les colonnes)
    formules = {
        'DX_AXE': f"={axe_info['X_FIN']}-{axe_info['X_DEBUT']}",
        'DY_AXE': f"={axe_info['Y_FIN']}-{axe_info['Y_DEBUT']}",
        'LONGUEUR_AXE': f"=SQRT(DX_AXE^2+DY_AXE^2)",

        'DEPORT_TRANSVERSAL': """=LET(
            dx_mes, X_MESURE-X_DEBUT,
            dy_mes, Y_MESURE-Y_DEBUT,
            proj_long, (dx_mes*DX_AXE + dy_mes*DY_AXE)/LONGUEUR_AXE,
            ratio, proj_long/LONGUEUR_AXE,
            x_proj, X_DEBUT + ratio*DX_AXE,
            y_proj, Y_DEBUT + ratio*DY_AXE,
            dx_trans, X_MESURE-x_proj,
            dy_trans, Y_MESURE-y_proj,
            deport_abs, SQRT(dx_trans^2+dy_trans^2),
            signe, IF((DX_AXE*dy_trans - DY_AXE*dx_trans)<0, -1, 1),
            deport_abs * signe
        )""",

        'PK_PROJETE': """=LET(
            dx_mes, X_MESURE-X_DEBUT,
            dy_mes, Y_MESURE-Y_DEBUT,
            proj_long, (dx_mes*DX_AXE + dy_mes*DY_AXE)/LONGUEUR_AXE,
            PK_DEBUT + proj_long
        )""",

        'DEPORT_VERTICAL': f"=Z_MESURE - {axe_info['Z_REF']}"
    }

    # Sauvegarder les formules
    with open("FORMULES_DEPORTS_AXE.txt", "w", encoding="utf-8") as f:
        f.write("📐 FORMULES EXCEL POUR CALCULS DE DÉPORTS\n\n")
        f.write("PARAMÈTRES DE L'AXE:\n")
        for param, valeur in axe_info.items():
            f.write(f"{param}: {valeur}\n")
        f.write("\nFORMULES:\n")
        for nom, formule in formules.items():
            f.write(f"\n{nom}:\n{formule}\n")

    print("✅ Formules sauvées: FORMULES_DEPORTS_AXE.txt")

if __name__ == "__main__":
    print("🚀 Système de calculs de déports par rapport à l'axe...")

    # Créer le système de calculs
    axe = creer_systeme_avec_deports()

    # Générer les formules
    generer_formules_deports()

    print(f"\\n🎉 SYSTÈME DE DÉPORTS PRÊT!")
    print(f"\\n📐 AXE DÉFINI:")
    print(f"   - Origine: PK 0 -> X=823216.66, Y=1091503.08, Z=-123.62")
    print(f"   - Fin: PK 100 -> X=823258.92, Y=1091412.45, Z=-123.62")
    print(f"   - Azimut: 172.2222 gr")
    print(f"   - Pente: 0.0%")

    print(f"\\n💡 CALCULS DISPONIBLES:")
    print(f"   - Déport transversal (⊥ à l'axe, + à droite)")
    print(f"   - PK projeté sur l'axe")
    print(f"   - Déport vertical (par rapport à Z=-123.62)")

    print(f"\\nVoulez-vous que je modifie le fichier Excel pour utiliser ces calculs de déports ?")
