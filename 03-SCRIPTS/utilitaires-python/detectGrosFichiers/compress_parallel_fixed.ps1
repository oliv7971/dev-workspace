# Script PowerShell - Compression parallèle des dossiers (sans suppression)
# Nécessite 7-Zip (7z.exe) dans le PATH ou préciser le chemin complet
# Version corrigée avec gestion d'erreurs améliorée

param(
    [string]$BasePath = $PSScriptRoot,
    [int]$MaxJobs = 4,
    [int]$CompressionLevel = 9,
    [switch]$WhatIf = $false
)

# Configuration
$sevenZipPath = "C:\Program Files\7-Zip\7z.exe"
$logFile = "$BasePath\log_compression.txt"

# Vérifications préliminaires
Write-Host "=== SCRIPT DE COMPRESSION PARALLÈLE ===" -ForegroundColor Cyan
Write-Host "Répertoire de base: $BasePath" -ForegroundColor White
Write-Host "Niveau de compression: $CompressionLevel (1=rapide, 9=maximum)" -ForegroundColor White
Write-Host "Jobs maximum: $MaxJobs" -ForegroundColor White
Write-Host "Mode simulation: $WhatIf" -ForegroundColor White

if (-not (Test-Path $sevenZipPath)) {
    Write-Error "7-Zip introuvable à l'emplacement: $sevenZipPath"
    Write-Host "Veuillez installer 7-Zip ou modifier le chemin dans le script." -ForegroundColor Red
    exit 1
}

# Initialiser le fichier de log
Remove-Item -Path $logFile -ErrorAction SilentlyContinue
Add-Content -Path $logFile -Value "[$(Get-Date)] === DÉBUT DE LA COMPRESSION ==="

# Obtenir la liste des dossiers
$folders = Get-ChildItem -Directory -Path $BasePath
Write-Host ""
Write-Host "Dossiers trouvés: $($folders.Count)" -ForegroundColor Green

if ($folders.Count -eq 0) {
    Write-Host "Aucun dossier trouvé dans: $BasePath" -ForegroundColor Yellow
    exit 0
}

# Afficher la liste des dossiers
foreach ($folder in $folders) {
    $folderSize = try {
        $size = (Get-ChildItem -Path $folder.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
        if ($size -gt 1GB) { "{0:N2} GB" -f ($size / 1GB) }
        elseif ($size -gt 1MB) { "{0:N2} MB" -f ($size / 1MB) }
        else { "{0:N2} KB" -f ($size / 1KB) }
    } catch { "Erreur calcul" }
    
    Write-Host "  - $($folder.Name) ($folderSize)" -ForegroundColor White
}

if ($WhatIf) {
    Write-Host ""
    Write-Host "=== MODE SIMULATION - Aucune compression ne sera effectuée ===" -ForegroundColor Magenta
} else {
    Write-Host ""
    $confirmation = Read-Host "Continuer avec la compression ? (O/N)"
    if ($confirmation -notmatch '^[OoYy]') {
        Write-Host "Opération annulée." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "=== DÉBUT DE LA COMPRESSION ===" -ForegroundColor Green
$startTime = Get-Date

$jobs = @()
$jobQueue = @()

# Préparer la queue des jobs
foreach ($folder in $folders) {
    $archive = "$BasePath\$($folder.Name).7z"
    $jobQueue += @{
        Folder = $folder
        Archive = $archive
        Name = $folder.Name
    }
}

$completedJobs = 0
$totalJobs = $jobQueue.Count

# Fonction pour démarrer un job
function Start-CompressionJob {
    param($JobInfo, $SevenZipPath, $CompressionLevel, $LogFile, $SimulationMode)
    
    $scriptBlock = {
        param($SevenZipPath, $FolderPath, $ArchivePath, $CompressionLevel, $FolderName, $LogFile, $SimulationMode)
        
        $result = @{
            FolderName = $FolderName
            Success = $false
            Message = ""
            StartTime = Get-Date
        }
        
        try {
            if ($SimulationMode) {
                Start-Sleep -Seconds (Get-Random -Minimum 2 -Maximum 6)
                $result.Success = $true
                $result.Message = "Simulation réussie"
            } else {
                # Construire la commande 7-Zip
                $arguments = @(
                    "a",
                    "`"$ArchivePath`"",
                    "`"$FolderPath\*`"",
                    "-mx=$CompressionLevel"
                )
                
                # Exécuter 7-Zip
                $process = Start-Process -FilePath $SevenZipPath -ArgumentList $arguments -NoNewWindow -Wait -PassThru -RedirectStandardOutput NUL -RedirectStandardError NUL
                
                if ($process.ExitCode -eq 0) {
                    $result.Success = $true
                    $archiveInfo = Get-Item $ArchivePath -ErrorAction SilentlyContinue
                    if ($archiveInfo) {
                        $archiveSize = "{0:N2} MB" -f ($archiveInfo.Length / 1MB)
                        $result.Message = "Archive créée: $archiveSize"
                    } else {
                        $result.Message = "Archive créée"
                    }
                } else {
                    $result.Message = "Erreur 7-Zip (code: $($process.ExitCode))"
                }
            }
        } catch {
            $result.Message = "Exception: $($_.Exception.Message)"
        }
        
        $result.EndTime = Get-Date
        $result.Duration = $result.EndTime - $result.StartTime
        
        # Log
        $logEntry = "[$(Get-Date)] $($result.FolderName): $(if ($result.Success) { 'OK' } else { 'ERREUR' }) - $($result.Message) (Durée: $($result.Duration.ToString('mm\:ss')))"
        Add-Content -Path $LogFile -Value $logEntry
        
        return $result
    }
    
    return Start-Job -ScriptBlock $scriptBlock -ArgumentList $SevenZipPath, $JobInfo.Folder.FullName, $JobInfo.Archive, $CompressionLevel, $JobInfo.Name, $LogFile, $SimulationMode
}

# Traitement avec limitation du nombre de jobs parallèles
$queueIndex = 0
$runningJobs = @()

while ($queueIndex -lt $totalJobs -or $runningJobs.Count -gt 0) {
    # Démarrer de nouveaux jobs si possible
    while ($runningJobs.Count -lt $MaxJobs -and $queueIndex -lt $totalJobs) {
        $jobInfo = $jobQueue[$queueIndex]
        Write-Host "Démarrage: $($jobInfo.Name)" -ForegroundColor Cyan
        
        $job = Start-CompressionJob -JobInfo $jobInfo -SevenZipPath $sevenZipPath -CompressionLevel $CompressionLevel -LogFile $logFile -SimulationMode $WhatIf
        $runningJobs += @{ Job = $job; Info = $jobInfo }
        $queueIndex++
    }
    
    # Vérifier les jobs terminés
    $finishedJobs = $runningJobs | Where-Object { $_.Job.State -ne "Running" }
    
    foreach ($finishedJob in $finishedJobs) {
        $result = Receive-Job -Job $finishedJob.Job
        
        if ($result.Success) {
            Write-Host "✓ $($result.FolderName) - $($result.Message) ($($result.Duration.ToString('mm\:ss')))" -ForegroundColor Green
        } else {
            Write-Host "✗ $($result.FolderName) - $($result.Message)" -ForegroundColor Red
        }
        
        Remove-Job -Job $finishedJob.Job
        $completedJobs++
    }
    
    # Mettre à jour la liste des jobs en cours
    $runningJobs = $runningJobs | Where-Object { $_.Job.State -eq "Running" }
    
    if ($runningJobs.Count -gt 0) {
        Write-Host "En cours: $($runningJobs.Count), Terminés: $completedJobs/$totalJobs" -ForegroundColor Yellow
        Start-Sleep -Seconds 1
    }
}

$endTime = Get-Date
$totalDuration = $endTime - $startTime

Write-Host ""
Write-Host "=== COMPRESSION TERMINÉE ===" -ForegroundColor Green
Write-Host "Durée totale: $($totalDuration.ToString('hh\:mm\:ss'))" -ForegroundColor White
Write-Host "Archives traitées: $totalJobs" -ForegroundColor White
Write-Host "Log disponible: $logFile" -ForegroundColor White

# Résumé des archives créées
if (-not $WhatIf) {
    Write-Host ""
    Write-Host "=== ARCHIVES CRÉÉES ===" -ForegroundColor Cyan
    $archives = Get-ChildItem -Path $BasePath -Filter "*.7z"
    $totalSize = 0
    
    foreach ($archive in $archives) {
        $size = $archive.Length / 1MB
        $totalSize += $size
        Write-Host "  $($archive.Name) - {0:N2} MB" -f $size -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Taille totale des archives: {0:N2} MB ({1:N2} GB)" -f $totalSize, ($totalSize / 1024) -ForegroundColor Green
}

Add-Content -Path $logFile -Value "[$(Get-Date)] === FIN DE LA COMPRESSION ==="
Add-Content -Path $logFile -Value "Durée totale: $($totalDuration.ToString('hh\:mm\:ss'))"
