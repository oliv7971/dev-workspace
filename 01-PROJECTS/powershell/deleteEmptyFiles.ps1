# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$BasePath = "C:\VotreCheminIci"          # Chemin à analyser
$WhatIf = $true                          # $true = simulation, $false = suppression réelle
$Verbose = $true                         # $true = affichage détaillé, $false = mode silencieux

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

# Vérifier que le répertoire de base existe
if (-not (Test-Path $BasePath)) {
    Write-Error "Le chemin '$BasePath' n'existe pas."
    exit 1
}

$deletedFiles = 0
$deletedFolders = 0

Write-Host "Analyse du répertoire : $BasePath" -ForegroundColor Cyan
Write-Host "Mode simulation : $WhatIf" -ForegroundColor Yellow
Write-Host ""

# Étape 1 : Supprimer tous les fichiers vides
Write-Host "Recherche des fichiers vides..." -ForegroundColor Green
$emptyFiles = Get-ChildItem -Path $BasePath -Recurse -File | Where-Object { $_.Length -eq 0 }

foreach ($file in $emptyFiles) {
    if ($Verbose) {
        Write-Host "  Fichier vide trouvé : $($file.FullName)" -ForegroundColor Gray
    }
    
    if (-not $WhatIf) {
        try {
            Remove-Item -Path $file.FullName -Force
            $deletedFiles++
            Write-Host "  ✓ Supprimé : $($file.FullName)" -ForegroundColor Red
        }
        catch {
            Write-Warning "Impossible de supprimer : $($file.FullName) - $($_.Exception.Message)"
        }
    }
    else {
        Write-Host "  [WhatIf] Suppression : $($file.FullName)" -ForegroundColor Yellow
        $deletedFiles++
    }
}

# Étape 2 : Supprimer les répertoires vides (du plus profond au moins profond)
Write-Host "`nRecherche des répertoires vides..." -ForegroundColor Green
do {
    $emptyFolders = Get-ChildItem -Path $BasePath -Recurse -Directory | 
                    Where-Object { (Get-ChildItem -Path $_.FullName -Force).Count -eq 0 } |
                    Sort-Object { $_.FullName.Split('\').Count } -Descending
    
    if ($emptyFolders.Count -eq 0) {
        break
    }
    
    foreach ($folder in $emptyFolders) {
        if ($Verbose) {
            Write-Host "  Répertoire vide trouvé : $($folder.FullName)" -ForegroundColor Gray
        }
        
        if (-not $WhatIf) {
            try {
                Remove-Item -Path $folder.FullName -Force
                $deletedFolders++
                Write-Host "  ✓ Supprimé : $($folder.FullName)" -ForegroundColor Red
            }
            catch {
                Write-Warning "Impossible de supprimer : $($folder.FullName) - $($_.Exception.Message)"
            }
        }
        else {
            Write-Host "  [WhatIf] Suppression : $($folder.FullName)" -ForegroundColor Yellow
            $deletedFolders++
        }
    }
} while ($emptyFolders.Count -gt 0 -and -not $WhatIf)

# Résumé
Write-Host "`n" -NoNewline
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host "RÉSUMÉ" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host "Fichiers vides supprimés : $deletedFiles" -ForegroundColor Green
Write-Host "Répertoires vides supprimés : $deletedFolders" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Cyan