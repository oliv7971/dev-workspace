<#  listeFichiersJuillet.ps1
    Liste tous les fichiers Excel (.xls, .xlsx, .xlsm) sous le dossier du script,
    modifiés entre le 01/07/2025 00:00 et le 01/08/2025 00:00,
    et exporte une liste sans troncature.
#>

# --- Point de départ = dossier du script (pas le répertoire courant de la session) ---
$StartDir = $PSScriptRoot
Set-Location -Path $StartDir

# --- Fenêtre de dates (juillet 2025) ---
$From = [datetime]'2025-07-01T00:00:00'
$To   = [datetime]'2025-08-01T00:00:00'   # exclusif

# --- Extensions ciblées ---
$Patterns = @('*.xls','*.xlsx','*.xlsm')

# --- Fichiers de sortie ---
$TxtOut = Join-Path $StartDir 'liste_fichiers_juillet.txt'
$CsvOut = Join-Path $StartDir 'liste_fichiers_juillet.csv'

try {
    # Récupération des fichiers
    $files = Get-ChildItem -Path $StartDir -Recurse -File -Include $Patterns -ErrorAction Stop |
        Where-Object { $_.LastWriteTime -ge $From -and $_.LastWriteTime -lt $To }

    # ✅ Sortie TXT brute, sans troncature
    $files | Select-Object -ExpandProperty FullName |
        Out-File -FilePath $TxtOut -Encoding UTF8

    # ✅ Sortie CSV (utile si tu veux trier/filtrer ensuite)
    $files |
        Select-Object FullName, Name, DirectoryName, Length, LastWriteTime |
        Export-Csv -Path $CsvOut -NoTypeInformation -Encoding UTF8

    Write-Host ""
    Write-Host "Fichiers trouvés : $($files.Count)" -ForegroundColor Green
    Write-Host "TXT : $TxtOut" -ForegroundColor Cyan
    Write-Host "CSV : $CsvOut" -ForegroundColor Cyan
}
catch {
    Write-Error "Erreur lors du listing : $($_.Exception.Message)"
    exit 1
}
