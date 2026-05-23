$start = (Get-Date).AddDays(-21)

Write-Host '=== KERNEL-POWER 41 (21 derniers jours) ===' -ForegroundColor Cyan
$kp = Get-WinEvent -FilterHashtable @{ LogName='System'; ProviderName='Microsoft-Windows-Kernel-Power'; Id=41; StartTime=$start } -MaxEvents 30 -EA SilentlyContinue
if ($kp) {
    $kp | ForEach-Object { Write-Host "[$($_.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'))] FREEZE/REBOOT brutal" -ForegroundColor Red }
} else {
    Write-Host "Aucun freeze detecte sur la periode." -ForegroundColor Green
}

Write-Host ''
Write-Host '=== WHEA HARDWARE ERRORS ===' -ForegroundColor Cyan
$whea = Get-WinEvent -FilterHashtable @{ LogName='System'; ProviderName='Microsoft-Windows-WHEA-Logger'; StartTime=$start } -MaxEvents 30 -EA SilentlyContinue
if ($whea) {
    foreach ($evt in $whea) {
        Write-Host "[$($evt.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'))] ID:$($evt.Id)" -ForegroundColor Red
        try {
            $xml = [xml]$evt.ToXml()
            $xml.Event.EventData.Data | Where-Object { $_.'#text' } | ForEach-Object {
                Write-Host "  $($_.Name) = $($_.'#text')" -ForegroundColor Yellow
            }
        } catch {}
    }
} else {
    Write-Host "Aucune erreur WHEA detectee." -ForegroundColor Green
}

Write-Host ''
Write-Host '=== TEMPERATURES WMI ACPI ===' -ForegroundColor Cyan
$zones = Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace root\WMI -EA SilentlyContinue
if ($zones) {
    $zones | ForEach-Object { Write-Host ("  Zone: {0:N1} degC" -f ($_.CurrentTemperature / 10 - 273.15)) }
} else {
    Write-Host "  Temperature WMI ACPI non disponible." -ForegroundColor DarkYellow
}

Write-Host ''
Write-Host '=== BUGCHECK / BSOD ===' -ForegroundColor Cyan
$bsod = Get-WinEvent -FilterHashtable @{ LogName='System'; ProviderName='Microsoft-Windows-WER-SystemErrorReporting'; Id=1001; StartTime=$start } -MaxEvents 10 -EA SilentlyContinue
if ($bsod) {
    $bsod | ForEach-Object { Write-Host "[$($_.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'))] BSOD : $($_.Message -split '\n' | Select-Object -First 2)" -ForegroundColor Red }
} else {
    Write-Host "Aucun BSOD." -ForegroundColor Green
}

Write-Host ''
Write-Host '=== ERREURS CRITIQUES SYSTEME ===' -ForegroundColor Cyan
Get-WinEvent -FilterHashtable @{ LogName='System'; Level=1; StartTime=$start } -MaxEvents 20 -EA SilentlyContinue |
    ForEach-Object { Write-Host "[$($_.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'))] $($_.ProviderName) / ID:$($_.Id)" -ForegroundColor Yellow }
