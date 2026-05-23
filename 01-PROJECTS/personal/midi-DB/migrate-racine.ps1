# migrate-racine.ps1
# Migre les dossiers encore a la racine de 22-MUSIQUE MIDI KAR
# vers leur categorie definitive dans 01-MIDI ou 02-KAR
param([bool]$DryRun = $true)

$base = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"
$mode = if ($DryRun) { "[SIMULATION]" } else { "[EXECUTION]" }

Write-Host ""
Write-Host "======================================="
Write-Host " MIGRATION RACINE - $mode"
Write-Host "======================================="

# Table de migration dossiers : source (relatif a base) -> destination (relatif a base)
$migrations = @(
    # Midis generiques divers -> DIVERS
    @{ Src = "midis";                Dst = "01-MIDI\DIVERS\midis" },
    @{ Src = "_MIDI";                Dst = "01-MIDI\DIVERS\_MIDI" },

    # Themes de films/TV/jeux -> DIVERS
    @{ Src = "02-MIDI THEMES";       Dst = "01-MIDI\DIVERS\THEMES" },

    # Tubes divers -> VARIETES-INTER
    @{ Src = "03-MIDIS TUBES";       Dst = "01-MIDI\VARIETES-INTER\TUBES" },

    # Artistes (contenu mixte) -> VARIETES-INTER
    @{ Src = "10-MIDI ARTISTS";      Dst = "01-MIDI\VARIETES-INTER\ARTISTS" },

    # Classement par lettres -> DIVERS
    @{ Src = "21 MIDI PAR LETTRES";  Dst = "01-MIDI\DIVERS\PAR-LETTRES" },

    # Pros midi -> DIVERS
    @{ Src = "01-MIDI PROS";         Dst = "01-MIDI\DIVERS\MIDI-PROS" },

    # Midi Files generiques -> DIVERS
    @{ Src = "Midi Files";           Dst = "01-MIDI\DIVERS\Midi-Files" },

    # Presets MIDI -> KORG (presets pour synthes/arrangeurs)
    @{ Src = "Presets MIDI";         Dst = "03-KORG\Presets-MIDI" }
)

# Fichiers a la racine : Goldman/France -> CHANSON-FR, reste -> VARIETES-INTER, PDFs -> 00-INBOX
$rootFiles = @(
    @{ Pattern = "goldman|france|frenchcn|LE-FRANCE";  Dst = "01-MIDI\CHANSON-FR"; IsRegex = $true },
    @{ Pattern = "\.pdf$";                              Dst = "00-INBOX";            IsRegex = $true },
    @{ Pattern = ".*";                                  Dst = "01-MIDI\VARIETES-INTER"; IsRegex = $true }
)

foreach ($m in $migrations) {
    $srcPath = Join-Path $base $m.Src
    $dstPath = Join-Path $base $m.Dst

    if (-not (Test-Path -LiteralPath $srcPath)) {
        Write-Host "  [ABSENT]  '$($m.Src)' - ignore"
        continue
    }

    # Compter les fichiers (simulation seulement pour info)
    $n = (Get-ChildItem -LiteralPath $srcPath -Recurse -File -EA SilentlyContinue).Count

    Write-Host ""
    Write-Host "  DEPLACER : $($m.Src) ($n fichiers)"
    Write-Host "         -> $($m.Dst)"

    if (-not $DryRun) {
        $dstParent = Split-Path $dstPath -Parent
        if (-not (Test-Path -LiteralPath $dstParent)) {
            New-Item -ItemType Directory -Path $dstParent -Force -EA SilentlyContinue | Out-Null
        }

        if (Test-Path -LiteralPath $dstPath) {
            Write-Host "    [FUSION] destination existe, deplacement du contenu..."
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
Write-Host "--- Fichiers a la racine ---"

$rootFilesList = Get-ChildItem -LiteralPath $base -File -EA SilentlyContinue
foreach ($f in $rootFilesList) {
    # Determiner la destination selon le nom
    $dst = $null
    if ($f.Name -match '(?i)goldman|france|frenchchan|LE-FRANCE') {
        $dst = "01-MIDI\CHANSON-FR"
    } elseif ($f.Extension -match '(?i)\.pdf') {
        $dst = "00-INBOX"
    } else {
        $dst = "01-MIDI\VARIETES-INTER"
    }

    $dstPath = Join-Path $base $dst
    Write-Host "  $($f.Name) -> $dst"

    if (-not $DryRun) {
        if (-not (Test-Path -LiteralPath $dstPath)) {
            New-Item -ItemType Directory -Path $dstPath -Force -EA SilentlyContinue | Out-Null
        }
        Move-Item -LiteralPath $f.FullName -Destination $dstPath -Force -EA SilentlyContinue
    }
}

Write-Host ""
Write-Host "======================================="
Write-Host " FIN $mode"
if ($DryRun) {
    Write-Host " >> Aucun fichier touche - relancer avec -DryRun `$false <<"
}
Write-Host "======================================="
