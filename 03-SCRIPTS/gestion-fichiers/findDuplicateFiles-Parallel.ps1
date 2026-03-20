# =============================================================================
# SCRIPT DE RECHERCHE DE DOUBLONS - VERSION PARALLÈLE
# =============================================================================
# Cette version divise le travail en chunks pour la parallélisation
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$BasePath = "C:\VotreCheminIci"          # Chemin à analyser
$Action = "Report"                       # "Report", "Delete", "Move"
$MoveToPath = "C:\Doublons"             # Dossier de destination si Action = "Move"
$WhatIf = $true                         # $true = simulation, $false = action réelle
$Verbose = $true                        # $true = affichage détaillé
$MinFileSize = 0                        # Taille minimum en bytes
$HashAlgorithm = "SHA256"               # SHA256 ou MD5
$ExcludeExtensions = @(".tmp", ".log")  # Extensions à exclure

# PARAMÈTRES DE PARALLÉLISATION
$EnableParallel = $true                 # $true = traitement parallèle
$MaxParallelJobs = 4                    # Nombre de jobs simultanés (recommandé : nb de cœurs CPU)
$ChunkSize = 1000                       # Fichiers par chunk

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

# Fonction pour traiter un chunk de fichiers
$ProcessChunkScript = {
    param($Files, $Algorithm)
    
    $results = @()
    foreach ($file in $Files) {
        try {
            $hash = (Get-FileHash -Path $file.FullName -Algorithm $Algorithm).Hash
            $results += [PSCustomObject]@{
                Path = $file.FullName
                Hash = $hash
                Size = $file.Length
                LastWriteTime = $file.LastWriteTime
            }
        }
        catch {
            Write-Warning "Erreur hash pour $($file.FullName): $($_.Exception.Message)"
        }
    }
    return $results
}

# Vérifier que le répertoire de base existe
if (-not (Test-Path $BasePath)) {
    Write-Error "Le chemin '$BasePath' n'existe pas."
    exit 1
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "RECHERCHE DE DOUBLONS - VERSION PARALLÈLE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Répertoire analysé : $BasePath" -ForegroundColor White
Write-Host "Mode parallèle : $EnableParallel" -ForegroundColor White
if ($EnableParallel) {
    Write-Host "Jobs simultanés : $MaxParallelJobs" -ForegroundColor White
    Write-Host "Taille des chunks : $ChunkSize fichiers" -ForegroundColor White
}
Write-Host ""

# Étape 1 : Collecter tous les fichiers
Write-Host "📁 Collecte des fichiers..." -ForegroundColor Green
$allFiles = Get-ChildItem -Path $BasePath -Recurse -File | Where-Object {
    $_.Length -ge $MinFileSize -and
    ($ExcludeExtensions.Count -eq 0 -or $_.Extension -notin $ExcludeExtensions)
}

Write-Host "   Fichiers trouvés : $($allFiles.Count)" -ForegroundColor Gray

# Étape 2 : Grouper par taille
Write-Host "📏 Groupement par taille..." -ForegroundColor Green
$groupedBySize = $allFiles | Group-Object Length | Where-Object { $_.Count -gt 1 }
$candidateFiles = $groupedBySize | ForEach-Object { $_.Group }

Write-Host "   Candidats doublons : $($candidateFiles.Count)" -ForegroundColor Gray

if ($candidateFiles.Count -eq 0) {
    Write-Host "✅ Aucun fichier de taille identique trouvé !" -ForegroundColor Green
    exit 0
}

# Étape 3 : Traitement parallèle ou séquentiel
Write-Host "🔐 Calcul des empreintes..." -ForegroundColor Green

if ($EnableParallel -and $candidateFiles.Count -gt $ChunkSize) {
    Write-Host "   Mode parallèle activé ($MaxParallelJobs jobs)" -ForegroundColor Cyan
    
    # Diviser en chunks
    $chunks = @()
    for ($i = 0; $i -lt $candidateFiles.Count; $i += $ChunkSize) {
        $endIndex = [Math]::Min($i + $ChunkSize - 1, $candidateFiles.Count - 1)
        $chunks += ,@($candidateFiles[$i..$endIndex])
    }
    
    Write-Host "   Chunks créés : $($chunks.Count)" -ForegroundColor Gray
    
    # Traitement parallèle
    $jobs = @()
    $chunkIndex = 0
    
    foreach ($chunk in $chunks) {
        # Attendre qu'un slot se libère
        while ((Get-Job -State Running).Count -ge $MaxParallelJobs) {
            Start-Sleep -Milliseconds 100
        }
        
        $chunkIndex++
        Write-Host "   Lancement chunk $chunkIndex/$($chunks.Count)" -ForegroundColor Gray
        
        $job = Start-Job -ScriptBlock $ProcessChunkScript -ArgumentList $chunk, $HashAlgorithm
        $jobs += $job
    }
    
    # Attendre tous les jobs
    Write-Host "   Attente des résultats..." -ForegroundColor Yellow
    $allResults = @()
    
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job -Wait
        $allResults += $result
        Remove-Job -Job $job
    }
    
} else {
    Write-Host "   Mode séquentiel" -ForegroundColor Yellow
    $allResults = & $ProcessChunkScript $candidateFiles $HashAlgorithm
}

# Étape 4 : Identifier les doublons
Write-Host "🔍 Analyse des résultats..." -ForegroundColor Green
$hashGroups = $allResults | Group-Object Hash | Where-Object { $_.Count -gt 1 }

if ($hashGroups.Count -eq 0) {
    Write-Host "✅ Aucun doublon détecté !" -ForegroundColor Green
    exit 0
}

# Étape 5 : Afficher et traiter les doublons
Write-Host "⚠️  Doublons détectés : $($hashGroups.Count) groupes" -ForegroundColor Red
Write-Host ""

$totalDuplicateFiles = 0
$totalWastedSpace = 0

foreach ($group in $hashGroups) {
    $files = $group.Group
    $duplicateCount = $files.Count - 1
    $totalDuplicateFiles += $duplicateCount
    $wastedSpace = $files[0].Size * $duplicateCount
    $totalWastedSpace += $wastedSpace
    
    Write-Host "📄 Groupe de doublons ($(Format-FileSize $files[0].Size)) - $($files.Count) fichiers :" -ForegroundColor Yellow
    
    for ($i = 0; $i -lt $files.Count; $i++) {
        $file = $files[$i]
        $status = if ($i -eq 0) { "[ORIGINAL]" } else { "[DOUBLON]" }
        $color = if ($i -eq 0) { "Green" } else { "Red" }
        
        if ($Verbose) {
            Write-Host "   $status $($file.Path)" -ForegroundColor $color
        }
        
        # Actions sur les doublons (traitement séquentiel pour la sécurité)
        if ($i -gt 0) {
            switch ($Action) {
                "Delete" {
                    if (-not $WhatIf) {
                        try {
                            Remove-Item -Path $file.Path -Force
                            Write-Host "   ✓ Supprimé : $($file.Path)" -ForegroundColor Red
                        }
                        catch {
                            Write-Warning "   ❌ Impossible de supprimer : $($file.Path)"
                        }
                    }
                    else {
                        Write-Host "   [WhatIf] Suppression : $($file.Path)" -ForegroundColor Yellow
                    }
                }
                "Move" {
                    if ($MoveToPath) {
                        $relativePath = $file.Path.Substring($BasePath.Length).TrimStart('\')
                        $newPath = Join-Path $MoveToPath $relativePath
                        
                        if (-not $WhatIf) {
                            $newDir = Split-Path $newPath -Parent
                            if (-not (Test-Path $newDir)) {
                                New-Item -Path $newDir -ItemType Directory -Force | Out-Null
                            }
                            try {
                                Move-Item -Path $file.Path -Destination $newPath -Force
                                Write-Host "   ✓ Déplacé vers : $newPath" -ForegroundColor Blue
                            }
                            catch {
                                Write-Warning "   ❌ Impossible de déplacer : $($file.Path)"
                            }
                        }
                        else {
                            Write-Host "   [WhatIf] Déplacement vers : $newPath" -ForegroundColor Yellow
                        }
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
Write-Host "Groupes de doublons : $($hashGroups.Count)" -ForegroundColor Yellow
Write-Host "Fichiers doublons : $totalDuplicateFiles" -ForegroundColor Red
Write-Host "Espace gaspillé : $(Format-FileSize $totalWastedSpace)" -ForegroundColor Red
Write-Host "Mode parallèle : $EnableParallel" -ForegroundColor White
Write-Host "=" * 60 -ForegroundColor Cyan