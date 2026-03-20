# Script PowerShell - Compression parallèle des dossiers (sans suppression)
# Version corrigée - Nécessite 7-Zip (7z.exe)

# CORRECTION 1: Enlever les guillemets doubles en trop
$sevenZip = "C:\Program Files\7-Zip\7z.exe"
$basePath = $PSScriptRoot
$folders = Get-ChildItem -Directory -Path $basePath
$logFile = "$basePath\log_compression.txt"
Remove-Item -Path $logFile -ErrorAction SilentlyContinue

Write-Host "=== COMPRESSION PARALLÈLE ===" -ForegroundColor Cyan
Write-Host "Répertoire: $basePath" -ForegroundColor White
Write-Host "Dossiers trouvés: $($folders.Count)" -ForegroundColor White

# LIMITATION : Maximum 4 jobs en parallèle
$maxJobs = 4
$jobs = @()

foreach ($folder in $folders) {
    # Attendre si trop de jobs en cours
    while ((Get-Job -State Running).Count -ge $maxJobs) {
        Start-Sleep -Milliseconds 500
    }
    
    $archive = "$basePath\$($folder.Name).7z"
    
    # CORRECTION 2: Arguments en tableau
    $arguments = @("a", "`"$archive`"", "`"$($folder.FullName)`"", "-mx=9")
    
    Write-Host "Compression de $($folder.Name)..." -ForegroundColor Green
    
    $jobs += Start-Job -ScriptBlock {
        param($sevenZip, $arguments, $folder, $logFile)
        try {
            $outputFile = "$($folder.FullName)_7z_output.txt"
            $errorFile = "$($folder.FullName)_7z_error.txt"
            
            # CORRECTION 3: Fichiers différents pour stdout et stderr
            $process = Start-Process -FilePath $sevenZip -ArgumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $outputFile -RedirectStandardError $errorFile -PassThru
            
            $output = if (Test-Path $outputFile) { Get-Content $outputFile } else { @() }
            $errors = if (Test-Path $errorFile) { Get-Content $errorFile } else { @() }
            
            if ($process.ExitCode -eq 0) {
                Add-Content -Path $logFile -Value "[$(Get-Date)] Compression de $($folder.Name) : OK"
            } else {
                Add-Content -Path $logFile -Value "[$(Get-Date)] Compression de $($folder.Name) : ERREUR (code: $($process.ExitCode))"
            }
            
            Remove-Item $outputFile -ErrorAction SilentlyContinue
            Remove-Item $errorFile -ErrorAction SilentlyContinue
            
        } catch {
            Add-Content -Path $logFile -Value "[$(Get-Date)] Compression de $($folder.Name) : EXCEPTION: $_"
        }
    } -ArgumentList $sevenZip, $arguments, $folder, $logFile
}

Write-Host "Compression lancée en parallèle. Log: $logFile" -ForegroundColor Yellow
Wait-Job $jobs
Remove-Job $jobs
Write-Host "Compressions terminées." -ForegroundColor Green
