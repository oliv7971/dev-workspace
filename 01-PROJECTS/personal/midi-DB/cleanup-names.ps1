# cleanup-names.ps1
# Passe 1 : renomme les sous-dossiers de GROUPES ROCK (strip [site]- et _(N_midi...)_date)
# Passe 2 : aplatie les poupees russes (dossier contenant un seul sous-dossier, pas de fichiers)
param(
    [bool]$DryRun = $true,
    [bool]$Passe1 = $true,
    [bool]$Passe2 = $true
)

$base = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"
$mode = if ($DryRun) { "[SIMULATION]" } else { "[EXECUTION]" }

Write-Host ""
Write-Host "======================================="
Write-Host " NETTOYAGE NOMS/STRUCTURE - $mode"
Write-Host "======================================="

# -------------------------------------------------------
# PASSE 1 : Renommage GROUPES ROCK
# -------------------------------------------------------
if ($Passe1) {
Write-Host ""
Write-Host "--- PASSE 1 : Renommage sous-dossiers GROUPES ROCK ---"

$rockPath = "$base\01-MIDI\ROCK-POP\GROUPES ROCK"
$dirs = Get-ChildItem -LiteralPath $rockPath -Directory -EA SilentlyContinue

foreach ($dir in $dirs) {
    $oldName = $dir.Name
    # Supprime le prefixe [xxx.xxx.xxx]-
    $newName = $oldName -replace '^\[.*?\]-', ''
    # Supprime le suffixe _(N_midi_&_kar_files)_MM-YYYY et variantes (avec (1) etc.)
    $newName = $newName -replace '_\(\d+_midi.*?\)_\d{2}-\d{4}\(?[\d]*\)?$', ''
    # Supprime les parentheses numeriques de doublon restantes ex: (1)
    $newName = $newName -replace '\(\d+\)$', ''
    $newName = $newName.Trim('_').Trim()

    if ($newName -ne $oldName) {
        $newPath = Join-Path $rockPath $newName
        Write-Host "  RENOMMER : '$oldName'"
        Write-Host "          -> '$newName'"
        if (-not $DryRun) {
            # Si le dossier cible existe deja (doublon), fusionner
            if (Test-Path -LiteralPath $newPath) {
                Write-Host "    [FUSION] cible existe, deplacement du contenu..."
                Get-ChildItem -LiteralPath $dir.FullName | ForEach-Object {
                    Move-Item -LiteralPath $_.FullName -Destination $newPath -Force -EA SilentlyContinue
                }
                Remove-Item -LiteralPath $dir.FullName -Force -EA SilentlyContinue
            } else {
                Rename-Item -LiteralPath $dir.FullName -NewName $newName -EA SilentlyContinue
            }
        }
    }
}

} # fin Passe1

# -------------------------------------------------------
# PASSE 2 : Aplatissement poupees russes
# Detecte : dossier contenant exactement 1 sous-dossier et 0 fichiers
# -------------------------------------------------------
if ($Passe2) {
Write-Host ""
Write-Host "--- PASSE 2 : Aplatissement poupees russes ---"

$searchPaths = @(
    "$base\99-A-TRIER",
    "$base\01-MIDI\DIVERS",
    "$base\01-MIDI\VARIETES-INTER",
    "$base\01-MIDI\CHANSON-FR",
    "$base\01-MIDI\ROCK-POP",
    "$base\01-MIDI\JAZZ",
    "$base\01-MIDI\CLASSIQUE"
)

# Dossiers a exclure du traitement passe 2 (geres separement)
$excludeFromFlattening = @(
    "800000_Drum_Percussion_MIDI_Archive[6_19_15]"
)

foreach ($searchPath in $searchPaths) {
    # Plusieurs passes pour aplatir recursivement
    $maxPasses = 5
    for ($pass = 1; $pass -le $maxPasses; $pass++) {
        $found = $false
        $allDirs = Get-ChildItem -LiteralPath $searchPath -Recurse -Directory -Depth 4 -EA SilentlyContinue
        foreach ($dir in $allDirs) {
            # Ignorer les dossiers exclus (drums, archives speciales)
            if ($excludeFromFlattening | Where-Object { $dir.FullName -like "*$_*" }) { continue }
            $children    = Get-ChildItem -LiteralPath $dir.FullName -EA SilentlyContinue
            $subDirs     = $children | Where-Object { $_.PSIsContainer }
            $files       = $children | Where-Object { -not $_.PSIsContainer }

            if ($subDirs.Count -eq 1 -and $files.Count -eq 0) {
                $child   = $subDirs[0]
                $parent  = $dir.FullName
                Write-Host "  APLATIR : $($dir.FullName -replace [regex]::Escape($base), '')"
                Write-Host "         -> remonte '$($child.Name)' dans '$($dir.Parent.Name)'"
                if (-not $DryRun) {
                    $tmpName = $child.Name + "_tmp_" + (Get-Random)
                    $tmpPath = Join-Path $dir.Parent.FullName $tmpName
                    Move-Item -LiteralPath $child.FullName -Destination $tmpPath -Force -EA SilentlyContinue
                    Remove-Item -LiteralPath $parent -Force -Recurse -EA SilentlyContinue
                    Rename-Item -LiteralPath $tmpPath -NewName $child.Name -EA SilentlyContinue
                    $found = $true
                } else {
                    $found = $true
                }
            }
        }
        if (-not $found) { break }
        if ($DryRun) { break }  # En simulation une passe suffit
    }
}
} # fin Passe2

Write-Host ""
Write-Host "======================================="
Write-Host " FIN $mode"
if ($DryRun) {
    Write-Host " >> Aucun fichier touche - relancer avec -DryRun `$false <<"
}
Write-Host "======================================="
