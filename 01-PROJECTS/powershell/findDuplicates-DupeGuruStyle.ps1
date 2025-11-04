# =============================================================================
# SCRIPT DE DÉTECTION DE DOUBLONS - STYLE DUPEGURU
# =============================================================================
# Compare un ou plusieurs répertoires "à nettoyer" avec un répertoire "référence"
# Supprime les doublons internes ET les fichiers déjà présents dans la référence
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================

# RÉPERTOIRE DE RÉFÉRENCE (vos données déjà organisées/classées)
$ReferencePath = "D:\MesDocumentsClasses"

# RÉPERTOIRES À NETTOYER (nouvelles données potentiellement en double)
$PathsToClean = @(
    "D:\Telechargements",
    "D:\ATrier",
    "E:\Backup"
)

# OPTIONS DE TRAITEMENT
$Action = "Report"                       # "Report" / "Delete" / "Move" / "Quarantine"
$QuarantinePath = "D:\Doublons_Detectes" # Dossier de quarantaine
$WhatIf = $true                         # $true = simulation, $false = action réelle
$Verbose = $true                        # $true = affichage détaillé

# OPTIONS D'ANALYSE
$MinFileSize = 1KB                      # Ignorer fichiers < 1KB (0 = tout analyser)
$HashAlgorithm = "SHA256"               # SHA256 (précis) ou MD5 (rapide)
$ExcludeExtensions = @(".tmp", ".log")  # Extensions à ignorer

# OPTIONS AVANCÉES
$RemoveInternalDuplicates = $true       # Supprimer les doublons INTERNES aux répertoires à nettoyer
$CreateDetailedReport = $true           # Créer un rapport CSV détaillé
$ReportPath = ".\rapport_doublons.csv"  # Chemin du rapport

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

# Fonction pour formater la taille des fichiers
function Format-FileSize {
    param([long]$Size)
    
    if ($Size -lt 1KB) { return "$Size B" }
    elseif ($Size -lt 1MB) { return "{0:N2} KB" -f ($Size / 1KB) }
    elseif ($Size -lt 1GB) { return "{0:N2} MB" -f ($Size / 1MB) }
    else { return "{0:N2} GB" -f ($Size / 1GB) }
}

# Fonction pour calculer le hash d'un fichier
function Get-FileHashSafe {
    param([string]$FilePath)
    
    try {
        return (Get-FileHash -LiteralPath $FilePath -Algorithm $HashAlgorithm -ErrorAction Stop).Hash
    }
    catch {
        Write-Warning "Impossible de calculer le hash pour : $FilePath - $($_.Exception.Message)"
        return $null
    }
}

# Fonction pour construire un index de fichiers
function Build-FileIndex {
    param(
        [string[]]$Paths,
        [string]$Description
    )
    
    Write-Host "📋 Construction de l'index : $Description..." -ForegroundColor Green
    
    $index = @{}
    $fileList = @()
    $totalFiles = 0
    
    foreach ($path in $Paths) {
        if (-not (Test-Path $path)) {
            Write-Warning "Le chemin '$path' n'existe pas, ignoré."
            continue
        }
        
        Write-Host "   Analyse de : $path" -ForegroundColor Gray
        $files = Get-ChildItem -LiteralPath $path -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
            $_.Length -ge $MinFileSize -and
            ($ExcludeExtensions.Count -eq 0 -or $_.Extension -notin $ExcludeExtensions)
        }
        
        Write-Host "   Fichiers trouvés : $($files.Count)" -ForegroundColor Gray
        
        $processedInPath = 0
        foreach ($file in $files) {
            $processedInPath++
            if ($processedInPath % 100 -eq 0) {
                Write-Progress -Activity "Indexation $Description" -Status "$path" -PercentComplete (($processedInPath / $files.Count) * 100)
            }
            
            $hash = Get-FileHashSafe -FilePath $file.FullName
            if ($hash) {
                if (-not $index.ContainsKey($hash)) {
                    $index[$hash] = @()
                }
                $index[$hash] += $file
                $fileList += [PSCustomObject]@{
                    Path = $file.FullName
                    Hash = $hash
                    Size = $file.Length
                    Directory = $file.DirectoryName
                }
                $totalFiles++
            }
        }
        Write-Progress -Activity "Indexation $Description" -Completed
    }
    
    Write-Host "   Total indexé : $totalFiles fichiers" -ForegroundColor Cyan
    return @{
        Index = $index
        Files = $fileList
    }
}

# Fonction pour traiter les doublons
function Process-Duplicate {
    param(
        [System.IO.FileInfo]$File,
        [string]$Reason,
        [string]$ReferenceFile = $null
    )
    
    $script:duplicatesFound++
    $script:totalSpaceSaved += $File.Length
    
    # Ajouter au rapport
    if ($CreateDetailedReport) {
        $script:reportData += [PSCustomObject]@{
            FichierDouble = $File.FullName
            Taille = Format-FileSize $File.Length
            Raison = $Reason
            Reference = $ReferenceFile
            DateModification = $File.LastWriteTime
            Action = $Action
        }
    }
    
    if ($Verbose) {
        Write-Host "   🔴 DOUBLON : $($File.FullName)" -ForegroundColor Red
        Write-Host "      Raison : $Reason" -ForegroundColor Gray
        Write-Host "      Taille : $(Format-FileSize $File.Length)" -ForegroundColor Gray
        if ($ReferenceFile) {
            Write-Host "      Référence : $ReferenceFile" -ForegroundColor Gray
        }
    }
    
    # Exécuter l'action
    switch ($Action) {
        "Delete" {
            if (-not $WhatIf) {
                try {
                    Remove-Item -LiteralPath $File.FullName -Force -ErrorAction Stop
                    Write-Host "   ✅ Supprimé" -ForegroundColor Green
                    $script:filesProcessed++
                }
                catch {
                    Write-Warning "   ❌ Impossible de supprimer : $($_.Exception.Message)"
                }
            }
            else {
                Write-Host "   [WhatIf] Suppression simulée" -ForegroundColor Yellow
                $script:filesProcessed++
            }
        }
        
        "Move" {
            $relativePath = $File.FullName.Substring([System.IO.Path]::GetPathRoot($File.FullName).Length)
            $newPath = Join-Path $QuarantinePath $relativePath
            $newDir = Split-Path $newPath -Parent
            
            if (-not $WhatIf) {
                try {
                    if (-not (Test-Path $newDir)) {
                        New-Item -Path $newDir -ItemType Directory -Force | Out-Null
                    }
                    Move-Item -LiteralPath $File.FullName -Destination $newPath -Force -ErrorAction Stop
                    Write-Host "   ✅ Déplacé vers quarantaine" -ForegroundColor Blue
                    $script:filesProcessed++
                }
                catch {
                    Write-Warning "   ❌ Impossible de déplacer : $($_.Exception.Message)"
                }
            }
            else {
                Write-Host "   [WhatIf] Déplacement simulé vers : $newPath" -ForegroundColor Yellow
                $script:filesProcessed++
            }
        }
        
        "Quarantine" {
            # Alias pour Move
            $relativePath = $File.FullName.Substring([System.IO.Path]::GetPathRoot($File.FullName).Length)
            $newPath = Join-Path $QuarantinePath $relativePath
            $newDir = Split-Path $newPath -Parent
            
            if (-not $WhatIf) {
                try {
                    if (-not (Test-Path $newDir)) {
                        New-Item -Path $newDir -ItemType Directory -Force | Out-Null
                    }
                    Move-Item -LiteralPath $File.FullName -Destination $newPath -Force -ErrorAction Stop
                    Write-Host "   ✅ Mis en quarantaine" -ForegroundColor Blue
                    $script:filesProcessed++
                }
                catch {
                    Write-Warning "   ❌ Impossible de mettre en quarantaine : $($_.Exception.Message)"
                }
            }
            else {
                Write-Host "   [WhatIf] Quarantaine simulée" -ForegroundColor Yellow
                $script:filesProcessed++
            }
        }
    }
}

# Variables globales pour les statistiques
$script:duplicatesFound = 0
$script:filesProcessed = 0
$script:totalSpaceSaved = 0
$script:reportData = @()

# Bannière
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "DÉTECTION DE DOUBLONS - STYLE DUPEGURU" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Répertoire de référence : $ReferencePath" -ForegroundColor White
Write-Host "Répertoires à nettoyer :" -ForegroundColor White
foreach ($path in $PathsToClean) {
    Write-Host "  - $path" -ForegroundColor Gray
}
Write-Host "Action : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host ""

# Vérification des chemins
$validPathsToClean = @()
foreach ($path in $PathsToClean) {
    if (Test-Path $path) {
        $validPathsToClean += $path
    }
    else {
        Write-Warning "Chemin ignoré (n'existe pas) : $path"
    }
}

if ($validPathsToClean.Count -eq 0) {
    Write-Error "Aucun répertoire valide à nettoyer !"
    exit 1
}

if (-not (Test-Path $ReferencePath)) {
    Write-Error "Le répertoire de référence n'existe pas : $ReferencePath"
    exit 1
}

# Créer le dossier de quarantaine si nécessaire
if (($Action -eq "Move" -or $Action -eq "Quarantine") -and -not $WhatIf) {
    if (-not (Test-Path $QuarantinePath)) {
        New-Item -Path $QuarantinePath -ItemType Directory -Force | Out-Null
        Write-Host "📁 Dossier de quarantaine créé : $QuarantinePath" -ForegroundColor Green
    }
}

# Étape 1 : Indexer le répertoire de référence
Write-Host "`n🔵 ÉTAPE 1 : Indexation du répertoire de référence" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
$referenceData = Build-FileIndex -Paths @($ReferencePath) -Description "Référence"

# Étape 2 : Indexer les répertoires à nettoyer
Write-Host "`n🔵 ÉTAPE 2 : Indexation des répertoires à nettoyer" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
$toCleanData = Build-FileIndex -Paths $validPathsToClean -Description "À nettoyer"

# Étape 3 : Détecter les doublons par rapport à la référence
Write-Host "`n🔵 ÉTAPE 3 : Détection des doublons vs référence" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$referenceDuplicates = 0
foreach ($hash in $toCleanData.Index.Keys) {
    if ($referenceData.Index.ContainsKey($hash)) {
        # Fichier existe déjà dans la référence
        $referenceFiles = $referenceData.Index[$hash]
        $duplicateFiles = $toCleanData.Index[$hash]
        
        foreach ($duplicateFile in $duplicateFiles) {
            $referenceDuplicates++
            Process-Duplicate -File $duplicateFile -Reason "Existe déjà dans la référence" -ReferenceFile $referenceFiles[0].FullName
        }
    }
}

Write-Host "   Doublons vs référence : $referenceDuplicates" -ForegroundColor Yellow

# Étape 4 : Détecter les doublons internes (si activé)
Write-Host "`n🔵 ÉTAPE 4 : Détection des doublons internes" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$internalDuplicates = 0
if ($RemoveInternalDuplicates) {
    foreach ($hash in $toCleanData.Index.Keys) {
        # Ignorer si déjà traité comme doublon de référence
        if ($referenceData.Index.ContainsKey($hash)) {
            continue
        }
        
        $filesWithSameHash = $toCleanData.Index[$hash]
        if ($filesWithSameHash.Count -gt 1) {
            # Garder le premier, supprimer les autres
            for ($i = 1; $i -lt $filesWithSameHash.Count; $i++) {
                $internalDuplicates++
                Process-Duplicate -File $filesWithSameHash[$i] -Reason "Doublon interne (copie $($i+1)/$($filesWithSameHash.Count))" -ReferenceFile $filesWithSameHash[0].FullName
            }
        }
    }
    Write-Host "   Doublons internes : $internalDuplicates" -ForegroundColor Yellow
}
else {
    Write-Host "   Détection des doublons internes désactivée" -ForegroundColor Gray
}

# Étape 5 : Créer le rapport détaillé
if ($CreateDetailedReport -and $script:reportData.Count -gt 0) {
    Write-Host "`n🔵 ÉTAPE 5 : Création du rapport" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    
    try {
        $script:reportData | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8
        Write-Host "   ✅ Rapport créé : $ReportPath" -ForegroundColor Green
        Write-Host "   📊 Lignes : $($script:reportData.Count)" -ForegroundColor Gray
    }
    catch {
        Write-Warning "Impossible de créer le rapport : $($_.Exception.Message)"
    }
}

# Résumé final
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "RÉSUMÉ DE L'ANALYSE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Fichiers de référence analysés : $($referenceData.Files.Count)" -ForegroundColor White
Write-Host "Fichiers à nettoyer analysés : $($toCleanData.Files.Count)" -ForegroundColor White
Write-Host ""
Write-Host "Doublons vs référence : $referenceDuplicates" -ForegroundColor Yellow
Write-Host "Doublons internes : $internalDuplicates" -ForegroundColor Yellow
Write-Host "Total doublons détectés : $script:duplicatesFound" -ForegroundColor Red
Write-Host ""
Write-Host "Espace disque gaspillé : $(Format-FileSize $script:totalSpaceSaved)" -ForegroundColor Magenta
Write-Host "Fichiers traités : $script:filesProcessed" -ForegroundColor Green
Write-Host ""
Write-Host "Action configurée : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host "=" * 80 -ForegroundColor Cyan

if ($WhatIf -and $Action -ne "Report") {
    Write-Host ""
    Write-Host "💡 Pour exécuter réellement les actions, changez `$WhatIf = `$false" -ForegroundColor Cyan
}

if ($script:duplicatesFound -gt 0 -and -not $WhatIf) {
    Write-Host ""
    Write-Host "✅ Nettoyage terminé ! Vos répertoires sont maintenant dédoublonnés." -ForegroundColor Green
}