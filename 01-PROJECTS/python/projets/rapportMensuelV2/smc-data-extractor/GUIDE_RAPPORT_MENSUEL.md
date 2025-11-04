# Guide Complet - Rapport Mensuel SMC
## Processus automatisé Octobre 2025

---

## 📋 Vue d'ensemble

Ce guide décrit le processus complet pour générer un rapport mensuel SMC, de l'extraction des données brutes jusqu'aux fichiers formatés prêts à copier dans Word.

**Durée totale estimée : 15-20 minutes**

---

## 🗂️ Structure des dossiers

### Dossier d'entrée (données brutes)
```
C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\
└── 251103-rapport mensuel octobre\
    └── 1-tableaux\
        ├── GGS\        (4 fichiers SMC)
        └── GHA\        (5 fichiers SMC)
```

### Dossier de sortie (résultats)
```
└── 2-extractions\
    └── smc_output\
        ├── Convergences_SMC.csv
        ├── Deplacements_SMC.csv
        ├── Dates_SMC.csv
        ├── Convergences_Ligne_SMC_2025_10.csv
        ├── Deplacements_Ligne_SMC_2025_10.csv
        ├── Deplacements_Ligne_SMC_2025_10_avec_nb_cibles.csv
        ├── Convergences_Formatees_Complet.xlsx       ← NOUVEAU
        └── Deplacements_Spatial_Complet.xlsx         ← NOUVEAU

└── 3-pdf-annexes\
    └── (72 PDF générés : convergences + déplacements + graphiques)
```

---

## ⚙️ ÉTAPE 1 : Extraction des données

### 1.1 Lancer l'interface graphique

```bash
cd C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2
python src/smc_gui.py
```

### 1.2 Paramétrer l'extraction

Dans l'interface :
- **Dossier racine** : `C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\1-tableaux`
- **Mois** : `2025-10` (format YYYY-MM)
- **Dossier de sortie** : `C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\2-extractions`

### 1.3 Options à cocher
- ✅ **Extraire convergences**
- ✅ **Extraire déplacements**
- ✅ **Générer récapitulatifs ligne**
- ✅ **Modes** : Périodique ET Cumulé

### 1.4 Lancer l'extraction
Cliquer sur **"Extraire les données"**

**Résultat attendu :**
```
✓ 72 convergences extraites
✓ 183 déplacements extraits
✓ 9 sections identifiées
✓ Fichiers CSV générés dans smc_output/
```

---

## 📄 ÉTAPE 2 : Génération des PDF

### 2.1 Créer le script de génération (si première fois du mois)

```python
# Créer : generate_pdf_octobre.py
from excel_to_pdf_native import print_excel_files_native
import os

root_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\1-tableaux"
output_folder = r"C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251103-rapport mensuel octobre\3-pdf-annexes"

os.makedirs(output_folder, exist_ok=True)

print("Génération des PDF pour Octobre 2025...")
print_excel_files_native(root_folder, output_folder, log_callback=None)
print("Terminé !")
```

### 2.2 Exécuter la génération

```bash
cd C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\smc-data-extractor
python generate_pdf_octobre.py
```

**Résultat attendu :**
```
✓ 72 fichiers PDF créés
✓ Pour chaque section (9 sections) :
  - 1 PDF convergences
  - 1 PDF déplacements  
  - 6 PDF graphiques individuels
✓ Format : A4 paysage, en-têtes répétés
```

---

## 🎯 ÉTAPE 3 : Ajout du nombre de cibles

### 3.1 Exécuter le script

```bash
cd C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\smc-data-extractor
python add_nb_cibles_column.py
```

**Ce que fait ce script :**
- Lit `Deplacements_Ligne_SMC_2025_10.csv`
- Détecte automatiquement le nombre de cibles (5 ou 7) selon la présence de colonnes IG/ID
- Crée `Deplacements_Ligne_SMC_2025_10_avec_nb_cibles.csv`

**Résultat attendu :**
```
✓ Colonne Nb_cibles ajoutée
✓ 5 cibles : GGS C003, C007, GHA T41, GVA C105
✓ 7 cibles : GGS C020, C031, GHA C04, T15, T28
```

---

## 📊 ÉTAPE 4 : Formatage des déplacements (présentation spatiale)

### 4.1 Générer le fichier Excel spatial

```bash
python generate_spatial_deplacements.py
```

**Ce que fait ce script :**
- Lit `Deplacements_Ligne_SMC_2025_10_avec_nb_cibles.csv`
- Crée **une feuille Excel par section**
- Chaque feuille contient :
  - **Tableau PÉRIODIQUE** avec disposition spatiale des cibles
  - **Tableau CUMULÉ** avec disposition spatiale des cibles
- Adapte automatiquement la disposition selon 5 ou 7 cibles

**Fichier généré :**
```
Deplacements_Spatial_Complet.xlsx
```

**Format :**
- Police : Lucida Sans 8.5
- Largeur colonnes : 11.29
- Fond blanc avec bordures fines
- Disposition spatiale :
  ```
  5 cibles:              7 cibles:
  BG      HG             BG      IG
      CH                 HG      CH
  HD      BD             HD      ID      BD
  ```

---

## 📈 ÉTAPE 5 : Formatage des convergences (tableaux optimisés)

### 5.1 Générer le fichier Excel formaté

```bash
python generate_convergences_formatees.py
```

**Ce que fait ce script :**
- Lit `Convergences_Ligne_SMC_2025_10.csv`
- Crée **une feuille Excel par section**
- Chaque feuille contient UN SEUL tableau avec :
  - **Uniquement les colonnes pertinentes** (5 ou 7 cibles)
  - Pas de colonnes vides !
  - 2 lignes : périodique + cumulé

**Fichier généré :**
```
Convergences_Formatees_Complet.xlsx
```

**Format :**
- Police : Lucida Sans 9
- 1 décimale après la virgule
- Colonnes 5 cibles : Mode, BG, HG, HD, BD, LH, LB
- Colonnes 7 cibles : Mode, BG, IG, HG, HD, ID, BD, LH, LI, LB

---

## 📝 ÉTAPE 6 : Intégration dans Word

### 6.1 Copier les convergences

1. Ouvrir `Convergences_Formatees_Complet.xlsx`
2. Pour chaque section :
   - Aller sur la feuille correspondante (ex: "GGS C003")
   - Sélectionner le tableau complet
   - Copier (Ctrl+C)
   - Coller dans Word à l'emplacement prévu

### 6.2 Copier les déplacements

1. Ouvrir `Deplacements_Spatial_Complet.xlsx`
2. Pour chaque section :
   - Aller sur la feuille correspondante
   - Copier le tableau PÉRIODIQUE (si besoin)
   - Copier le tableau CUMULÉ (si besoin)
   - Coller dans Word

### 6.3 Insérer les PDF

Les 72 PDF sont dans `3-pdf-annexes\` :
- Insérer comme annexes ou imprimer selon besoin
- Nomenclature : `[Galerie]_[Section]_[Type]_[Date].pdf`

---

## 🔧 Scripts de référence

### Localisation des scripts

```
C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\smc-data-extractor\
├── generate_pdf_octobre.py                    ← Génération PDF
├── add_nb_cibles_column.py                    ← Ajout nb cibles
├── generate_spatial_deplacements.py           ← Déplacements spatiaux
└── generate_convergences_formatees.py         ← Convergences formatées
```

### Environnement virtuel

```bash
# Activer l'environnement
C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\.venv\Scripts\Activate.ps1

# Ou exécuter directement
C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\.venv\Scripts\python.exe script.py
```

---

## 🎨 Personnalisation

### Modifier la police ou la taille

**Déplacements (Lucida Sans 8.5)** :
```python
# Dans generate_spatial_deplacements.py, ligne ~32
title_font = Font(name='Lucida Sans', size=8.5, bold=True, color="FFFFFF")
header_font = Font(name='Lucida Sans', size=8.5, bold=True, color="FFFFFF")
data_font = Font(name='Lucida Sans', size=8.5)
```

**Convergences (Lucida Sans 9)** :
```python
# Dans generate_convergences_formatees.py, ligne ~20
title_font = Font(name='Lucida Sans', size=9, bold=True, color="FFFFFF")
header_font = Font(name='Lucida Sans', size=9, bold=True, color="FFFFFF")
data_font = Font(name='Lucida Sans', size=9)
```

### Modifier le nombre de décimales

**Convergences (1 décimale)** :
```python
# Dans generate_convergences_formatees.py, fonction format_value()
return round(float(val), 1)  # 1 décimale
```

**Déplacements (2 décimales)** :
```python
# Dans generate_spatial_deplacements.py, fonction format_value()
return round(float(val), 2)  # 2 décimales
```

---

## ⚠️ Dépannage

### Problème : Module non trouvé
```bash
# Réinstaller les dépendances
pip install pandas openpyxl xlrd matplotlib numpy PyYAML pywin32
```

### Problème : Erreur d'encodage avec emojis
✅ **Déjà résolu** : Les emojis ont été retirés des fichiers sources
- `unified_extractor.py` : Remplacés par [*], [>], [OK], [ERREUR]

### Problème : Excel ne s'ouvre pas pour les PDF
- Vérifier que Microsoft Excel est installé
- Vérifier que pywin32 est installé : `pip install pywin32`

---

## 📅 Checklist mensuelle

Pour le mois prochain (Novembre 2025) :

- [ ] **Étape 1** : Copier les fichiers SMC dans `251104-rapport mensuel novembre\1-tableaux\`
- [ ] **Étape 2** : Lancer `smc_gui.py` avec mois = `2025-11`
- [ ] **Étape 3** : Créer `generate_pdf_novembre.py` (copier/adapter octobre)
- [ ] **Étape 4** : Exécuter `add_nb_cibles_column.py`
- [ ] **Étape 5** : Exécuter `generate_spatial_deplacements.py`
- [ ] **Étape 6** : Exécuter `generate_convergences_formatees.py`
- [ ] **Étape 7** : Copier les tableaux Excel vers Word
- [ ] **Étape 8** : Insérer les PDF en annexes

**Temps estimé : 15-20 minutes** ⏱️

---

## 📞 Support

Pour toute question ou amélioration, se référer à :
- `README.md` : Documentation générale
- `docs/user_guide.md` : Guide utilisateur détaillé
- Historique de conversation GitHub Copilot (Octobre 2025)

---

**Dernière mise à jour : 3 novembre 2025**  
**Version : Octobre 2025 (v1.0)**
