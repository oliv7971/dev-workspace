# Script de Backup et Synchronisation
# Usage: .\backup-dev.ps1 [-Mode "local"|"cloud"|"git"|"all"]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("local", "cloud", "git", "all")]
    [string]$Mode = "all"
)

# Configuration
$sourceDir = "C:\data\20-DEVELOPPEMENT"
$backupBase = "C:\data\20-DEVELOPPEMENT\05-ARCHIVE\backup\DEV"
$cloudDir = "$env:OneDrive\DEV-Sync"  # Ajuster selon votre cloud
$logFile = "$sourceDir\02-TOOLS\logs\backup-$(Get-Date -Format 'yyyyMMdd').log"

# Fonction de logging
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append
    Write-Host "$timestamp - $Message"
}

# Créer dossiers si nécessaire
if (!(Test-Path "$(Split-Path $logFile)")) {
    New-Item -ItemType Directory -Path "$(Split-Path $logFile)" -Force
}

Write-Log "=== Début backup/sync - Mode: $Mode ==="

# Backup local
if ($Mode -eq "local" -or $Mode -eq "all") {
    Write-Log "Backup local en cours..."
    $backupDir = "$backupBase-$(Get-Date -Format 'yyyyMMdd-HHmm')"

    $excludeDirs = @('.git', '__pycache__', '.venv', 'node_modules', 'bin', 'obj', '03-SANDBOX\temp', '10-INSTALL')
    $excludeArgs = $excludeDirs | ForEach-Object { "/XD `"$_`"" }

    $robocopyArgs = @(
        "`"$sourceDir`""
        "`"$backupDir`""
        "/MIR"
        "/R:3"
        "/W:1"
        "/LOG+:`"$logFile`""
    ) + $excludeArgs

    & robocopy @robocopyArgs
    Write-Log "Backup local terminé : $backupDir"
}

# Synchronisation cloud
if ($Mode -eq "cloud" -or $Mode -eq "all") {
    Write-Log "Synchronisation cloud en cours..."

    if (Test-Path $cloudDir) {
        # Sync projets importants
        robocopy "$sourceDir\01-PROJECTS" "$cloudDir\01-PROJECTS" /MIR /XD .venv __pycache__ .git node_modules /XF *.exe *.log

        # Sync configurations
        robocopy "$sourceDir\.vscode" "$cloudDir\.vscode" /MIR
        robocopy "$sourceDir\02-TOOLS\configs" "$cloudDir\configs" /MIR

        # Sync documentation
        robocopy "$sourceDir\02-TOOLS\docs" "$cloudDir\docs" /MIR

        Write-Log "Synchronisation cloud terminée"
    } else {
        Write-Log "ATTENTION: Dossier cloud introuvable - $cloudDir"
    }
}

# Commit Git
if ($Mode -eq "git" -or $Mode -eq "all") {
    Write-Log "Commit Git en cours..."

    Push-Location $sourceDir
    try {
        if (Get-Command git -ErrorAction SilentlyContinue) {
            $gitStatus = & git status --porcelain
            if ($gitStatus) {
                & git add .
                $commitMsg = "Auto-backup $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
                & git commit -m $commitMsg

                # Push si remote configuré
                $remoteUrl = & git remote get-url origin 2>$null
                if ($remoteUrl) {
                    & git push
                    Write-Log "Git push terminé vers $remoteUrl"
                } else {
                    Write-Log "Aucun remote Git configuré"
                }
            } else {
                Write-Log "Aucune modification Git à commiter"
            }
        } else {
            Write-Log "Git non installé - ignorer sync Git"
        }
    }
    catch {
        Write-Log "ERREUR Git: $($_.Exception.Message)"
    }
    finally {
        Pop-Location
    }
}

# Nettoyage vieux backups (garder 7 derniers)
if ($Mode -eq "local" -or $Mode -eq "all") {
    Write-Log "Nettoyage anciens backups..."
    $oldBackups = Get-ChildItem "$backupBase-*" | Sort-Object Name -Descending | Select-Object -Skip 7
    foreach ($old in $oldBackups) {
        Remove-Item $old.FullName -Recurse -Force
        Write-Log "Supprimé ancien backup: $($old.Name)"
    }
}

Write-Log "=== Fin backup/sync ==="
