#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Diagnostic des écrans noirs / freezes Windows
.DESCRIPTION
    Analyse les journaux d'événements Windows pour identifier les causes
    possibles d'écrans noirs et de blocages système.
.NOTES
    Exécuter en tant qu'administrateur pour accéder à tous les logs.
#>

[CmdletBinding()]
param(
    [int]$HeuresAnalyse = 48,
    [string]$RapportPath = (Join-Path $PSScriptRoot ("Rapport-Diag_{0}.txt" -f (Get-Date -Format 'yyyy-MM-dd_HHmmss')))
)

$ErrorActionPreference = 'SilentlyContinue'

# --- Fonctions utilitaires ---
function Write-Section {
    param([string]$Title)
    $sep = '=' * 70
    $block = "`n$sep`n  $Title`n$sep"
    Write-Host $block -ForegroundColor Cyan
    $block
}

function Write-SubSection {
    param([string]$Title)
    $block = "`n--- $Title ---"
    Write-Host $block -ForegroundColor Yellow
    $block
}

function Format-EventEntry {
    param($Evt)
    $msg = $Evt.Message
    # Gérer le cas où Message est un tableau (ex: WHEA affiche System.Object[])
    if ($msg -is [array]) {
        $msg = $msg -join ' '
    }
    $msgLines = if ($msg -and $msg -notmatch '^System\.Object\[\]$') {
        ($msg -split "`n" | Select-Object -First 5 | ForEach-Object { $_.Trim() } | Where-Object { $_ }) -join "`n  "
    } else {
        # Tenter d'extraire les données depuis le XML de l'événement
        $fallback = '(pas de message lisible)'
        try {
            $xml = [xml]$Evt.ToXml()
            $dataNodes = $xml.Event.EventData.Data
            if ($dataNodes) {
                $parts = foreach ($d in $dataNodes) {
                    if ($d.Name -and $d.'#text') { "$($d.Name)=$($d.'#text')" }
                    elseif ($d.'#text') { $d.'#text' }
                }
                if ($parts) { $fallback = ($parts -join ', ') }
            }
        } catch {}
        $fallback
    }
    "[{0}] ID:{1} Source:{2}`n  {3}" -f $Evt.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'),
        $Evt.Id, $Evt.ProviderName, $msgLines
}

function Get-WheaDetails {
    param($Evt)
    try {
        $xml = [xml]$Evt.ToXml()
        $data = $xml.Event.EventData.Data
        $details = @()
        $pciDevice = $null
        $corrErrStatus = $null
        $uncorrErrStatus = $null
        foreach ($d in $data) {
            if ($d.'#text' -and $d.Name) {
                $details += "    $($d.Name) = $($d.'#text')"
                if ($d.Name -eq 'PrimaryDeviceName') { $pciDevice = $d.'#text' }
                if ($d.Name -eq 'CorrectableErrorStatus') { $corrErrStatus = $d.'#text' }
                if ($d.Name -eq 'UncorrectableErrorStatus') { $uncorrErrStatus = $d.'#text' }
            }
        }
        # Résolution du nom PnP du device fautif
        if ($pciDevice -match 'PCI\\(.+)') {
            $instanceId = $pciDevice -replace '^PCI\\','' -replace '\\.*',''
            $pnpDev = Get-PnpDevice | Where-Object { $_.InstanceId -match [regex]::Escape($instanceId) } | Select-Object -First 1
            if ($pnpDev) {
                $details = @("    >> DEVICE FAUTIF : $($pnpDev.FriendlyName) [$($pnpDev.Status)]") + $details
            }
        }
        # Décodage CorrectableErrorStatus (PCIe AER)
        if ($corrErrStatus -and $corrErrStatus -ne '0x0') {
            $val = [Convert]::ToInt64($corrErrStatus, 16)
            $corrMeanings = @()
            if ($val -band 0x0001) { $corrMeanings += 'Receiver Error' }
            if ($val -band 0x0040) { $corrMeanings += 'Bad TLP' }
            if ($val -band 0x0080) { $corrMeanings += 'Bad DLLP' }
            if ($val -band 0x0100) { $corrMeanings += 'Replay Num Rollover' }
            if ($val -band 0x1000) { $corrMeanings += 'Replay Timer Timeout' }
            if ($val -band 0x2000) { $corrMeanings += 'Advisory Non-Fatal Error' }
            if ($corrMeanings) {
                $details = @("    >> PCIe Correctable Errors : $($corrMeanings -join ', ')") + $details
            }
        }
        if ($uncorrErrStatus -and $uncorrErrStatus -ne '0x0') {
            $val = [Convert]::ToInt64($uncorrErrStatus, 16)
            $uncorrMeanings = @()
            if ($val -band 0x00010) { $uncorrMeanings += 'Data Link Protocol Error' }
            if ($val -band 0x01000) { $uncorrMeanings += 'Poisoned TLP' }
            if ($val -band 0x02000) { $uncorrMeanings += 'Flow Control Protocol Error' }
            if ($val -band 0x04000) { $uncorrMeanings += 'Completion Timeout' }
            if ($val -band 0x08000) { $uncorrMeanings += 'Completer Abort' }
            if ($val -band 0x10000) { $uncorrMeanings += 'Unexpected Completion' }
            if ($val -band 0x20000) { $uncorrMeanings += 'Receiver Overflow' }
            if ($val -band 0x40000) { $uncorrMeanings += 'Malformed TLP' }
            if ($val -band 0x80000) { $uncorrMeanings += 'ECRC Error' }
            if ($val -band 0x100000) { $uncorrMeanings += 'Unsupported Request' }
            if ($uncorrMeanings) {
                $details = @("    >> PCIe Uncorrectable Errors : $($uncorrMeanings -join ', ')") + $details
            }
        }
        if ($details.Count -gt 0) { return $details -join "`n" }
    } catch {}
    return $null
}

# --- Début du diagnostic ---
$rapport = @()
$dateDebut = (Get-Date).AddHours(-$HeuresAnalyse)

$rapport += Write-Section "DIAGNOSTIC ECRAN NOIR / FREEZE - $(Get-Date -Format 'dd/MM/yyyy HH:mm')"
$rapport += "Période analysée : dernières $HeuresAnalyse heures (depuis $($dateDebut.ToString('dd/MM/yyyy HH:mm')))"

# ============================================================
# 1. ARRÊTS INATTENDUS (Event ID 6008)
# ============================================================
$rapport += Write-Section "1. ARRETS INATTENDUS / REDEMARRAGES BRUTAUX"

$unexpectedShutdowns = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Id        = 6008
    StartTime = $dateDebut
} -MaxEvents 20 2>$null

if ($unexpectedShutdowns) {
    $rapport += ">> $($unexpectedShutdowns.Count) arrêt(s) inattendu(s) détecté(s) !"
    Write-Host ">> $($unexpectedShutdowns.Count) arrêt(s) inattendu(s) détecté(s) !" -ForegroundColor Red
    foreach ($evt in $unexpectedShutdowns) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun arrêt inattendu enregistré."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 2. KERNEL-POWER (Event ID 41) - Coupure brutale
# ============================================================
$rapport += Write-Section "2. KERNEL-POWER (coupures brutales)"

$kernelPower = Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Microsoft-Windows-Kernel-Power'
    Id           = 41
    StartTime    = $dateDebut
} -MaxEvents 20 2>$null

if ($kernelPower) {
    $rapport += ">> $($kernelPower.Count) événement(s) Kernel-Power 41 (= le système a redémarré sans arrêt propre)"
    Write-Host ">> $($kernelPower.Count) événement(s) Kernel-Power 41" -ForegroundColor Red
    foreach ($evt in $kernelPower) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun événement Kernel-Power 41."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 3. BUGCHECK / BSOD (Event ID 1001)
# ============================================================
$rapport += Write-Section "3. BUGCHECK / ECRAN BLEU (BSOD)"

$bugchecks = Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Microsoft-Windows-WER-SystemErrorReporting'
    Id           = 1001
    StartTime    = $dateDebut
} -MaxEvents 20 2>$null

if ($bugchecks) {
    $rapport += ">> $($bugchecks.Count) BSOD/BugCheck détecté(s) !"
    Write-Host ">> $($bugchecks.Count) BSOD/BugCheck détecté(s) !" -ForegroundColor Red
    foreach ($evt in $bugchecks) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun BugCheck/BSOD enregistré."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 4. PILOTES GRAPHIQUES (Display / GPU)
# ============================================================
$rapport += Write-Section "4. PROBLEMES GPU / PILOTES GRAPHIQUES"

# Display driver stopped responding (TDR) - Event 4101
$tdr = Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Display'
    StartTime    = $dateDebut
} -MaxEvents 30 2>$null

# Also check for nvlddmkm (NVIDIA) or atikmpag (AMD) errors
$gpuErrors = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = @(1, 2, 3)  # Critical, Error, Warning
    StartTime = $dateDebut
} -MaxEvents 500 2>$null | Where-Object {
    $_.ProviderName -match 'display|nvlddmkm|atikmdag|atikmpag|dxgkrnl|dxgmms|igfx|gpu|video' -or
    $_.Message -match 'display|gpu|graphi|video|render|TDR|nvlddmkm|atikmdag'
}

$gpuAll = @()
if ($tdr) { $gpuAll += $tdr }
if ($gpuErrors) { $gpuAll += $gpuErrors }
$gpuAll = $gpuAll | Sort-Object TimeCreated -Descending | Select-Object -Unique -First 20

if ($gpuAll) {
    $rapport += ">> $($gpuAll.Count) événement(s) liés au GPU/affichage"
    Write-Host ">> $($gpuAll.Count) événement(s) GPU/affichage" -ForegroundColor Red
    foreach ($evt in $gpuAll) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucune erreur GPU/affichage détectée."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 5. ERREURS DISQUE / STOCKAGE
# ============================================================
$rapport += Write-Section "5. ERREURS DISQUE / STOCKAGE"

$diskErrors = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = @(1, 2, 3)
    StartTime = $dateDebut
} -MaxEvents 500 2>$null | Where-Object {
    $_.ProviderName -match 'disk|ntfs|storahci|stornvme|volmgr|partition|iastor|vhdmp' -or
    $_.Message -match 'disque|disk|I/O|secteur|bad block|storage'
}

if ($diskErrors) {
    $rapport += ">> $($diskErrors.Count) erreur(s) disque détectée(s)"
    Write-Host ">> $($diskErrors.Count) erreur(s) disque" -ForegroundColor Red
    foreach ($evt in ($diskErrors | Select-Object -First 15)) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucune erreur disque détectée."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 6. ERREURS MÉMOIRE (RAM)
# ============================================================
$rapport += Write-Section "6. ERREURS MEMOIRE (RAM)"

$memErrors = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = @(1, 2, 3)
    StartTime = $dateDebut
} -MaxEvents 500 2>$null | Where-Object {
    $_.ProviderName -match 'MemoryDiagnostics|WHEA' -or
    $_.Message -match 'memory|mémoire|parity|hardware error|machine check'
}

if ($memErrors) {
    $rapport += ">> $($memErrors.Count) erreur(s) mémoire détectée(s) !"
    Write-Host ">> $($memErrors.Count) erreur(s) mémoire" -ForegroundColor Red
    foreach ($evt in ($memErrors | Select-Object -First 15)) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucune erreur mémoire détectée."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# -- Résultats du dernier diagnostic mémoire Windows (mdsched.exe) --
$rapport += Write-SubSection "Dernier diagnostic memoire Windows (mdsched.exe)"

$mdsched = Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    Id      = 1101
} -MaxEvents 1 2>$null

if ($mdsched) {
    $mdMsg = $mdsched.Message
    $mdDate = $mdsched.TimeCreated.ToString('dd/MM/yyyy HH:mm:ss')
    if ($mdMsg -match 'aucune erreur|no.*(error|problem)') {
        $line = "mdsched ($mdDate) : AUCUNE ERREUR detectee - RAM OK"
        $rapport += $line
        Write-Host $line -ForegroundColor Green
    } elseif ($mdMsg -match 'erreur|error|problem') {
        $line = "mdsched ($mdDate) : ERREURS DETECTEES !"
        $rapport += $line
        Write-Host $line -ForegroundColor Red
        $rapport += "  $mdMsg"
    } else {
        $line = "mdsched ($mdDate) : $mdMsg"
        $rapport += $line
        Write-Host $line
    }
} else {
    # Tenter aussi le log dédié MemoryDiagnostics-Results
    $mdschedDebug = Get-WinEvent -LogName 'Microsoft-Windows-MemoryDiagnostics-Results/Debug' -MaxEvents 1 2>$null
    if ($mdschedDebug) {
        $mdDate = $mdschedDebug.TimeCreated.ToString('dd/MM/yyyy HH:mm:ss')
        $line = "mdsched ($mdDate) : Résultat trouvé (log Debug). Vérifiez l'Observateur d'événements."
        $rapport += $line
        Write-Host $line -ForegroundColor Yellow
    } else {
        $msg = "Aucun résultat mdsched trouvé. Lancez 'mdsched.exe' pour tester la RAM (redémarrage requis)."
        $rapport += $msg
        Write-Host $msg -ForegroundColor Yellow
    }
}

# ============================================================
# 7. WHEA (Windows Hardware Error Architecture)
# ============================================================
$rapport += Write-Section "7. ERREURS MATERIELLES (WHEA)"

$whea = Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Microsoft-Windows-WHEA-Logger'
    StartTime    = $dateDebut
} -MaxEvents 30 2>$null

if ($whea) {
    $rapport += ">> $($whea.Count) erreur(s) matérielle(s) WHEA"
    Write-Host ">> $($whea.Count) erreur(s) WHEA" -ForegroundColor Red

    # Résumé par device fautif
    $wheaDevices = @{}
    foreach ($evt in $whea) {
        try {
            $xml = [xml]$evt.ToXml()
            $pdn = ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'PrimaryDeviceName' }).'#text'
            if ($pdn) {
                $shortId = ($pdn -replace 'PCI\\','') -replace '&SUBSYS.*',''
                if (-not $wheaDevices[$shortId]) { $wheaDevices[$shortId] = 0 }
                $wheaDevices[$shortId]++
            }
        } catch {}
    }
    if ($wheaDevices.Count -gt 0) {
        $rapport += "  Devices PCIe sources d'erreurs :"
        foreach ($kv in ($wheaDevices.GetEnumerator() | Sort-Object Value -Descending)) {
            $pnp = Get-PnpDevice | Where-Object { $_.InstanceId -match [regex]::Escape($kv.Key) } | Select-Object -First 1
            $devName = if ($pnp) { $pnp.FriendlyName } else { $kv.Key }
            $line = "    - $devName : $($kv.Value) erreur(s)"
            $rapport += $line
            Write-Host $line -ForegroundColor Red
        }
    }

    foreach ($evt in $whea) {
        $rapport += Format-EventEntry $evt
        $details = Get-WheaDetails $evt
        if ($details) {
            $rapport += "  Détails WHEA :"
            $rapport += $details
        }
    }

    # Conseils PCIe si Replay Timer Timeout détecté
    $hasReplayTimeout = $whea | ForEach-Object {
        try { $xml=[xml]$_.ToXml(); ($xml.Event.EventData.Data | Where-Object { $_.Name -eq 'CorrectableErrorStatus' }).'#text' } catch {}
    } | Where-Object { $_ -eq '0x1000' }
    if ($hasReplayTimeout) {
        $advice = @(
            "  [CONSEIL - PCIe Replay Timer Timeout detecte]",
            "  1. Gestionnaire de perif -> device fautif -> Alimentation -> decocher 'autoriser extinction'",
            "  2. BIOS : desactiver PCIe ASPM (Active State Power Management)",
            "  3. Mettre a jour le driver du device fautif depuis le site du fabricant de la carte mere",
            "  4. Envisager mise a jour BIOS"
        )
        foreach ($a in $advice) { $rapport += $a; Write-Host $a -ForegroundColor Yellow }
    }
} else {
    $msg = "Aucune erreur WHEA détectée."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 8. ALIMENTATION / VEILLE / HIBERNATION
# ============================================================
$rapport += Write-Section "8. EVENEMENTS ALIMENTATION / VEILLE"

$powerEvents = Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Microsoft-Windows-Kernel-Power'
    StartTime    = $dateDebut
} -MaxEvents 50 2>$null | Where-Object { $_.Id -in @(42, 107, 109, 137, 506) }

# ID 42 = entrée en veille, 107 = reprise, 109 = batterie/alim, 137 = firmware, 506 = changement perf
if ($powerEvents) {
    $rapport += "$($powerEvents.Count) événement(s) d'alimentation/veille"
    foreach ($evt in ($powerEvents | Select-Object -First 15)) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun événement d'alimentation notable."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 9. ERREURS CRITIQUES TOUTES SOURCES (System)
# ============================================================
$rapport += Write-Section "9. TOUTES LES ERREURS CRITIQUES (System Log)"

$critical = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = 1  # Critical
    StartTime = $dateDebut
} -MaxEvents 30 2>$null

if ($critical) {
    $rapport += ">> $($critical.Count) événement(s) CRITIQUE(S)"
    Write-Host ">> $($critical.Count) événement(s) CRITIQUE(S)" -ForegroundColor Red
    foreach ($evt in $critical) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun événement critique dans le journal System."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 10. ERREURS APPLICATION (crash d'apps)
# ============================================================
$rapport += Write-Section "10. CRASHS APPLICATION"

$appCrashes = Get-WinEvent -FilterHashtable @{
    LogName   = 'Application'
    Id        = @(1000, 1002, 1001)  # App crash, App hang, WER
    StartTime = $dateDebut
} -MaxEvents 30 2>$null

if ($appCrashes) {
    $rapport += "$($appCrashes.Count) crash/hang d'application(s)"
    foreach ($evt in ($appCrashes | Select-Object -First 15)) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun crash d'application détecté."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 11. TEMPÉRATURES / THROTTLING (si dispo)
# ============================================================
$rapport += Write-Section "11. SURCHAUFFE / THERMAL THROTTLING"

$thermal = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = @(1, 2, 3)
    StartTime = $dateDebut
} -MaxEvents 500 2>$null | Where-Object {
    $_.Message -match 'thermal|temperature|overheat|throttl|surchauffe'
}

if ($thermal) {
    $rapport += ">> $($thermal.Count) événement(s) de surchauffe/throttling !"
    Write-Host ">> $($thermal.Count) événement(s) thermiques" -ForegroundColor Red
    foreach ($evt in ($thermal | Select-Object -First 10)) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucun événement de surchauffe détecté dans les logs."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 12. PILOTES DEFAILLANTS RECENTS
# ============================================================
$rapport += Write-Section "12. PILOTES AYANT GENERE DES ERREURS"

$driverErrors = Get-WinEvent -FilterHashtable @{
    LogName   = 'System'
    Level     = @(1, 2)  # Critical, Error
    StartTime = $dateDebut
} -MaxEvents 500 2>$null | Where-Object {
    $_.Message -match 'driver|pilote|\\\\Driver\\\\'
}

if ($driverErrors) {
    $rapport += "$($driverErrors.Count) erreur(s) liée(s) à des pilotes"
    $grouped = $driverErrors | Group-Object ProviderName | Sort-Object Count -Descending
    foreach ($g in $grouped) {
        $line = "  - $($g.Name) : $($g.Count) erreur(s)"
        $rapport += $line
        Write-Host $line
    }
    $rapport += ""
    foreach ($evt in ($driverErrors | Select-Object -First 10)) {
        $rapport += Format-EventEntry $evt
    }
} else {
    $msg = "Aucune erreur de pilote détectée."
    $rapport += $msg; Write-Host $msg -ForegroundColor Green
}

# ============================================================
# 13. SANTE BATTERIE (laptop)
# ============================================================
$rapport += Write-Section "13. SANTE BATTERIE"

$battery = Get-CimInstance Win32_Battery 2>$null
if ($battery) {
    $batInfo = @(
        "Statut        : $($battery.Status)"
        "Charge        : $($battery.EstimatedChargeRemaining)%"
        "En charge     : $(if ($battery.BatteryStatus -eq 2) { 'Oui' } else { 'Non' })"
    )
    # Vérifier santé via powercfg
    $battReportPath = Join-Path $env:TEMP 'battery-report.html'
    $null = & powercfg /batteryreport /output $battReportPath 2>$null
    if (Test-Path $battReportPath) {
        $battHtml = Get-Content $battReportPath -Raw 2>$null
        if ($battHtml -match 'DESIGN CAPACITY.*?([\d,\.]+)\s*mWh' ) {
            $designCap = $Matches[1] -replace ',', ''
            if ($battHtml -match 'FULL CHARGE CAPACITY.*?([\d,\.]+)\s*mWh') {
                $fullCap = $Matches[1] -replace ',', ''
                $healthPct = [math]::Round(([double]$fullCap / [double]$designCap) * 100, 1)
                $batInfo += "Capacité design   : $designCap mWh"
                $batInfo += "Capacité actuelle : $fullCap mWh"
                $batInfo += "Santé batterie    : $healthPct%"
                if ($healthPct -lt 50) {
                    $batInfo += ">> BATTERIE TRES DEGRADEE - peut causer des coupures !"
                    Write-Host ">> BATTERIE TRES DEGRADEE ($healthPct%)" -ForegroundColor Red
                } elseif ($healthPct -lt 75) {
                    $batInfo += ">> Batterie usée - remplacement conseillé"
                    Write-Host ">> Batterie usée ($healthPct%)" -ForegroundColor Yellow
                }
            }
        }
        Remove-Item $battReportPath -Force 2>$null
    }
    foreach ($line in $batInfo) { $rapport += $line; Write-Host $line }
} else {
    $msg = "Aucune batterie détectée (PC fixe ou batterie non reconnue)."
    $rapport += $msg; Write-Host $msg
}

# ============================================================
# 14. TEMPERATURES ACTUELLES
# ============================================================
$rapport += Write-Section "14. TEMPERATURES ACTUELLES"

$tempFound = $false

# Méthode 1 : WMI MSAcpi_ThermalZoneTemperature (nécessite admin)
$thermalZones = Get-CimInstance -Namespace 'root/WMI' -ClassName 'MSAcpi_ThermalZoneTemperature' 2>$null
if ($thermalZones) {
    $tempFound = $true
    foreach ($tz in $thermalZones) {
        $tempC = [math]::Round(($tz.CurrentTemperature / 10) - 273.15, 1)
        $label = if ($tz.InstanceName) { $tz.InstanceName -replace '.*\\', '' } else { 'Zone' }
        $line = "$label : ${tempC}°C"
        if ($tempC -gt 90) {
            $line += " >> CRITIQUE !"
            Write-Host $line -ForegroundColor Red
        } elseif ($tempC -gt 75) {
            $line += " >> CHAUD"
            Write-Host $line -ForegroundColor Yellow
        } else {
            Write-Host $line -ForegroundColor Green
        }
        $rapport += $line
    }
}

# Méthode 2 : Open Hardware Monitor / Libre Hardware Monitor (si installé)
if (-not $tempFound) {
    $ohmSensors = Get-CimInstance -Namespace 'root/OpenHardwareMonitor' -ClassName 'Sensor' -Filter "SensorType='Temperature'" 2>$null
    if (-not $ohmSensors) {
        $ohmSensors = Get-CimInstance -Namespace 'root/LibreHardwareMonitor' -ClassName 'Sensor' -Filter "SensorType='Temperature'" 2>$null
    }
    if ($ohmSensors) {
        $tempFound = $true
        foreach ($s in ($ohmSensors | Sort-Object Name)) {
            $tempC = [math]::Round($s.Value, 1)
            $line = "$($s.Name) ($($s.Parent)) : ${tempC}°C"
            if ($tempC -gt 90) {
                $line += " >> CRITIQUE !"
                Write-Host $line -ForegroundColor Red
            } elseif ($tempC -gt 75) {
                $line += " >> CHAUD"
                Write-Host $line -ForegroundColor Yellow
            } else {
                Write-Host $line -ForegroundColor Green
            }
            $rapport += $line
        }
    }
}

if (-not $tempFound) {
    $msg = "Températures non disponibles via WMI. Options pour un suivi précis :"
    $rapport += $msg; Write-Host $msg -ForegroundColor Yellow
    $tips = @(
        "  - HWiNFO64 (gratuit) : surveillance temps réel"
        "  - Open/Libre Hardware Monitor : expose les températures via WMI (ce script les lira automatiquement)"
    )
    foreach ($t in $tips) { $rapport += $t; Write-Host $t -ForegroundColor Yellow }
}

# ============================================================
# 15. DETAILS RAM PAR SLOT
# ============================================================
$rapport += Write-Section "15. DETAILS RAM PAR SLOT"

$ramSticks = Get-CimInstance Win32_PhysicalMemory 2>$null
if ($ramSticks) {
    $slotNum = 0
    foreach ($stick in $ramSticks) {
        $slotNum++
        $capacityGB = [math]::Round($stick.Capacity / 1GB, 1)
        $speed = $stick.Speed
        $manufacturer = if ($stick.Manufacturer) { $stick.Manufacturer.Trim() } else { 'Inconnu' }
        $partNumber = if ($stick.PartNumber) { $stick.PartNumber.Trim() } else { 'N/A' }
        $locator = if ($stick.DeviceLocator) { $stick.DeviceLocator } else { "Slot $slotNum" }
        $line = "$locator : $capacityGB Go | $speed MHz | $manufacturer | $partNumber"
        $rapport += $line
        Write-Host $line
    }
    $rapport += ">> Pour tester chaque barrette individuellement, retirez-en une et testez avec mdsched.exe"
} else {
    $msg = "Impossible de lire les infos RAM."
    $rapport += $msg; Write-Host $msg
}

# ============================================================
# 16. INFOS SYSTÈME
# ============================================================
$rapport += Write-Section "16. INFORMATIONS SYSTEME"

$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$bios = Get-CimInstance Win32_BIOS
$gpu = Get-CimInstance Win32_VideoController
$cpu = Get-CimInstance Win32_Processor

$sysInfo = @(
    "Nom PC        : $($cs.Name)"
    "Fabricant     : $($cs.Manufacturer) - $($cs.Model)"
    "OS            : $($os.Caption) $($os.Version) (Build $($os.BuildNumber))"
    "BIOS          : $($bios.SMBIOSBIOSVersion)"
    "CPU           : $($cpu.Name)"
    "RAM totale    : $([math]::Round($cs.TotalPhysicalMemory / 1GB, 1)) Go"
    "Dernier boot  : $($os.LastBootUpTime.ToString('dd/MM/yyyy HH:mm:ss'))"
    "Uptime        : $((Get-Date) - $os.LastBootUpTime | ForEach-Object { '{0}j {1}h {2}m' -f $_.Days, $_.Hours, $_.Minutes })"
)

foreach ($g in $gpu) {
    $vram = if ($g.AdapterRAM -gt 0) { "$([math]::Round($g.AdapterRAM / 1GB, 1)) Go" } else { "N/A" }
    $sysInfo += "GPU           : $($g.Name) (VRAM: $vram, Driver: $($g.DriverVersion), Date: $($g.DriverDate))"
}

foreach ($line in $sysInfo) {
    $rapport += $line
    Write-Host $line
}

# ============================================================
# 17. MINIDUMPS (BSOD crash dumps)
# ============================================================
$rapport += Write-Section "17. FICHIERS MINIDUMP (crash dumps)"

$dumpPath = "$env:SystemRoot\Minidump"
if (Test-Path $dumpPath) {
    $dumps = Get-ChildItem $dumpPath -Filter '*.dmp' | Sort-Object LastWriteTime -Descending | Select-Object -First 10
    if ($dumps) {
        $rapport += "$($dumps.Count) fichier(s) minidump trouvé(s) :"
        Write-Host "$($dumps.Count) fichier(s) minidump" -ForegroundColor Yellow
        foreach ($d in $dumps) {
            $line = "  $($d.Name) - $($d.LastWriteTime.ToString('dd/MM/yyyy HH:mm:ss')) - $([math]::Round($d.Length / 1KB)) Ko"
            $rapport += $line
            Write-Host $line
        }
        $rapport += ">> Utilisez WinDbg ou BlueScreenView pour analyser ces dumps."
    } else {
        $rapport += "Dossier Minidump existe mais aucun fichier .dmp trouvé."
    }
} else {
    $rapport += "Pas de dossier Minidump trouvé."
}

$memDump = "$env:SystemRoot\MEMORY.DMP"
if (Test-Path $memDump) {
    $dmpInfo = Get-Item $memDump
    $rapport += "Dump mémoire complet trouvé : $($dmpInfo.LastWriteTime.ToString('dd/MM/yyyy HH:mm:ss')) ($([math]::Round($dmpInfo.Length / 1MB)) Mo)"
}

# ============================================================
# 18. RÉSUMÉ ET RECOMMANDATIONS
# ============================================================
$rapport += Write-Section "18. RESUME ET RECOMMANDATIONS"

$issues = @()

if ($unexpectedShutdowns) { $issues += "- ARRETS INATTENDUS détectés ($($unexpectedShutdowns.Count)x) : le PC s'est éteint brutalement" }
if ($kernelPower) { $issues += "- KERNEL-POWER 41 ($($kernelPower.Count)x) : souvent lié à l'alimentation, la surchauffe ou un pilote défaillant" }
if ($bugchecks) { $issues += "- BSOD/BUGCHECK ($($bugchecks.Count)x) : crash système avec écran bleu (même si vous ne l'avez pas vu)" }
if ($gpuAll) { $issues += "- ERREURS GPU ($($gpuAll.Count)x) : problème de pilote graphique ou GPU défaillant" }
if ($diskErrors) { $issues += "- ERREURS DISQUE ($($diskErrors.Count)x) : problème potentiel de stockage" }
if ($memErrors) { $issues += "- ERREURS MEMOIRE ($($memErrors.Count)x) : RAM potentiellement défectueuse" }
if ($whea) { $issues += "- ERREURS WHEA ($($whea.Count)x) : erreur matérielle détectée par le processeur" }
if ($thermal) { $issues += "- SURCHAUFFE ($($thermal.Count)x) : le PC chauffe trop, vérifiez ventilation/pâte thermique" }
if ($battery -and $healthPct -and $healthPct -lt 50) { $issues += "- BATTERIE TRES DEGRADEE ($healthPct%) : peut causer des coupures soudaines" }

if ($issues.Count -gt 0) {
    $rapport += "PROBLEMES DETECTES :"
    Write-Host "`nPROBLEMES DETECTES :" -ForegroundColor Red
    foreach ($i in $issues) {
        $rapport += $i
        Write-Host $i -ForegroundColor Yellow
    }
} else {
    $msg = "Aucun problème majeur détecté dans les logs analysés."
    $rapport += $msg
    Write-Host $msg -ForegroundColor Green
}

# Recommandations priorisées selon les problèmes détectés
$recommandations = @()
$recommandations += "RECOMMANDATIONS (par priorité) :"

if ($memErrors -or $whea) {
    # Adapter la recommandation selon le résultat mdsched
    if ($mdsched -and $mdsched.Message -match 'aucune erreur|no.*(error|problem)') {
        $recommandations += @"

  [INFO] MEMOIRE RAM :
    - mdsched.exe n'a détecté aucune erreur (test du $($mdsched.TimeCreated.ToString('dd/MM/yyyy')))
    - L'erreur WHEA peut venir du CPU (cache/bus) ou de l'alimentation, pas forcément de la RAM
    - Pour un test plus approfondi : MemTest86 (USB bootable) - laisser tourner 4-8h
    - Si 2 barrettes : tester CHAQUE barrette seule pour isoler un problème intermittent
"@
    } else {
        $recommandations += @"

  [PRIORITE 1] TESTER LA RAM :
    a) Lancer 'mdsched.exe' (diagnostic mémoire Windows, redémarrage requis)
    b) Mieux : télécharger MemTest86 (USB bootable) - laisser tourner 4-8h
    c) Si 2 barrettes : tester CHAQUE barrette seule (retirer l'autre)
       -> Si erreur avec une seule barrette = RAM défectueuse à remplacer
"@
    }
}

if ($gpu) {
    $oldDrivers = $gpu | Where-Object { $_.DriverDate -and $_.DriverDate -lt (Get-Date).AddYears(-2) }
    if ($oldDrivers) {
        $recommandations += @"

  [PRIORITE 2] METTRE A JOUR LES PILOTES GPU :
    - Vos pilotes GPU datent de plus de 2 ans !
    - NVIDIA : https://www.nvidia.com/Download/index.aspx
    - Intel : https://www.intel.com/content/www/us/en/download-center
    - NE PAS utiliser Windows Update pour les pilotes GPU
"@
    }
}

if ($battery -and $healthPct -and $healthPct -lt 75) {
    $recommandations += @"

  [PRIORITE] BATTERIE USEE ($healthPct%) :
    - Une batterie dégradée peut causer des coupures même sur secteur
    - Envisager le remplacement de la batterie
    - Tester sans batterie (sur secteur uniquement) pour isoler le problème
"@
}

$recommandations += @"

  AUTRES VERIFICATIONS :
  - Vérifier les températures avec HWiNFO64 (gratuit) en continu
  - Vérifier le disque : chkdsk /f
  - Désactiver le démarrage rapide : Panneau de config > Options d'alimentation
  - Vérifier le chargeur/câble d'alimentation (usure, faux contact)
  - Nettoyer la poussière interne (ventilateurs, grilles)
  - Changer la pâte thermique si jamais fait (laptop de 2016)
"@

foreach ($r in $recommandations) { $rapport += $r }

# ============================================================
# EXPORT DU RAPPORT
# ============================================================
$rapport += Write-Section "FIN DU RAPPORT"

$rapportTexte = $rapport -join "`n"
$rapportTexte | Out-File -FilePath $RapportPath -Encoding UTF8

Write-Host "`n`nRapport sauvegardé dans : $RapportPath" -ForegroundColor Green
Write-Host "Ouvrez ce fichier pour voir le détail complet." -ForegroundColor Green
