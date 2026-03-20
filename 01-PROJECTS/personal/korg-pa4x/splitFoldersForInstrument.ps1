# =============================================================================
# SCRIPT DE DIVISION DE DOSSIERS POUR INSTRUMENTS DE MUSIQUE
# =============================================================================
# Ce script divise les dossiers contenant trop de fichiers en sous-dossiers
# numérotés pour assurer la compatibilité avec les instruments de musique
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$BasePath = "C:\MusiqueInstrument"       # Chemin racine à traiter
$MaxFilesPerFolder = 256                 # Limite de fichiers par dossier (256 ou 512)
$WhatIf = $true                         # $true = simulation, $false = action réelle
$Verbose = $true                        # $true = affichage détaillé
$CreateBackup = $true                   # $true = créer une sauvegarde avant modification
$BackupPath = "C:\MusiqueInstrument_Backup"  # Chemin de sauvegarde
$PreserveSorting = $true               # $true = maintenir l'ordre alphabétique
$FolderNamePattern = "Batch_{0:D2}"    # Format des noms de dossiers (Batch_01, Batch_02...)
$FileExtensions = @(".mp3", ".wav", ".flac", ".m4a", ".ogg")  # Extensions à traiter (vide = tous)

# Options avancées
$MinFilesToSplit = 10                  # Minimum de fichiers avant division
$RecursiveDepth = -1                   # Profondeur (-1 = illimitée)

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

# Fonction pour créer une sauvegarde
function New-Backup {
    param([string]$SourcePath, [string]$BackupPath)
    
    if ($CreateBackup -and -not $WhatIf) {
        Write-Host "💾 Création de la sauvegarde..." -ForegroundColor Yellow
        try {
            if (Test-Path $BackupPath) {
                $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
                $BackupPath = "${BackupPath}_$timestamp"
            }
            Copy-Item -Path $SourcePath -Destination $BackupPath -Recurse -Force
            Write-Host "   ✓ Sauvegarde créée : $BackupPath" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Warning "Impossible de créer la sauvegarde : $($_.Exception.Message)"
            return $false
        }
    }
    return $true
}

# Fonction pour obtenir les fichiers musicaux
function Get-MusicFiles {
    param([string]$Path)
    
    $files = Get-ChildItem -Path $Path -File
    
    if ($FileExtensions.Count -gt 0) {
        $files = $files | Where-Object { $_.Extension.ToLower() -in $FileExtensions }
    }
    
    if ($PreserveSorting) {
        $files = $files | Sort-Object Name
    }
    
    return $files
}

# Fonction pour diviser un dossier
function Split-Folder {
    param(
        [string]$FolderPath,
        [int]$MaxFiles,
        [string]$Pattern
    )
    
    $files = Get-MusicFiles -Path $FolderPath
    $folderName = Split-Path $FolderPath -Leaf
    
    if ($files.Count -le $MaxFiles) {
        if ($Verbose) {
            Write-Host "   ✓ $folderName : $($files.Count) fichiers (OK)" -ForegroundColor Green
        }
        return $false  # Pas de division nécessaire
    }
    
    Write-Host "📁 Division nécessaire : $folderName ($($files.Count) fichiers)" -ForegroundColor Yellow
    
    # Calculer le nombre de sous-dossiers nécessaires
    $batchCount = [Math]::Ceiling($files.Count / $MaxFiles)
    Write-Host "   Création de $batchCount sous-dossiers..." -ForegroundColor Gray
    
    $batchIndex = 1
    $processedFiles = 0
    
    for ($i = 0; $i -lt $files.Count; $i += $MaxFiles) {
        $endIndex = [Math]::Min($i + $MaxFiles - 1, $files.Count - 1)
        $batchFiles = $files[$i..$endIndex]
        
        # Nom du sous-dossier
        $batchFolderName = $Pattern -f $batchIndex
        $batchFolderPath = Join-Path $FolderPath $batchFolderName
        
        Write-Host "   📂 $batchFolderName : $($batchFiles.Count) fichiers" -ForegroundColor Cyan
        
        if (-not $WhatIf) {
            try {
                # Créer le sous-dossier
                if (-not (Test-Path $batchFolderPath)) {
                    New-Item -Path $batchFolderPath -ItemType Directory -Force | Out-Null
                }
                
                # Déplacer les fichiers
                foreach ($file in $batchFiles) {
                    $newPath = Join-Path $batchFolderPath $file.Name
                    Move-Item -Path $file.FullName -Destination $newPath -Force
                    $processedFiles++
                    
                    if ($Verbose) {
                        Write-Host "     → $($file.Name)" -ForegroundColor DarkGray
                    }
                }
                
                Write-Host "   ✓ Sous-dossier créé : $batchFolderName" -ForegroundColor Green
            }
            catch {
                Write-Warning "Erreur lors de la création du sous-dossier $batchFolderName : $($_.Exception.Message)"
            }
        }
        else {
            Write-Host "   [WhatIf] Création du sous-dossier : $batchFolderName" -ForegroundColor Yellow
            foreach ($file in $batchFiles) {
                if ($Verbose) {
                    Write-Host "     [WhatIf] → $($file.Name)" -ForegroundColor DarkGray
                }
            }
            $processedFiles += $batchFiles.Count
        }
        
        $batchIndex++
    }
    
    return $true  # Division effectuée
}

# Fonction pour traiter récursivement
function Invoke-DirectoryProcessing {
    param(
        [string]$Path,
        [int]$CurrentDepth = 0
    )
    
    if ($RecursiveDepth -ne -1 -and $CurrentDepth -gt $RecursiveDepth) {
        return
    }
    
    $folders = Get-ChildItem -Path $Path -Directory | Sort-Object Name
    $stats = @{
        FoldersProcessed = 0
        FoldersSplit = 0
        FilesProcessed = 0
    }
    
    foreach ($folder in $folders) {
        # Ignorer les dossiers de sauvegarde et les sous-dossiers créés
        if ($folder.FullName -eq $BackupPath -or $folder.Name -match "^Batch_\d+$") {
            continue
        }
        
        $stats.FoldersProcessed++
        
        # Traiter d'abord les sous-dossiers
        $subStats = Invoke-DirectoryProcessing -Path $folder.FullName -CurrentDepth ($CurrentDepth + 1)
        $stats.FoldersProcessed += $subStats.FoldersProcessed
        $stats.FoldersSplit += $subStats.FoldersSplit
        $stats.FilesProcessed += $subStats.FilesProcessed
        
        # Puis traiter le dossier actuel
        $files = Get-MusicFiles -Path $folder.FullName
        
        if ($files.Count -ge $MinFilesToSplit) {
            $wasSplit = Split-Folder -FolderPath $folder.FullName -MaxFiles $MaxFilesPerFolder -Pattern $FolderNamePattern
            if ($wasSplit) {
                $stats.FoldersSplit++
                $stats.FilesProcessed += $files.Count
            }
        }
        elseif ($Verbose -and $files.Count -gt 0) {
            Write-Host "   ✓ $($folder.Name) : $($files.Count) fichiers (pas de division nécessaire)" -ForegroundColor Green
        }
    }
    
    return $stats
}

# Vérifier que le répertoire de base existe
if (-not (Test-Path $BasePath)) {
    Write-Error "Le chemin '$BasePath' n'existe pas."
    exit 1
}

# Affichage de la configuration
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "DIVISION DE DOSSIERS POUR INSTRUMENT DE MUSIQUE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Répertoire racine : $BasePath" -ForegroundColor White
Write-Host "Limite par dossier : $MaxFilesPerFolder fichiers" -ForegroundColor White
Write-Host "Extensions traitées : $($FileExtensions -join ', ')" -ForegroundColor White
Write-Host "Format des sous-dossiers : $FolderNamePattern" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host "Sauvegarde : $CreateBackup" -ForegroundColor $(if($CreateBackup){"Green"}else{"Red"})
Write-Host ""

# Créer une sauvegarde si demandée
if ($CreateBackup) {
    $backupSuccess = New-Backup -SourcePath $BasePath -BackupPath $BackupPath
    if (-not $backupSuccess -and -not $WhatIf) {
        Write-Host "❌ Échec de la sauvegarde. Arrêt du traitement." -ForegroundColor Red
        exit 1
    }
}

# Analyser d'abord la structure
Write-Host "🔍 Analyse de la structure..." -ForegroundColor Green
$allFolders = Get-ChildItem -Path $BasePath -Directory -Recurse
$foldersNeedingSplit = @()

foreach ($folder in $allFolders) {
    $files = Get-MusicFiles -Path $folder.FullName
    if ($files.Count -gt $MaxFilesPerFolder) {
        $foldersNeedingSplit += [PSCustomObject]@{
            Path = $folder.FullName
            Name = $folder.Name
            FileCount = $files.Count
            BatchesNeeded = [Math]::Ceiling($files.Count / $MaxFilesPerFolder)
        }
    }
}

Write-Host "   Dossiers analysés : $($allFolders.Count)" -ForegroundColor Gray
Write-Host "   Dossiers à diviser : $($foldersNeedingSplit.Count)" -ForegroundColor $(if($foldersNeedingSplit.Count -gt 0){"Yellow"}else{"Green"})

if ($foldersNeedingSplit.Count -eq 0) {
    Write-Host "✅ Aucun dossier ne dépasse la limite de $MaxFilesPerFolder fichiers !" -ForegroundColor Green
    exit 0
}

# Afficher le plan de division
Write-Host ""
Write-Host "📋 Plan de division :" -ForegroundColor Yellow
foreach ($folder in $foldersNeedingSplit) {
    Write-Host "   📁 $($folder.Name) : $($folder.FileCount) fichiers → $($folder.BatchesNeeded) sous-dossiers" -ForegroundColor Gray
}
Write-Host ""

# Traitement principal
Write-Host "🚀 Début du traitement..." -ForegroundColor Green
$startTime = Get-Date
$finalStats = Invoke-DirectoryProcessing -Path $BasePath

$endTime = Get-Date
$duration = $endTime - $startTime

# Résumé final
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "RÉSUMÉ DU TRAITEMENT" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Dossiers traités : $($finalStats.FoldersProcessed)" -ForegroundColor White
Write-Host "Dossiers divisés : $($finalStats.FoldersSplit)" -ForegroundColor Yellow
Write-Host "Fichiers déplacés : $($finalStats.FilesProcessed)" -ForegroundColor Green
Write-Host "Limite configurée : $MaxFilesPerFolder fichiers par dossier" -ForegroundColor White
Write-Host "Durée du traitement : $($duration.ToString('mm\:ss'))" -ForegroundColor Gray
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
if ($CreateBackup -and -not $WhatIf) {
    Write-Host "Sauvegarde disponible : $BackupPath" -ForegroundColor Cyan
}
Write-Host "=" * 70 -ForegroundColor Cyan

if ($WhatIf) {
    Write-Host ""
    Write-Host "💡 Pour exécuter réellement, changez `$WhatIf = `$false" -ForegroundColor Cyan
}

if ($finalStats.FoldersSplit -gt 0 -and -not $WhatIf) {
    Write-Host ""
    Write-Host "🎵 Vos dossiers sont maintenant compatibles avec votre instrument !" -ForegroundColor Green
    Write-Host "   Chaque sous-dossier contient maximum $MaxFilesPerFolder fichiers." -ForegroundColor Green
}