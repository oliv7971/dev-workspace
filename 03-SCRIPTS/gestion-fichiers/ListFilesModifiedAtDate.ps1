# Définir la date cible
$targetDate = Get-Date "2025-02-13"

# Définir le répertoire de base
$baseDirectory = "C:\Users\Public\Documents\Leica Captivate\TS"

# Définir le chemin du fichier de sortie
$outputFile = "C:\data\search.log"

# Rechercher les fichiers modifiés à la date cible
$files = Get-ChildItem -Path $baseDirectory -Recurse -File | Where-Object { $_.LastWriteTime.Date -eq $targetDate.Date }

# Afficher les fichiers trouvés et les enregistrer dans un fichier
$files | ForEach-Object {
    "Fichier : $_.FullName" | Out-File -FilePath $outputFile -Append
    "Modifié le : $_.LastWriteTime" | Out-File -FilePath $outputFile -Append
    "-------------------------------------" | Out-File -FilePath $outputFile -Append
}

# Afficher un message de confirmation
Write-Output "Les résultats ont été enregistrés dans $outputFile"
