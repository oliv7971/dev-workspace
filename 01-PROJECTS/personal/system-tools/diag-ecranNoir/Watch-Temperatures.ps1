<#
.SYNOPSIS
    Surveillance continue des temperatures des composants PC
.DESCRIPTION
    Echantillonne les temperatures CPU/GPU/disques a intervalle regulier
    et les enregistre dans un fichier CSV pour analyse post-crash.
    Sources tentees dans l'ordre :
      1. LibreHardwareMonitorLib.dll charge directement (le plus complet, sans WMI)
      2. LibreHardwareMonitor / OpenHardwareMonitor via WMI (si provider actif)
      3. MSAcpi_ThermalZoneTemperature (BIOS WMI) -> fallback minimal
.PARAMETER IntervalleSecondes
    Frequence d'echantillonnage en secondes (defaut : 5)
.PARAMETER DureeMinutes
    Duree totale de surveillance en minutes. 0 = infini (defaut : 0)
.PARAMETER FichierCSV
    Chemin du fichier CSV de sortie. Genere automatiquement si omis.
.PARAMETER LhmDllPath
    Chemin complet vers LibreHardwareMonitorLib.dll si non detecte automatiquement.
.PARAMETER SeuilAlerteC
    Temperature en degres Celsius declenchant une alerte console (defaut : 85)
.PARAMETER SeuilCritiqueC
    Temperature en degres Celsius consideree critique (defaut : 95)
.EXAMPLE
    .\Watch-Temperatures.ps1
    .\Watch-Temperatures.ps1 -IntervalleSecondes 10 -DureeMinutes 120
    .\Watch-Temperatures.ps1 -LhmDllPath "C:\Tools\LHM\LibreHardwareMonitorLib.dll"
.NOTES
    Pour des donnees completes (CPU, GPU, NVMe) sans WMI provider :
      1. Telechargez LibreHardwareMonitor (zip portable, sans installation) :
         https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases
      2. Decompressez l'archive
      3. Copiez LibreHardwareMonitorLib.dll dans le meme dossier que ce script
         OU passez son chemin avec -LhmDllPath
      LibreHardwareMonitor.exe n'a PAS besoin de tourner, la DLL seule suffit.
#>

[CmdletBinding()]
param(
    [int]    $IntervalleSecondes = 5,
    [int]    $DureeMinutes       = 0,
    [string] $FichierCSV = (Join-Path $PSScriptRoot ("Temperatures_{0}.csv" -f (Get-Date -Format 'yyyy-MM-dd_HHmmss'))),
    [string] $LhmDllPath = '',
    [int]    $SeuilAlerteC   = 85,
    [int]    $SeuilCritiqueC = 95
)

$ErrorActionPreference = 'SilentlyContinue'
Set-StrictMode -Off

# Avertissement si pas admin (certaines sources WMI necessitent les droits admin)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[INFO] Session non-admin : la DLL LHM fonctionnera, mais les sources WMI/ACPI peuvent etre indisponibles." -ForegroundColor DarkYellow
}

# ---------------------------------------------------------------------------
# Source 1 : LibreHardwareMonitorLib.dll directement (sans WMI provider)
# ---------------------------------------------------------------------------

function Find-LhmDll {
    param([string]$HintPath)
    $candidates = @(
        $HintPath,
        (Join-Path $PSScriptRoot 'LibreHardwareMonitorLib.dll'),
        (Join-Path $PSScriptRoot 'LHM\LibreHardwareMonitorLib.dll'),
        (Join-Path $env:ProgramFiles 'LibreHardwareMonitor\LibreHardwareMonitorLib.dll'),
        (Join-Path ${env:ProgramFiles(x86)} 'LibreHardwareMonitor\LibreHardwareMonitorLib.dll'),
        (Join-Path $env:LOCALAPPDATA 'LibreHardwareMonitor\LibreHardwareMonitorLib.dll')
    ) | Where-Object { $_ -and (Test-Path $_) }
    return $candidates | Select-Object -First 1
}

$lhmDll    = Find-LhmDll -HintPath $LhmDllPath
$lhmLoaded = $false

if ($lhmDll) {
    try {
        Add-Type -Path $lhmDll
        $lhmLoaded = $true
        Write-Host "[OK] LibreHardwareMonitorLib.dll charge : $lhmDll" -ForegroundColor Cyan
    } catch {
        Write-Host "[WARN] Echec chargement DLL : $_" -ForegroundColor Yellow
    }
}

$lhmComputer = $null
if ($lhmLoaded) {
    try {
        $lhmComputer = New-Object LibreHardwareMonitor.Hardware.Computer
        $lhmComputer.IsCpuEnabled         = $true
        $lhmComputer.IsGpuEnabled         = $true
        $lhmComputer.IsMotherboardEnabled = $true
        $lhmComputer.IsStorageEnabled     = $true
        $lhmComputer.IsNetworkEnabled     = $false
        $lhmComputer.IsMemoryEnabled      = $false
        $lhmComputer.Open()
    } catch {
        $lhmComputer = $null
        Write-Host "[WARN] Initialisation LHM echouee : $_" -ForegroundColor Yellow
    }
}

function Get-TempDll {
    if (-not $lhmComputer) { return @() }
    $results = [System.Collections.Generic.List[PSCustomObject]]::new()
    foreach ($hw in $lhmComputer.Hardware) {
        $hw.Update()
        foreach ($sensor in $hw.Sensors) {
            if ($sensor.SensorType -eq [LibreHardwareMonitor.Hardware.SensorType]::Temperature -and $null -ne $sensor.Value) {
                $results.Add([PSCustomObject]@{
                    Composant = $hw.Name
                    Capteur   = $sensor.Name
                    TempC     = [math]::Round([double]$sensor.Value, 1)
                    Source    = 'LHM-DLL'
                })
            }
        }
        foreach ($subhw in $hw.SubHardware) {
            $subhw.Update()
            foreach ($sensor in $subhw.Sensors) {
                if ($sensor.SensorType -eq [LibreHardwareMonitor.Hardware.SensorType]::Temperature -and $null -ne $sensor.Value) {
                    $results.Add([PSCustomObject]@{
                        Composant = "$($hw.Name) / $($subhw.Name)"
                        Capteur   = $sensor.Name
                        TempC     = [math]::Round([double]$sensor.Value, 1)
                        Source    = 'LHM-DLL'
                    })
                }
            }
        }
    }
    return $results
}

# ---------------------------------------------------------------------------
# Source 2 : WMI LHM / OHM (si provider WMI est actif)
# ---------------------------------------------------------------------------

function Get-TempWmi {
    $ns    = $null
    $label = ''
    if (Get-CimInstance -Namespace 'root/LibreHardwareMonitor' -ClassName '__Namespace' 2>$null) {
        $ns = 'root/LibreHardwareMonitor'; $label = 'LHM-WMI'
    } elseif (Get-CimInstance -Namespace 'root/OpenHardwareMonitor' -ClassName '__Namespace' 2>$null) {
        $ns = 'root/OpenHardwareMonitor'; $label = 'OHM-WMI'
    }
    if (-not $ns) { return @() }
    $sensors = Get-CimInstance -Namespace $ns -ClassName 'Sensor' -Filter "SensorType='Temperature'" 2>$null
    if (-not $sensors) { return @() }
    return $sensors | ForEach-Object {
        [PSCustomObject]@{
            Composant = $_.Parent -replace '.*/', ''
            Capteur   = $_.Name
            TempC     = [math]::Round($_.Value, 1)
            Source    = $label
        }
    }
}

# ---------------------------------------------------------------------------
# Source 3 : ACPI BIOS (fallback)
# ---------------------------------------------------------------------------

function Get-TempAcpi {
    $zones = Get-CimInstance -Namespace 'root/WMI' -ClassName 'MSAcpi_ThermalZoneTemperature' 2>$null
    if (-not $zones) { return @() }
    return $zones | ForEach-Object {
        $label = if ($_.InstanceName) { $_.InstanceName -replace '.*\\', '' } else { 'ThermalZone' }
        [PSCustomObject]@{
            Composant = 'BIOS/ACPI'
            Capteur   = $label
            TempC     = [math]::Round(($_.CurrentTemperature / 10) - 273.15, 1)
            Source    = 'ACPI'
        }
    }
}

# ---------------------------------------------------------------------------
# Determination de la source active
# ---------------------------------------------------------------------------

$wmiOk = (Get-CimInstance -Namespace 'root/LibreHardwareMonitor' -ClassName '__Namespace' 2>$null) -or
         (Get-CimInstance -Namespace 'root/OpenHardwareMonitor'  -ClassName '__Namespace' 2>$null)

$sourceMode = if ($lhmComputer) { 'DLL' } elseif ($wmiOk) { 'WMI' } else { 'ACPI' }

if ($sourceMode -eq 'ACPI') {
    Write-Host @"

[AVERTISSEMENT] Aucune source de temperature complete disponible.
  Seules les zones ACPI limitees seront lues.

  Pour un suivi complet (CPU / GPU / NVMe) - methode la plus simple :
    1. Telechargez LibreHardwareMonitor (zip portable, sans installation) :
       https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases
    2. Decompressez l'archive
    3. Copiez LibreHardwareMonitorLib.dll dans le meme dossier que ce script
    4. Relancez ce script (LibreHardwareMonitor.exe n'a PAS besoin de tourner)

"@ -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Affichage d'une ligne de temperature
# ---------------------------------------------------------------------------

function Write-TempLine {
    param([PSCustomObject]$Mesure)
    $t   = $Mesure.TempC
    $txt = "  {0,-35} {1,-28} {2,6:N1} degC" -f $Mesure.Composant, $Mesure.Capteur, $t
    if ($t -ge $SeuilCritiqueC) {
        Write-Host ($txt + "  !! CRITIQUE") -ForegroundColor Red
    } elseif ($t -ge $SeuilAlerteC) {
        Write-Host ($txt + "  /!\ CHAUD")   -ForegroundColor Yellow
    } else {
        Write-Host $txt -ForegroundColor Green
    }
}

# ---------------------------------------------------------------------------
# Preparation du fichier CSV
# ---------------------------------------------------------------------------

$csvDir = Split-Path $FichierCSV
if ($csvDir -and -not (Test-Path $csvDir)) {
    New-Item -ItemType Directory -Path $csvDir -Force | Out-Null
}
"Horodatage,Composant,Capteur,TempC,Source,Alerte" | Set-Content -Path $FichierCSV -Encoding UTF8
Write-Host "Fichier CSV : $FichierCSV" -ForegroundColor DarkGray

# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------

$heure_fin = if ($DureeMinutes -gt 0) { (Get-Date).AddMinutes($DureeMinutes) } else { [datetime]::MaxValue }
$nbEchantillons = 0
$alertesTotal   = 0
$critiquesTotal = 0

Write-Host ""
$dureeLabel = if ($DureeMinutes -gt 0) { "${DureeMinutes} min" } else { 'infinie' }
Write-Host "  Surveillance demarree | Source : $sourceMode | Intervalle : ${IntervalleSecondes}s | Duree : $dureeLabel" -ForegroundColor Cyan
Write-Host "  Ctrl+C pour arreter proprement" -ForegroundColor DarkGray

try {
    while ((Get-Date) -lt $heure_fin) {
        $horodatage = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        $nbEchantillons++

        $mesures = switch ($sourceMode) {
            'DLL'   { Get-TempDll }
            'WMI'   { Get-TempWmi }
            default { Get-TempAcpi }
        }
        if (-not $mesures -or $mesures.Count -eq 0) { $mesures = Get-TempAcpi }

        Write-Host ""
        Write-Host "  $horodatage  [echan. #$nbEchantillons]" -ForegroundColor White
        Write-Host ('-' * 75)

        if ($mesures -and $mesures.Count -gt 0) {
            $mesures | Sort-Object Composant, Capteur | ForEach-Object { Write-TempLine $_ }

            Write-Host ""
            $mesures | Group-Object Composant | Sort-Object Name | ForEach-Object {
                $max   = ($_.Group | Measure-Object TempC -Maximum).Maximum
                $color = if ($max -ge $SeuilCritiqueC) { 'Red' } elseif ($max -ge $SeuilAlerteC) { 'Yellow' } else { 'DarkGray' }
                Write-Host ("  max {0,-35} {1,6:N1} degC" -f $_.Name, $max) -ForegroundColor $color
            }

            foreach ($m in $mesures) {
                $alerte = if ($m.TempC -ge $SeuilCritiqueC) { 'CRITIQUE' } elseif ($m.TempC -ge $SeuilAlerteC) { 'CHAUD' } else { '' }
                if ($m.TempC -ge $SeuilAlerteC)   { $alertesTotal++ }
                if ($m.TempC -ge $SeuilCritiqueC) { $critiquesTotal++ }
                Add-Content -Path $FichierCSV -Encoding UTF8 -Value (
                    '"{0}","{1}","{2}",{3},"{4}","{5}"' -f
                        $horodatage,
                        ($m.Composant -replace '"', '""'),
                        ($m.Capteur   -replace '"', '""'),
                        $m.TempC, $m.Source, $alerte
                )
            }
        } else {
            Write-Host "  (aucune temperature disponible)" -ForegroundColor DarkGray
        }

        Start-Sleep -Seconds $IntervalleSecondes
    }
} catch [System.Management.Automation.StopUpstreamCommandsException] {
    # Ctrl+C propre
} finally {
    if ($lhmComputer) { try { $lhmComputer.Close() } catch {} }
    Write-Host ""
    Write-Host ('=' * 75) -ForegroundColor Cyan
    Write-Host "  SURVEILLANCE TERMINEE"
    Write-Host "  Echantillons          : $nbEchantillons"
    Write-Host "  Alertes chaleur (>= ${SeuilAlerteC} degC)    : $alertesTotal"
    Write-Host "  Alertes critiques (>= ${SeuilCritiqueC} degC) : $critiquesTotal"
    Write-Host "  CSV                   : $FichierCSV"
    Write-Host ('=' * 75) -ForegroundColor Cyan
}
