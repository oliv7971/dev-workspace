#!/usr/bin/env python3
"""
Démonstration complète de la saisie d'axes via Excel
Création des modèles Excel et test d'import/export
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from pathlib import Path
from core.geometrie import Point
from core.axe import AxeEnPlan, ProfilEnLong
from data_io.excel import ExcelIO
import math

def creer_modeles_excel():
    """Crée les modèles Excel pour la saisie d'axes"""
    print("=" * 80)
    print("📝 CRÉATION DES MODÈLES EXCEL POUR SAISIE D'AXES")
    print("=" * 80)
    
    # Créer le répertoire exemples
    exemples_dir = Path("exemples")
    exemples_dir.mkdir(exist_ok=True)
    
    # ========================================================================
    # 1. MODÈLE SAISIE PAR ÉLÉMENTS
    # ========================================================================
    print("\n1. 📋 Modèle saisie par éléments géométriques")
    
    # Feuille éléments
    elements_data = [
        {"Element": 1, "Type": "AD", "Param1": 50.0, "Param2": 150.0, "Param3": "", "Description": "Alignement 150m, Gis=50g"},
        {"Element": 2, "Type": "CL", "Param1": "", "Param2": 500.0, "Param3": 100.0, "Description": "Clothoïde ∞→R500m, L=100m"},
        {"Element": 3, "Type": "C", "Param1": 500.0, "Param2": 60.0, "Param3": "", "Description": "Arc R=500m, Δ=60g"},
        {"Element": 4, "Type": "CL", "Param1": 500.0, "Param2": "", "Param3": 100.0, "Description": "Clothoïde R500m→∞, L=100m"},
        {"Element": 5, "Type": "AD", "Param1": 110.0, "Param2": 200.0, "Param3": "", "Description": "Alignement 200m, Gis=110g"},
    ]
    
    # Feuille profil en long
    profil_data = []
    pm_values = [0, 50, 150, 250, 350, 450, 550]
    z_values = [100.0, 101.0, 103.0, 104.5, 106.0, 107.2, 108.5]
    
    for i, (pm, z) in enumerate(zip(pm_values, z_values)):
        if i > 0:
            pente = (z - z_values[i-1]) / (pm - pm_values[i-1]) * 100
        else:
            pente = 2.0
        
        profil_data.append({
            "PM": pm,
            "Z": z,
            "Pente": round(pente, 2),
            "Description": f"Point profil PM{pm}"
        })
    
    # Feuille paramètres
    parametres_data = [
        {"Parametre": "PM_Debut", "Valeur": 1000.0, "Unite": "m", "Description": "PM de début d'axe"},
        {"Parametre": "X_Debut", "Valeur": 500000.0, "Unite": "m", "Description": "Coordonnée X du début"},
        {"Parametre": "Y_Debut", "Valeur": 2000000.0, "Unite": "m", "Description": "Coordonnée Y du début"},
        {"Parametre": "Z_Debut", "Valeur": 100.0, "Unite": "m", "Description": "Altitude du début"},
        {"Parametre": "Systeme_Coord", "Valeur": "Lambert93", "Unite": "", "Description": "Système de coordonnées"},
        {"Parametre": "Nom_Axe", "Valeur": "RD123_Troncon_A", "Unite": "", "Description": "Nom de l'axe"},
    ]
    
    # Créer le fichier Excel
    fichier_elements = exemples_dir / "modele_saisie_elements.xlsx"
    with pd.ExcelWriter(fichier_elements, engine='openpyxl') as writer:
        pd.DataFrame(elements_data).to_excel(writer, sheet_name='Elements', index=False)
        pd.DataFrame(profil_data).to_excel(writer, sheet_name='Profil', index=False)
        pd.DataFrame(parametres_data).to_excel(writer, sheet_name='Parametres', index=False)
    
    print(f"  ✅ Créé: {fichier_elements}")
    print("     - Feuille 'Elements': Définition géométrique")
    print("     - Feuille 'Profil': Profil en long")
    print("     - Feuille 'Parametres': Configuration axe")
    
    # ========================================================================
    # 2. MODÈLE SAISIE PAR SOMMETS
    # ========================================================================
    print("\n2. 🎯 Modèle saisie par sommets")
    
    sommets_data = [
        {"Sommet": "S1", "X": 500000.0, "Y": 2000000.0, "Z": 100.0, "PM": 0.0, "Rayon": "", "Type": "Debut"},
        {"Sommet": "S2", "X": 500150.0, "Y": 2000000.0, "Z": 103.0, "PM": 150.0, "Rayon": 500.0, "Type": "Courbe_D"},
        {"Sommet": "S3", "X": 500300.0, "Y": 2000100.0, "Z": 106.0, "PM": 350.0, "Rayon": "", "Type": "Tangente"},
        {"Sommet": "S4", "X": 500500.0, "Y": 2000150.0, "Z": 108.5, "PM": 550.0, "Rayon": "", "Type": "Fin"},
    ]
    
    # Clothoïdes associées
    clothoides_data = [
        {"Sommet": "S2", "L_Entree": 100.0, "L_Sortie": 100.0, "A_Entree": 223.6, "A_Sortie": 223.6},
        {"Sommet": "S3", "L_Entree": 0.0, "L_Sortie": 0.0, "A_Entree": "", "A_Sortie": ""},
    ]
    
    fichier_sommets = exemples_dir / "modele_saisie_sommets.xlsx"
    with pd.ExcelWriter(fichier_sommets, engine='openpyxl') as writer:
        pd.DataFrame(sommets_data).to_excel(writer, sheet_name='Sommets', index=False)
        pd.DataFrame(clothoides_data).to_excel(writer, sheet_name='Clothoides', index=False)
        pd.DataFrame(parametres_data).to_excel(writer, sheet_name='Parametres', index=False)
    
    print(f"  ✅ Créé: {fichier_sommets}")
    print("     - Feuille 'Sommets': Points caractéristiques")
    print("     - Feuille 'Clothoides': Paramètres de transition")
    
    # ========================================================================
    # 3. MODÈLE POINTS À TRAITER
    # ========================================================================
    print("\n3. 📍 Modèle points à projeter")
    
    points_data = [
        {"ID": "P001", "X": 500075.0, "Y": 1999980.0, "Z": 102.5, "Type": "Borne", "Description": "Borne kilométrique"},
        {"ID": "P002", "X": 500125.0, "Y": 2000020.0, "Z": 103.2, "Type": "Ouvrage", "Description": "Buse DN800"},
        {"ID": "P003", "X": 500200.0, "Y": 1999950.0, "Z": 105.8, "Type": "Vegetation", "Description": "Arbre à abattre"},
        {"ID": "P004", "X": 500275.0, "Y": 2000080.0, "Z": 104.9, "Type": "Reseau", "Description": "Poteau EDF"},
        {"ID": "P005", "X": 500425.0, "Y": 2000125.0, "Z": 107.1, "Type": "Sondage", "Description": "Sondage géotechnique"},
    ]
    
    fichier_points = exemples_dir / "modele_points_a_traiter.xlsx"
    pd.DataFrame(points_data).to_excel(fichier_points, index=False)
    
    print(f"  ✅ Créé: {fichier_points}")
    print("     - Points externes à projeter sur l'axe")
    
    # ========================================================================
    # 4. MODÈLE RÉSULTATS
    # ========================================================================
    print("\n4. 📊 Modèle résultats (exemple)")
    
    resultats_data = [
        {"ID": "P001", "X": 500075.0, "Y": 1999980.0, "Z": 102.5, "PM": 1075.0, "Deport_H": -20.0, "Deport_V": 0.5, "Distance_3D": 20.01},
        {"ID": "P002", "X": 500125.0, "Y": 2000020.0, "Z": 103.2, "PM": 1125.0, "Deport_H": 20.0, "Deport_V": 0.2, "Distance_3D": 20.01},
        {"ID": "P003", "X": 500200.0, "Y": 1999950.0, "Z": 105.8, "PM": 1200.0, "Deport_H": -50.0, "Deport_V": 0.8, "Distance_3D": 50.01},
    ]
    
    fichier_resultats = exemples_dir / "exemple_resultats.xlsx"
    pd.DataFrame(resultats_data).to_excel(fichier_resultats, index=False)
    
    print(f"  ✅ Créé: {fichier_resultats}")
    
    return {
        'elements': fichier_elements,
        'sommets': fichier_sommets,
        'points': fichier_points,
        'resultats': fichier_resultats
    }

def tester_import_excel():
    """Test d'import depuis Excel"""
    print("\n" + "=" * 80)
    print("🔄 TEST D'IMPORT DEPUIS EXCEL")
    print("=" * 80)
    
    io_excel = ExcelIO()
    
    # Test import points
    print("\n1. 📍 Import de points")
    fichier_points = "exemples/modele_points_a_traiter.xlsx"
    
    try:
        points = io_excel.charger_points(fichier_points)
        print(f"  ✅ {len(points)} points chargés")
        
        for i, point in enumerate(points[:3]):  # Afficher les 3 premiers
            print(f"     Point {i+1}: ({point.x}, {point.y}, {point.z:.1f})")
            if hasattr(point, 'id'):
                print(f"               ID: {point.id}")
    except Exception as e:
        print(f"  ❌ Erreur import points: {e}")
    
    # Test import définition d'axe
    print("\n2. 🛤️ Import définition d'axe")
    fichier_elements = "exemples/modele_saisie_elements.xlsx"
    
    try:
        elements_def = io_excel.charger_definition_axe(fichier_elements)
        print(f"  ✅ {len(elements_def)} éléments chargés")
        
        for i, elem in enumerate(elements_def):
            print(f"     Élément {i+1}: {elem['type']} - {elem}")
    except Exception as e:
        print(f"  ❌ Erreur import éléments: {e}")
    
    # Test import profil
    print("\n3. 📈 Import profil en long")
    try:
        profil = io_excel.charger_profil_long(fichier_elements)
        print(f"  ✅ Profil chargé avec {len(profil.points)} points")
        
        for i, (pm, z) in enumerate(list(profil.points.items())[:3]):
            print(f"     PM {pm}m: Z={z:.2f}m")
    except Exception as e:
        print(f"  ❌ Erreur import profil: {e}")

def demo_workflow_complet():
    """Démonstration du workflow complet de saisie"""
    print("\n" + "=" * 80)
    print("🔄 WORKFLOW COMPLET DE SAISIE D'AXE")
    print("=" * 80)
    
    io_excel = ExcelIO()
    
    # Étape 1: Charger la définition d'axe
    print("\n📋 ÉTAPE 1: Chargement définition d'axe")
    try:
        elements_def = io_excel.charger_definition_axe("exemples/modele_saisie_elements.xlsx", "Elements")
        profil = io_excel.charger_profil_long("exemples/modele_saisie_elements.xlsx", "Profil")
        
        print(f"  ✅ {len(elements_def)} éléments géométriques")
        print(f"  ✅ Profil avec {len(profil.points)} points")
    except Exception as e:
        print(f"  ❌ Erreur chargement: {e}")
        return
    
    # Étape 2: Construire l'axe
    print("\n🏗️ ÉTAPE 2: Construction de l'axe")
    axe = AxeEnPlan("Axe depuis Excel")
    axe.pm_debut = 1000.0
    
    # Point de départ
    pt_debut = Point(500000.0, 2000000.0, 100.0)
    pt_courant = pt_debut
    gis_courant = 50.0  # Premier gisement
    
    try:
        for i, elem_def in enumerate(elements_def):
            if elem_def['type'] == 'AD':
                # Alignement droit
                gis_courant = elem_def['gisement']
                longueur = elem_def['longueur']
                
                # Calculer le point final
                gis_rad = gis_courant * math.pi / 200
                pt_fin = Point(
                    pt_courant.x + longueur * math.sin(gis_rad),
                    pt_courant.y + longueur * math.cos(gis_rad),
                    pt_courant.z + longueur * 0.02  # Pente 2%
                )
                
                alignement = axe.ajouter_alignement(pt_courant, pt_fin)
                print(f"  ✅ Alignement {i+1}: {longueur:.0f}m, gis={gis_courant:.1f}g")
                pt_courant = pt_fin
                
            elif elem_def['type'] == 'C':
                # Arc circulaire (implémentation simplifiée)
                rayon = elem_def['rayon']
                if 'deviation' in elem_def:
                    deviation = elem_def['deviation']
                else:
                    deviation = 60.0  # Par défaut
                
                # Calculer centre et angles (approximatif)
                centre = Point(pt_courant.x + rayon, pt_courant.y, pt_courant.z)
                angle_debut = gis_courant
                angle_fin = (gis_courant + deviation) % 400
                
                arc = axe.ajouter_arc(centre, rayon, angle_debut, angle_fin)
                print(f"  ✅ Arc {i+1}: R={rayon:.0f}m, Δ={deviation:.1f}g")
                gis_courant = angle_fin
                
            elif elem_def['type'] == 'CL':
                # Clothoïde (implémentation simplifiée)
                rayon_debut = elem_def.get('rayon_debut', float('inf'))
                rayon_fin = elem_def.get('rayon_fin', float('inf'))
                longueur = elem_def['longueur']
                
                clothoide = axe.ajouter_clothoide(pt_courant, gis_courant, rayon_debut, rayon_fin, longueur)
                print(f"  ✅ Clothoïde {i+1}: L={longueur:.0f}m")
                
                # Mettre à jour position (approximatif)
                gis_rad = gis_courant * math.pi / 200
                pt_courant = Point(
                    pt_courant.x + longueur * math.sin(gis_rad),
                    pt_courant.y + longueur * math.cos(gis_rad),
                    pt_courant.z + longueur * 0.02
                )
        
        print(f"\n  🎯 Axe construit: {axe.longueur_totale():.1f}m total")
        
    except Exception as e:
        print(f"  ❌ Erreur construction: {e}")
        return
    
    # Étape 3: Charger points à traiter
    print("\n📍 ÉTAPE 3: Chargement points à projeter")
    try:
        points = io_excel.charger_points("exemples/modele_points_a_traiter.xlsx")
        print(f"  ✅ {len(points)} points chargés")
    except Exception as e:
        print(f"  ❌ Erreur chargement points: {e}")
        return
    
    # Étape 4: Calculs de projection
    print("\n🎯 ÉTAPE 4: Projections sur l'axe")
    resultats = []
    
    for point in points:
        try:
            pm, deport = axe.projeter_point(point)
            pt_proj = axe.point_at_pm(pm)
            distance_3d = ((point.x - pt_proj.x)**2 + (point.y - pt_proj.y)**2 + (point.z - pt_proj.z)**2)**0.5
            
            resultat = {
                'ID': getattr(point, 'id', 'P?'),
                'X': point.x,
                'Y': point.y,
                'Z': point.z,
                'PM': pm,
                'Deport_H': deport,
                'Deport_V': point.z - pt_proj.z,
                'Distance_3D': distance_3d
            }
            
            resultats.append(resultat)
            print(f"  📍 {resultat['ID']}: PM={pm:.1f}m, Dép={deport:.1f}m")
            
        except Exception as e:
            print(f"  ❌ Erreur projection {getattr(point, 'id', '?')}: {e}")
    
    # Étape 5: Export des résultats
    print("\n💾 ÉTAPE 5: Export des résultats")
    try:
        fichier_sortie = "exemples/resultats_calculs.xlsx"
        df_resultats = pd.DataFrame(resultats)
        df_resultats.to_excel(fichier_sortie, index=False)
        print(f"  ✅ Résultats exportés: {fichier_sortie}")
        print(f"     {len(resultats)} points traités")
        
        # Statistiques
        deports = [r['Deport_H'] for r in resultats]
        print(f"     Déport min: {min(deports):.1f}m")
        print(f"     Déport max: {max(deports):.1f}m")
        print(f"     Déport moyen: {sum(deports)/len(deports):.1f}m")
        
    except Exception as e:
        print(f"  ❌ Erreur export: {e}")

def creer_documentation():
    """Crée la documentation des formats Excel"""
    print("\n" + "=" * 80)
    print("📚 DOCUMENTATION DES FORMATS EXCEL")
    print("=" * 80)
    
    doc_content = """
# Guide de Saisie d'Axes via Excel

## 📋 Formats Supportés

### 1. Saisie par Éléments Géométriques

**Fichier**: `modele_saisie_elements.xlsx`

#### Feuille "Elements"
| Colonne | Description | Exemples |
|---------|-------------|----------|
| Element | Numéro d'ordre | 1, 2, 3, ... |
| Type | Type d'élément | AD, C, CL |
| Param1 | Premier paramètre | Gisement (AD), Rayon (C), R_début (CL) |
| Param2 | Second paramètre | Longueur (AD), Déviation (C), R_fin (CL) |
| Param3 | Troisième paramètre | - (AD), - (C), Longueur (CL) |

**Types d'éléments:**
- **AD** (Alignement Droit): Param1=Gisement(g), Param2=Longueur(m)
- **C** (Arc Circulaire): Param1=Rayon(m), Param2=Déviation(g) ou Longueur(m)
- **CL** (Clothoïde): Param1=R_début(m), Param2=R_fin(m), Param3=Longueur(m)

#### Feuille "Profil"
| Colonne | Description | Unité |
|---------|-------------|-------|
| PM | Point métrique | m |
| Z | Altitude | m |
| Pente | Pente locale | % |

#### Feuille "Parametres"
| Paramètre | Description |
|-----------|-------------|
| PM_Debut | PM de début d'axe |
| X_Debut | Coordonnée X de début |
| Y_Debut | Coordonnée Y de début |
| Z_Debut | Altitude de début |
| Nom_Axe | Nom de l'axe |

### 2. Saisie par Points à Projeter

**Fichier**: `modele_points_a_traiter.xlsx`

| Colonne | Description | Obligatoire |
|---------|-------------|-------------|
| ID | Identifiant unique | Oui |
| X | Coordonnée X | Oui |
| Y | Coordonnée Y | Oui |
| Z | Altitude | Non |
| Type | Type de point | Non |
| Description | Description | Non |

### 3. Fichier de Résultats

**Fichier**: `resultats_calculs.xlsx`

| Colonne | Description |
|---------|-------------|
| ID | Identifiant du point |
| X, Y, Z | Coordonnées originales |
| PM | Point métrique sur l'axe |
| Deport_H | Déport horizontal (+ = droite) |
| Deport_V | Déport vertical |
| Distance_3D | Distance 3D au point projeté |

## 🔄 Workflow de Travail

1. **Préparation**: Utiliser les modèles Excel fournis
2. **Saisie géométrie**: Remplir la définition d'axe
3. **Import**: Charger l'axe dans le calculateur
4. **Points**: Ajouter les points à traiter
5. **Calculs**: Lancer les projections
6. **Export**: Récupérer les résultats Excel

## ⚠️ Conventions Importantes

- **Gisements**: En grades (0-400g), Nord = 0g, sens horaire
- **Coordonnées**: Système Lambert ou local
- **Déports**: Positifs à droite de l'axe
- **Rayons**: Positifs = virage droite, négatifs = virage gauche
- **Clothoïdes**: Rayon infini = alignement (laisser vide)

## 🎯 Exemples Pratiques

Les fichiers modèles contiennent des données réalistes pour tester le système.
"""
    
    # Sauvegarder la documentation
    with open("exemples/GUIDE_SAISIE_EXCEL.md", "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    print("  ✅ Documentation créée: exemples/GUIDE_SAISIE_EXCEL.md")

def main():
    """Fonction principale"""
    print("🚀 DÉMONSTRATION COMPLÈTE - SAISIE D'AXES VIA EXCEL")
    
    # 1. Créer les modèles
    fichiers = creer_modeles_excel()
    
    # 2. Tester les imports
    tester_import_excel()
    
    # 3. Workflow complet
    demo_workflow_complet()
    
    # 4. Documentation
    creer_documentation()
    
    print("\n" + "=" * 80)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 80)
    print("📁 Fichiers créés dans le dossier 'exemples/':")
    print("   - modele_saisie_elements.xlsx (Définition d'axe)")
    print("   - modele_saisie_sommets.xlsx (Saisie par sommets)")
    print("   - modele_points_a_traiter.xlsx (Points à projeter)")
    print("   - exemple_resultats.xlsx (Format de sortie)")
    print("   - GUIDE_SAISIE_EXCEL.md (Documentation)")
    print("\n🎯 Le système est prêt pour la saisie d'axes via Excel !")

if __name__ == "__main__":
    main()