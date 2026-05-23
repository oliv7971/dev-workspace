$base = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"

$folders = @(
    "00-INBOX",

    "01-MIDI\CHANSON-FR",
    "01-MIDI\VARIETES-INTER",
    "01-MIDI\ROCK-POP",
    "01-MIDI\CLASSIQUE",
    "01-MIDI\JAZZ",
    "01-MIDI\MUSETTE-VALSE",
    "01-MIDI\ANNEES-80",
    "01-MIDI\TOONS-JINGLES",
    "01-MIDI\DRUMS-PERCUS",
    "01-MIDI\DIVERS",

    "02-KAR\CHANSON-FR",
    "02-KAR\VARIETES-INTER",
    "02-KAR\ROCK-POP",
    "02-KAR\CLASSIQUE",
    "02-KAR\JAZZ",
    "02-KAR\MUSETTE-VALSE",
    "02-KAR\ANNEES-80",
    "02-KAR\TOONS-JINGLES",
    "02-KAR\DIVERS",

    "03-KORG\PA4X\_STYLES-EXPORTES",
    "03-KORG\PA4X\_MIDI-A-CONVERTIR",
    "03-KORG\KRONOS\_SETS",
    "03-KORG\KRONOS\_MIDI-A-CONVERTIR",

    "99-A-TRIER"
)

foreach ($f in $folders) {
    $path = Join-Path $base $f
    if (-not (Test-Path -LiteralPath $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "  [CREE] $f"
    } else {
        Write-Host "  [EXISTE] $f"
    }
}

Write-Host ""
Write-Host "Structure créée dans : $base"
