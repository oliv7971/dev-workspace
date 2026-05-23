# migrate-from-trier.ps1
# Migre les dossiers de 99-A-TRIER vers leur categorie definitive
param([bool]$DryRun = $true)

$base = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"
$trier = "$base\99-A-TRIER"
$mode = if ($DryRun) { "[SIMULATION]" } else { "[EXECUTION]" }

Write-Host ""
Write-Host "======================================="
Write-Host " MIGRATION 99-A-TRIER - $mode"
Write-Host "======================================="

# Table de migration : source (relatif a 99-A-TRIER) -> destination (relatif a base)
$migrations = @(
    # Styles arranger Ketron -> KORG
    @{ Src = "Y2K";                              Dst = "03-KORG\Y2K-Ketron-Arranger" },

    # Arranger Variator IT -> KORG
    @{ Src = "vArrangerMidifiles_IT";            Dst = "03-KORG\vArranger-IT" },

    # Packs de production MIDI EDM/Synth -> DIVERS (pas assez specifique pour genre)
    @{ Src = "51 Big Pack MIDI";                 Dst = "01-MIDI\DIVERS\51-Big-Pack-MIDI" },

    # Pack neerlandais, varietes internationales -> VARIETES-INTER
    @{ Src = "MIDI Pack Collection Vol.1-2 MIDI"; Dst = "01-MIDI\VARIETES-INTER\MIDI-Pack-Collection-Vol1-2" },

    # Pack international artists -> VARIETES-INTER
    @{ Src = "8000 MIDI's Internacional Artists PACK"; Dst = "01-MIDI\VARIETES-INTER\8000-Internacional-Artists" },

    # Varietes inter (already named correctly) -> VARIETES-INTER
    @{ Src = "12 PACKS VARIETES INTER";          Dst = "01-MIDI\VARIETES-INTER\12-Packs-Varietes-Inter" },

    # PlanetKeyboard bonus -> DIVERS
    @{ Src = "05_PlanetKeyboard_Bonus_PK_Midifiles"; Dst = "01-MIDI\DIVERS\PlanetKeyboard-Bonus" },

    # 355 midi's divers -> DIVERS (a affiner plus tard)
    @{ Src = "98 355 midi's";                    Dst = "01-MIDI\DIVERS\355-midis" },

    # Archive 130000 (issue du flattening de midifiles 2) -> DIVERS\GRANDES-ARCHIVES
    @{ Src = "130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]"; Dst = "01-MIDI\DIVERS\130000-Archive" },

    # Archive 130000 doublon (issue de 99 130000_Pop_Rock_Classical_) -> DIVERS\GRANDES-ARCHIVES
    @{ Src = "99 130000_Pop_Rock_Classical_";    Dst = "01-MIDI\DIVERS\99-130000-Archive" }
)

foreach ($m in $migrations) {
    $srcPath = Join-Path $trier $m.Src
    $dstPath = Join-Path $base  $m.Dst

    if (-not (Test-Path -LiteralPath $srcPath)) {
        Write-Host "  [ABSENT]  '$($m.Src)' - ignore"
        continue
    }

    Write-Host ""
    Write-Host "  DEPLACER : $($m.Src)"
    Write-Host "         -> $($m.Dst)"

    if (-not $DryRun) {
        # Creer le dossier parent si necessaire
        $dstParent = Split-Path $dstPath -Parent
        if (-not (Test-Path -LiteralPath $dstParent)) {
            New-Item -ItemType Directory -Path $dstParent -Force -EA SilentlyContinue | Out-Null
        }

        if (Test-Path -LiteralPath $dstPath) {
            Write-Host "    [FUSION] destination existe deja, deplacement du contenu..."
            Get-ChildItem -LiteralPath $srcPath | ForEach-Object {
                Move-Item -LiteralPath $_.FullName -Destination $dstPath -Force -EA SilentlyContinue
            }
            Remove-Item -LiteralPath $srcPath -Force -Recurse -EA SilentlyContinue
        } else {
            Move-Item -LiteralPath $srcPath -Destination $dstPath -EA Stop
        }
        Write-Host "    [OK]"
    }
}

Write-Host ""
Write-Host "======================================="
Write-Host " FIN $mode"
if ($DryRun) {
    Write-Host " >> Aucun fichier touche - relancer avec -DryRun `$false <<"
}
Write-Host "======================================="
