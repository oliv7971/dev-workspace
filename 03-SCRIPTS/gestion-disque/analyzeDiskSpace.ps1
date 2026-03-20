# =============================================================================
# ANALYSEUR D'ESPACE DISQUE - DETECTEUR DE GROS CONSOMMATEURS
# =============================================================================
# Ce script analyse l'utilisation de l'espace disque et identifie :
# - Les plus gros dossiers
# - Les plus gros fichiers
# - La répartition par type de fichier
# - Les répertoires cachés qui prennent de l'espace
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$DriveLetter = "C:"                     # Disque à analyser (C:, D:, etc.)
$MaxDepthLevel = 3                      # Profondeur d'analyse (3 = C:\Dossier\SousDossier\)
$TopFoldersCount = 20                   # Nombre de plus gros dossiers à afficher
$TopFilesCount = 50                     # Nombre de plus gros fichiers à afficher
$MinFolderSizeMB = 100                  # Taille minimum des dossiers à analyser (en MB)
$ShowHiddenFolders = $true              # Analyser les dossiers cachés/système
$ExportToCSV = $true                    # Exporter les résultats en CSV
$OutputPath = "C:\temp"                 # Dossier de sortie pour les rapports

# Extensions à surveiller particulièrement
$SuspiciousExtensions = @(".log", ".tmp", ".bak", ".old", ".cache", ".dmp")

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

# Fonction pour formater la taille
function Format-FileSize {
    param([long]$Size)
    
    if ($Size -eq 0) { return "0 B" }
    elseif ($Size -lt 1KB) { return "$Size B" }
    elseif ($Size -lt 1MB) { return "{0:N2} KB" -f ($Size / 1KB) }
    elseif ($Size -lt 1GB) { return "{0:N2} MB" -f ($Size / 1MB) }
    elseif ($Size -lt 1TB) { return "{0:N2} GB" -f ($Size / 1GB) }
    else { return "{0:N2} TB" -f ($Size / 1TB) }
}

# Fonction pour calculer la taille d'un dossier
function Get-FolderSize {
    param(
        [string]$FolderPath,
        [int]$CurrentDepth = 0
    )
    
    $totalSize = 0
    $fileCount = 0
    
    try {
        # Obtenir les fichiers du dossier actuel
        $files = Get-ChildItem -LiteralPath $FolderPath -File -Force -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $totalSize += $file.Length
            $fileCount++
        }
        
        # Si on n'a pas atteint la profondeur max, analyser les sous-dossiers
        if ($CurrentDepth -lt $MaxDepthLevel) {
            $subFolders = Get-ChildItem -LiteralPath $FolderPath -Directory -Force -ErrorAction SilentlyContinue
            foreach ($subFolder in $subFolders) {
                $subResult = Get-FolderSize -FolderPath $subFolder.FullName -CurrentDepth ($CurrentDepth + 1)
                $totalSize += $subResult.Size
                $fileCount += $subResult.FileCount
            }
        }
    }
    catch {
        Write-Verbose "Erreur d'accès : $FolderPath - $($_.Exception.Message)"
    }
    
    return @{
        Size = $totalSize
        FileCount = $fileCount
    }
}

# Créer le dossier de sortie
if ($ExportToCSV -and -not (Test-Path $OutputPath)) {
    New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "ANALYSE DE L'ESPACE DISQUE - $DriveLetter" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Démarrage de l'analyse : $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Vérifier que le disque existe
if (-not (Test-Path $DriveLetter)) {
    Write-Error "Le disque '$DriveLetter' n'existe pas ou n'est pas accessible."
    exit 1
}

# Obtenir les informations générales du disque
$drive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $DriveLetter }
$totalSpace = $drive.Size
$freeSpace = $drive.FreeSpace
$usedSpace = $totalSpace - $freeSpace

Write-Host "📊 INFORMATIONS GÉNÉRALES DU DISQUE" -ForegroundColor Green
Write-Host "Espace total : $(Format-FileSize $totalSpace)" -ForegroundColor White
Write-Host "Espace utilisé : $(Format-FileSize $usedSpace) ($([math]::Round(($usedSpace/$totalSpace)*100, 2))%)" -ForegroundColor Red
Write-Host "Espace libre : $(Format-FileSize $freeSpace) ($([math]::Round(($freeSpace/$totalSpace)*100, 2))%)" -ForegroundColor Green
Write-Host ""

# Analyse des dossiers racine
Write-Host "🔍 ANALYSE DES DOSSIERS PRINCIPAUX" -ForegroundColor Green
$rootFolders = Get-ChildItem -Path $DriveLetter -Directory -Force -ErrorAction SilentlyContinue

$folderAnalysis = @()
$totalAnalyzed = 0

foreach ($folder in $rootFolders) {
    Write-Host "   Analyse en cours : $($folder.Name)..." -ForegroundColor Gray
    
    $folderInfo = Get-FolderSize -FolderPath $folder.FullName
    $folderSizeMB = $folderInfo.Size / 1MB
    
    if ($folderSizeMB -ge $MinFolderSizeMB) {
        $folderAnalysis += [PSCustomObject]@{
            Name = $folder.Name
            Path = $folder.FullName
            SizeBytes = $folderInfo.Size
            SizeFormatted = Format-FileSize $folderInfo.Size
            SizeMB = [math]::Round($folderSizeMB, 2)
            FileCount = $folderInfo.FileCount
            PercentOfDisk = [math]::Round(($folderInfo.Size / $totalSpace) * 100, 2)
            IsHidden = $folder.Attributes -match "Hidden"
            IsSystem = $folder.Attributes -match "System"
        }
    }
    
    $totalAnalyzed += $folderInfo.Size
}

# Trier et afficher les plus gros dossiers
$topFolders = $folderAnalysis | Sort-Object SizeBytes -Descending | Select-Object -First $TopFoldersCount

Write-Host ""
Write-Host "📁 TOP $TopFoldersCount DES PLUS GROS DOSSIERS" -ForegroundColor Yellow
Write-Host ("-" * 70) -ForegroundColor Yellow
foreach ($folder in $topFolders) {
    $attributes = @()
    if ($folder.IsHidden) { $attributes += "CACHÉ" }
    if ($folder.IsSystem) { $attributes += "SYSTÈME" }
    $attributeStr = if ($attributes.Count -gt 0) { " [" + ($attributes -join ", ") + "]" } else { "" }
    
    Write-Host ("{0,-40} {1,15} ({2,6}%){3}" -f 
        $folder.Name, 
        $folder.SizeFormatted, 
        $folder.PercentOfDisk,
        $attributeStr) -ForegroundColor $(if($folder.PercentOfDisk -gt 10){"Red"}elseif($folder.PercentOfDisk -gt 5){"Yellow"}else{"White"})
}

# Analyse des plus gros fichiers
Write-Host ""
Write-Host "🔍 RECHERCHE DES PLUS GROS FICHIERS..." -ForegroundColor Green

$bigFiles = @()
try {
    Get-ChildItem -Path $DriveLetter -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -gt 100MB } |
        Sort-Object Length -Descending |
        Select-Object -First $TopFilesCount |
        ForEach-Object {
            $bigFiles += [PSCustomObject]@{
                Name = $_.Name
                Path = $_.FullName
                SizeBytes = $_.Length
                SizeFormatted = Format-FileSize $_.Length
                Extension = $_.Extension.ToLower()
                LastModified = $_.LastWriteTime
                IsSuspicious = $_.Extension.ToLower() -in $SuspiciousExtensions
            }
        }
}
catch {
    Write-Warning "Erreur lors de la recherche des gros fichiers : $($_.Exception.Message)"
}

if ($bigFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "📄 TOP $($bigFiles.Count) DES PLUS GROS FICHIERS" -ForegroundColor Yellow
    Write-Host ("-" * 70) -ForegroundColor Yellow
    foreach ($file in $bigFiles) {
        $suspiciousStr = if ($file.IsSuspicious) { " ⚠️ SUSPECT" } else { "" }
        Write-Host ("{0,-30} {1,15} {2}{3}" -f 
            $file.Name, 
            $file.SizeFormatted,
            $file.Extension,
            $suspiciousStr) -ForegroundColor $(if($file.IsSuspicious){"Red"}else{"White"})
    }
}

# Analyse par extension
Write-Host ""
Write-Host "📋 ANALYSE PAR TYPE DE FICHIER" -ForegroundColor Green

$extensionAnalysis = @{}
try {
    Get-ChildItem -Path $DriveLetter -Recurse -File -Force -ErrorAction SilentlyContinue |
        Group-Object Extension |
        ForEach-Object {
            $totalSize = ($_.Group | Measure-Object Length -Sum).Sum
            if ($totalSize -gt 0) {
                $extensionAnalysis[$_.Name.ToLower()] = @{
                    Count = $_.Count
                    TotalSize = $totalSize
                    SizeFormatted = Format-FileSize $totalSize
                }
            }
        }
}
catch {
    Write-Warning "Erreur lors de l'analyse des extensions : $($_.Exception.Message)"
}

$topExtensions = $extensionAnalysis.GetEnumerator() | 
    Sort-Object { $_.Value.TotalSize } -Descending | 
    Select-Object -First 15

Write-Host ("-" * 70) -ForegroundColor Yellow
foreach ($ext in $topExtensions) {
    $extName = if ($ext.Key -eq "") { "(sans extension)" } else { $ext.Key }
    Write-Host ("{0,-15} {1,8} fichiers {2,15}" -f 
        $extName, 
        $ext.Value.Count, 
        $ext.Value.SizeFormatted) -ForegroundColor White
}

# Export CSV si demandé
if ($ExportToCSV) {
    try {
        $csvFolders = "$OutputPath\disk_analysis_folders_$timestamp.csv"
        $topFolders | Export-Csv -Path $csvFolders -NoTypeInformation -Encoding UTF8
        
        if ($bigFiles.Count -gt 0) {
            $csvFiles = "$OutputPath\disk_analysis_files_$timestamp.csv"
            $bigFiles | Export-Csv -Path $csvFiles -NoTypeInformation -Encoding UTF8
        }
        
        Write-Host ""
        Write-Host "📄 Rapports exportés :" -ForegroundColor Green
        Write-Host "   Dossiers : $csvFolders" -ForegroundColor Gray
        if ($bigFiles.Count -gt 0) {
            Write-Host "   Fichiers : $csvFiles" -ForegroundColor Gray
        }
    }
    catch {
        Write-Warning "Impossible d'exporter les rapports : $($_.Exception.Message)"
    }
}

# Recommandations
Write-Host ""
Write-Host "💡 RECOMMANDATIONS DE NETTOYAGE" -ForegroundColor Cyan
Write-Host ("-" * 70) -ForegroundColor Cyan

# Identifier les dossiers suspects
$suspiciousFolders = $topFolders | Where-Object { 
    $_.Name -match "(temp|cache|log|backup|old)" -or 
    $_.IsHidden -or 
    $_.PercentOfDisk -gt 15 
}

if ($suspiciousFolders.Count -gt 0) {
    Write-Host "🔍 Dossiers à examiner :" -ForegroundColor Yellow
    foreach ($folder in $suspiciousFolders) {
        Write-Host "   - $($folder.Name) ($($folder.SizeFormatted))" -ForegroundColor Red
    }
}

# Fichiers suspects
$suspiciousFiles = $bigFiles | Where-Object { $_.IsSuspicious }
if ($suspiciousFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  Fichiers suspects à vérifier :" -ForegroundColor Yellow
    foreach ($file in $suspiciousFiles) {
        Write-Host "   - $($file.Name) ($($file.SizeFormatted))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🔧 Actions suggérées :" -ForegroundColor Cyan
Write-Host "   1. Vider la corbeille" -ForegroundColor Gray
Write-Host "   2. Nettoyer %TEMP% et %TMP%" -ForegroundColor Gray
Write-Host "   3. Utiliser 'Nettoyage de disque' Windows" -ForegroundColor Gray
Write-Host "   4. Vérifier les points de restauration système" -ForegroundColor Gray
Write-Host "   5. Analyser les dossiers 'Windows\SoftwareDistribution'" -ForegroundColor Gray

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Analyse terminée : $(Get-Date)" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan