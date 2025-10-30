# ⚡ findDuplicateFiles-Parallel.ps1 - Guide d'utilisation

## Description
Version parallélisée du script de détection de doublons. Utilise plusieurs processus simultanés pour accélérer le traitement sur de gros volumes de fichiers.

## Utilisation principale
- Analyse de très gros volumes (>100k fichiers)
- Traitement plus rapide sur machines multi-cœurs
- Optimisation pour serveurs/NAS performants

## Configuration rapide
```powershell
$BasePath = "D:\GrosVolume"          # Dossier à analyser
$EnableParallel = $true              # Activer parallélisation
$MaxParallelJobs = 4                 # Nombre de processus (= nb cœurs CPU)
$ChunkSize = 1000                    # Fichiers par processus
```

## Quand utiliser cette version
✅ **Utilisez-la quand** :
- Plus de 10 000 fichiers à traiter
- Machine avec 4+ cœurs CPU
- SSD ou stockage rapide
- Beaucoup de RAM disponible (8GB+)

❌ **Évitez-la quand** :
- Moins de 1000 fichiers (version classique suffira)
- Disque dur mécanique lent
- Machine avec peu de RAM
- Stockage réseau lent

## Configuration optimale
```powershell
# Pour machine 8 cœurs avec SSD
$MaxParallelJobs = 6                 # Laissez 2 cœurs pour le système
$ChunkSize = 2000                    # Chunks plus gros = moins d'overhead

# Pour NAS ou stockage lent  
$MaxParallelJobs = 2                 # Moins de concurrence I/O
$ChunkSize = 500                     # Chunks plus petits
```

## Performances attendues
- **Gain typique** : 2-4x plus rapide que la version classique
- **100k fichiers** : 10-20 minutes (vs 45-60 min en séquentiel)
- **1M fichiers** : 1-3 heures (vs 6-8h en séquentiel)

## Surveillance recommandée
- **Task Manager** : Vérifier usage CPU et RAM
- **Performances disque** : Éviter la saturation I/O
- **Température** : Surveiller si traitement long

## Précautions spécifiques
⚠️ **Plus complexe que la version classique**
- Consomme plus de RAM (multiply par nb de jobs)
- Peut saturer le stockage réseau
- Plus difficile à interrompre proprement

## Workflow recommandé
1. **Test petit volume** : Valider configuration sur sous-dossier
2. **Surveillance** : Lancer et surveiller ressources système
3. **Ajustement** : Modifier nb de jobs si problèmes performance

## Cas d'usage typiques
- **Serveurs de fichiers** : Nettoyage de gros volumes
- **Archives d'entreprise** : Traitement batch nocturne
- **NAS hautes performances** : Optimisation pour SSD
- **Workstations puissantes** : Traitement de bibliothèques massives

## Résultat attendu
- Même résultat que version classique mais plus rapide
- Utilisation optimale des ressources multi-cœurs
- Traitement efficace de très gros volumes