# Script d'installation multi-machines
# Usage: .\install-on-new-machine.ps1 [-Drive "D"] [-WorkspaceName "20-DEVELOPPEMENT"]

param(
    [Parameter(Mandatory=$false)]
    [string]$Drive = "C",

    [Parameter(Mandatory=$false)]
    [string]$WorkspaceName = "20-DEVELOPPEMENT",

    [Parameter(Mandatory=$false)]
    [string]$GitUrl = "https://github.com/olivierboissardggc2-max/dev-workspace.git"
)

Write-Host "=== Installation workspace sur nouvelle machine ===" -ForegroundColor Green

$targetPath = "${Drive}:\data\${WorkspaceName}"

# Vérification des prérequis
Write-Host "1. Vérification des prérequis..." -ForegroundColor Yellow

# Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "   Installation de Git..." -ForegroundColor Yellow
    winget install Git.Git
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
}
Write-Host "   ✅ Git disponible" -ForegroundColor Green

# VS Code
if (!(Get-Command code -ErrorAction SilentlyContinue)) {
    Write-Host "   Installation de VS Code..." -ForegroundColor Yellow
    winget install Microsoft.VisualStudioCode
}
Write-Host "   ✅ VS Code disponible" -ForegroundColor Green

# Clonage ou création du workspace
Write-Host "2. Configuration du workspace..." -ForegroundColor Yellow

if ($GitUrl) {
    Write-Host "   Clonage depuis GitHub..." -ForegroundColor Yellow
    if (Test-Path $targetPath) {
        Write-Host "   ⚠️  Le dossier existe déjà : $targetPath" -ForegroundColor Yellow
        $response = Read-Host "   Supprimer et recréer ? (y/N)"
        if ($response -eq 'y') {
            Remove-Item $targetPath -Recurse -Force
        } else {
            Write-Host "   ❌ Installation annulée" -ForegroundColor Red
            exit 1
        }
    }

    # Créer le dossier parent si nécessaire
    $parentPath = Split-Path $targetPath
    if (!(Test-Path $parentPath)) {
        New-Item -ItemType Directory -Path $parentPath -Force
    }

    git clone $GitUrl $targetPath
    Set-Location $targetPath
} else {
    Write-Host "   Initialisation locale..." -ForegroundColor Yellow
    if (!(Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath -Force
    }
    Set-Location $targetPath
    git init
}

# Configuration Git locale
Write-Host "3. Configuration Git..." -ForegroundColor Yellow
$userName = git config --global user.name
$userEmail = git config --global user.email

if (!$userName) {
    $userName = Read-Host "   Nom d'utilisateur Git"
    git config --global user.name "$userName"
}
if (!$userEmail) {
    $userEmail = Read-Host "   Email Git"
    git config --global user.email "$userEmail"
}

Write-Host "   ✅ Git configuré pour $userName <$userEmail>" -ForegroundColor Green

# Adaptation des scripts pour le nouveau lecteur
Write-Host "4. Adaptation des configurations..." -ForegroundColor Yellow

$scriptPath = Join-Path $targetPath "02-TOOLS\scripts\backup-dev.ps1"
if (Test-Path $scriptPath) {
    Write-Host "   ✅ Script de backup détecté et adaptatif" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Script de backup non trouvé" -ForegroundColor Yellow
}

# Instructions finales
Write-Host ""
Write-Host "=== Installation terminée ! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes :" -ForegroundColor Yellow
Write-Host "1. Ouvrir VS Code dans ce dossier : code ." -ForegroundColor White
Write-Host "2. Activer Settings Sync :" -ForegroundColor White
Write-Host "   - Ctrl+Shift+P → 'Settings Sync: Turn On'" -ForegroundColor Gray
Write-Host "   - Se connecter avec le même compte GitHub/Microsoft" -ForegroundColor Gray
Write-Host "3. Tester le backup : .\02-TOOLS\scripts\backup-dev.ps1 -Mode git" -ForegroundColor White
Write-Host ""
Write-Host "Workspace installé dans : $targetPath" -ForegroundColor Cyan
