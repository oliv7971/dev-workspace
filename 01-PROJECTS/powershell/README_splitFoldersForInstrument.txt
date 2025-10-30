# 🎵 splitFoldersForInstrument.ps1 - Guide d'utilisation

## Description
Script PowerShell qui divise automatiquement les dossiers contenant trop de fichiers musicaux en sous-dossiers numérotés pour assurer la compatibilité avec les instruments de musique ayant des limitations de lecture.

## Problème résolu
Certains instruments de musique (synthés, échantillonneurs, etc.) ne peuvent pas lire les dossiers contenant plus de 256 ou 512 fichiers. Ce script divise automatiquement ces dossiers.

## Configuration rapide
```powershell
$BasePath = "D:\MusiqueInstrument"       # Bibliothèque musicale
$MaxFilesPerFolder = 256                 # Limite de votre instrument (256 ou 512)
$WhatIf = $true                         # Simulation d'abord
$CreateBackup = $true                   # Sauvegarde automatique
```

## Formats de noms supportés
```powershell
$FolderNamePattern = "Batch_{0:D2}"     # Résultat: Batch_01, Batch_02...
$FolderNamePattern = "Part_{0:D3}"      # Résultat: Part_001, Part_002...
$FolderNamePattern = "Vol_{0}"          # Résultat: Vol_1, Vol_2...
```

## Extensions musicales
```powershell
$FileExtensions = @(".mp3", ".wav", ".flac", ".m4a", ".ogg")
# Laissez vide @() pour traiter tous les types de fichiers
```

## Exemple de transformation
```
AVANT:
📁 AlbumComplet (847 fichiers .mp3)

APRÈS:
📁 AlbumComplet
├── 📂 Batch_01 (256 fichiers)
├── 📂 Batch_02 (256 fichiers)  
├── 📂 Batch_03 (256 fichiers)
└── 📂 Batch_04 (79 fichiers)
```

## Fonctionnalités intelligentes
✅ **Préserve l'ordre alphabétique** des fichiers
✅ **Sauvegarde automatique** avant modification
✅ **Analyse préalable** avec plan de division
✅ **Traitement récursif** de toute l'arborescence
✅ **Évite les dossiers déjà divisés** (Batch_XX)

## Workflow recommandé
1. **Configuration** : Définir la limite selon votre instrument
2. **Analyse** : Lancer avec `$WhatIf = $true` pour voir le plan
3. **Vérification** : Examiner quels dossiers seront divisés
4. **Sauvegarde** : S'assurer que `$CreateBackup = $true`
5. **Exécution** : Changer `$WhatIf = $false`

## Instruments typiques et leurs limites
- **Roland** : Souvent 256 fichiers par dossier
- **Korg** : Généralement 512 fichiers par dossier
- **Yamaha** : Variable selon modèle (256-512)
- **Akai MPC** : Souvent 128-256 fichiers
- **Native Instruments** : Généralement pas de limite

## Précautions importantes
⚠️ **Modifications irréversibles de l'arborescence**
- Les fichiers sont DÉPLACÉS, pas copiés
- La structure de dossiers est modifiée
- Toujours faire une sauvegarde (`$CreateBackup = $true`)
- Tester sur un petit dossier d'abord

## Options de sécurité
```powershell
$CreateBackup = $true                    # Sauvegarde automatique
$BackupPath = "D:\Musique_Backup"       # Dossier de sauvegarde
$MinFilesToSplit = 10                   # Ne divise que si >10 fichiers
```

## Cas d'usage typiques
- **Préparation pour sampler** : Diviser une bibliothèque de samples
- **Export vers instrument** : Préparer des dossiers compatibles
- **Migration de données** : Adapter une collection existante
- **Nouveau workflow** : Organiser pour instrument spécifique

## Résultat attendu
- Dossiers divisés en sous-dossiers compatibles
- Chaque sous-dossier respecte la limite configurée
- Structure préservée pour navigation sur instrument
- Sauvegarde disponible pour récupération

## Post-traitement
Après division, votre instrument pourra :
- Lire tous les dossiers sans erreur
- Naviguer dans les sous-dossiers (Batch_01, Batch_02...)
- Accéder à tous vos fichiers musicaux
- Fonctionner sans limitation technique