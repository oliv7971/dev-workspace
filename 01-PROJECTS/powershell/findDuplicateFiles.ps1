# =============================================================================
# SCRIPT DE RECHERCHE DE FICHIERS DOUBLONS
# =============================================================================
# Ce script recherche les fichiers doublons basés sur leur hash (empreinte)
# et peut optionnellement les supprimer ou les déplacer
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$BasePath = "C:\VotreCheminIci"          # Chemin à analyser
$Action = "Report"                       # "Report", "Delete", "Move"
$MoveToPath = "C:\Doublons"             # Dossier de destination si Action = "Move"
$WhatIf = $true                         # $true = simulation, $false = action réelle
$Verbose = $true                        # $true = affichage détaillé
$MinFileSize = 0                        # Taille minimum en bytes (0 = tous les fichiers)
$HashAlgorithm = "SHA256"               # SHA256 (précis) ou MD5 (plus rapide)
$ExcludeExtensions = @(".tmp", ".log")  # Extensions à exclure (vide pour tout inclure)

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

# Vérifier que le répertoire de base existe
if (-not (Test-Path $BasePath)) {
    Write-Error "Le chemin '$BasePath' n'existe pas."
    exit 1
}

# Créer le dossier de destination si nécessaire
if ($Action -eq "Move" -and -not $WhatIf -and -not (Test-Path $MoveToPath)) {
    New-Item -Path $MoveToPath -ItemType Directory -Force | Out-Null
    Write-Host "Dossier créé : $MoveToPath" -ForegroundColor Green
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RECHERCHE DE FICHIERS DOUBLONS" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Répertoire analysé : $BasePath" -ForegroundColor White
Write-Host "Action configurée : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host "Algorithme de hash : $HashAlgorithm" -ForegroundColor White
Write-Host "Taille minimum : $(Format-FileSize $MinFileSize)" -ForegroundColor White
Write-Host ""

# Étape 1 : Collecter tous les fichiers
Write-Host "📁 Collecte des fichiers..." -ForegroundColor Green
$allFiles = Get-ChildItem -Path $BasePath -Recurse -File | Where-Object {
    $_.Length -ge $MinFileSize -and
    ($ExcludeExtensions.Count -eq 0 -or $_.Extension -notin $ExcludeExtensions)
}

Write-Host "   Fichiers trouvés : $($allFiles.Count)" -ForegroundColor Gray

# Étape 2 : Grouper par taille (optimisation)
Write-Host "📏 Groupement par taille..." -ForegroundColor Green
$groupedBySize = $allFiles | Group-Object Length | Where-Object { $_.Count -gt 1 }
Write-Host "   Groupes de tailles identiques : $($groupedBySize.Count)" -ForegroundColor Gray

# Étape 3 : Calculer les hash pour les fichiers de même taille
Write-Host "🔐 Calcul des empreintes (hash)..." -ForegroundColor Green
$duplicates = @{}
$totalFiles = ($groupedBySize | Measure-Object -Property Count -Sum).Sum
$processedFiles = 0

foreach ($sizeGroup in $groupedBySize) {
    Write-Progress -Activity "Calcul des hash" -Status "Progression" -PercentComplete (($processedFiles / $totalFiles) * 100)
    
    foreach ($file in $sizeGroup.Group) {
        $hash = Get-FileHashSafe -FilePath $file.FullName
        if ($hash) {
            if (-not $duplicates.ContainsKey($hash)) {
                $duplicates[$hash] = @()
            }
            $duplicates[$hash] += $file
        }
        $processedFiles++
    }
}

Write-Progress -Activity "Calcul des hash" -Completed

# Étape 4 : Identifier les vrais doublons
$trueDuplicates = $duplicates.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 }

Write-Host "🔍 Analyse terminée !" -ForegroundColor Green
Write-Host ""

# Étape 5 : Afficher les résultats
if ($trueDuplicates.Count -eq 0) {
    Write-Host "✅ Aucun fichier doublon trouvé !" -ForegroundColor Green
    exit 0
}

Write-Host "⚠️  Doublons détectés : $($trueDuplicates.Count) groupes" -ForegroundColor Red
Write-Host ""

$totalDuplicateFiles = 0
$totalWastedSpace = 0

foreach ($duplicate in $trueDuplicates) {
    $files = $duplicate.Value
    $duplicateCount = $files.Count - 1  # Le premier n'est pas un doublon
    $totalDuplicateFiles += $duplicateCount
    $wastedSpace = $files[0].Length * $duplicateCount
    $totalWastedSpace += $wastedSpace
    
    Write-Host "📄 Groupe de doublons ($(Format-FileSize $files[0].Length)) - $($files.Count) fichiers :" -ForegroundColor Yellow
    Write-Host "   Hash: $($duplicate.Key)" -ForegroundColor Gray
    
    for ($i = 0; $i -lt $files.Count; $i++) {
        $file = $files[$i]
        $status = if ($i -eq 0) { "[ORIGINAL]" } else { "[DOUBLON]" }
        $color = if ($i -eq 0) { "Green" } else { "Red" }
        
        if ($Verbose) {
            Write-Host "   $status $($file.FullName)" -ForegroundColor $color
        }
        
        # Actions sur les doublons (pas sur l'original)
        if ($i -gt 0) {
            switch ($Action) {
                "Delete" {
                    if (-not $WhatIf) {
                        try {
                            Remove-Item -Path $file.FullName -Force
                            Write-Host "   ✓ Supprimé : $($file.FullName)" -ForegroundColor Red
                        }
                        catch {
                            Write-Warning "   ❌ Impossible de supprimer : $($file.FullName) - $($_.Exception.Message)"
                        }
                    }
                    else {
                        Write-Host "   [WhatIf] Suppression : $($file.FullName)" -ForegroundColor Yellow
                    }
                }
                "Move" {
                    $relativePath = $file.FullName.Substring($BasePath.Length).TrimStart('\')
                    $newPath = Join-Path $MoveToPath $relativePath
                    $newDir = Split-Path $newPath -Parent
                    
                    if (-not $WhatIf) {
                        try {
                            if (-not (Test-Path $newDir)) {
                                New-Item -Path $newDir -ItemType Directory -Force | Out-Null
                            }
                            Move-Item -Path $file.FullName -Destination $newPath -Force
                            Write-Host "   ✓ Déplacé vers : $newPath" -ForegroundColor Blue
                        }
                        catch {
                            Write-Warning "   ❌ Impossible de déplacer : $($file.FullName) - $($_.Exception.Message)"
                        }
                    }
                    else {
                        Write-Host "   [WhatIf] Déplacement vers : $newPath" -ForegroundColor Yellow
                    }
                }
            }
        }
    }
    Write-Host ""
}

# Résumé final
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RÉSUMÉ" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Groupes de doublons : $($trueDuplicates.Count)" -ForegroundColor Yellow
Write-Host "Fichiers doublons : $totalDuplicateFiles" -ForegroundColor Red
Write-Host "Espace gaspillé : $(Format-FileSize $totalWastedSpace)" -ForegroundColor Red
Write-Host "Action configurée : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host "=" * 60 -ForegroundColor Cyan

if ($WhatIf -and $Action -ne "Report") {
    Write-Host ""
    Write-Host "💡 Pour exécuter réellement les actions, changez `$WhatIf = `$false" -ForegroundColor Cyan
}