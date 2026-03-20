# =============================================================================
# DIAGNOSTIC RAPIDE D'ESPACE DISQUE
# =============================================================================
# Version simplifiée pour un diagnostic immédiat des gros consommateurs
# =============================================================================

# =============================================================================
# CONFIGURATION - Modifiez ces variables selon vos besoins
# =============================================================================
$DriveLetter = "C:"                     # Disque à analyser
$TopCount = 15                          # Nombre d'éléments à afficher

# =============================================================================
# NE PAS MODIFIER EN DESSOUS DE CETTE LIGNE
# =============================================================================

function Format-Size {
    param([long]$Size)
    if ($Size -lt 1GB) { return "{0:N0} MB" -f ($Size / 1MB) }
    else { return "{0:N1} GB" -f ($Size / 1GB) }
}

Write-Host "🔍 DIAGNOSTIC RAPIDE - $DriveLetter" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Info disque
$drive = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $DriveLetter }
$usedSpace = $drive.Size - $drive.FreeSpace
Write-Host "Espace utilisé : $(Format-Size $usedSpace) / $(Format-Size $drive.Size)" -ForegroundColor Yellow
Write-Host ""

# TOP dossiers racine
Write-Host "📁 TOP DOSSIERS (niveau racine)" -ForegroundColor Green
$folders = Get-ChildItem -Path $DriveLetter -Directory -Force -ErrorAction SilentlyContinue

$folderSizes = foreach ($folder in $folders) {
    Write-Progress -Activity "Analyse" -Status $folder.Name
    try {
        $size = (Get-ChildItem -LiteralPath $folder.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | 
                 Measure-Object Length -Sum).Sum
        [PSCustomObject]@{
            Name = $folder.Name
            Size = $size
            SizeFormatted = Format-Size $size
        }
    }
    catch {
        [PSCustomObject]@{
            Name = $folder.Name + " (ERREUR ACCÈS)"
            Size = 0
            SizeFormatted = "N/A"
        }
    }
}

$folderSizes | Sort-Object Size -Descending | Select-Object -First $TopCount | 
    ForEach-Object { 
        Write-Host ("{0,-30} {1,10}" -f $_.Name, $_.SizeFormatted) -ForegroundColor $(if($_.Size -gt 10GB){"Red"}elseif($_.Size -gt 5GB){"Yellow"}else{"White"})
    }

Write-Host ""
Write-Host "🔍 RECHERCHE GROS FICHIERS (>1GB)..." -ForegroundColor Green

# TOP fichiers volumineux
$bigFiles = Get-ChildItem -Path $DriveLetter -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 1GB } |
    Sort-Object Length -Descending |
    Select-Object -First $TopCount

if ($bigFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "📄 GROS FICHIERS TROUVÉS" -ForegroundColor Red
    $bigFiles | ForEach-Object {
        Write-Host ("{0,-40} {1,10}" -f $_.Name, (Format-Size $_.Length)) -ForegroundColor Red
        Write-Host "    → $($_.DirectoryName)" -ForegroundColor Gray
    }
}
else {
    Write-Host "Aucun fichier > 1GB trouvé" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 Vérifiez en priorité :" -ForegroundColor Cyan
Write-Host "   • Corbeille Windows" -ForegroundColor Gray
Write-Host "   • C:\Windows\SoftwareDistribution" -ForegroundColor Gray
Write-Host "   • C:\Windows\Temp" -ForegroundColor Gray
Write-Host "   • %USERPROFILE%\AppData\Local\Temp" -ForegroundColor Gray
Write-Host "   • Points de restauration système" -ForegroundColor Gray

Write-Progress -Completed -Activity "Analyse"
Write-Host ""
Write-Host "✅ Diagnostic terminé !" -ForegroundColor Green