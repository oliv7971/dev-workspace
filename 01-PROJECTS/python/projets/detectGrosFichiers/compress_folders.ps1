# Script PowerShell pour zipper les dossiers en parallèle
# Auteur: GitHub Copilot
# Date: 6 septembre 2025

param(
    [string]$RootPath = "D:\BURE-CHANTIER 4-DEBUT2025",
    [string]$SpecialFolder = "10-ACTIVITES",
    [int]$MaxParallelJobs = 4,
    [switch]$WhatIf = $false
)

Write-Host "=== SCRIPT DE COMPRESSION PARALLÈLE ===" -ForegroundColor Cyan
Write-Host "Répertoire racine: $RootPath" -ForegroundColor White
Write-Host "Dossier spécial: $SpecialFolder" -ForegroundColor White
Write-Host "Jobs parallèles max: $MaxParallelJobs" -ForegroundColor White
Write-Host "Mode simulation: $WhatIf" -ForegroundColor White

# Vérifications
if (-not (Test-Path $RootPath)) {
    Write-Error "Le chemin racine n'existe pas: $RootPath"
    exit 1
}

# Obtenir tous les dossiers
$allFolders = Get-ChildItem -Path $RootPath -Directory
$normalFolders = $allFolders | Where-Object { $_.Name -ne $SpecialFolder }
$specialFolderPath = Join-Path $RootPath $SpecialFolder

Write-Host ""
Write-Host "Dossiers normaux trouvés: $($normalFolders.Count)"
foreach ($folder in $normalFolders) {
    Write-Host "  - $($folder.Name)" -ForegroundColor White
}

# Traiter le dossier spécial
if (Test-Path $specialFolderPath) {
    $subFolders = Get-ChildItem -Path $specialFolderPath -Directory
    Write-Host ""
    Write-Host "Sous-dossiers dans $SpecialFolder : $($subFolders.Count)" -ForegroundColor Yellow
    foreach ($subFolder in $subFolders) {
        Write-Host "  - $($subFolder.Name)" -ForegroundColor Yellow
    }
}

Write-Host ""
$confirmation = Read-Host "Continuer avec la compression ? (O/N)"
if ($confirmation -notmatch '^[OoYy]') {
    Write-Host "Opération annulée." -ForegroundColor Yellow
    exit 0
}

# Compression des dossiers normaux
Write-Host ""
Write-Host "=== COMPRESSION DES DOSSIERS NORMAUX ===" -ForegroundColor Cyan
$jobs = @()

foreach ($folder in $normalFolders) {
    $sourcePath = $folder.FullName
    $archivePath = "$sourcePath.7z"
    
    if ($WhatIf) {
        Write-Host "[SIMULATION] 7z a -mx5 '$archivePath' '$sourcePath\*'" -ForegroundColor Yellow
    } else {
        $scriptBlock = {
            param($SourcePath, $ArchivePath)
            $folderName = Split-Path $SourcePath -Leaf
            try {
                $result = & "C:\Program Files\7-Zip\7z.exe" a -mx5 "$ArchivePath" "$SourcePath\*" 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Remove-Item "$SourcePath" -Recurse -Force
                    return @{ Success = $true; Message = "OK"; Name = $folderName }
                } else {
                    return @{ Success = $false; Message = $result; Name = $folderName }
                }
            } catch {
                return @{ Success = $false; Message = $_.Exception.Message; Name = $folderName }
            }
        }
        
        $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $sourcePath, $archivePath
        $jobs += $job
        Write-Host "Job démarré pour: $($folder.Name)" -ForegroundColor Green
    }
}

# Attendre les jobs normaux
if (-not $WhatIf -and $jobs.Count -gt 0) {
    Write-Host "Attente des jobs normaux..."
    $jobs | Wait-Job | ForEach-Object {
        $result = Receive-Job $_
        if ($result.Success) {
            Write-Host "? $($result.Name)" -ForegroundColor Green
        } else {
            Write-Host "? $($result.Name): $($result.Message)" -ForegroundColor Red
        }
        Remove-Job $_
    }
}

# Compression des sous-dossiers spéciaux
if (Test-Path $specialFolderPath) {
    Write-Host ""
    Write-Host "=== COMPRESSION DES SOUS-DOSSIERS DE $SpecialFolder ===" -ForegroundColor Cyan
    $subJobs = @()
    $subFolders = Get-ChildItem -Path $specialFolderPath -Directory
    
    foreach ($subFolder in $subFolders) {
        $sourcePath = $subFolder.FullName
        $archivePath = "$sourcePath.7z"
        
        if ($WhatIf) {
            Write-Host "[SIMULATION] 7z a -mx5 '$archivePath' '$sourcePath\*'" -ForegroundColor Yellow
        } else {
            $scriptBlock = {
                param($SourcePath, $ArchivePath)
                $folderName = Split-Path $SourcePath -Leaf
                try {
                    $result = & "C:\Program Files\7-Zip\7z.exe" a -mx5 "$ArchivePath" "$SourcePath\*" 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Remove-Item "$SourcePath" -Recurse -Force
                        return @{ Success = $true; Message = "OK"; Name = $folderName }
                    } else {
                        return @{ Success = $false; Message = $result; Name = $folderName }
                    }
                } catch {
                    return @{ Success = $false; Message = $_.Exception.Message; Name = $folderName }
                }
            }
            
            $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $sourcePath, $archivePath
            $subJobs += $job
            Write-Host "Job démarré pour: $SpecialFolder\$($subFolder.Name)" -ForegroundColor Green
        }
    }
    
    # Attendre les jobs spéciaux
    if (-not $WhatIf -and $subJobs.Count -gt 0) {
        Write-Host "Attente des jobs spéciaux..."
        $subJobs | Wait-Job | ForEach-Object {
            $result = Receive-Job $_
            if ($result.Success) {
                Write-Host "? $SpecialFolder\$($result.Name)" -ForegroundColor Green
            } else {
                Write-Host "? $SpecialFolder\$($result.Name): $($result.Message)" -ForegroundColor Red
            }
            Remove-Job $_
        }
    }
}

Write-Host ""
Write-Host "=== TERMINÉ ===" -ForegroundColor Green
