# 🗑️ deleteEmptyFiles.ps1 - Guide d'utilisation

## Description
Script PowerShell qui supprime automatiquement tous les fichiers vides (0 byte) et les dossiers vides de manière récursive.

## Utilisation principale
- Nettoyer un disque dur ou NAS après transferts/suppressions
- Éliminer les résidus de synchronisations ratées
- Préparer une arborescence avant archivage

## Configuration rapide
```powershell
$BasePath = "D:\MonDossier"    # Dossier à nettoyer
$WhatIf = $true               # $true = simulation, $false = action réelle
$Verbose = $true              # $true = détails, $false = silencieux
```

## Workflow recommandé
1. **Test** : Lancer avec `$WhatIf = $true` pour voir ce qui serait supprimé
2. **Vérification** : Examiner la liste des fichiers/dossiers détectés
3. **Action** : Changer `$WhatIf = $false` pour supprimer réellement

## Précautions
⚠️ **ATTENTION** : Suppression définitive, pas de corbeille !
- Toujours tester avec `$WhatIf = $true` d'abord
- Vérifier que les fichiers vides ne sont pas importants
- Faire une sauvegarde si nécessaire

## Cas d'usage typiques
- **Après migration** : Nettoyer les fichiers corrompus (0 byte)
- **Synchronisation** : Éliminer les échecs de copie
- **Maintenance NAS** : Nettoyage périodique des dossiers vides
- **Avant archivage** : Structure propre sans résidus

## Résultat attendu
- Fichiers de 0 byte supprimés
- Dossiers vides supprimés (de manière récursive)
- Rapport détaillé avec nombres de suppressions