# Script PowerShell - Compression parallèle des dossiers (sans suppression)
# Nécessite 7-Zip (7z.exe) dans le PATH ou préciser le chemin complet
# Version corrigée avec gestion d'erreurs améliorée

param(
    [string]$BasePath = $PSScriptRoot,
    [int]$MaxJobs = 4,
    [int]$CompressionLevel = 9,
    [switch]$WhatIf = $false,
    [switch]$NoConfirm = $false,
    [switch]$SkipSizeCalculation = $false,
    [switch]$VerifyArchives = $true
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
Write-Host "Vérification archives: $VerifyArchives" -ForegroundColor White

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
    if ($SkipSizeCalculation) {
        Write-Host "  - $($folder.Name)" -ForegroundColor White
    } else {
        $folderSize = try {
            $size = (Get-ChildItem -Path $folder.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            if ($size -gt 1GB) { "{0:N2} GB" -f ($size / 1GB) }
            elseif ($size -gt 1MB) { "{0:N2} MB" -f ($size / 1MB) }
            elseif ($size -gt 0) { "{0:N2} KB" -f ($size / 1KB) }
            else { "Taille inconnue" }
        } catch { "Taille inconnue" }
        
        Write-Host "  - $($folder.Name) ($folderSize)" -ForegroundColor White
    }
}

if ($WhatIf) {
    Write-Host ""
    Write-Host "=== MODE SIMULATION - Aucune compression ne sera effectuée ===" -ForegroundColor Magenta
} elseif (-not $NoConfirm) {
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
    param($JobInfo, $SevenZipPath, $CompressionLevel, $LogFile, $SimulationMode, $VerifyArchive)
    
    $scriptBlock = {
        param($SevenZipPath, $FolderPath, $ArchivePath, $CompressionLevel, $FolderName, $LogFile, $SimulationMode, $VerifyArchive)
        
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
                # Créer fichiers temporaires pour les sorties
                $tempOut = [System.IO.Path]::GetTempFileName()
                $tempErr = [System.IO.Path]::GetTempFileName()
                
                try {
                    # Méthode alternative : Utiliser l'opérateur d'appel & au lieu de Start-Process
                    # Plus fiable avec les chemins contenant des espaces
                    $exitCode = 0
                    try {
                        & $SevenZipPath a $ArchivePath "$FolderPath\*" "-mx=$CompressionLevel" > $tempOut 2> $tempErr
                        $exitCode = $LASTEXITCODE
                    }
                    catch {
                        $exitCode = -1
                    }
                    
                    if ($exitCode -eq 0) {
                        # Archive créée avec succès
                        $archiveInfo = Get-Item $ArchivePath -ErrorAction SilentlyContinue
                        $archiveSize = if ($archiveInfo) { "{0:N2} MB" -f ($archiveInfo.Length / 1MB) } else { "?" }
                        
                        # ÉTAPE DE VÉRIFICATION
                        if ($VerifyArchive) {
                            $tempVerifyOut = [System.IO.Path]::GetTempFileName()
                            $tempVerifyErr = [System.IO.Path]::GetTempFileName()
                            try {
                                # Tester l'intégrité avec l'opérateur d'appel (plus fiable)
                                & $SevenZipPath t $ArchivePath > $tempVerifyOut 2> $tempVerifyErr
                                $verifyExitCode = $LASTEXITCODE
                                
                                if ($verifyExitCode -eq 0) {
                                    $result.Success = $true
                                    $result.Message = "Archive créée et VÉRIFIÉE: $archiveSize"
                                } else {
                                    $result.Success = $false
                                    $verifyError = if (Test-Path $tempVerifyErr) { (Get-Content $tempVerifyErr -Raw).Trim() } else { "Erreur inconnue" }
                                    $result.Message = "Archive créée ($archiveSize) mais VÉRIFICATION ÉCHOUÉE (code: $verifyExitCode) - $verifyError"
                                    # Optionnel: Supprimer l'archive corrompue
                                    # Remove-Item $ArchivePath -Force -ErrorAction SilentlyContinue
                                }
                            } finally {
                                Remove-Item $tempVerifyOut -ErrorAction SilentlyContinue
                                Remove-Item $tempVerifyErr -ErrorAction SilentlyContinue
                            }
                        } else {
                            # Pas de vérification
                            $result.Success = $true
                            $result.Message = "Archive créée: $archiveSize"
                        }
                    } else {
                        $errorContent = if (Test-Path $tempErr) { Get-Content $tempErr -Raw } else { "" }
                        $result.Message = "Erreur 7-Zip (code: $exitCode) - $errorContent"
                    }
                } finally {
                    # Nettoyer les fichiers temporaires
                    Remove-Item $tempOut -ErrorAction SilentlyContinue
                    Remove-Item $tempErr -ErrorAction SilentlyContinue
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
    
    return Start-Job -ScriptBlock $scriptBlock -ArgumentList $SevenZipPath, $JobInfo.Folder.FullName, $JobInfo.Archive, $CompressionLevel, $JobInfo.Name, $LogFile, $SimulationMode, $VerifyArchive
}

# Traitement avec limitation du nombre de jobs parallèles
$queueIndex = 0
$runningJobs = [System.Collections.ArrayList]::new()

while ($queueIndex -lt $totalJobs -or $runningJobs.Count -gt 0) {
    # Démarrer de nouveaux jobs si possible
    while ($runningJobs.Count -lt $MaxJobs -and $queueIndex -lt $totalJobs) {
        $jobInfo = $jobQueue[$queueIndex]
        Write-Host "Démarrage: $($jobInfo.Name)" -ForegroundColor Cyan
        
        $job = Start-CompressionJob -JobInfo $jobInfo -SevenZipPath $sevenZipPath -CompressionLevel $CompressionLevel -LogFile $logFile -SimulationMode $WhatIf -VerifyArchive $VerifyArchives
        [void]$runningJobs.Add([PSCustomObject]@{ 
            Job = $job
            JobInfo = $jobInfo
        })
        $queueIndex++
    }
    
    # Vérifier les jobs terminés
    $finishedJobs = @($runningJobs | Where-Object { $_.Job.State -ne "Running" })
    
    foreach ($finishedJob in $finishedJobs) {
        $result = Receive-Job -Job $finishedJob.Job
        
        if ($result.Success) {
            Write-Host "[OK] $($result.FolderName) - $($result.Message) ($($result.Duration.ToString('mm\:ss')))" -ForegroundColor Green
        } else {
            Write-Host "[ERREUR] $($result.FolderName) - $($result.Message)" -ForegroundColor Red
        }
        
        Remove-Job -Job $finishedJob.Job
        $completedJobs++
    }
    
    # Mettre à jour la liste des jobs en cours - Recréer l'ArrayList
    $stillRunning = @($runningJobs | Where-Object { $_.Job.State -eq "Running" })
    $runningJobs.Clear()
    foreach ($job in $stillRunning) {
        [void]$runningJobs.Add($job)
    }
    
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
        Write-Host ("  {0} - {1:N2} MB" -f $archive.Name, $size) -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host ("Taille totale des archives: {0:N2} MB ({1:N2} GB)" -f $totalSize, ($totalSize / 1024)) -ForegroundColor Green
}

Add-Content -Path $logFile -Value "[$(Get-Date)] === FIN DE LA COMPRESSION ==="
Add-Content -Path $logFile -Value "Durée totale: $($totalDuration.ToString('hh\:mm\:ss'))"
