# Outils et Scripts de Développement

Ce répertoire contient les scripts de développement, tests et analyses qui ne font pas partie du workflow principal du rapport mensuel.

---

## 📁 Structure

### `analysis/` - Scripts d'analyse et d'investigation
Scripts utilisés pour analyser les données, détecter des problèmes, et comprendre la structure des fichiers.

**Fichiers :**
- `analyze_doublons_bas_droit.py` - Analyse des doublons dans les données bas droit
- `analyze_generated_file.py` - Vérification des fichiers générés
- `analyze_problematic_lines.py` - Investigation des lignes problématiques
- `analyze_vrais_doublons.py` - Détection de vrais doublons dans les données
- `diagnostic_doublons.py` - Diagnostic général des doublons
- `read_convergences_septembre.py` - Lecture/analyse du fichier convergences septembre
- `read_convert_excel.py` - Analyse du fichier de conversion Excel
- `scan_corrupted_lines.py` - Scanner de lignes corrompues
- `generate_carrure_complete.py` - Génération complète des données carrure
- `generate_syntheses.py` - Génération de synthèses de données
- `prepare_complete_synthesis.py` - Préparation des synthèses complètes
- `transform_to_columns.py` - Transformation de données en colonnes

**Usage :** Ponctuel, pour investigations et analyses lors du développement

---

### `debug/` - Scripts de débogage
Scripts utilisés pour déboguer des problèmes spécifiques pendant le développement.

**Fichiers :**
- `debug_after_cleaning.py` - Débogage après nettoyage des données
- `debug_deplacements.py` - Débogage spécifique aux déplacements
- `unified_complete_gui.py` - Ancienne version GUI (obsolète)
- `unified_final_gui.py` - Ancienne version GUI (obsolète)
- `unified_gui.py` - Ancienne version GUI (obsolète)

**Usage :** Ponctuel, pour résoudre des bugs

---

### `fixes/` - Scripts de correction
Scripts qui ont été utilisés pour corriger des problèmes de données ou de structure.

**Fichiers :**
- `fix_all_bas_droit_advanced.py` - Correction avancée des données bas droit
- `fix_dh_deplacements.py` - Correction des valeurs DH dans les déplacements
- `fix_dh_naming.py` - Correction de la nomenclature DH
- `fix_grd_mapping.py` - Correction du mapping GRD
- `metric_name_corrector.py` - Correction des noms de métriques
- `regenerate_grd_corrected.py` - Régénération des données GRD corrigées
- `extraction_clean.py` - Extraction avec nettoyage

**Usage :** Historique, ces corrections ont été intégrées dans le code principal

---

### `tests/` - Scripts de test
Scripts de test unitaires, d'intégration et de validation.

**Fichiers :**
- `test_carrure_precise.py` - Test extraction carrure précise
- `test_correction.py` - Test des corrections
- `test_corrector_real_data.py` - Test du correcteur avec données réelles
- `test_generation_colonnes.py` - Test génération de colonnes
- `test_pdf_native_septembre.py` - Test génération PDF septembre
- `test_pdf_standardizer.py` - Test standardisateur PDF
- `test_20pages.pdf` - Fichier PDF de test
- `test_20pages_INTELLIGENT.pdf` - Fichier PDF de test (version intelligente)
- `pdf_standardizer.py` - Ancien standardisateur PDF (obsolète)
- `run_pdf_standardizer.py` - Lanceur ancien standardisateur (obsolète)
- `run_pdf_standardizer_windows.py` - Lanceur Windows ancien standardisateur (obsolète)
- `LANCER_PDF_STANDARDIZER.bat` - Batch ancien standardisateur (obsolète)

**Usage :** Tests ponctuels, certains scripts sont obsolètes

---

### Scripts déjà existants (non déplacés)
Certains scripts étaient déjà dans `tools/` avant le nettoyage :
- `analyze_carrure_headers.py` - Analyse des en-têtes carrure
- `carrure_analyzer.py` - Analyseur carrure
- `demo_carrure_extraction.py` - Démo extraction carrure
- `smc_config_helper.py` - Assistant configuration SMC
- `test_comparaison_versions.py` - Comparaison de versions
- `test_extractor_columns.py` - Test colonnes extracteur

---

## ⚠️ Important

**Ces scripts ne sont PAS nécessaires pour le workflow mensuel normal !**

Le workflow mensuel utilise uniquement les scripts à la racine :
- `add_nb_cibles_column.py` - Ajout colonne nombre de cibles
- `generate_convergences_formatees.py` - Formatage convergences
- `generate_spatial_deplacements.py` - Formatage déplacements spatial
- `generate_pdf_octobre.py` - Génération PDF (à adapter chaque mois)

Voir **GUIDE_RAPPORT_MENSUEL.md** pour le processus complet.

---

## 🧹 Nettoyage futur

Si ces scripts ne sont plus utilisés après quelques mois, ils peuvent être :
1. Archivés dans `archive/`
2. Supprimés si complètement obsolètes
3. Conservés s'ils servent pour des analyses ponctuelles

**Dernière organisation : 3 novembre 2025**
