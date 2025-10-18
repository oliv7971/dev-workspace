# 🎯 SYSTÈME D'EXTRACTION UNIFIÉ SMC & CARRURE

**Version :** 2.0 - Extension Carrure
**Date :** 2 octobre 2025

## 🚀 NOUVEAUTÉS VERSION 2.0

### ✅ SUPPORT AUSCULTATION DE CARRURE
- **Nouveau module :** `carrure_extractor.py`
- **Interface unifiée :** `unified_gui.py`
- **Détection automatique** des types de fichiers (SMC + Carrure)
- **Extraction parallèle** des deux formats

## 📊 TYPES DE DONNÉES SUPPORTÉS

### 🔧 SMC (existant)
- **Onglets :** Convergences, Déplacements, Résultats observations
- **Données :** Convergences, déplacements de points, coordonnées XYZ
- **Format :** Fichiers contenant "SMC" dans le nom

### 🏗️ CARRURE (nouveau)
- **Onglets :** Déplacements carrure, Déplacements cintres-longerons
- **Données :** Déplacements des points de carrure, mesures de cintres
- **Format :** Fichiers contenant "carrure" dans le nom

## 🎮 UTILISATION

### Interface Unifiée (Recommandée)
```bash
python unified_gui.py
```

**Fonctionnalités :**
- 🤖 **Détection automatique** - Traite SMC et Carrure automatiquement
- 🔧 **SMC uniquement** - Mode spécialisé SMC
- 🏗️ **Carrure uniquement** - Mode spécialisé Carrure
- 📁 **Séparation optionnelle** - Sous-dossiers SMC/ et CARRURE/

### Interfaces Spécialisées
```bash
# Interface SMC originale
python src/smc_gui.py

# Extraction carrure en ligne de commande
python carrure_extractor.py
```

## 📁 STRUCTURE PROJET

```
smc-data-extractor/
├── 🆕 unified_gui.py              # Interface unifiée principale
├── 🆕 carrure_extractor.py        # Module extraction carrure
├── src/
│   ├── smc_gui.py                 # Interface SMC originale
│   └── smc_evolutions.py          # Module extraction SMC
├── tools/
│   ├── 🆕 carrure_analyzer.py     # Analyseur fichiers carrure
│   ├── 🆕 demo_carrure_extraction.py # Démonstration carrure
│   ├── smc_config_helper.py       # Assistant configuration
│   └── test_extractor_columns.py  # Tests colonnes SMC
├── config/                        # Fichiers de configuration
├── 🆕 archive/                    # Versions archivées
└── docs/                          # Documentation
```

## 🔍 DÉTECTION AUTOMATIQUE

Le système détecte automatiquement les types de fichiers :

**SMC :** `*SMC*.xlsx`, `*SMC*.xlsm`
**Carrure :** `*carrure*.xlsx`, `*carrure*.xlsm`

### Exemple de détection
```
📁 Source: .../1-tableaux/
├── GGS/
│   ├── 03_104-GGS_SMC_C003_PM001_25_08-25.xlsm     ← SMC
│   └── 03_100-GGS-GRD-double carrure-XYZ-25-09-10.xlsm ← CARRURE
```

## 📊 DONNÉES EXTRAITES

### SMC (format existant)
- `convergences_summary.csv` - Synthèse des convergences
- `deplacements_points.csv` - Déplacements des points
- `recap_ligne_*.csv` - Récapitulatifs en ligne

### Carrure (nouveau format)
- `carrure_deplacements.csv` - Déplacements de carrure (36+ lignes)
- `cintres_deplacements.csv` - Déplacements des cintres (37+ lignes)
- `carrure_summary_report.txt` - Rapport de synthèse

### Structure des données Carrure
```csv
# carrure_deplacements.csv
date,jours_ecoules,front,file_type,sheet_name,point_1_dpm,point_1_dh,point_1_dz,...
2023-11-03,1,<valeur>,carrure,Déplacements carrure,-0.403,0.510,-0.299,...

# cintres_deplacements.csv
date,jours_ecoules,front,file_type,sheet_name,cintre_col_4,cintre_col_5,...
2023-11-03,1,<valeur>,carrure,Déplacements cintres-longerons,<valeur>,<valeur>,...
```

## ⚙️ OPTIONS D'EXTRACTION

- ✅ **Générer CSV** - Export des données en format CSV
- ✅ **Récapitulatifs en ligne** - Synthèses additionnelles
- ✅ **Séparation par type** - Sous-dossiers SMC/ et CARRURE/

## 🔧 CONFIGURATION

### Chemins par défaut mis à jour
```python
# Septembre 2025 (ajusté depuis août)
default_path = r"C:\data\11-CHANTIERS\BURE\...\250902-rapport mensuel septembre\1-tableaux"
month = "2025-09"
```

### Assistant de configuration
```bash
python tools/smc_config_helper.py
```
Suggère automatiquement les chemins selon le mois actuel.

## 🧪 TESTS ET VALIDATION

### Tests disponibles
```bash
# Test extraction carrure
python tools/demo_carrure_extraction.py

# Analyse structure fichiers
python tools/carrure_analyzer.py

# Test interface unifiée
python -c "import unified_gui; print('✅ Interface OK')"
```

### Validation données
- **Période couverte :** 2023-11-03 à 2025-09-10
- **Volume Carrure :** 36 lignes déplacements + 37 lignes cintres
- **Cohérence dates :** Parsing automatique format Excel

## 📈 ÉVOLUTIONS APPORTÉES

### Depuis version 1.0 (SMC uniquement)
1. ✅ **Extension Carrure** - Support complet nouveau format
2. ✅ **Interface unifiée** - Gestion simultanée SMC + Carrure
3. ✅ **Détection automatique** - Plus besoin de choisir manuellement
4. ✅ **Architecture modulaire** - Extracteurs indépendants
5. ✅ **Organisation améliorée** - Dossiers tools/ et archive/
6. ✅ **Noms de fichiers clarifiés** - Plus de doublons/versions multiples

### Compatibilité
- ✅ **100% rétrocompatible** avec le système SMC existant
- ✅ **Interface SMC originale** toujours disponible
- ✅ **Données SMC** inchangées dans leur format

## 🚀 PROCHAINES ÉTAPES POSSIBLES

- 🔮 Support d'autres formats d'auscultation
- 📊 Graphiques unifiés SMC + Carrure
- 🔄 Intégration bases de données
- 📱 Interface web pour consultation

---

**🎯 VOTRE AUTOMATISATION DE RAPPORTS EST MAINTENANT POLYVALENTE !**

Plus besoin de traiter séparément SMC et Carrure - **un seul outil pour tout !** 🚀
