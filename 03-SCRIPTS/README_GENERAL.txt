# 📚 Collection de scripts PowerShell - Vue d'ensemble

## Scripts disponibles

### 🗑️ **deleteEmptyFiles.ps1**
**Nettoyage** - Supprime fichiers vides (0 byte) et dossiers vides
- **Quand** : Après transferts, migrations, synchronisations ratées
- **Résultat** : Structure propre sans résidus

### 🔍 **findDuplicateFiles.ps1** 
**Détection classique** - Trouve les doublons basés sur le contenu
- **Quand** : Nettoyer bibliothèques photos/musique/documents
- **Résultat** : Suppression/déplacement des doublons

### ⚡ **findDuplicateFiles-Parallel.ps1**
**Détection rapide** - Version parallélisée pour gros volumes
- **Quand** : Plus de 10k fichiers, machines multi-cœurs
- **Résultat** : Même chose mais 2-4x plus rapide

### 🧹 **cleanBeforeCopy.ps1**
**Nettoyage intelligent** - Compare source vs référence avant copie
- **Quand** : Éviter doublons avant ajout de nouvelles données
- **Résultat** : Source nettoyé, copie sans doublons

### 🎵 **splitFoldersForInstrument.ps1**
**Division pour instruments** - Divise dossiers trop volumineux
- **Quand** : Instrument limité à 256/512 fichiers par dossier
- **Résultat** : Sous-dossiers compatibles (Batch_01, Batch_02...)

## Workflow typique de nettoyage complet

### 1️⃣ **Préparation** - deleteEmptyFiles.ps1
```
Nettoie les fichiers vides et dossiers vides
→ Structure propre pour la suite
```

### 2️⃣ **Analyse** - findDuplicateFiles.ps1 ou version parallèle
```
Détecte et supprime les vrais doublons
→ Économise espace disque significatif
```

### 3️⃣ **Intégration** - cleanBeforeCopy.ps1
```
Compare nouvelles données vs archives existantes
→ Évite d'ajouter des doublons
```

### 4️⃣ **Finalisation** - splitFoldersForInstrument.ps1 (si besoin)
```
Divise pour compatibilité instruments
→ Structure finale optimisée
```

## Conseils généraux d'utilisation

### 🛡️ **Sécurité AVANT TOUT**
- ✅ Toujours commencer avec `$WhatIf = $true`
- ✅ Faire des sauvegardes avant modifications importantes
- ✅ Tester sur un petit sous-dossier d'abord
- ✅ Vérifier l'espace disque disponible

### ⚡ **Performance**
- Version classique : < 10k fichiers
- Version parallèle : > 10k fichiers
- SSD recommandé pour gros volumes
- Éviter pendant sauvegardes/synchronisations

### 📋 **Workflow recommandé**
1. **Analyse** : Mode "Report" pour voir ce qui sera fait
2. **Test** : Petit dossier avec `$WhatIf = $true`
3. **Sauvegarde** : Si données importantes
4. **Action** : `$WhatIf = $false` pour exécuter

## Maintenance régulière suggérée

### 🗓️ **Mensuel**
- deleteEmptyFiles.ps1 sur dossiers actifs
- findDuplicateFiles.ps1 sur nouvelles données

### 🗓️ **Trimestriel** 
- findDuplicateFiles-Parallel.ps1 sur gros volumes
- cleanBeforeCopy.ps1 avant intégrations importantes

### 🗓️ **Selon besoin**
- splitFoldersForInstrument.ps1 pour nouveaux instruments
- cleanBeforeCopy.ps1 avant migrations/archivages

## Support et dépannage

### ❓ **Problèmes courants**
- **Erreurs de permissions** : Exécuter en administrateur
- **Fichiers verrouillés** : Fermer applications qui utilisent les fichiers
- **Performance lente** : Réduire la taille des chunks ou utiliser SSD
- **Espace disque** : Vérifier avant traitement de gros volumes

### 📧 **Logs et rapports**
Tous les scripts génèrent des rapports détaillés avec :
- Nombre de fichiers traités
- Espace disque libéré/économisé
- Erreurs rencontrées
- Temps de traitement

Conservez ces documentations avec vos scripts pour référence future ! 📖