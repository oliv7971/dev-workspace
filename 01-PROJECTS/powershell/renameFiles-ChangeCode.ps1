# =============================================================================
# SCRIPT DE RENOMMAGE DE FICHIERS - Changer un code dans le nom
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================

# Repertoire contenant les fichiers a renommer
$BasePath = "C:\data\11-CHANTIERS\BURE\10-ACTIVITES\Rapports d'activité\2025\251201-rapport mensuel novembre\3-pdf-annexes"

# Code a remplacer
$OldCode = "03_107-GGS_SMC_C060"
$NewCode = "03_108-GGS_SMC_C060"

# Mode simulation : $true = voir sans renommer, $false = renommer vraiment
$WhatIf = $true

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

Write-Host "=== RENOMMAGE DE FICHIERS ===" -ForegroundColor Cyan
Write-Host "Repertoire : $BasePath" -ForegroundColor White
Write-Host "Remplacer  : '$OldCode'" -ForegroundColor Yellow
Write-Host "Par        : '$NewCode'" -ForegroundColor Green
Write-Host "Mode simulation : $WhatIf" -ForegroundColor $(if($WhatIf){"Yellow"}else{"Green"})
Write-Host ""

# Verifier que le repertoire existe
if (-not (Test-Path -LiteralPath $BasePath)) {
    Write-Error "Le repertoire n'existe pas : $BasePath"
    exit 1
}

# Trouver les fichiers correspondants
$files = Get-ChildItem -LiteralPath $BasePath -File | Where-Object { $_.Name -like "$OldCode*" }

Write-Host "Fichiers trouves : $($files.Count)" -ForegroundColor Cyan
Write-Host ""

if ($files.Count -eq 0) {
    Write-Host "Aucun fichier correspondant au pattern '$OldCode*'" -ForegroundColor Yellow
    exit 0
}

# Renommer les fichiers
$renamed = 0
$errors = 0

foreach ($file in $files) {
    $newName = $file.Name -replace [regex]::Escape($OldCode), $NewCode
    $newPath = Join-Path $file.DirectoryName $newName
    
    Write-Host "  $($file.Name)" -ForegroundColor White -NoNewline
    Write-Host " -> " -ForegroundColor Gray -NoNewline
    Write-Host "$newName" -ForegroundColor Green
    
    if (-not $WhatIf) {
        try {
            Rename-Item -LiteralPath $file.FullName -NewName $newName -ErrorAction Stop
            $renamed++
        }
        catch {
            Write-Host "    [ERREUR] $($_.Exception.Message)" -ForegroundColor Red
            $errors++
        }
    }
    else {
        $renamed++
    }
}

Write-Host ""
Write-Host "=== RESULTAT ===" -ForegroundColor Cyan
if ($WhatIf) {
    Write-Host "Fichiers a renommer : $renamed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[SIMULATION] Pour renommer vraiment, changez `$WhatIf = `$false" -ForegroundColor Cyan
}
else {
    Write-Host "Fichiers renommes : $renamed" -ForegroundColor Green
    if ($errors -gt 0) {
        Write-Host "Erreurs : $errors" -ForegroundColor Red
    }
}
