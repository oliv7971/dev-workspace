# 🔍 findDuplicateFiles.ps1 - Guide d'utilisation

## Description
Script PowerShell qui détecte les fichiers doublons basés sur leur contenu réel (hash SHA256/MD5), pas sur leur nom. Peut supprimer ou déplacer les doublons détectés.

## Utilisation principale
- Nettoyer une bibliothèque de photos/musique/documents
- Récupérer de l'espace disque en éliminant les doublons
- Identifier les fichiers dupliqués avant archivage

## Configuration rapide
```powershell
$BasePath = "D:\MesDocuments"         # Dossier à analyser
$Action = "Report"                    # "Report", "Delete", "Move"
$WhatIf = $true                      # $true = simulation
$HashAlgorithm = "SHA256"            # SHA256 (précis) ou MD5 (rapide)
$MinFileSize = 1MB                   # Ignorer fichiers < 1MB
```

## Actions disponibles
- **"Report"** : Affiche les doublons sans rien modifier (RECOMMANDÉ pour débuter)
- **"Delete"** : Supprime les doublons (garde le premier trouvé)
- **"Move"** : Déplace les doublons vers un dossier spécifique

## Workflow recommandé
1. **Analyse** : `$Action = "Report"` et `$WhatIf = $true`
2. **Examen** : Vérifier la liste des doublons détectés
3. **Action** : Changer l'action et `$WhatIf = $false`

## Optimisations pour gros volumes
```powershell
$MinFileSize = 10MB              # Ignorer petits fichiers
$HashAlgorithm = "MD5"           # Plus rapide pour tests
$ExcludeExtensions = @(".tmp", ".cache", ".log")
```

## Performances attendues
- **10k fichiers** : 5-15 minutes
- **100k fichiers** : 30-60 minutes  
- **1M fichiers** : 3-8 heures

## Précautions
⚠️ **Le script se base sur le CONTENU, pas le nom**
- Deux fichiers identiques avec noms différents = doublons détectés
- Fichiers similaires mais pas identiques = pas de doublon
- Toujours commencer par "Report" pour vérifier

## Cas d'usage typiques
- **Bibliothèque photos** : Éliminer les doublons après imports multiples
- **Collection musique** : Nettoyer après conversions/téléchargements
- **Archives documents** : Supprimer copies multiples
- **Nettoyage NAS** : Récupération d'espace disque

## Résultat attendu
- Liste détaillée des groupes de doublons
- Calcul de l'espace disque gaspillé
- Action sur les doublons selon configuration