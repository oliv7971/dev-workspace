# 🧹 cleanBeforeCopy.ps1 - Guide d'utilisation

## Description
Script PowerShell qui compare des fichiers entre un répertoire "source" (nouvelles données) et un/plusieurs répertoires "référence" (déjà classés) pour supprimer les doublons du répertoire source AVANT la copie.

## Utilisation principale
- Éviter les doublons avant d'ajouter de nouvelles données
- Nettoyer un dossier "à trier" par rapport aux archives existantes
- Optimiser l'espace avant transfert vers NAS

## Configuration rapide
```powershell
$SourcePath = "D:\NouvellesDonnees"      # Dossier à nettoyer
$ReferencePath = "D:\DonneesClassees"    # Archive de référence
$Action = "Report"                       # "Report", "Delete", "Move"
$WhatIf = $true                         # Simulation d'abord
```

## Configuration multi-références
```powershell
$CheckMultipleReferences = $true
$MultipleReferencePaths = @(
    "D:\Archive2023",
    "D:\Archive2024", 
    "D:\Backup",
    "E:\PhotosClassees"
)
```

## Actions disponibles
- **"Report"** : Affiche les doublons détectés (RECOMMANDÉ pour débuter)
- **"Delete"** : Supprime les doublons du dossier source
- **"Move"** : Déplace les doublons vers quarantaine

## Workflow typique
1. **Analyse** : `$Action = "Report"` pour voir les doublons
2. **Décision** : Examiner quels fichiers sont déjà présents
3. **Nettoyage** : `$Action = "Delete"` pour supprimer du source
4. **Copie sécurisée** : Copier les fichiers restants sans doublons

## Avantages clés
✅ **Préserve les données classées** (jamais modifiées)
✅ **Évite les doublons** dans l'archive finale
✅ **Économise l'espace** disque et temps de transfert
✅ **Support multi-archives** pour comparaisons complexes

## Cas d'usage typiques

### **Workflow photos**
```
Source: D:\PhotosAppareil\        (nouvelles photos)
Référence: D:\PhotosClassees\     (collection organisée)
→ Supprime les photos déjà présentes avant import
```

### **Workflow documents**
```
Source: D:\DocumentsATrier\       (documents en attente)
References: 
  - D:\Archives2023\
  - D:\Archives2024\
  - E:\DocumentsImportants\
→ Nettoie contre plusieurs archives
```

### **Workflow musique**
```
Source: D:\MusiqueNouvelle\       (albums téléchargés)
Référence: D:\BibliothèqueMP3\    (collection existante)
→ Évite les doublons d'albums
```

## Précautions importantes
⚠️ **Le répertoire SOURCE est modifié, pas la référence**
- Les fichiers sont supprimés/déplacés UNIQUEMENT du dossier source
- Les archives de référence restent intactes
- Toujours tester avec `$WhatIf = $true` d'abord

## Options de sécurité
```powershell
$Action = "Move"                         # Quarantaine au lieu de suppression
$QuarantinePath = "D:\DoublonsDetectes" # Dossier de récupération
```

## Résultat attendu
- Dossier source nettoyé des doublons
- Rapport détaillé des fichiers traités
- Espace disque libéré calculé
- Copie ultérieure sans risque de doublons