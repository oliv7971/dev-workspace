#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Corrige les erreurs WHEA PCIe "Replay Timer Timeout" sur Intel Wireless-AC 7265
.DESCRIPTION
    L'Intel 7265 sur le GL552VW génère des erreurs WHEA (CorrectableErrorStatus=0x1000)
    dues à l'ASPM (PCIe Active State Power Management) qui endort la carte trop agressivement.
    Ce script désactive les options d'économie d'énergie PCIe côté Windows.
.NOTES
    A exécuter en administrateur. Un redémarrage est nécessaire après.
#>

$ErrorActionPreference = 'SilentlyContinue'

Write-Host "=== Fix WHEA PCIe - Intel Wireless-AC 7265 ===" -ForegroundColor Cyan
Write-Host "GL552VW - CorrectableErrorStatus 0x1000 (Replay Timer Timeout)" -ForegroundColor DarkGray
Write-Host ""

# -----------------------------------------------------------------------
# 1. Trouver la clé registre du driver Intel WiFi 7265
# -----------------------------------------------------------------------
Write-Host "[1] Recherche du driver Intel WiFi dans le registre..." -ForegroundColor Yellow
$netClassKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
$wifiKey = $null

Get-ChildItem $netClassKey -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $desc = (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).DriverDesc
        if ($desc -match 'Intel.*7265|Intel.*Wireless-AC') {
            $wifiKey = $_.PSPath
        }
    } catch {}
}

if (-not $wifiKey) {
    Write-Host "  [!] Driver Intel 7265 non trouve dans le registre." -ForegroundColor Red
    Write-Host "      Verifiez que le driver Intel WiFi est installe." -ForegroundColor Red
} else {
    Write-Host "  -> Cle trouvee : $wifiKey" -ForegroundColor Green

    # Desactiver Selective Suspend (permet au bus PCIe de "dormir" -> cause les timeouts)
    New-ItemProperty -Path $wifiKey -Name "EnableSelectiveSuspend" -Value 0 -PropertyType DWord -Force | Out-Null
    Write-Host "  -> EnableSelectiveSuspend = 0 (OFF)" -ForegroundColor Green

    # MIMO Power Save -> 3 = Disabled
    New-ItemProperty -Path $wifiKey -Name "MIMOPowerSaveMode" -Value 3 -PropertyType DWord -Force | Out-Null
    Write-Host "  -> MIMOPowerSaveMode = 3 (Disabled)" -ForegroundColor Green

    # System Idle Power Saver -> 0 = Disabled
    New-ItemProperty -Path $wifiKey -Name "ITHIdleSavingModeEnabled" -Value 0 -PropertyType DWord -Force | Out-Null
    Write-Host "  -> ITHIdleSavingModeEnabled = 0 (Disabled)" -ForegroundColor Green
}

Write-Host ""

# -----------------------------------------------------------------------
# 2. Désactiver PCIe Link State Power Management sur tous les plans
# -----------------------------------------------------------------------
Write-Host "[2] Desactivation du PCIe ASPM dans les plans d'alimentation..." -ForegroundColor Yellow

$pciSubGroup  = "381b4222-f694-41f0-9685-ff5bb260df2e"  # PCI Express
$pciSetting   = "dd848b2a-8a1d-451f-9e18-c8a8754c4f3e"  # Link State Power Management

$plans = powercfg /list | Select-String -Pattern '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
foreach ($line in $plans) {
    $guid = ([regex]::Match($line, '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')).Value
    if (-not $guid) { continue }

    # Vérifier si ce plan a le sous-groupe PCIe (powercfg retourne exit code 1 si absent)
    $query = & powercfg /query $guid $pciSubGroup $pciSetting 2>&1
    if ($LASTEXITCODE -eq 0) {
        powercfg /setacvalueindex $guid $pciSubGroup $pciSetting 0 2>&1 | Out-Null
        powercfg /setdcvalueindex $guid $pciSubGroup $pciSetting 0 2>&1 | Out-Null
        Write-Host "  -> Plan $guid : PCIe ASPM = 0 (Off)" -ForegroundColor Green
    } else {
        Write-Host "  -> Plan $guid : Parametre PCIe ASPM absent (plan Hautes perf. = deja OK)" -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------
# 3. Désactiver Device Idle pour le WiFi via WDF (si applicable)
# -----------------------------------------------------------------------
Write-Host ""
Write-Host "[3] Parametre AllowIdleIrpInD3 sur le peripherique WiFi..." -ForegroundColor Yellow

$devEnumKey = "HKLM:\SYSTEM\CurrentControlSet\Enum\PCI\VEN_8086&DEV_095A&SUBSYS_50108086&REV_59"
$devInstances = Get-ChildItem $devEnumKey -ErrorAction SilentlyContinue

foreach ($inst in $devInstances) {
    $wdfPath = Join-Path $inst.PSPath "Device Parameters\WDF"
    try {
        if (-not (Test-Path $wdfPath)) {
            New-Item -Path $wdfPath -Force | Out-Null
        }
        New-ItemProperty -Path $wdfPath -Name "IdleInWorkingState" -Value 0 -PropertyType DWord -Force | Out-Null
        New-ItemProperty -Path $wdfPath -Name "WakeFromSleepSupported" -Value 0 -PropertyType DWord -Force | Out-Null
        Write-Host "  -> IdleInWorkingState = 0 et WakeFromSleepSupported = 0" -ForegroundColor Green
    } catch {
        Write-Host "  -> Chemin WDF non applicable pour cette instance." -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------
# 4. Résumé et prochaines étapes
# -----------------------------------------------------------------------
Write-Host ""
Write-Host "=== Terminé ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Actions appliquees :" -ForegroundColor White
Write-Host "  - Selective Suspend desactive (driver Intel 7265)" -ForegroundColor Gray
Write-Host "  - PCIe ASPM desactive dans les plans alimentation" -ForegroundColor Gray
Write-Host "  - WDF Idle desactive pour le peripherique WiFi" -ForegroundColor Gray
Write-Host ""
Write-Host "A faire manuellement :" -ForegroundColor Yellow
Write-Host "  1. Redemarrer Windows" -ForegroundColor White
Write-Host "  2. Gestionnaire de peripheriques -> Intel Dual Band Wireless-AC 7265" -ForegroundColor White
Write-Host "       -> Proprietes -> Onglet 'Gestion de l'alimentation'" -ForegroundColor White
Write-Host "       -> DECOCHER 'Autoriser l ordinateur a eteindre ce peripherique...'" -ForegroundColor White
Write-Host "  3. Dans l'onglet 'Avance' du meme driver :" -ForegroundColor White
Write-Host "       -> 'System Idle Power Saver' -> Disabled" -ForegroundColor White
Write-Host "       -> 'U-APSD support' -> Disabled" -ForegroundColor White
Write-Host ""
Write-Host "BIOS GL552VW - pour desactiver les C-States (optionnel) :" -ForegroundColor Yellow
Write-Host "  F2 au demarrage -> F7 (Advanced Mode)" -ForegroundColor White
Write-Host "  Advanced -> CPU Configuration -> CPU C States Support -> Disabled" -ForegroundColor White
Write-Host "  (si absent : Advanced -> Platform Misc Configuration -> PCI Express Native Power Mgmt)" -ForegroundColor White
Write-Host ""
Write-Host "Redemarrez maintenant pour appliquer les changements driver." -ForegroundColor Cyan
