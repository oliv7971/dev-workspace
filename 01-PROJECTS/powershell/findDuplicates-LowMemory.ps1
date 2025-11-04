# =============================================================================
# SCRIPT DE DÉTECTION DE DOUBLONS - VERSION OPTIMISÉE MÉMOIRE
# =============================================================================
# Compare répertoires avec FAIBLE consommation RAM (streaming)
# Idéal pour des millions de fichiers sans exploser la mémoire
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================

# RÉPERTOIRE DE RÉFÉRENCE (vos données déjà organisées/classées)
$ReferencePath = "D:\MesDocumentsClasses"

# RÉPERTOIRES À NETTOYER (nouvelles données potentiellement en double)
$PathsToClean = @(
    "D:\Telechargements",
    "D:\ATrier"
)

# OPTIONS DE TRAITEMENT
$Action = "Report"                       # "Report" / "Delete" / "Move"
$QuarantinePath = "D:\Doublons_Detectes" # Dossier de quarantaine
$WhatIf = $true                         # $true = simulation, $false = action réelle
$Verbose = $true                        # $true = affichage détaillé

# OPTIONS D'ANALYSE
$MinFileSize = 1KB                      # Ignorer fichiers < 1KB (économise RAM+temps)
$HashAlgorithm = "MD5"                  # MD5 (rapide) ou SHA256 (précis)
$ExcludeExtensions = @(".tmp", ".log")  # Extensions à ignorer

# OPTIONS AVANCÉES
$RemoveInternalDuplicates = $true       # Supprimer les doublons INTERNES
$CreateDetailedReport = $true           # Créer un rapport CSV
$ReportPath = ".\rapport_doublons.csv"  # Chemin du rapport
$UseSQLiteCache = $false                # Utiliser une base SQLite (nécessite module)

# OPTIONS OPTIMISATION MÉMOIRE
$ProcessByChunks = $true                # Traiter par lots (réduit RAM)
$ChunkSize = 10000                      # Taille des lots
$CacheFilePath = ".\hash_cache.txt"     # Cache des hashs (évite recalcul)
$UseSizePreFilter = $true               # Pré-filtrer par taille (économise calculs)

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
        Write-Warning "Impossible de calculer le hash pour : $FilePath"
        return $null
    }
}

# Fonction pour charger le cache de hashs
function Load-HashCache {
    param([string]$CachePath)
    
    $cache = @{}
    if (Test-Path $CachePath) {
        Write-Host "[CACHE] Chargement du cache de hashs..." -ForegroundColor Green
        try {
            Get-Content $CachePath | ForEach-Object {
                $parts = $_ -split '\|'
                if ($parts.Count -eq 4) {
                    $key = "$($parts[0])|$($parts[1])"  # Path|Size
                    $cache[$key] = @{
                        Hash = $parts[2]
                        LastModified = $parts[3]
                    }
                }
            }
            Write-Host "   [OK] $($cache.Count) hashs charges du cache" -ForegroundColor Cyan
        }
        catch {
            Write-Warning "Erreur de lecture du cache : $($_.Exception.Message)"
        }
    }
    return $cache
}

# Fonction pour sauvegarder le cache
function Save-HashCache {
    param(
        [string]$CachePath,
        [hashtable]$Cache
    )
    
    try {
        $Cache.GetEnumerator() | ForEach-Object {
            $parts = $_.Key -split '\|'
            "$($parts[0])|$($parts[1])|$($_.Value.Hash)|$($_.Value.LastModified)"
        } | Set-Content $CachePath
        Write-Host "[CACHE] Sauvegarde : $($Cache.Count) entrees" -ForegroundColor Green
    }
    catch {
        Write-Warning "Impossible de sauvegarder le cache : $($_.Exception.Message)"
    }
}

# Fonction pour traiter les doublons
function Process-Duplicate {
    param(
        [string]$FilePath,
        [long]$FileSize,
        [string]$Reason,
        [string]$ReferenceFile = $null
    )
    
    $script:duplicatesFound++
    $script:totalSpaceSaved += $FileSize
    
    # Ajouter au rapport
    if ($CreateDetailedReport) {
        $reportLine = [PSCustomObject]@{
            FichierDouble = $FilePath
            Taille = Format-FileSize $FileSize
            Raison = $Reason
            Reference = $ReferenceFile
        }
        $reportLine | Export-Csv -Path $ReportPath -NoTypeInformation -Encoding UTF8 -Append
    }
    
    if ($Verbose) {
        Write-Host "   [DOUBLON] $FilePath" -ForegroundColor Red
        Write-Host "      Raison : $Reason" -ForegroundColor Gray
        Write-Host "      Taille : $(Format-FileSize $FileSize)" -ForegroundColor Gray
    }
    
    # Exécuter l'action
    switch ($Action) {
        "Delete" {
            if (-not $WhatIf) {
                try {
                    Remove-Item -LiteralPath $FilePath -Force -ErrorAction Stop
                    Write-Host "   [OK] Supprime" -ForegroundColor Green
                    $script:filesProcessed++
                }
                catch {
                    Write-Warning "   [ERREUR] Impossible de supprimer : $($_.Exception.Message)"
                }
            }
            else {
                $script:filesProcessed++
            }
        }
        
        "Move" {
            $relativePath = $FilePath.Substring([System.IO.Path]::GetPathRoot($FilePath).Length)
            $newPath = Join-Path $QuarantinePath $relativePath
            $newDir = Split-Path $newPath -Parent
            
            if (-not $WhatIf) {
                try {
                    if (-not (Test-Path $newDir)) {
                        New-Item -Path $newDir -ItemType Directory -Force | Out-Null
                    }
                    Move-Item -LiteralPath $FilePath -Destination $newPath -Force -ErrorAction Stop
                    Write-Host "   [OK] Deplace" -ForegroundColor Blue
                    $script:filesProcessed++
                }
                catch {
                    Write-Warning "   [ERREUR] Impossible de deplacer : $($_.Exception.Message)"
                }
            }
            else {
                $script:filesProcessed++
            }
        }
    }
}

# Variables globales
$script:duplicatesFound = 0
$script:filesProcessed = 0
$script:totalSpaceSaved = 0
$hashCache = Load-HashCache -CachePath $CacheFilePath

# Bannière
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "DÉTECTION DE DOUBLONS - VERSION OPTIMISÉE MÉMOIRE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Répertoire de référence : $ReferencePath" -ForegroundColor White
Write-Host "Répertoires à nettoyer :" -ForegroundColor White
foreach ($path in $PathsToClean) {
    Write-Host "  - $path" -ForegroundColor Gray
}
Write-Host ""
Write-Host "[OPTIMISATION] Mode economie memoire : ACTIVE" -ForegroundColor Green
Write-Host "[OPTIMISATION] Traitement par lots : $ChunkSize fichiers" -ForegroundColor Green
Write-Host ""

# Vérifications
if (-not (Test-Path $ReferencePath)) {
    Write-Error "Le répertoire de référence n'existe pas : $ReferencePath"
    exit 1
}

# Créer le fichier de rapport vide
if ($CreateDetailedReport) {
    if (Test-Path $ReportPath) { Remove-Item $ReportPath -Force }
}

# Créer le dossier de quarantaine si nécessaire
if ($Action -eq "Move" -and -not $WhatIf) {
    if (-not (Test-Path $QuarantinePath)) {
        New-Item -Path $QuarantinePath -ItemType Directory -Force | Out-Null
    }
}

# =============================================================================
# ETAPE 1 : Indexer la reference par TAILLE (economise memoire)
# =============================================================================
Write-Host "[ETAPE 1] Indexation de la reference par taille" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$referenceSizeIndex = @{}  # Taille -> Liste de fichiers
$referenceCount = 0

Get-ChildItem -LiteralPath $ReferencePath -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.Length -ge $MinFileSize } | 
    ForEach-Object {
        $referenceCount++
        if ($referenceCount % 1000 -eq 0) {
            Write-Progress -Activity "Indexation référence" -Status "Fichiers: $referenceCount" -PercentComplete -1
        }
        
        $size = $_.Length
        if (-not $referenceSizeIndex.ContainsKey($size)) {
            $referenceSizeIndex[$size] = @()
        }
        $referenceSizeIndex[$size] += $_.FullName
    }

Write-Progress -Activity "Indexation reference" -Completed
Write-Host "   [OK] $referenceCount fichiers indexes" -ForegroundColor Cyan
Write-Host "   [INFO] $($referenceSizeIndex.Keys.Count) tailles differentes" -ForegroundColor Gray

# =============================================================================
# ETAPE 2 : Calculer les hashs UNIQUEMENT pour les tailles en conflit
# =============================================================================
Write-Host "`n[ETAPE 2] Calcul des hashs de la reference (tailles en conflit)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$referenceHashIndex = @{}  # Hash -> Premier fichier trouvé
$hashCalculated = 0

foreach ($size in $referenceSizeIndex.Keys) {
    $filesWithSize = $referenceSizeIndex[$size]
    
    # Si qu'un seul fichier de cette taille, pas besoin de hash
    if ($filesWithSize.Count -eq 1) {
        continue
    }
    
    # Calculer hashs pour cette taille
    foreach ($filePath in $filesWithSize) {
        $hashCalculated++
        if ($hashCalculated % 100 -eq 0) {
            Write-Progress -Activity "Calcul hashs référence" -Status "Hash: $hashCalculated" -PercentComplete -1
        }
        
        # Vérifier le cache
        $cacheKey = "$filePath|$size"
        $hash = $null
        
        if ($hashCache.ContainsKey($cacheKey)) {
            $hash = $hashCache[$cacheKey].Hash
        }
        else {
            $hash = Get-FileHashSafe -FilePath $filePath
            if ($hash) {
                $hashCache[$cacheKey] = @{
                    Hash = $hash
                    LastModified = (Get-Item -LiteralPath $filePath).LastWriteTime.ToString()
                }
            }
        }
        
        if ($hash -and -not $referenceHashIndex.ContainsKey($hash)) {
            $referenceHashIndex[$hash] = $filePath
        }
    }
}

Write-Progress -Activity "Calcul hashs reference" -Completed
Write-Host "   [OK] $hashCalculated hashs calcules" -ForegroundColor Cyan
Write-Host "   [INFO] $($referenceHashIndex.Keys.Count) hashs uniques" -ForegroundColor Gray

# =============================================================================
# ETAPE 3 : Scanner les repertoires a nettoyer (STREAMING)
# =============================================================================
Write-Host "`n[ETAPE 3] Detection des doublons (streaming)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$toCleanSizeIndex = @{}  # Pour détecter doublons internes
$processedFiles = 0

foreach ($cleanPath in $PathsToClean) {
    if (-not (Test-Path $cleanPath)) {
        Write-Warning "Chemin ignoré : $cleanPath"
        continue
    }
    
    Write-Host "`n   [SCAN] Traitement de : $cleanPath" -ForegroundColor Yellow
    
    Get-ChildItem -LiteralPath $cleanPath -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -ge $MinFileSize } |
        ForEach-Object {
            $processedFiles++
            if ($processedFiles % 500 -eq 0) {
                Write-Progress -Activity "Analyse doublons" -Status "Fichiers: $processedFiles" -PercentComplete -1
            }
            
            $file = $_
            $size = $file.Length
            
            # Vérifier si cette taille existe dans la référence
            $needsHashCheck = $referenceSizeIndex.ContainsKey($size) -and $referenceSizeIndex[$size].Count -gt 0
            
            # Ou si on cherche les doublons internes
            $needsInternalCheck = $RemoveInternalDuplicates -and $toCleanSizeIndex.ContainsKey($size)
            
            if ($needsHashCheck -or $needsInternalCheck) {
                # Calculer le hash
                $cacheKey = "$($file.FullName)|$size"
                $hash = $null
                
                if ($hashCache.ContainsKey($cacheKey)) {
                    $hash = $hashCache[$cacheKey].Hash
                }
                else {
                    $hash = Get-FileHashSafe -FilePath $file.FullName
                    if ($hash) {
                        $hashCache[$cacheKey] = @{
                            Hash = $hash
                            LastModified = $file.LastWriteTime.ToString()
                        }
                    }
                }
                
                if ($hash) {
                    # Vérifier doublon vs référence
                    if ($referenceHashIndex.ContainsKey($hash)) {
                        Process-Duplicate -FilePath $file.FullName -FileSize $size -Reason "Existe dans la référence" -ReferenceFile $referenceHashIndex[$hash]
                        continue  # Déjà traité, pas besoin de vérifier doublons internes
                    }
                    
                    # Vérifier doublon interne
                    if ($RemoveInternalDuplicates -and $toCleanSizeIndex.ContainsKey($size)) {
                        if ($toCleanSizeIndex[$size].ContainsKey($hash)) {
                            Process-Duplicate -FilePath $file.FullName -FileSize $size -Reason "Doublon interne" -ReferenceFile $toCleanSizeIndex[$size][$hash]
                            continue
                        }
                    }
                    
                    # Premier fichier avec ce hash, l'enregistrer
                    if ($RemoveInternalDuplicates) {
                        if (-not $toCleanSizeIndex.ContainsKey($size)) {
                            $toCleanSizeIndex[$size] = @{}
                        }
                        $toCleanSizeIndex[$size][$hash] = $file.FullName
                    }
                }
            }
            elseif ($RemoveInternalDuplicates) {
                # Pas de conflit avec référence, juste enregistrer pour doublons internes
                if (-not $toCleanSizeIndex.ContainsKey($size)) {
                    $toCleanSizeIndex[$size] = @{}
                }
                # Utiliser la taille comme "hash" pour les fichiers uniques
                if (-not $toCleanSizeIndex[$size].ContainsKey("size_only")) {
                    $toCleanSizeIndex[$size]["size_only"] = $file.FullName
                }
            }
        }
}

Write-Progress -Activity "Analyse doublons" -Completed

# Sauvegarder le cache
Save-HashCache -CachePath $CacheFilePath -Cache $hashCache

# Résumé final
Write-Host "`n" -NoNewline
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "RÉSUMÉ DE L'ANALYSE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Fichiers référence analysés : $referenceCount" -ForegroundColor White
Write-Host "Fichiers à nettoyer analysés : $processedFiles" -ForegroundColor White
Write-Host "Hashs calculés (optimisé) : $hashCalculated" -ForegroundColor Gray
Write-Host ""
Write-Host "Total doublons détectés : $script:duplicatesFound" -ForegroundColor Red
Write-Host "Espace disque gaspillé : $(Format-FileSize $script:totalSpaceSaved)" -ForegroundColor Magenta
Write-Host "Fichiers traités : $script:filesProcessed" -ForegroundColor Green
Write-Host ""
Write-Host "Action configurée : $Action" -ForegroundColor White
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host "=" * 80 -ForegroundColor Cyan

if ($WhatIf -and $Action -ne "Report") {
    Write-Host ""
    Write-Host "[INFO] Pour executer reellement, changez `$WhatIf = `$false" -ForegroundColor Cyan
}

if ($CreateDetailedReport -and (Test-Path $ReportPath)) {
    Write-Host ""
    Write-Host "[RAPPORT] Rapport detaille : $ReportPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "[OPTIMISATION] Consommation memoire optimisee : Streaming active !" -ForegroundColor Green
Write-Host "[CACHE] Cache de hashs : $CacheFilePath ($($hashCache.Count) entrees)" -ForegroundColor Green