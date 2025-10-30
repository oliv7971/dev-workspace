# =============================================================================
# SCRIPT DE NETTOYAGE AVANT COPIE - SUPPRESSION DES DOUBLONS EXISTANTS
# =============================================================================
# Ce script compare des fichiers entre un répertoire source (à copier) 
# et un répertoire référence (déjà classé) pour supprimer les doublons
# du répertoire source avant la copie
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$SourcePath = "C:\NouvellesDonnees"      # Répertoire des fichiers à copier
$ReferencePath = "C:\DonneesClassees"    # Répertoire de référence (déjà classé)
$Action = "Report"                       # "Report", "Delete", "Move"
$QuarantinePath = "C:\DoublonsDetectes" # Dossier de quarantaine si Action = "Move"
$WhatIf = $true                         # $true = simulation, $false = action réelle
$Verbose = $true                        # $true = affichage détaillé
$MinFileSize = 0                        # Taille minimum en bytes (0 = tous les fichiers)
$HashAlgorithm = "SHA256"               # SHA256 (précis) ou MD5 (plus rapide)
$ExcludeExtensions = @(".tmp", ".log")  # Extensions à exclure
$CheckMultipleReferences = $false       # $true = vérifier plusieurs répertoires de référence

# Répertoires de référence multiples (si $CheckMultipleReferences = $true)
$MultipleReferencePaths = @(
    "C:\Archive1",
    "C:\Archive2", 
    "C:\Backup"
)

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
        return (Get-FileHash -Path $FilePath -Algorithm $HashAlgorithm).Hash
    }
    catch {
        Write-Warning "Impossible de calculer le hash pour : $FilePath - $($_.Exception.Message)"
        return $null
    }
}

# Fonction pour créer un index des fichiers avec leur hash
function New-FileIndex {
    param(
        [string[]]$Paths,
        [string]$Description
    )
    
    Write-Host "📋 Construction de l'index : $Description..." -ForegroundColor Green
    
    $index = @{}
    $totalFiles = 0
    
    foreach ($path in $Paths) {
        if (-not (Test-Path $path)) {
            Write-Warning "Le chemin '$path' n'existe pas, ignoré."
            continue
        }
        
        $files = Get-ChildItem -Path $path -Recurse -File | Where-Object {
            $_.Length -ge $MinFileSize -and
            ($ExcludeExtensions.Count -eq 0 -or $_.Extension -notin $ExcludeExtensions)
        }
        
        Write-Host "   Fichiers dans $path : $($files.Count)" -ForegroundColor Gray
        
        foreach ($file in $files) {
            $hash = Get-FileHashSafe -FilePath $file.FullName
            if ($hash) {
                if (-not $index.ContainsKey($hash)) {
                    $index[$hash] = @()
                }
                $index[$hash] += $file
                $totalFiles++
            }
        }
    }
    
    Write-Host "   Total indexé : $totalFiles fichiers" -ForegroundColor Gray
    return $index
}

# Vérifications initiales
if (-not (Test-Path $SourcePath)) {
    Write-Error "Le répertoire source '$SourcePath' n'existe pas."
    exit 1
}

# Déterminer les répertoires de référence
$referencePaths = if ($CheckMultipleReferences) {
    $MultipleReferencePaths | Where-Object { Test-Path $_ }
} else {
    @($ReferencePath) | Where-Object { Test-Path $_ }
}

if ($referencePaths.Count -eq 0) {
    Write-Error "Aucun répertoire de référence valide trouvé."
    exit 1
}

# Créer le dossier de quarantaine si nécessaire
if ($Action -eq "Move" -and -not $WhatIf -and -not (Test-Path $QuarantinePath)) {
    New-Item -Path $QuarantinePath -ItemType Directory -Force | Out-Null
    Write-Host "Dossier de quarantaine créé : $QuarantinePath" -ForegroundColor Green
}

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "NETTOYAGE AVANT COPIE - DETECTION DES DOUBLONS" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Répertoire source : $SourcePath" -ForegroundColor White
Write-Host "Répertoires de référence :" -ForegroundColor White
foreach ($refPath in $referencePaths) {
    Write-Host "  - $refPath" -ForegroundColor Gray
}
Write-Host "Action configurée : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host ""

# Étape 1 : Construire l'index des fichiers de référence
$referenceIndex = New-FileIndex -Paths $referencePaths -Description "Fichiers de référence"

# Étape 2 : Construire l'index des fichiers source
$sourceIndex = New-FileIndex -Paths @($SourcePath) -Description "Fichiers source"

# Étape 3 : Identifier les doublons
Write-Host "🔍 Recherche des doublons..." -ForegroundColor Green
$duplicatesFound = @()
$totalSpaceSaved = 0

foreach ($hash in $sourceIndex.Keys) {
    if ($referenceIndex.ContainsKey($hash)) {
        # Doublon détecté !
        $sourceFiles = $sourceIndex[$hash]
        $referenceFiles = $referenceIndex[$hash]
        
        foreach ($sourceFile in $sourceFiles) {
            $duplicatesFound += [PSCustomObject]@{
                SourceFile = $sourceFile
                ReferenceFiles = $referenceFiles
                Hash = $hash
                Size = $sourceFile.Length
            }
            $totalSpaceSaved += $sourceFile.Length
        }
    }
}

# Étape 4 : Afficher les résultats
if ($duplicatesFound.Count -eq 0) {
    Write-Host "✅ Aucun doublon détecté ! Tous les fichiers source sont uniques." -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Résumé :" -ForegroundColor Cyan
    Write-Host "   Fichiers source analysés : $($sourceIndex.Values.Count)" -ForegroundColor Gray
    Write-Host "   Fichiers référence analysés : $($referenceIndex.Values.Count)" -ForegroundColor Gray
    exit 0
}

Write-Host "⚠️  Doublons détectés : $($duplicatesFound.Count) fichiers" -ForegroundColor Red
Write-Host "💾 Espace qui sera libéré : $(Format-FileSize $totalSpaceSaved)" -ForegroundColor Yellow
Write-Host ""

# Étape 5 : Traiter les doublons
$processedCount = 0
foreach ($duplicate in $duplicatesFound) {
    $sourceFile = $duplicate.SourceFile
    $referenceFiles = $duplicate.ReferenceFiles
    
    Write-Host "📄 Doublon détecté ($(Format-FileSize $sourceFile.Length)) :" -ForegroundColor Yellow
    Write-Host "   Source    : $($sourceFile.FullName)" -ForegroundColor Red
    Write-Host "   Référence(s) :" -ForegroundColor Green
    foreach ($refFile in $referenceFiles) {
        Write-Host "     - $($refFile.FullName)" -ForegroundColor Gray
    }
    
    if ($Verbose) {
        Write-Host "   Hash: $($duplicate.Hash)" -ForegroundColor DarkGray
    }
    
    # Actions sur le fichier source
    switch ($Action) {
        "Delete" {
            if (-not $WhatIf) {
                try {
                    Remove-Item -Path $sourceFile.FullName -Force
                    Write-Host "   ✓ Supprimé du répertoire source" -ForegroundColor Red
                    $processedCount++
                }
                catch {
                    Write-Warning "   ❌ Impossible de supprimer : $($sourceFile.FullName) - $($_.Exception.Message)"
                }
            }
            else {
                Write-Host "   [WhatIf] Suppression du répertoire source" -ForegroundColor Yellow
                $processedCount++
            }
        }
        "Move" {
            $relativePath = $sourceFile.FullName.Substring($SourcePath.Length).TrimStart('\')
            $quarantinePath = Join-Path $QuarantinePath $relativePath
            $quarantineDir = Split-Path $quarantinePath -Parent
            
            if (-not $WhatIf) {
                try {
                    if (-not (Test-Path $quarantineDir)) {
                        New-Item -Path $quarantineDir -ItemType Directory -Force | Out-Null
                    }
                    Move-Item -Path $sourceFile.FullName -Destination $quarantinePath -Force
                    Write-Host "   ✓ Déplacé vers quarantaine : $quarantinePath" -ForegroundColor Blue
                    $processedCount++
                }
                catch {
                    Write-Warning "   ❌ Impossible de déplacer : $($sourceFile.FullName) - $($_.Exception.Message)"
                }
            }
            else {
                Write-Host "   [WhatIf] Déplacement vers : $quarantinePath" -ForegroundColor Yellow
                $processedCount++
            }
        }
        "Report" {
            Write-Host "   ℹ️  Fichier marqué comme doublon (aucune action)" -ForegroundColor Cyan
        }
    }
    Write-Host ""
}

# Résumé final
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "RÉSUMÉ DU NETTOYAGE" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Fichiers source analysés : $($sourceIndex.Values.Count)" -ForegroundColor White
Write-Host "Fichiers référence analysés : $($referenceIndex.Values.Count)" -ForegroundColor White
Write-Host "Doublons détectés : $($duplicatesFound.Count)" -ForegroundColor Red
Write-Host "Fichiers traités : $processedCount" -ForegroundColor Green
Write-Host "Espace libéré : $(Format-FileSize $totalSpaceSaved)" -ForegroundColor Yellow
Write-Host "Action configurée : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host "=" * 70 -ForegroundColor Cyan

if ($WhatIf -and $Action -ne "Report") {
    Write-Host ""
    Write-Host "💡 Pour exécuter réellement les actions, changez `$WhatIf = `$false" -ForegroundColor Cyan
}

if ($Action -eq "Delete" -and $duplicatesFound.Count -gt 0) {
    Write-Host ""
    Write-Host "🚀 Après nettoyage, vous pouvez copier les fichiers restants du répertoire source" -ForegroundColor Green
    Write-Host "   vers le répertoire de référence sans risque de doublons !" -ForegroundColor Green
}