# 📅 Guide Rapport Mensuel - NOVEMBRE 2025

**Date de création** : 1er décembre 2025  
**Période couverte** : Novembre 2025  
**Dossier** : `251201-rapport mensuel novembre`

---

## 🔧 Préparation effectuée

### ✅ Scripts mis à jour
Les chemins ont été modifiés dans tous les scripts :
- `generate_spatial_deplacements.py` → novembre (2025_11)
- `generate_convergences_formatees.py` → novembre (2025_11)
- `add_nb_cibles_column.py` → novembre (2025_11)
- `generate_pdf_octobre.py` → novembre (titre aussi mis à jour)

### ✅ Structure de dossiers créée
```
251201-rapport mensuel novembre/
├── 1-tableaux/              (existant - à remplir avec les Excel sources)
├── 2-extractions/
│   └── smc_output/          (extractions CSV et Excel formatés)
└── 3-pdf-annexes/           (PDFs générés)
```

---

## 📋 Procédure de génération

### ÉTAPE 1 : Préparer les données sources
Placer les fichiers Excel sources dans :
```
C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\1-tableaux
```

### ÉTAPE 2 : Extraction des données
```bash
# Aller dans le répertoire du projet
cd C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\smc-data-extractor

# Activer l'environnement virtuel
C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\.venv\Scripts\python.exe

# Lancer l'extraction (à adapter selon votre processus)
python unified_extractor.py
```

### ÉTAPE 3 : Ajouter la colonne Nb_cibles
```bash
python add_nb_cibles_column.py
```

**Ce script :**
- Lit `Deplacements_Ligne_SMC_2025_11.csv`
- Ajoute la colonne `Nb_cibles` (5 ou 7 selon la section)
- Génère `Deplacements_Ligne_SMC_2025_11_avec_nb_cibles.csv`

### ÉTAPE 4 : Générer les déplacements spatiaux
```bash
python generate_spatial_deplacements.py
```

**Ce script génère :**
- `Deplacements_Spatial_Complet.xlsx`
- 9 feuilles (une par section)
- Disposition spatiale adaptée (5 ou 7 cibles)
- Format : Lucida Sans 8.5, colonnes 11.29, fond blanc

### ÉTAPE 5 : Générer les convergences formatées
```bash
python generate_convergences_formatees.py
```

**Ce script génère :**
- `Convergences_Formatees_Complet.xlsx`
- Colonnes adaptées au nombre de cibles
- Format optimisé

### ÉTAPE 6 : Générer les PDFs
```bash
python generate_pdf_octobre.py
```

**Ce script :**
- Lit tous les Excel de `1-tableaux/`
- Génère des PDFs dans `3-pdf-annexes/`

---

## 📊 Fichiers attendus

### Entrées (dans 2-extractions/smc_output/)
- `Deplacements_Ligne_SMC_2025_11.csv`
- `Convergences_Ligne_SMC_2025_11.csv`

### Sorties générées
- `Deplacements_Ligne_SMC_2025_11_avec_nb_cibles.csv`
- `Deplacements_Spatial_Complet.xlsx`
- `Convergences_Formatees_Complet.xlsx`

---

## 🎯 Sections attendues

### Sections avec 5 cibles
- GGS C003
- GGS C007
- GHA T41
- GVA C105

### Sections avec 7 cibles
- GGS C020
- GGS C031
- GHA C04
- GHA T15
- GHA T28

**Note** : Si de nouvelles sections apparaissent, le système les détectera automatiquement !

---

## ⚠️ Points d'attention

1. **Vérifier les noms de fichiers** : Ils doivent contenir `2025_11` pour novembre
2. **Séparateur CSV** : Les fichiers doivent utiliser le point-virgule (`;`)
3. **Colonne Nb_cibles** : Obligatoire pour la génération spatiale
4. **Encodage** : UTF-8 pour éviter les problèmes d'accents

---

## 🔄 Différences avec octobre

### Chemins mis à jour
- `251103-rapport mensuel octobre` → `251201-rapport mensuel novembre`
- `2025_10` → `2025_11`

### Scripts inchangés
Tous les scripts fonctionnent de la même manière, seuls les chemins ont changé.

---

*Guide créé le 1er décembre 2025*
