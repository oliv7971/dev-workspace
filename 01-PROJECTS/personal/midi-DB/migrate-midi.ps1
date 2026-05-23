# migrate-midi.ps1
# Param : -DryRun $true (simulation) | -DryRun $false (execution reelle)
param([bool]$DryRun = $true)

$base = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"

# Table de migration : source (relatif) => destination (relatif)
# Move-Item deplace le DOSSIER source DANS le dossier destination (conserve le nom d'origine)
$migrations = @(
    # -- Migrations directes (genre clairement identifie) --
    @{ Src="15 MUSETTE";                         Dst="01-MIDI\MUSETTE-VALSE" },
    @{ Src="11 MIDI FRANCAIS";                   Dst="01-MIDI\CHANSON-FR" },
    @{ Src="FRANCAIS";                           Dst="01-MIDI\CHANSON-FR" },
    @{ Src="GROUPES ROCK";                       Dst="01-MIDI\ROCK-POP" },
    @{ Src="midi international rock";            Dst="01-MIDI\ROCK-POP" },
    @{ Src="16 midis80";                         Dst="01-MIDI\ANNEES-80" },
    @{ Src="04 MIDIS CLASSIQUE";                 Dst="01-MIDI\CLASSIQUE" },
    @{ Src="52 Toons1000";                       Dst="01-MIDI\TOONS-JINGLES" },
    @{ Src="53 midi_menagerie";                  Dst="01-MIDI\DIVERS" },
    @{ Src="82-midifiles 4 korg";                Dst="03-KORG\PA4X\_MIDI-A-CONVERTIR" },
    @{ Src="23-MIDI KAR";                        Dst="02-KAR\DIVERS" },

    # -- Grands packs -> 99-A-TRIER --
    @{ Src="midifiles 2";                        Dst="99-A-TRIER" },
    @{ Src="800000_Drum_Percussion_MIDI_Archive[6_19_15]"; Dst="99-A-TRIER" },
    @{ Src="99 130000_Pop_Rock_Classical_";      Dst="99-A-TRIER" },
    @{ Src="51 Big Pack MIDI";                   Dst="99-A-TRIER" },
    @{ Src="8000 MIDI's Internacional Artists PACK"; Dst="99-A-TRIER" },
    @{ Src="Y2K";                                Dst="99-A-TRIER" },
    @{ Src="MIDI Pack Collection Vol.1-2 MIDI";  Dst="99-A-TRIER" },
    @{ Src="12 PACKS VARIETES INTER";            Dst="99-A-TRIER" },
    @{ Src="05_PlanetKeyboard_Bonus_PK_Midifiles"; Dst="99-A-TRIER" },
    @{ Src="98 355 midi's";                      Dst="99-A-TRIER" },
    @{ Src="22 VA2";                             Dst="99-A-TRIER" }
)

$mode = if ($DryRun) { "[SIMULATION]" } else { "[EXECUTION]" }
Write-Host ""
Write-Host "======================================="
Write-Host " MIGRATION MIDI - $mode"
Write-Host "======================================="
Write-Host ""

$ok = 0; $skip = 0; $err = 0

foreach ($m in $migrations) {
    $srcPath = Join-Path $base $m.Src
    $dstPath = Join-Path $base $m.Dst

    if (-not (Test-Path -LiteralPath $srcPath)) {
        Write-Host "  [ABSENT]  $($m.Src)"
        $skip++
        continue
    }

    Write-Host "  [DEPLACE]  $($m.Src)  =>  $($m.Dst)"

    if (-not $DryRun) {
        try {
            Move-Item -LiteralPath $srcPath -Destination $dstPath -Force -EA Stop
            $ok++
        } catch {
            Write-Host "    ERREUR : $_"
            $err++
        }
    } else {
        $ok++
    }
}

Write-Host ""
Write-Host "---------------------------------------"
Write-Host "  A deplacer : $ok   |   Absents : $skip   |   Erreurs : $err"
Write-Host "---------------------------------------"
if ($DryRun) {
    Write-Host ""
    Write-Host "  >> Mode SIMULATION - aucun fichier n'a ete touche <<"
    Write-Host "  >> Pour executer : .\migrate-midi.ps1 -DryRun `$false <<"
}
Write-Host ""
