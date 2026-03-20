# STATUS DES FICHIERS AUTOLISP
**Date de nettoyage** : 4 novembre 2025

## 📁 Structure du Workspace

```
a_classer/
├── _backup/                              # Archives des versions antérieures
│   ├── place-tcpoint-backup.lsp
│   └── place-tcpoint-clean.lsp
├── _tests/                               # Scripts de test et débogage
│   ├── test-angle.lsp
│   └── test-debug.lsp
└── [fichiers opérationnels]              # Scripts prêts à l'emploi
```

---

## ✅ FICHIERS OPÉRATIONNELS

### 🔧 Gestion des Calques

#### `fusion-calques-pro.lsp`
- **Commande** : `FUSION-PRO`
- **Description** : Fusionne les calques `PRO_INS_***` vers `INS_***`
- **État** : ✅ Opérationnel
- **Taille** : 280 lignes
- **Usage** : 
  ```
  (load "fusion-calques-pro.lsp")
  FUSION-PRO
  ```

---

### 📍 Placement de Points

#### `place-point-bas-polyligne.lsp`
- **Commandes** : `POINTBAS`, `POINTBAS2`
- **Description** : Place des points aux sommets les plus bas des polylignes 3D
- **État** : ✅ Opérationnel
- **Taille** : 282 lignes
- **Calques ciblés** :
  - `REC_INS_GC_GAL_Boulons_Epinglage_Cintres_mes`
  - `REC_INS_GC_GAL_Boulons_Epinglage_Cintres_theo`

#### `place-tcpoint.lsp` ⭐
- **Commande** : `PLACE-TCPOINT`
- **Description** : Place des blocs TCPOINT aux extrémités des lignes/polylignes du côté du centre
- **État** : ✅ Opérationnel (Version restaurée v2.1)
- **Taille** : 917 lignes
- **Version** : v2.1 (enhanced 2025-09-08)
- **Paramètres configurables** :
  - `*NOM-BLOC-TCPOINT*` : "TCPOINT"
  - `*SUFFIXE-CALQUE*` : "_tete"
  - `*CALQUE-CENTRES*` : "_INTERSEC_AXE_2D"
  - `*RAYON-PROXIMITE*` : 10.0
  - `*MODE-AUTO*` : T (détection auto)
- **Fonctionnalités** :
  - Détection automatique des centres
  - Sélection automatique ou manuelle
  - Calcul distance point-to-segment précis
  - Gestion robuste VARIANT/SAFEARRAY
- **Note** : ⚠️ Ancien fichier corrompu supprimé, version propre restaurée

#### `recrpoints.lsp`
- **Commande** : `RECRPOINTS`
- **Description** : Convertit les POINTs et blocs TCPOINT* en DBPOINT AutoCAD
- **État** : ✅ Opérationnel
- **Taille** : 123 lignes
- **Fonctionnalités** :
  - Conversion OCS → WCS
  - Conservation du calque d'origine
  - Récapitulatif par calque

---

### 📏 Simplification des Cotes

#### `simplif-cotes.lsp` ⭐
- **Commande** : `SIMPLIF-COTES`
- **Description** : Simplifie les cotes en supprimant 1 sur 2 selon un parcours géométrique
- **État** : ✅ Opérationnel
- **Taille** : 216 lignes
- **Modes disponibles** :
  - **Mode [A]utomatique** : Détection automatique de l'ordre (tri par angle polaire)
  - **Mode [P]olyligne** : Utilise une polyligne de référence
- **Documentation** : Voir `README-simplif-cotes.md`
- **Usage** :
  ```
  (load "simplif-cotes.lsp")
  SIMPLIF-COTES
  ```

#### `simplif-cotes-semi-auto.lsp`
- **Commande** : `SIMPLIF-COTES-SEMI`
- **Description** : Version semi-automatique avec sélection de zone et centre manuel
- **État** : ✅ Opérationnel
- **Taille** : 379 lignes
- **Paramètre** : `*CALQUE-COTES*` = "REC_INS_GC_GAL_Beton_soutenement_txt"
- **Workflow** :
  1. Sélection zone de la coupe
  2. Clic pour définir le centre
  3. Tri par angle + suppression alternée

#### `simplif-cotes-simple.lsp`
- **Commande** : `SIMPLIF-TEST`
- **Description** : Version ultra-simplifiée pour tests et débogage
- **État** : ✅ Opérationnel
- **Taille** : 146 lignes
- **Paramètre** : `*CALQUE-COTES*` = "REC_INS_GC_GAL_Beton soutenement_texte"
- **Note** : Version de test sans gestion d'erreurs complexe

---

## 📦 FICHIERS ARCHIVÉS

### Dossier `_backup/`

#### `place-tcpoint-backup.lsp`
- **Description** : Ancienne version de sauvegarde
- **État** : Archivé (identique à la version restaurée)
- **Raison** : Conservation historique

#### `place-tcpoint-clean.lsp`
- **Description** : Version nettoyée sans accents
- **État** : Archivé
- **Raison** : Intermédiaire de nettoyage, non nécessaire

---

## 🧪 FICHIERS DE TEST

### Dossier `_tests/`

#### `test-angle.lsp`
- **Commande** : `TEST-ANGLE`
- **Description** : Diagnostic des problèmes de calcul d'angle
- **Usage** : Tests de coordonnées problématiques (nombres très petits)

#### `test-debug.lsp`
- **Commande** : `TEST-DEBUG`
- **Description** : Diagnostic simplifié pour tests de sélection et angles
- **Usage** : Vérification du filtrage par calque et calcul d'angles

---

## 📊 STATISTIQUES

- **Fichiers opérationnels** : 8
- **Fichiers archivés** : 2
- **Fichiers de test** : 2
- **Total lignes de code opérationnel** : ~2,343 lignes
- **Documentation** : 1 fichier README

---

## 🎯 UTILISATION RECOMMANDÉE

### Pour placement de points/blocs :
```autolisp
(load "place-tcpoint.lsp")
(load "place-point-bas-polyligne.lsp")
(load "recrpoints.lsp")
```

### Pour simplification de cotes :
```autolisp
(load "simplif-cotes.lsp")           ; Version complète
; OU
(load "simplif-cotes-semi-auto.lsp") ; Version semi-automatique
```

### Pour gestion de calques :
```autolisp
(load "fusion-calques-pro.lsp")
```

---

## 🔍 NOTES IMPORTANTES

1. ⚠️ **place-tcpoint.lsp** : Fichier restauré depuis version clean-restore après corruption
2. 📚 Les fichiers de simplification de cotes ont chacun leur utilité selon le contexte
3. 🧪 Les fichiers de test sont conservés pour débogage futur
4. 💾 Les backups sont conservés au cas où

---

## 🚀 PROCHAINES ÉTAPES

- [ ] Tester `place-tcpoint.lsp` après restauration
- [ ] Vérifier la compatibilité AutoCAD
- [ ] Documenter les paramètres personnalisables
- [ ] Créer un script de chargement automatique (.LSP ou .MNL)

---

**Dernière mise à jour** : 4 novembre 2025  
**Nettoyage effectué par** : GitHub Copilot
