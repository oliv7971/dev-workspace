<#
.SYNOPSIS
    Phase 2 - Nettoyage approfondi des données Kawai K5000S
.DESCRIPTION
    - Déplace les contenus restants (sounds, patches, etc.) vers la nouvelle structure
    - Identifie les doublons par hash et les supprime
    - Nettoie les dossiers vides
    - Sépare le site web Kawai France (hors-K5000)
    
    Mode dry-run par défaut.
.PARAMETER Execute
    Active l'exécution réelle
#>

param(
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$base = "D:\01-MUSIQUE\03-KAWAI"

function JP($a, $b) { Join-Path $a $b }

$moves = @()
$deletes = @()

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Phase 2 - Nettoyage approfondi K5000" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# ============================================================
# 1. KAWAI\sounds => Tri dans la nouvelle structure
# ============================================================
Write-Host "--- 1. KAWAI\sounds ---" -ForegroundColor Yellow

# sounds\K5000archive => 02-PATCHES\collections\K5000archive
$src = "$base\KAWAI\sounds\K5000archive"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\K5000archive") $rel; Cat="sounds-K5000archive" }
    }
}

# sounds\supplement40S => already in 02-PATCHES\banks\supplement40S (doublons)
# sounds\KAAtoKA1 => already in 02-PATCHES\collections (doublon)
# sounds\k5keditorA4 => already in 04-SOFTWARE\editors (doublon)

# sounds\collect1&2 => 02-PATCHES\collections\collect1_and_2
$src = "$base\KAWAI\sounds\collect1&2"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\collect1_and_2") $rel; Cat="sounds-collect" }
    }
}

# sounds\arp => 02-PATCHES\collections\arpeggio
$src = "$base\KAWAI\sounds\arp"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\arpeggio") $rel; Cat="sounds-arp" }
    }
}

# sounds\K5k ASL libs => 02-PATCHES\collections\K5k_ASL_libs
$src = "$base\KAWAI\sounds\K5k ASL libs"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\K5k_ASL_libs") $rel; Cat="sounds-ASL" }
    }
}

# sounds\K5k demo => 02-PATCHES\collections\K5k_demo
$src = "$base\KAWAI\sounds\K5k demo"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\K5k_demo") $rel; Cat="sounds-demo" }
    }
}

# sounds\K5KS300/K5KS404 => 02-PATCHES\collections\firmware_dumps
foreach ($fw in @("K5KS300","K5KS404")) {
    $src = "$base\KAWAI\sounds\$fw"
    if (Test-Path $src) {
        Get-ChildItem $src -Recurse -File | ForEach-Object {
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\firmware_dumps") $_.Name; Cat="sounds-firmware" }
        }
    }
}

# sounds\k5ksharc + k5ksharc_001 => 02-PATCHES\collections\k5ksharc
foreach ($sh in @("k5ksharc","k5ksharc_001")) {
    $src = "$base\KAWAI\sounds\$sh"
    if (Test-Path $src) {
        Get-ChildItem $src -Recurse -File | ForEach-Object {
            $rel = $_.FullName.Substring($src.Length)
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\k5ksharc") $rel; Cat="sounds-sharc" }
        }
    }
}

# sounds\K5kW Techno => 02-PATCHES\collections\K5kW_Techno
$src = "$base\KAWAI\sounds\K5kW Techno"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\K5kW_Techno") $rel; Cat="sounds-techno" }
    }
}

# sounds\convert => 04-SOFTWARE\tools\convert
$src = "$base\KAWAI\sounds\convert"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\tools") $_.Name; Cat="sounds-tools" }
    }
}

# Individual KA1 files at root of sounds\ => 02-PATCHES\collections\individual_patches
$indivSrc = Get-ChildItem "$base\KAWAI\sounds" -File | Where-Object { $_.Extension -in @(".KA1",".ka1",".kra",".KRA") }
foreach ($f in $indivSrc) {
    $moves += [PSCustomObject]@{ Source=$f.FullName; Target=JP (JP $base "02-PATCHES\collections\individual_patches") $f.Name; Cat="sounds-individual" }
}

# ZIP files in sounds\ => _ARCHIVES (deduplicated later)
$zipSrc = Get-ChildItem "$base\KAWAI\sounds" -File | Where-Object { $_.Extension -in @(".zip",".ZIP") }
foreach ($f in $zipSrc) {
    $moves += [PSCustomObject]@{ Source=$f.FullName; Target=JP (JP $base "_ARCHIVES") $f.Name; Cat="sounds-archives" }
}

# Small single-file subdirs (copernic, ep2080, haleluya, soloist, vocaliz, wavetable) => individual_patches
foreach ($sd in @("copernic","ep2080","haleluya","soloist","vocaliz","wavetable")) {
    $src = "$base\KAWAI\sounds\$sd"
    if (Test-Path $src) {
        Get-ChildItem $src -Recurse -File | ForEach-Object {
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\individual_patches") $_.Name; Cat="sounds-misc" }
        }
    }
}

# ============================================================
# 2. KAWAI\patchs => Analysis text files + pscan tool
# ============================================================
Write-Host "--- 2. KAWAI\patchs ---" -ForegroundColor Yellow

# .KA1.txt files = patch analysis dumps => 02-PATCHES\analysis
$src = "$base\KAWAI\patchs"
if (Test-Path $src) {
    Get-ChildItem $src -File | Where-Object { $_.Extension -eq ".txt" } | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\analysis") $_.Name; Cat="patchs-analysis" }
    }
    Get-ChildItem $src -File | Where-Object { $_.Extension -eq ".html" } | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\web-resources") $_.Name; Cat="patchs-html" }
    }
    Get-ChildItem $src -File | Where-Object { $_.Extension -eq ".exe" } | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\tools") $_.Name; Cat="patchs-tools" }
    }
}

# ============================================================
# 3. KAWAI\kawai = site web Kawai France => _HORS-K5000
# ============================================================
Write-Host "--- 3. KAWAI\kawai (site Kawai FR) ---" -ForegroundColor Yellow

$src = "$base\KAWAI\kawai"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "_HORS-K5000\site_kawai_france") $rel; Cat="hors-k5000-siteweb" }
    }
}

# ============================================================
# 4. KAWAI\kawai-k5 = docs Kawai K5 (ancien synth) => _HORS-K5000
# ============================================================
Write-Host "--- 4. KAWAI\kawai-k5 ---" -ForegroundColor Yellow

$src = "$base\KAWAI\kawai-k5"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "_HORS-K5000\kawai_k5_docs") $rel; Cat="hors-k5000-k5" }
    }
}

# ============================================================
# 5. KAWAI\mao => docs MAO
# ============================================================
$src = "$base\KAWAI\mao"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\mao") $_.Name; Cat="mao" }
    }
}

# ============================================================
# 6. KAWAI\K5000tip => 01-DOCUMENTATION\tips
# ============================================================
$src = "$base\KAWAI\K5000tip"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\tips") $_.Name; Cat="tips" }
    }
}

# ============================================================
# 7. KAWAI\sounddiver => 04-SOFTWARE\sounddiver
# ============================================================
$src = "$base\KAWAI\sounddiver"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\sounddiver\misc") $rel; Cat="sounddiver-misc" }
    }
}

# ============================================================
# 8. KAWAI\k5kleitr(1) => doublon de k5kleitr
# ============================================================
# Already moved k5kleitr - this is a duplicate. Will be caught by hash match.
$src = "$base\KAWAI\k5kleitr(1)"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\sound-designers\k5kleitr") $rel; Cat="sd-k5kleitr-dup" }
    }
}

# ============================================================
# 9. KAWAI\KAAtoKA1 => tools
# ============================================================
$src = "$base\KAWAI\KAAtoKA1"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\tools") $_.Name; Cat="tools" }
    }
}

# ============================================================
# 10. KAWAI\patch library / patch soft windows => patches/software
# ============================================================
$src = "$base\KAWAI\patch library"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\tools") $_.Name; Cat="patch-library" }
    }
}

# ============================================================
# 11. KAWAI\ root files (remaining PDFs, ZIPs, misc)
# ============================================================
Write-Host "--- 11. KAWAI root files ---" -ForegroundColor Yellow

$kawaiRootFiles = Get-ChildItem "$base\KAWAI" -File
foreach ($f in $kawaiRootFiles) {
    $target = switch -Regex ($f.Extension) {
        '\.pdf$' { JP (JP $base "01-DOCUMENTATION\manuels") $f.Name }
        '\.(zip|rar)$' { JP (JP $base "_ARCHIVES") $f.Name }
        '\.exe$' { JP (JP $base "04-SOFTWARE\tools") $f.Name }
        '\.htm$' { JP (JP $base "01-DOCUMENTATION\web-resources") $f.Name }
        '\.(txt|LIB)$' { JP (JP $base "01-DOCUMENTATION\notes") $f.Name }
        '\.(jpg|gif|png|mp3)$' { JP (JP $base "01-DOCUMENTATION\media") $f.Name }
        default { $null }
    }
    if ($target) {
        $moves += [PSCustomObject]@{ Source=$f.FullName; Target=$target; Cat="kawai-root" }
    }
}

# ============================================================
# 12. 04-KAWAI DISKS remaining content
# ============================================================
Write-Host "--- 12. 04-KAWAI DISKS ---" -ForegroundColor Yellow

# data => 02-PATCHES\collections\factory_data
$src = "$base\04-KAWAI DISKS\data"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\factory_data") $rel; Cat="disks-data" }
    }
}

# patches => 02-PATCHES\collections\disks_patches
$src = "$base\04-KAWAI DISKS\patches"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\disks_patches") $rel; Cat="disks-patches" }
    }
}

# programs => 02-PATCHES\collections\disks_programs
$src = "$base\04-KAWAI DISKS\programs"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\disks_programs") $rel; Cat="disks-programs" }
    }
}

# Kawai K5000 => big folder with KSF samples
$src = "$base\04-KAWAI DISKS\Kawai K5000"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $ext = $_.Extension.ToUpper()
        if ($ext -eq ".KSF") {
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "03-SAMPLES-KSF\Kawai_K5000_Disks") $rel; Cat="disks-KSF" }
        } else {
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\Kawai_K5000_Disks") $rel; Cat="disks-patches" }
        }
    }
}

# Kawai_K5000W_SupplementDisk (remaining) => 02-PATCHES\banks
$src = "$base\04-KAWAI DISKS\Kawai_K5000W_SupplementDisk"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\banks\Kawai_K5000W_SupplementDisk") $rel; Cat="disks-supplement" }
    }
}

# Remaining PDFs+ZIPs in 04-KAWAI DISKS root
Get-ChildItem "$base\04-KAWAI DISKS" -File | ForEach-Object {
    if ($_.Extension -eq ".pdf") {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\manuels") $_.Name; Cat="disks-pdf" }
    } elseif ($_.Extension -eq ".zip") {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "_ARCHIVES") $_.Name; Cat="disks-zip" }
    }
}

# ============================================================
# 13. 02-SOUNDS remaining
# ============================================================
Write-Host "--- 13. 02-SOUNDS ---" -ForegroundColor Yellow

# K5000archive => already mapped above, but this is another copy
$src = "$base\02-SOUNDS\K5000archive"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\K5000archive") $rel; Cat="sounds2-archive" }
    }
}

# k5000s support => 02-PATCHES\collections\k5000s_support
$src = "$base\02-SOUNDS\k5000s support"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\k5000s_support") $rel; Cat="sounds2-support" }
    }
}

# OB => 02-PATCHES\collections\OB
$src = "$base\02-SOUNDS\OB"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\OB") $_.Name; Cat="sounds2-OB" }
    }
}

# Remaining zip
Get-ChildItem "$base\02-SOUNDS" -File | ForEach-Object {
    $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "_ARCHIVES") $_.Name; Cat="sounds2-zip" }
}

# ============================================================
# 14. 01-KAWAI remaining (kawai = another copy of K5000archive + patches)
# ============================================================
Write-Host "--- 14. 01-KAWAI ---" -ForegroundColor Yellow

$src = "$base\01-KAWAI\kawai"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\_01kawai_kawai") $rel; Cat="01kawai-content" }
    }
}
# Root files
Get-ChildItem "$base\01-KAWAI" -File | ForEach-Object {
    $target = switch -Regex ($_.Extension) {
        '\.pdf$' { JP (JP $base "01-DOCUMENTATION\manuels") $_.Name }
        '\.(zip|rar)$' { JP (JP $base "_ARCHIVES") $_.Name }
        default { $null }
    }
    if ($target) { $moves += [PSCustomObject]@{ Source=$_.FullName; Target=$target; Cat="01kawai-root" } }
}

# ============================================================
# 15. 03-KAWAI remaining
# ============================================================
Write-Host "--- 15. 03-KAWAI ---" -ForegroundColor Yellow

$src = "$base\03-KAWAI\KAWAI"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\_03kawai_content") $rel; Cat="03kawai-content" }
    }
}
$src = "$base\03-KAWAI\k5000"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\manuels") $_.Name; Cat="03kawai-docs" }
    }
}
Get-ChildItem "$base\03-KAWAI" -File | ForEach-Object {
    $target = switch -Regex ($_.Extension) {
        '\.pdf$' { JP (JP $base "01-DOCUMENTATION\manuels") $_.Name }
        '\.(zip|rar)$' { JP (JP $base "_ARCHIVES") $_.Name }
        '\.exe$' { JP (JP $base "04-SOFTWARE\tools") $_.Name }
        default { $null }
    }
    if ($target) { $moves += [PSCustomObject]@{ Source=$_.FullName; Target=$target; Cat="03kawai-root" } }
}

# ============================================================
# 16. 04-KAWAI remaining
# ============================================================
Write-Host "--- 16. 04-KAWAI ---" -ForegroundColor Yellow

$src = "$base\04-KAWAI\kawai"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\_04kawai_content") $rel; Cat="04kawai-content" }
    }
}
Get-ChildItem "$base\04-KAWAI" -File | ForEach-Object {
    $target = switch -Regex ($_.Extension) {
        '\.pdf$' { JP (JP $base "01-DOCUMENTATION\manuels") $_.Name }
        '\.(zip|rar)$' { JP (JP $base "_ARCHIVES") $_.Name }
        default { $null }
    }
    if ($target) { $moves += [PSCustomObject]@{ Source=$_.FullName; Target=$target; Cat="04kawai-root" } }
}

# ============================================================
# 17. 03-SOFTWARE : garder seulement MidiQuestPro12 (déjà déplacé)
# ============================================================
Write-Host "--- 17. 03-SOFTWARE ---" -ForegroundColor Yellow

# SoundDiver folders
foreach ($sd in @("Emagic SoundDiver v3.0.5.4-OxYGeN","Emagic_SoundDiver_3.0.5.4")) {
    $src = "$base\03-SOFTWARE\$sd"
    if (Test-Path $src) {
        Get-ChildItem $src -Recurse -File | ForEach-Object {
            $rel = $_.FullName.Substring($src.Length)
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\sounddiver\SoundDiver_v3.0.5.4") $rel; Cat="sw-sounddiver" }
        }
    }
}
# Root files
Get-ChildItem "$base\03-SOFTWARE" -File | ForEach-Object {
    $target = switch -Regex ($_.Name) {
        'k5kcuis' { JP (JP $base "04-SOFTWARE\editors\k5kcuis") $_.Name }
        'SoundDiver' { JP (JP $base "_ARCHIVES") $_.Name }
        'MidiQuest' { JP (JP $base "_ARCHIVES\midiquest_old") $_.Name }  # ALL old versions to archive
        default { $null }
    }
    if ($target) { $moves += [PSCustomObject]@{ Source=$_.FullName; Target=$target; Cat="sw-root" } }
}

# ============================================================
# 18. Remaining small dirs (KAWAI\Emagic_SoundDiver, SoundDiver_Kawai_K5000_OEM, etc.)
# ============================================================
Write-Host "--- 18. Various remaining ---" -ForegroundColor Yellow

$src = "$base\KAWAI\Emagic_SoundDiver_3.0.5.4"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\sounddiver\SoundDiver_v3.0.5.4") $rel; Cat="kawai-sd" }
    }
}

$src = "$base\SoundDiver_Kawai_K5000_OEM"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length)
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "04-SOFTWARE\sounddiver\SoundDiver_K5000_OEM") $rel; Cat="sd-oem2" }
    }
}

# K5000 EAJ BANKS 1-8
$src = "$base\K5000 EAJ BANKS 1-8"
if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
        $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\banks\EAJ_BANKS_1-14") $_.Name; Cat="eaj-banks" }
    }
}

# KAWAI K5000 (docs - should be all dupes)
Get-ChildItem "$base\KAWAI K5000" -File -EA SilentlyContinue | ForEach-Object {
    $target = switch -Regex ($_.Extension) {
        '\.pdf$' { JP (JP $base "01-DOCUMENTATION\manuels") $_.Name }
        '\.(zip|rar)$' { JP (JP $base "_ARCHIVES") $_.Name }
        default { $null }
    }
    if ($target) { $moves += [PSCustomObject]@{ Source=$_.FullName; Target=$target; Cat="kawaik5000-root" } }
}

# 01-DOCUMENTATION KAWAI (remaining 3 files)
Get-ChildItem "$base\01-DOCUMENTATION KAWAI" -Recurse -File -EA SilentlyContinue | ForEach-Object {
    $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\manuels") $_.Name; Cat="olddoc" }
}

# Root loose files
foreach ($f in @("emagic-sounddiver-3.0.5.2 [1].exe","JSynthLib-0.20.0.jar")) {
    $fp = "$base\$f"
    if (Test-Path -LiteralPath $fp) {
        $moves += [PSCustomObject]@{ Source=$fp; Target=JP (JP $base "04-SOFTWARE\editors\JSynthLib") $f; Cat="root-sw" }
    }
}
# Root zips
Get-ChildItem $base -File -Depth 0 | Where-Object { $_.Extension -in @(".zip",".zipp") -and $_.DirectoryName -eq $base } | ForEach-Object {
    $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "_ARCHIVES") $_.Name; Cat="root-archive" }
}
# Root pdf
Get-ChildItem $base -File -Depth 0 | Where-Object { $_.Extension -eq ".pdf" -and $_.DirectoryName -eq $base } | ForEach-Object {
    $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "01-DOCUMENTATION\manuels") $_.Name; Cat="root-pdf" }
}

# collect2, collect2_2, kawaiSounds - small stragglers
foreach ($d in @("collect2","collect2_2","kawaiSounds")) {
    $src = "$base\$d"
    if (Test-Path $src) {
        Get-ChildItem $src -Recurse -File | ForEach-Object {
            $moves += [PSCustomObject]@{ Source=$_.FullName; Target=JP (JP $base "02-PATCHES\collections\collect2") $_.Name; Cat="straggler" }
        }
    }
}

# ============================================================
# EXECUTION
# ============================================================
Write-Host "`n=======================================" -ForegroundColor Cyan
Write-Host "Résumé Phase 2" -ForegroundColor Cyan
Write-Host "=======================================`n" -ForegroundColor Cyan

$moves | Group-Object Cat | Sort-Object Count -Descending | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count) fichiers" -ForegroundColor White
}
Write-Host "`n  TOTAL: $($moves.Count) opérations`n" -ForegroundColor Yellow

if (-not $Execute) {
    Write-Host "  *** MODE DRY-RUN ***" -ForegroundColor Magenta
    Write-Host "  Relancez avec -Execute pour effectuer.`n" -ForegroundColor Magenta
    $moves | Export-Csv -Path "$base\_PLAN-PHASE2.csv" -NoTypeInformation -Encoding UTF8
    Write-Host "  Plan exporté : $base\_PLAN-PHASE2.csv" -ForegroundColor Green
} else {
    Write-Host "  *** EXECUTION ***`n" -ForegroundColor Red
    $success = 0; $skipped = 0; $errors = 0

    foreach ($m in $moves) {
        try {
            if (-not (Test-Path -LiteralPath $m.Source)) { continue }
            $tDir = Split-Path $m.Target -Parent
            if (-not (Test-Path $tDir)) { New-Item $tDir -ItemType Directory -Force | Out-Null }
            
            if (Test-Path -LiteralPath $m.Target) {
                # Target exists - check hash
                $sh = (Get-FileHash -LiteralPath $m.Source -Algorithm MD5).Hash
                $th = (Get-FileHash -LiteralPath $m.Target -Algorithm MD5).Hash
                if ($sh -eq $th) {
                    $skipped++
                } else {
                    $bn = [IO.Path]::GetFileNameWithoutExtension($m.Target)
                    $ext = [IO.Path]::GetExtension($m.Target)
                    $alt = JP (Split-Path $m.Target -Parent) "${bn}_v2${ext}"
                    Move-Item -LiteralPath $m.Source -Destination $alt -Force
                    $success++
                }
            } else {
                Move-Item -LiteralPath $m.Source -Destination $m.Target -Force
                $success++
            }
        } catch {
            Write-Host "  ERR: $($m.Source) -> $_" -ForegroundColor Red
            $errors++
        }
    }

    Write-Host "`n  Déplacés: $success | Doublons ignorés: $skipped | Erreurs: $errors" -ForegroundColor $(if($errors){"Yellow"}else{"Green"})

    # Clean empty directories
    Write-Host "`n  Nettoyage des dossiers vides..." -ForegroundColor Yellow
    $cleaned = 0
    do {
        $emptyDirs = Get-ChildItem $base -Recurse -Directory | Where-Object { 
            (Get-ChildItem $_.FullName -Recurse -File -EA SilentlyContinue | Measure-Object).Count -eq 0 -and
            $_.FullName -notmatch "\\(01-DOCUMENTATION|02-PATCHES|03-SAMPLES|04-SOFTWARE|05-GOTEK|06-MIDI|_ARCHIVES|_HORS)" 
        }
        foreach ($ed in $emptyDirs) {
            try { Remove-Item $ed.FullName -Recurse -Force; $cleaned++ } catch {}
        }
    } while ($emptyDirs.Count -gt 0)
    Write-Host "  $cleaned dossiers vides supprimés" -ForegroundColor Green
}
