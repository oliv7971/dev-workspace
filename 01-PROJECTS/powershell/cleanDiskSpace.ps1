# =============================================================================
# NETTOYEUR D'ESPACE DISQUE AUTOMATIQUE
# =============================================================================
# Script pour nettoyer automatiquement les emplacements qui consomment 
# beaucoup d'espace disque de manière inutile
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$WhatIf = $true                         # $true = simulation, $false = nettoyage réel
$CleanTempFiles = $true                 # Nettoyer les fichiers temporaires
$CleanDownloads = $false                # Nettoyer les téléchargements (ATTENTION!)
$CleanRecycleBin = $true                # Vider la corbeille
$CleanSystemTemp = $true                # Nettoyer C:\Windows\Temp
$CleanUserTemp = $true                  # Nettoyer %TEMP%
$CleanWindowsUpdate = $false            # Nettoyer SoftwareDistribution (ATTENTION!)
$CleanBrowserCache = $true              # Nettoyer les caches navigateurs
$CleanSystemLogs = $false               # Nettoyer les logs système (ATTENTION!)
$OlderThanDays = 30                     # Supprimer les fichiers plus anciens que X jours

# Seuils de sécurité
$MaxFileSize = 10GB                     # Ne pas supprimer de fichiers > 10GB sans confirmation
$MaxFolderSize = 50GB                   # Ne pas vider de dossiers > 50GB sans confirmation

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

function Format-Size {
    param([long]$Size)
    if ($Size -lt 1KB) { return "$Size B" }
    elseif ($Size -lt 1MB) { return "{0:N2} KB" -f ($Size / 1KB) }
    elseif ($Size -lt 1GB) { return "{0:N2} MB" -f ($Size / 1MB) }
    else { return "{0:N2} GB" -f ($Size / 1GB) }
}

function Get-FolderSize {
    param([string]$Path)
    try {
        return (Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue | 
                Measure-Object Length -Sum).Sum
    }
    catch {
        return 0
    }
}

function Remove-OldFiles {
    param(
        [string]$Path,
        [string]$Description,
        [int]$DaysOld = $OlderThanDays,
        [switch]$Recurse
    )
    
    if (-not (Test-Path $Path)) {
        Write-Host "   ⚠️  $Description : Dossier inexistant" -ForegroundColor Yellow
        return
    }
    
    $cutoffDate = (Get-Date).AddDays(-$DaysOld)
    
    try {
        $params = @{
            Path = $Path
            File = $true
            Force = $true
            ErrorAction = 'SilentlyContinue'
        }
        if ($Recurse) { $params.Recurse = $true }
        
        $oldFiles = Get-ChildItem @params | Where-Object { $_.LastWriteTime -lt $cutoffDate }
        
        if ($oldFiles.Count -eq 0) {
            Write-Host "   ✅ $Description : Aucun fichier ancien trouvé" -ForegroundColor Green
            return
        }
        
        $totalSize = ($oldFiles | Measure-Object Length -Sum).Sum
        $sizeStr = Format-Size $totalSize
        
        Write-Host "   📁 $Description : $($oldFiles.Count) fichiers ($sizeStr)" -ForegroundColor Cyan
        
        if (-not $WhatIf) {
            $deleted = 0
            $freedSpace = 0
            
            foreach ($file in $oldFiles) {
                if ($file.Length -gt $MaxFileSize) {
                    Write-Host "      ⚠️  Fichier volumineux ignoré : $($file.Name) ($(Format-Size $file.Length))" -ForegroundColor Yellow
                    continue
                }
                
                try {
                    $size = $file.Length
                    Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
                    $deleted++
                    $freedSpace += $size
                }
                catch {
                    Write-Host "      ❌ Erreur : $($file.Name)" -ForegroundColor Red
                }
            }
            
            Write-Host "      ✅ $deleted fichiers supprimés ($(Format-Size $freedSpace) libérés)" -ForegroundColor Green
        }
        else {
            Write-Host "      [SIMULATION] Suppression de $($oldFiles.Count) fichiers ($(Format-Size $totalSize))" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ $Description : Erreur d'accès" -ForegroundColor Red
    }
}

$totalFreed = 0
$startTime = Get-Date

Write-Host "🧹 NETTOYAGE AUTOMATIQUE D'ESPACE DISQUE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Red"})
Write-Host "Démarrage : $startTime" -ForegroundColor Gray
Write-Host ""

# 1. Nettoyage des fichiers temporaires utilisateur
if ($CleanUserTemp) {
    Write-Host "🗂️  NETTOYAGE FICHIERS TEMPORAIRES UTILISATEUR" -ForegroundColor Green
    
    $tempPaths = @(
        @{ Path = $env:TEMP; Description = "Dossier TEMP utilisateur" }
        @{ Path = "$env:USERPROFILE\AppData\Local\Temp"; Description = "AppData\Local\Temp" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Windows\INetCache"; Description = "Cache Internet Explorer" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Windows\WebCache"; Description = "Cache Web Windows" }
    )
    
    foreach ($tempPath in $tempPaths) {
        Remove-OldFiles -Path $tempPath.Path -Description $tempPath.Description -Recurse
    }
    Write-Host ""
}

# 2. Nettoyage système
if ($CleanSystemTemp) {
    Write-Host "🗂️  NETTOYAGE FICHIERS TEMPORAIRES SYSTÈME" -ForegroundColor Green
    
    $systemPaths = @(
        @{ Path = "C:\Windows\Temp"; Description = "Windows\Temp" }
        @{ Path = "C:\Windows\Prefetch"; Description = "Windows\Prefetch" }
    )
    
    foreach ($sysPath in $systemPaths) {
        Remove-OldFiles -Path $sysPath.Path -Description $sysPath.Description -Recurse
    }
    Write-Host ""
}

# 3. Nettoyage des caches navigateurs
if ($CleanBrowserCache) {
    Write-Host "🌐 NETTOYAGE CACHES NAVIGATEURS" -ForegroundColor Green
    
    $browserPaths = @(
        @{ Path = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"; Description = "Cache Chrome" }
        @{ Path = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"; Description = "Cache Edge" }
        @{ Path = "$env:APPDATA\Mozilla\Firefox\Profiles"; Description = "Cache Firefox" }
    )
    
    foreach ($browserPath in $browserPaths) {
        if ($browserPath.Description -eq "Cache Firefox") {
            # Firefox a une structure différente
            if (Test-Path $browserPath.Path) {
                $profiles = Get-ChildItem -Path $browserPath.Path -Directory -ErrorAction SilentlyContinue
                foreach ($profile in $profiles) {
                    $cachePath = Join-Path $profile.FullName "cache2"
                    Remove-OldFiles -Path $cachePath -Description "Firefox Cache ($($profile.Name))" -DaysOld 7 -Recurse
                }
            }
        }
        else {
            Remove-OldFiles -Path $browserPath.Path -Description $browserPath.Description -DaysOld 7 -Recurse
        }
    }
    Write-Host ""
}

# 4. Nettoyage Windows Update (ATTENTION)
if ($CleanWindowsUpdate) {
    Write-Host "🔄 NETTOYAGE WINDOWS UPDATE" -ForegroundColor Red
    Write-Host "   ⚠️  ATTENTION : Peut nécessiter le redémarrage du service" -ForegroundColor Yellow
    
    $updatePaths = @(
        @{ Path = "C:\Windows\SoftwareDistribution\Download"; Description = "Windows Update Download" }
    )
    
    foreach ($updatePath in $updatePaths) {
        $folderSize = Get-FolderSize -Path $updatePath.Path
        if ($folderSize -gt $MaxFolderSize) {
            Write-Host "   ⚠️  Dossier très volumineux ($(Format-Size $folderSize)) - ignoré pour sécurité" -ForegroundColor Yellow
        }
        else {
            Remove-OldFiles -Path $updatePath.Path -Description $updatePath.Description -DaysOld 7 -Recurse
        }
    }
    Write-Host ""
}

# 5. Nettoyage des logs système
if ($CleanSystemLogs) {
    Write-Host "📋 NETTOYAGE LOGS SYSTÈME" -ForegroundColor Red
    Write-Host "   ⚠️  ATTENTION : Peut supprimer des informations de diagnostic" -ForegroundColor Yellow
    
    $logPaths = @(
        @{ Path = "C:\Windows\Logs"; Description = "Logs Windows" }
        @{ Path = "C:\inetpub\logs"; Description = "Logs IIS" }
    )
    
    foreach ($logPath in $logPaths) {
        Remove-OldFiles -Path $logPath.Path -Description $logPath.Description -DaysOld 90 -Recurse
    }
    Write-Host ""
}

# 6. Vider la corbeille
if ($CleanRecycleBin) {
    Write-Host "🗑️  VIDAGE DE LA CORBEILLE" -ForegroundColor Green
    
    try {
        # Obtenir la taille de la corbeille
        $recycleBin = Get-WmiObject -Query "SELECT * FROM Win32_LogicalFileSecuritySetting WHERE Path='C:\\`$Recycle.Bin'" -ErrorAction SilentlyContinue
        
        if (-not $WhatIf) {
            Clear-RecycleBin -Force -ErrorAction SilentlyContinue
            Write-Host "   ✅ Corbeille vidée" -ForegroundColor Green
        }
        else {
            Write-Host "   [SIMULATION] Vidage de la corbeille" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ Impossible de vider la corbeille : $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 7. Nettoyage des téléchargements anciens (ATTENTION)
if ($CleanDownloads) {
    Write-Host "💾 NETTOYAGE TÉLÉCHARGEMENTS ANCIENS" -ForegroundColor Red
    Write-Host "   ⚠️  ATTENTION : Peut supprimer des fichiers importants" -ForegroundColor Yellow
    
    $downloadPath = "$env:USERPROFILE\Downloads"
    Remove-OldFiles -Path $downloadPath -Description "Téléchargements anciens" -DaysOld ($OlderThanDays * 2)
    Write-Host ""
}

# Résumé final
Write-Host "📊 RÉSUMÉ DU NETTOYAGE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Durée d'exécution : $((Get-Date) - $startTime)" -ForegroundColor Gray

if ($WhatIf) {
    Write-Host "⚠️  MODE SIMULATION ACTIVÉ" -ForegroundColor Yellow
    Write-Host "Pour effectuer le nettoyage réel, modifiez `$WhatIf = `$false" -ForegroundColor Yellow
}
else {
    Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 RECOMMANDATIONS SUPPLÉMENTAIRES :" -ForegroundColor Cyan
Write-Host "   • Exécutez 'cleanmgr.exe' (Nettoyage de disque Windows)" -ForegroundColor Gray
Write-Host "   • Vérifiez les points de restauration système" -ForegroundColor Gray
Write-Host "   • Défragmentez le disque si nécessaire" -ForegroundColor Gray
Write-Host "   • Utilisez 'sfc /scannow' si problèmes système" -ForegroundColor Gray