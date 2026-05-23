<#
.SYNOPSIS
    Script de réorganisation des données Kawai K5000S
.DESCRIPTION
    Réorganise D:\01-MUSIQUE\03-KAWAI selon le plan défini dans PLAN-ORGANISATION.md
    
    ETAPES :
    1. Analyse des doublons par hash MD5
    2. Création de la nouvelle arborescence
    3. Déplacement des fichiers (mode dry-run par défaut)
    
    SECURITE : Le mode dry-run est activé par défaut. 
    Rien n'est déplacé/supprimé tant que -Execute n'est pas passé.
.PARAMETER Execute
    Active le mode exécution réelle (par défaut = dry-run, affiche uniquement ce qui serait fait)
.PARAMETER SourceRoot
    Chemin racine des données Kawai (défaut: D:\01-MUSIQUE\03-KAWAI)
.EXAMPLE
    .\reorganise-k5000.ps1                    # Dry run - analyse uniquement
    .\reorganise-k5000.ps1 -Execute           # Exécution réelle
#>

param(
    [switch]$Execute,
    [string]$SourceRoot = "D:\01-MUSIQUE\03-KAWAI"
)

$ErrorActionPreference = "Stop"

# --- Configuration ---
$NewRoot = $SourceRoot  # On réorganise sur place

$TargetStructure = @{
    "01-DOCUMENTATION"          = @("manuels", "guides", "tips", "web-resources")
    "02-PATCHES"                = @("factory\v1", "factory\v3", "banks\EAJ_BANKS_1-14", "banks\supplement40S", "banks\Kawai_K5000W_SupplementDisk", "collections\collect2", "collections\K5000archive", "collections\alternateSoundCollection", "collections\Kawai_K5000_Ugo", "sound-designers")
    "03-SAMPLES-KSF"            = @("K5000_Wizoo_Disk")
    "04-SOFTWARE"               = @("editors\k5keditor_v0.75", "editors\k5keditor_v0.77.2", "editors\k5keditor_A4", "editors\k5kcuis", "editors\JSynthLib", "sounddiver\SoundDiver_K5000_OEM", "sounddiver\SoundDiver_v3.0.5.4", "midiquest", "drivers\usb_midi_driver")
    "05-GOTEK-HFE"              = @()
    "06-MIDI-FILES"             = @()
    "_ARCHIVES"                 = @()
    "_HORS-K5000"               = @("kawai_cl36", "kawai_ex_pro")
}

# Sound designers list (from KAWAI\ folder)
$SoundDesigners = @("k5kbass","k5kcarty","k5kchris","k5kgeof","k5khansn","k5kisvah","k5kjensg","k5kkenji","k5kleitr","k5kmattj","k5kmkniat","k5knicho","k5koldk","k5kpfava","k5kphonk","k5krobrt","k5ksasch","k5ksumma","k5ktaylr","k5kwall","k5kwesj","k5kxaza","k5kyitz2")

# ============================================================
# PHASE 1 : Analyse des doublons
# ============================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "PHASE 1 : Analyse des doublons par hash" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Calcul des hash MD5 de tous les fichiers... (peut prendre quelques minutes)" -ForegroundColor Yellow

$allFiles = Get-ChildItem -Path $SourceRoot -Recurse -File -ErrorAction SilentlyContinue
$totalCount = $allFiles.Count
Write-Host "  Nombre total de fichiers : $totalCount"

# Calculate hashes for files > 1KB to find meaningful duplicates
$hashTable = @{}
$duplicates = @()
$i = 0
foreach ($file in $allFiles) {
    $i++
    if ($i % 500 -eq 0) { Write-Host "  Progression : $i / $totalCount" }
    
    try {
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm MD5).Hash
        if (-not $hash) { continue }
        if ($hashTable.ContainsKey($hash)) {
            $hashTable[$hash] += @($file)
        } else {
            $hashTable[$hash] = @($file)
        }
    } catch {
        Write-Host "  ERREUR hash: $($file.FullName) - $_" -ForegroundColor Red
    }
}

$duplicateGroups = $hashTable.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 }
$duplicateCount = ($duplicateGroups | ForEach-Object { $_.Value.Count - 1 } | Measure-Object -Sum).Sum
$duplicateSize = ($duplicateGroups | ForEach-Object { 
    $sizes = $_.Value | Select-Object -Skip 1 | Measure-Object Length -Sum
    $sizes.Sum 
} | Measure-Object -Sum).Sum

Write-Host "`n  Groupes de doublons trouvés : $(($duplicateGroups | Measure-Object).Count)" -ForegroundColor Yellow
Write-Host "  Fichiers en double : $duplicateCount" -ForegroundColor Yellow
Write-Host "  Espace récupérable : $([math]::Round($duplicateSize / 1MB, 1)) Mo`n" -ForegroundColor Yellow

# Export duplicate report
$reportPath = Join-Path $SourceRoot "_RAPPORT-DOUBLONS.txt"
$reportContent = @("# Rapport de doublons - Kawai K5000S", "# Généré le $(Get-Date -Format 'yyyy-MM-dd HH:mm')", "# Groupes de doublons : $(($duplicateGroups | Measure-Object).Count)", "# Fichiers en double : $duplicateCount", "# Espace récupérable : $([math]::Round($duplicateSize / 1MB, 1)) Mo", "")

foreach ($group in ($duplicateGroups | Sort-Object { -($_.Value | Measure-Object Length -Sum).Sum })) {
    $size = $group.Value[0].Length
    $reportContent += "--- [$([math]::Round($size/1KB, 1)) KB] MD5: $($group.Key) ---"
    foreach ($f in $group.Value) {
        $reportContent += "  $($f.FullName)"
    }
    $reportContent += ""
}

if ($Execute) {
    $reportContent | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "  Rapport exporté : $reportPath" -ForegroundColor Green
} else {
    Write-Host "  [DRY-RUN] Rapport serait exporté : $reportPath" -ForegroundColor DarkGray
}

# ============================================================
# PHASE 2 : Mapping des déplacements
# ============================================================
Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "PHASE 2 : Plan de déplacement" -ForegroundColor Cyan
Write-Host "=======================================`n" -ForegroundColor Cyan

$moves = @()

# --- Documentation : PDFs ---
$pdfMappings = @{
    # Manuels
    "Kawai_K5000S_Manual.pdf"              = "01-DOCUMENTATION\manuels"
    "290082911-k5000s-manual.pdf"          = "01-DOCUMENTATION\manuels"  # doublon probable
    "kawai_k5000s_manual_1.pdf"            = "01-DOCUMENTATION\manuels"
    "kawai_k5000s_manual_2.pdf"            = "01-DOCUMENTATION\manuels"  # = Kawai_K5000S_Manual.pdf
    "kawai-k5000s-manual-2-476465.pdf"     = "01-DOCUMENTATION\manuels"  # doublon probable
    "k5000s-mode-d-emploi-fr-476472.pdf"   = "01-DOCUMENTATION\manuels"
    "Kawai_K5000R_manual.pdf"              = "01-DOCUMENTATION\manuels"
    "Kawai_K5000R_manual(1).pdf"           = "01-DOCUMENTATION\manuels"  # doublon
    "Kawai_K5000W_Manual.pdf"              = "01-DOCUMENTATION\manuels"
    "Kawai_K5000_MIDIImplementation.pdf"   = "01-DOCUMENTATION\manuels"
    "kawai_k5000_v2.0_midi.pdf"            = "01-DOCUMENTATION\manuels"
    "Kawai_K5000_ServiceManual.pdf"        = "01-DOCUMENTATION\manuels"
    "kawai_k5000s_r_w_service_manual.pdf"  = "01-DOCUMENTATION\manuels"
    "K5000x Service Manual.pdf"            = "01-DOCUMENTATION\manuels"
    # Guides Wizoo
    "kawai_k5000_wizoo_1_of_2.pdf"         = "01-DOCUMENTATION\guides"
    "kawai_k5000_wizoo_1_of_2-0001.pdf"    = "01-DOCUMENTATION\guides"   # doublon
    "82793724-kawai-k5000-wizoo-1-of-2.pdf"= "01-DOCUMENTATION\guides"   # doublon
    "kawai_k5000_wizoo_2_of_2.pdf"         = "01-DOCUMENTATION\guides"
}

# Find all PDFs and map them
$allPdfs = $allFiles | Where-Object { $_.Extension -eq ".pdf" }
foreach ($pdf in $allPdfs) {
    $targetDir = $pdfMappings[$pdf.Name]
    if ($targetDir) {
        $moves += [PSCustomObject]@{
            Source = $pdf.FullName
            Target = Join-Path (Join-Path $NewRoot $targetDir) $pdf.Name
            Category = "Documentation"
        }
    }
}

# --- Sound Designers (from KAWAI\ folder) ---
foreach ($sd in $SoundDesigners) {
    $sdPath = Join-Path $SourceRoot "KAWAI\$sd"
    if (Test-Path $sdPath) {
        $targetDir = Join-Path $NewRoot "02-PATCHES\sound-designers\$sd"
        $sdFiles = Get-ChildItem $sdPath -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $sdFiles) {
            $relPath = $f.FullName.Substring($sdPath.Length)
            $moves += [PSCustomObject]@{
                Source = $f.FullName
                Target = Join-Path $targetDir $relPath
                Category = "Patches-SoundDesigner"
            }
        }
    }
}

# --- Factory patches ---
$factoryMappings = @{
    "$SourceRoot\KAWAI\v1 factory"    = "02-PATCHES\factory\v1"
    "$SourceRoot\KAWAI\v3 factory"    = "02-PATCHES\factory\v3"
    "$SourceRoot\KAWAI\factoryBank"   = "02-PATCHES\factory\factoryBank"
}
foreach ($entry in $factoryMappings.GetEnumerator()) {
    if (Test-Path $entry.Key) {
        $files = Get-ChildItem $entry.Key -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $relPath = $f.FullName.Substring($entry.Key.Length)
            $moves += [PSCustomObject]@{
                Source = $f.FullName
                Target = Join-Path (Join-Path $NewRoot $entry.Value) $relPath
                Category = "Patches-Factory"
            }
        }
    }
}

# --- Banks ---
$bankMappings = @{
    "$SourceRoot\04-KAWAI DISKS\K5000_EAJ_BANKS_1-14" = "02-PATCHES\banks\EAJ_BANKS_1-14"
    "$SourceRoot\KAWAI\supplement40S"                   = "02-PATCHES\banks\supplement40S"
    "$SourceRoot\KAWAI\Kawai_K5000W_SupplementDisk"     = "02-PATCHES\banks\Kawai_K5000W_SupplementDisk"
}
foreach ($entry in $bankMappings.GetEnumerator()) {
    if (Test-Path $entry.Key) {
        $files = Get-ChildItem $entry.Key -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $relPath = $f.FullName.Substring($entry.Key.Length)
            $moves += [PSCustomObject]@{
                Source = $f.FullName
                Target = Join-Path (Join-Path $NewRoot $entry.Value) $relPath
                Category = "Patches-Banks"
            }
        }
    }
}

# --- Collections ---
$collectionMappings = @{
    "$SourceRoot\k5kcol2"                           = "02-PATCHES\collections\collect2"
    "$SourceRoot\KAWAI\alternateSoundCollection"    = "02-PATCHES\collections\alternateSoundCollection"
    "$SourceRoot\02-SOUNDS\Kawai_K5000_Ugo"         = "02-PATCHES\collections\Kawai_K5000_Ugo"
    "$SourceRoot\KAWAI\allka1"                      = "02-PATCHES\collections\allka1"
    "$SourceRoot\KAWAI\allkaa"                      = "02-PATCHES\collections\allkaa"
}
foreach ($entry in $collectionMappings.GetEnumerator()) {
    if (Test-Path $entry.Key) {
        $files = Get-ChildItem $entry.Key -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $relPath = $f.FullName.Substring($entry.Key.Length)
            $moves += [PSCustomObject]@{
                Source = $f.FullName
                Target = Join-Path (Join-Path $NewRoot $entry.Value) $relPath
                Category = "Patches-Collections"
            }
        }
    }
}

# --- Samples KSF (Wizoo) ---
$wizooPath = "$SourceRoot\KAWAI\K5000 Wizoo Disk"
if (Test-Path $wizooPath) {
    $files = Get-ChildItem $wizooPath -Recurse -File -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $relPath = $f.FullName.Substring($wizooPath.Length)
        $moves += [PSCustomObject]@{
            Source = $f.FullName
            Target = Join-Path (Join-Path $NewRoot "03-SAMPLES-KSF\K5000_Wizoo_Disk") $relPath
            Category = "Samples"
        }
    }
}

# --- Software ---
$softwareMappings = @{
    "$SourceRoot\01-KAWAI\k5keditorV0.75"                    = "04-SOFTWARE\editors\k5keditor_v0.75"
    "$SourceRoot\KAWAI\k5keditorV0.77.2"                     = "04-SOFTWARE\editors\k5keditor_v0.77.2"
    "$SourceRoot\KAWAI\k5keditorA4"                          = "04-SOFTWARE\editors\k5keditor_A4"
    "$SourceRoot\Emagic Sounddiver K5000 OEM"                = "04-SOFTWARE\sounddiver\SoundDiver_K5000_OEM"
    "$SourceRoot\Emagic_SoundDiver_3.0.5.4\Emagic SoundDiver 3.0.5.4" = "04-SOFTWARE\sounddiver\SoundDiver_v3.0.5.4"
    "$SourceRoot\KAWAI\usb_midi_driver"                      = "04-SOFTWARE\drivers\usb_midi_driver"
}
foreach ($entry in $softwareMappings.GetEnumerator()) {
    if (Test-Path $entry.Key) {
        $files = Get-ChildItem $entry.Key -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $relPath = $f.FullName.Substring($entry.Key.Length)
            $moves += [PSCustomObject]@{
                Source = $f.FullName
                Target = Join-Path (Join-Path $NewRoot $entry.Value) $relPath
                Category = "Software"
            }
        }
    }
}

# k5kcuis.exe - keep only one
$k5kcuis = Get-ChildItem $SourceRoot -Recurse -File -Filter "k5kcuis.exe" | Select-Object -First 1
if ($k5kcuis) {
    $moves += [PSCustomObject]@{
        Source = $k5kcuis.FullName
        Target = Join-Path $NewRoot "04-SOFTWARE\editors\k5kcuis\k5kcuis.exe"
        Category = "Software"
    }
}

# JSynthLib
$jsynthJar = Join-Path $SourceRoot "JSynthLib-0.20.0.jar"
if (Test-Path $jsynthJar) {
    $moves += [PSCustomObject]@{
        Source = $jsynthJar
        Target = Join-Path $NewRoot "04-SOFTWARE\editors\JSynthLib\JSynthLib-0.20.0.jar"
        Category = "Software"
    }
}

# MidiQuest - keep only the latest Pro x64 version
$mqPro = Join-Path $SourceRoot "03-SOFTWARE\MidiQuestPro12x64.0.0.exe"
if (Test-Path $mqPro) {
    $moves += [PSCustomObject]@{
        Source = $mqPro
        Target = Join-Path $NewRoot "04-SOFTWARE\midiquest\MidiQuestPro12x64.0.0.exe"
        Category = "Software"
    }
}

# --- Gotek HFE ---
$gotekPath = "$SourceRoot\Kawai K5000 Gotek Collection V1.0"
if (Test-Path $gotekPath) {
    $files = Get-ChildItem $gotekPath -Recurse -File -ErrorAction SilentlyContinue
    foreach ($f in $files) {
        $relPath = $f.FullName.Substring($gotekPath.Length)
        $moves += [PSCustomObject]@{
            Source = $f.FullName
            Target = Join-Path (Join-Path $NewRoot "05-GOTEK-HFE\Kawai_K5000_Gotek_Collection_V1.0") $relPath
            Category = "Gotek"
        }
    }
}

# --- MIDI files ---
$midiFiles = $allFiles | Where-Object { $_.Extension -in @(".mid", ".syx", ".mid2") }
foreach ($f in $midiFiles) {
    $moves += [PSCustomObject]@{
        Source = $f.FullName
        Target = Join-Path (Join-Path $NewRoot "06-MIDI-FILES") $f.Name
        Category = "MIDI"
    }
}

# --- Archives (ZIP/RAR) - collect unique copies ---
$archiveFiles = $allFiles | Where-Object { $_.Extension -in @(".zip", ".rar", ".zipp", ".gz", ".sit") }
$archiveHashes = @{}
foreach ($af in $archiveFiles) {
    try {
        $h = (Get-FileHash $af.FullName -Algorithm MD5).Hash
        if (-not $archiveHashes.ContainsKey($h)) {
            $archiveHashes[$h] = $af
            $moves += [PSCustomObject]@{
                Source = $af.FullName
                Target = Join-Path (Join-Path $NewRoot "_ARCHIVES") $af.Name
                Category = "Archive"
            }
        }
    } catch {}
}

# --- Hors-K5000 ---
$horsK5000 = @("$SourceRoot\02-SOUNDS\kawai_cl36", "$SourceRoot\02-SOUNDS\kawai_ex_pro")
foreach ($path in $horsK5000) {
    if (Test-Path $path) {
        $dirName = Split-Path $path -Leaf
        $files = Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $relPath = $f.FullName.Substring($path.Length)
            $moves += [PSCustomObject]@{
                Source = $f.FullName
                Target = Join-Path (Join-Path $NewRoot "_HORS-K5000\$dirName") $relPath
                Category = "Hors-K5000"
            }
        }
    }
}

# ============================================================
# PHASE 3 : Résumé et exécution
# ============================================================
Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "PHASE 3 : Résumé des actions" -ForegroundColor Cyan
Write-Host "=======================================`n" -ForegroundColor Cyan

$movesByCategory = $moves | Group-Object Category
foreach ($cat in $movesByCategory) {
    $catSize = ($cat.Group | ForEach-Object { 
        if (Test-Path $_.Source) { (Get-Item $_.Source).Length } else { 0 }
    } | Measure-Object -Sum).Sum
    Write-Host "  $($cat.Name): $($cat.Count) fichiers ($([math]::Round($catSize / 1MB, 1)) Mo)" -ForegroundColor White
}
Write-Host "`n  TOTAL : $($moves.Count) opérations de déplacement" -ForegroundColor Yellow

if (-not $Execute) {
    Write-Host "`n  *** MODE DRY-RUN ***" -ForegroundColor Magenta
    Write-Host "  Aucun fichier n'a été déplacé." -ForegroundColor Magenta
    Write-Host "  Relancez avec -Execute pour effectuer les déplacements.`n" -ForegroundColor Magenta
    
    # Save the move plan
    $planPath = Join-Path $SourceRoot "_PLAN-DEPLACEMENT.csv"
    $moves | Export-Csv -Path $planPath -NoTypeInformation -Encoding UTF8
    Write-Host "  Plan exporté : $planPath" -ForegroundColor Green
    Write-Host "  Rapport doublons : voir _RAPPORT-DOUBLONS.txt (sera généré avec -Execute)`n"
    
    # Show first 20 moves as preview
    Write-Host "  Aperçu des 20 premiers déplacements :" -ForegroundColor Gray
    $moves | Select-Object -First 20 | ForEach-Object {
        $src = $_.Source.Replace($SourceRoot, ".")
        $tgt = $_.Target.Replace($NewRoot, ".")
        Write-Host "    $src" -ForegroundColor DarkGray -NoNewline
        Write-Host " -> " -ForegroundColor Yellow -NoNewline
        Write-Host "$tgt" -ForegroundColor Green
    }
    if ($moves.Count -gt 20) {
        Write-Host "    ... et $($moves.Count - 20) de plus (voir le CSV)" -ForegroundColor DarkGray
    }
} else {
    Write-Host "`n  *** MODE EXECUTION ***" -ForegroundColor Red
    Write-Host "  Début des déplacements...`n" -ForegroundColor Red
    
    $success = 0
    $errors = 0
    
    foreach ($move in $moves) {
        try {
            $targetDir = Split-Path $move.Target -Parent
            if (-not (Test-Path $targetDir)) {
                New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
            }
            
            if (Test-Path $move.Source) {
                # Don't overwrite if target already exists
                if (-not (Test-Path $move.Target)) {
                    Move-Item -Path $move.Source -Destination $move.Target -Force
                    $success++
                } else {
                    # Target exists - check if same file
                    $srcHash = (Get-FileHash $move.Source -Algorithm MD5).Hash
                    $tgtHash = (Get-FileHash $move.Target -Algorithm MD5).Hash
                    if ($srcHash -eq $tgtHash) {
                        Write-Host "  DOUBLON IGNORÉ : $($move.Source)" -ForegroundColor DarkYellow
                    } else {
                        # Different file, rename with suffix
                        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($move.Target)
                        $ext = [System.IO.Path]::GetExtension($move.Target)
                        $newTarget = Join-Path (Split-Path $move.Target -Parent) "${baseName}_alt${ext}"
                        Move-Item -Path $move.Source -Destination $newTarget -Force
                        $success++
                    }
                }
            }
        } catch {
            Write-Host "  ERREUR : $($move.Source) -> $($move.Target) : $_" -ForegroundColor Red
            $errors++
        }
    }
    
    Write-Host "`n  Terminé !" -ForegroundColor Green
    Write-Host "  Succès : $success | Erreurs : $errors" -ForegroundColor $(if($errors -gt 0){"Yellow"}else{"Green"})
    
    # Generate duplicate report
    $reportContent | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "  Rapport des doublons : $reportPath"
}
