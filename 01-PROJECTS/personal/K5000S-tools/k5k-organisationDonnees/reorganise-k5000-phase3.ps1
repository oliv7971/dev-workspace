<#
.SYNOPSIS
    Phase 3 - Nettoyage final des donnees Kawai K5000S
.DESCRIPTION
    Verifie par hash MD5 que chaque fichier restant dans les anciens dossiers
    est bien un doublon d'un fichier deja present dans la nouvelle structure.
    Supprime les doublons confirmes et deplace les fichiers uniques.
    Nettoie les dossiers vides a la fin.
    
    Mode dry-run par defaut.
.PARAMETER Execute
    Active l'execution reelle (suppressions et deplacements)
#>

param(
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$base = "D:\01-MUSIQUE\03-KAWAI"

# Nouveaux dossiers (cibles = ne pas toucher)
$newDirs = @(
    "01-DOCUMENTATION",
    "02-PATCHES",
    "03-SAMPLES-KSF",
    "04-SOFTWARE",
    "05-GOTEK-HFE",
    "06-MIDI-FILES",
    "_ARCHIVES",
    "_HORS-K5000"
)

# Anciens dossiers a nettoyer
$oldDirs = @(
    "01-DOCUMENTATION KAWAI",
    "01-KAWAI",
    "02-SOUNDS",
    "03-KAWAI",
    "03-SOFTWARE",
    "04-KAWAI",
    "04-KAWAI DISKS",
    "collect2",
    "collect2_2",
    "KAWAI",
    "KAWAI K5000"
)

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Phase 3 - Nettoyage final K5000" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Execute) {'EXECUTION'} else {'DRY-RUN'})" -ForegroundColor $(if ($Execute) {'Red'} else {'Green'})
Write-Host "============================================`n" -ForegroundColor Cyan

# ============================================================
# Etape 1 : Construire un index hash de la nouvelle structure
# ============================================================
Write-Host "Construction de l'index des fichiers dans la nouvelle structure..." -ForegroundColor Yellow

$newIndex = @{}       # hash -> chemin complet
$newNameIndex = @{}   # nom fichier (lower) -> liste de chemins

foreach ($nd in $newDirs) {
    $ndPath = Join-Path $base $nd
    if (-not (Test-Path $ndPath)) { continue }
    
    Get-ChildItem $ndPath -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        $nameLower = $_.Name.ToLower()
        
        # Index par nom
        if (-not $newNameIndex.ContainsKey($nameLower)) {
            $newNameIndex[$nameLower] = @()
        }
        $newNameIndex[$nameLower] += $_.FullName
        
        # Index par hash (pour verif exacte)
        try {
            $h = (Get-FileHash -LiteralPath $_.FullName -Algorithm MD5 -ErrorAction SilentlyContinue).Hash
            if ($h) {
                if (-not $newIndex.ContainsKey($h)) {
                    $newIndex[$h] = $_.FullName
                }
            }
        } catch { }
    }
}

Write-Host "Index: $($newIndex.Count) hashes uniques, $($newNameIndex.Count) noms uniques`n" -ForegroundColor Gray

# ============================================================
# Etape 2 : Analyser chaque fichier restant dans les anciens dossiers
# ============================================================
Write-Host "Analyse des fichiers restants..." -ForegroundColor Yellow

$duplicates = @()    # Fichiers qui sont des doublons confirmes
$orphans = @()       # Fichiers uniques sans equivalent
$errors = @()

foreach ($od in $oldDirs) {
    $odPath = Join-Path $base $od
    if (-not (Test-Path $odPath)) { continue }
    
    $files = Get-ChildItem $odPath -Recurse -File -ErrorAction SilentlyContinue
    if (-not $files -or $files.Count -eq 0) { continue }
    
    Write-Host "  $od : $($files.Count) fichiers" -ForegroundColor Gray
    
    foreach ($f in $files) {
        try {
            $h = (Get-FileHash -LiteralPath $f.FullName -Algorithm MD5 -ErrorAction SilentlyContinue).Hash
            
            if ($h -and $newIndex.ContainsKey($h)) {
                # Doublon confirme par hash
                $duplicates += [PSCustomObject]@{
                    Source    = $f.FullName
                    MatchedBy = $newIndex[$h]
                    Hash      = $h
                    Size      = $f.Length
                }
            }
            else {
                # Pas de correspondance par hash => orphelin
                $orphans += [PSCustomObject]@{
                    Source = $f.FullName
                    Name   = $f.Name
                    Hash   = $h
                    Size   = $f.Length
                }
            }
        } catch {
            $errors += "ERREUR hash: $($f.FullName) - $_"
        }
    }
}

# ============================================================
# Etape 3 : Rapport
# ============================================================
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "RESULTATS DE L'ANALYSE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Doublons confirmes (a supprimer)  : $($duplicates.Count)" -ForegroundColor Green
Write-Host "Fichiers orphelins (a deplacer)   : $($orphans.Count)" -ForegroundColor Yellow
Write-Host "Erreurs                           : $($errors.Count)" -ForegroundColor $(if ($errors.Count -gt 0) {'Red'} else {'Gray'})

$dupSize = ($duplicates | Measure-Object -Property Size -Sum).Sum
Write-Host "Espace recuperable (doublons)     : $([math]::Round($dupSize / 1MB, 1)) Mo" -ForegroundColor Green

# Exporter le rapport detaille
$reportPath = Join-Path $base "_RAPPORT-PHASE3.txt"
$report = @()
$report += "=== RAPPORT PHASE 3 - $(Get-Date -Format 'yyyy-MM-dd HH:mm') ==="
$report += ""
$report += "=== DOUBLONS CONFIRMES ($($duplicates.Count) fichiers, $([math]::Round($dupSize / 1MB, 1)) Mo) ==="
foreach ($d in $duplicates | Sort-Object Source) {
    $report += "  DEL: $($d.Source)"
    $report += "  === $($d.MatchedBy)"
    $report += ""
}
$report += ""
$report += "=== ORPHELINS ($($orphans.Count) fichiers) ==="
foreach ($o in $orphans | Sort-Object Source) {
    $report += "  $($o.Source) ($([math]::Round($o.Size / 1KB, 1)) Ko)"
}
$report += ""
if ($errors.Count -gt 0) {
    $report += "=== ERREURS ==="
    $report += $errors
}
$report | Out-File $reportPath -Encoding UTF8
Write-Host "`nRapport detaille: $reportPath" -ForegroundColor Gray

# ============================================================
# Etape 4 : Traiter les orphelins
# ============================================================
if ($orphans.Count -gt 0) {
    Write-Host "`n--- Orphelins a deplacer ---" -ForegroundColor Yellow
    
    # Destination pour les orphelins non classes
    $orphanDest = Join-Path $base "_ARCHIVES\orphelins_phase3"
    
    foreach ($o in $orphans) {
        $ext = [System.IO.Path]::GetExtension($o.Name).ToLower()
        $nameLower = $o.Name.ToLower()
        
        # Determiner destination selon type/nom
        $dest = $null
        
        switch -Regex ($ext) {
            '\.ka1$'  { $dest = Join-Path $base "02-PATCHES\divers" }
            '\.kaa$'  { $dest = Join-Path $base "02-PATCHES\divers" }
            '\.kca$'  { $dest = Join-Path $base "02-PATCHES\divers" }
            '\.kba$'  { $dest = Join-Path $base "02-PATCHES\divers" }
            '\.kpt$'  { $dest = Join-Path $base "02-PATCHES\divers" }
            '\.ksf$'  { $dest = Join-Path $base "03-SAMPLES-KSF" }
            '\.hfe$'  { $dest = Join-Path $base "05-GOTEK-HFE" }
            '\.mid$'  { $dest = Join-Path $base "06-MIDI-FILES" }
            '\.syx$'  { $dest = Join-Path $base "02-PATCHES\sysex" }
            '\.pdf$'  { $dest = Join-Path $base "01-DOCUMENTATION\manuels" }
            '\.zip$'  { $dest = Join-Path $base "_ARCHIVES\zips_restants" }
            '\.rar$'  { $dest = Join-Path $base "_ARCHIVES\zips_restants" }
            default   { $dest = $orphanDest }
        }
        
        $targetFile = Join-Path $dest $o.Name
        $relSrc = $o.Source.Replace("$base\", "")
        $relDst = $targetFile.Replace("$base\", "")
        
        if ($Execute) {
            try {
                if (-not (Test-Path $dest)) { New-Item $dest -ItemType Directory -Force | Out-Null }
                if (-not (Test-Path $targetFile)) {
                    Move-Item -LiteralPath $o.Source -Destination $targetFile
                    Write-Host "  MOVED: $relSrc -> $relDst" -ForegroundColor Green
                } else {
                    Write-Host "  SKIP (existe): $relDst" -ForegroundColor DarkYellow
                }
            } catch {
                Write-Host "  ERREUR: $relSrc - $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  [DRY] MOVE: $relSrc -> $relDst" -ForegroundColor Gray
        }
    }
}

# ============================================================
# Etape 5 : Supprimer les doublons confirmes
# ============================================================
if ($duplicates.Count -gt 0) {
    Write-Host "`n--- Suppression des doublons confirmes ---" -ForegroundColor Yellow
    
    $delCount = 0
    foreach ($d in $duplicates) {
        $relSrc = $d.Source.Replace("$base\", "")
        if ($Execute) {
            try {
                Remove-Item -LiteralPath $d.Source -Force
                $delCount++
            } catch {
                Write-Host "  ERREUR DEL: $relSrc - $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  [DRY] DEL: $relSrc" -ForegroundColor DarkGray
        }
    }
    if ($Execute) { Write-Host "  Supprimes: $delCount / $($duplicates.Count)" -ForegroundColor Green }
}

# ============================================================
# Etape 6 : Nettoyer les dossiers vides
# ============================================================
Write-Host "`n--- Nettoyage des dossiers vides ---" -ForegroundColor Yellow

$cleanedDirs = 0
$maxPasses = 10
for ($pass = 1; $pass -le $maxPasses; $pass++) {
    $emptyDirs = @()
    foreach ($od in $oldDirs) {
        $odPath = Join-Path $base $od
        if (Test-Path $odPath) {
            # Le dossier lui-meme est-il vide?
            $fileCount = (Get-ChildItem $odPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
            if ($fileCount -eq 0) {
                $emptyDirs += $odPath
            } else {
                # Chercher des sous-dossiers vides
                Get-ChildItem $odPath -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                    if ((Get-ChildItem $_.FullName -File -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0 -and
                        (Get-ChildItem $_.FullName -Directory -ErrorAction SilentlyContinue | Measure-Object).Count -eq 0) {
                        $emptyDirs += $_.FullName
                    }
                }
            }
        }
    }
    
    if ($emptyDirs.Count -eq 0) { break }
    
    foreach ($ed in $emptyDirs) {
        $relDir = $ed.Replace("$base\", "")
        if ($Execute) {
            try {
                Remove-Item $ed -Recurse -Force
                $cleanedDirs++
            } catch {
                Write-Host "  ERREUR DIR: $relDir - $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  [DRY] RMDIR: $relDir" -ForegroundColor DarkGray
        }
    }
}

if ($Execute) {
    Write-Host "  Dossiers supprimes: $cleanedDirs" -ForegroundColor Green
}

# ============================================================
# Etape 7 : Nettoyer les fichiers temporaires de planification
# ============================================================
$planFiles = @("_inventory.txt", "_remaining_kawai.txt", "_PLAN-DEPLACEMENT.csv", "_PLAN-PHASE2.csv")
Write-Host "`n--- Fichiers de planification ---" -ForegroundColor Yellow
foreach ($pf in $planFiles) {
    $pfPath = Join-Path $base $pf
    if (Test-Path $pfPath) {
        if ($Execute) {
            try {
                Remove-Item $pfPath -Force
                Write-Host "  DEL: $pf" -ForegroundColor Green
            } catch { Write-Host "  ERREUR: $pf - $_" -ForegroundColor Red }
        } else {
            Write-Host "  [DRY] DEL: $pf" -ForegroundColor DarkGray
        }
    }
}

# ============================================================
# Resume final
# ============================================================
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "RESUME PHASE 3" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Doublons: $($duplicates.Count) fichiers ($([math]::Round($dupSize / 1MB, 1)) Mo)" -ForegroundColor Green
Write-Host "Orphelins: $($orphans.Count) fichiers" -ForegroundColor Yellow
Write-Host "Erreurs: $($errors.Count)" -ForegroundColor $(if ($errors.Count -gt 0) {'Red'} else {'Gray'})

if (-not $Execute) {
    Write-Host "`nPour executer: .\reorganise-k5000-phase3.ps1 -Execute" -ForegroundColor White
}

Write-Host ""
