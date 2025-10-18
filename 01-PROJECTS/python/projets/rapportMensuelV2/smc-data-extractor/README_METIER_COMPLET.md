# 🎯 SYSTÈME D'EXTRACTION UNIFIÉ SMC & CARRURE - VERSION MÉTIER COMPLÈTE

**Version :** 3.0 - Logique Métier Complète
**Date :** 2 octobre 2025

## 🚀 LOGIQUE MÉTIER IMPLÉMENTÉE

### 📊 **DERNIÈRES VALEURS CUMULATIVES**
- **Définition :** La dernière valeur mesurée de chaque métrique (déplacement cumulé total)
- **Usage :** Position actuelle des points d'auscultation
- **Calcul :** Dernière valeur chronologique dans toutes les données

### 📈 **VALEURS PÉRIODIQUES MENSUELLES**
- **Définition :** Évolution mensuelle = Valeur fin mois - Valeur fin mois précédent
- **Usage :** Vitesse de déformation sur la période
- **Calcul :** `Périodique = Dernière valeur mois N - Dernière valeur mois N-1`

### 🎨 **GRAPHIQUES PAR ZONES COLORÉES**
- **Détection :** Zones séparées par cellules de même couleur que A1
- **Génération :** Un graphique par zone détectée
- **Format :** PDF avec graphiques temporels par métrique

## 📁 FICHIERS GÉNÉRÉS

### 📊 **Rapport Principal**
```
rapport_unifie_YYYY_MM.csv
```
**Colonnes :**
- `metric` - Nom de la métrique (BG, HG, DPM, DH, DZ, etc.)
- `periodic_mm` - Valeur périodique mensuelle (mm)
- `cumulative_mm` - Dernière valeur cumulative (mm)
- `date_last_cumulative` - Date de la dernière mesure
- `galerie` - Galerie (GGS, GVA, etc.)
- `section` - Section (C003, T15, etc.)
- `data_type` - Type de données (smc/carrure)
- `sheet_type` - Type d'onglet (convergences/deplacements/carrure_deplacements/etc.)

### 📋 **Synthèse Exécutive**
```
synthese_dernieres_valeurs_YYYY_MM.txt
```
**Contenu :**
- Nombre de métriques par type
- Zones de graphique détectées
- Période d'extraction
- Statistiques générales

### 📈 **Graphiques**
```
graphiques_par_zones/
└── graphiques_unifie_YYYY_MM.pdf
```

## 🎮 UTILISATION

### Interface Complète (Recommandée)
```bash
python unified_complete_gui.py
```

**Fonctionnalités interface :**
- 🤖 **Détection automatique** SMC + Carrure
- 📊 **Rapport CSV unifié** avec toutes les métriques
- 📈 **Graphiques par zones** selon couleurs Excel
- ⚙️ **Options avancées** configurable

### Système Unifié (Ligne de commande)
```bash
python unified_extractor.py
```

## 📊 EXEMPLE DE DONNÉES EXTRAITES

### SMC - Convergences
```csv
metric,periodic_mm,cumulative_mm,date_last_cumulative,galerie,section,data_type,sheet_type
BG,-0.15,-2.45,2025-09-30,GGS,C003,smc,convergences
HG,-0.12,-1.87,2025-09-30,GGS,C003,smc,convergences
```

### Carrure - Déplacements
```csv
metric,periodic_mm,cumulative_mm,date_last_cumulative,galerie,section,data_type,sheet_type
carrure_col_4,-0.08,-1.23,2025-09-10,GGS,UNKNOWN,carrure,carrure_deplacements
carrure_col_5,-0.05,-0.89,2025-09-10,GGS,UNKNOWN,carrure,carrure_deplacements
```

## 🔍 ALGORITHME D'EXTRACTION

### 1. **Détection des fichiers**
```python
# SMC: fichiers contenant "SMC"
smc_files = ["*SMC*.xlsx", "*SMC*.xlsm"]

# Carrure: fichiers contenant "carrure"
carrure_files = ["*carrure*.xlsx", "*carrure*.xlsm"]
```

### 2. **Extraction par onglet**
- **SMC :** `Convergences`, `Déplacements`
- **Carrure :** `Déplacements carrure`, `Déplacements cintres-longerons`

### 3. **Calcul des évolutions**
```python
# Pour chaque métrique:
1. Filtrer données par mois cible
2. Trier par date chronologique
3. Dernière valeur cumulative = dernière mesure toutes périodes
4. Dernière valeur mois = dernière mesure du mois
5. Dernière valeur mois précédent = dernière mesure avant le mois
6. Valeur périodique = valeur_mois - valeur_mois_precedent
```

### 4. **Détection zones graphiques**
```python
# Pour chaque onglet:
1. Récupérer couleur cellule A1 comme référence
2. Scanner toutes les cellules
3. Si couleur == couleur_référence ET contenu != vide:
   → Créer zone de graphique
4. Générer un graphique par zone
```

## ⚙️ CONFIGURATION

### Paramètres par défaut
```python
# Période
target_month = "2025-09"  # Format YYYY-MM

# Chemins
default_input = r"...\250902-rapport mensuel septembre\1-tableaux"
default_output = r"C:\temp\extraction_unifiee_complete"

# Options
generate_csv = True          # Rapport CSV unifié
generate_graphs = True       # Graphiques par zones
generate_ligne_summaries = True  # Récapitulatifs additionnels
```

### Structure des onglets
```python
# SMC
smc_headers_row = 9         # Ligne des en-têtes
smc_data_start_row = 10     # Première ligne de données
smc_date_col = 2            # Colonne Date

# Carrure
carrure_headers_row = 10    # Ligne des en-têtes
carrure_data_start_row = 12 # Première ligne de données
carrure_date_col = 2        # Colonne Date
```

## 🔧 MAINTENANCE ET EXTENSION

### Ajouter un nouveau type de fichier
1. Étendre `detect_file_types()` avec nouveau pattern
2. Créer `extract_NOUVEAU_data()`
3. Implémenter `extract_NOUVEAU_sheet_data()`
4. Ajouter au traitement dans `run_unified_extraction()`

### Modifier la logique de calcul
- **Valeurs périodiques :** Modifier `calculate_evolutions()`
- **Détection zones :** Modifier `detect_graph_zones_by_color()`
- **Parsing dates :** Modifier `parse_date()`

### Nouveaux formats de sortie
- **Excel :** Ajouter export via `openpyxl`
- **JSON :** Ajouter export via `json`
- **Base de données :** Ajouter connecteur DB

## 📈 PERFORMANCES

### Données traitées
- **SMC :** ~50-100 lignes par fichier, 2-20 métriques
- **Carrure :** ~30-50 lignes par fichier, 10-60 métriques
- **Performance :** ~1-2 secondes par fichier Excel

### Optimisations
- Lecture `data_only=True` pour performance
- Cache des couleurs de cellules
- Tri unique des données par date
- Génération graphique optimisée

## 🎯 AVANTAGES SYSTÈME UNIFIÉ

### ✅ **Consolidation**
- **Un seul outil** pour tous les types d'auscultation
- **Format unifié** de sortie
- **Logique métier cohérente**

### ✅ **Automatisation**
- **Détection automatique** des types
- **Calculs périodiques** automatiques
- **Graphiques** générés automatiquement

### ✅ **Traçabilité**
- **Dates exactes** de chaque mesure
- **Séparation claire** valeurs cumulatives/périodiques
- **Logs détaillés** d'exécution

---

**🎯 VOTRE AUTOMATISATION DE RAPPORTS MENSUELLE EST MAINTENANT COMPLÈTE !**

Plus besoin de calculs manuels - le système extrait automatiquement :
- ✅ **Dernières valeurs** (position actuelle)
- ✅ **Valeurs périodiques** (évolution mensuelle)
- ✅ **Graphiques par zones** (visualisation)

**Un seul clic pour analyser tous vos fichiers SMC et Carrure !** 🚀
