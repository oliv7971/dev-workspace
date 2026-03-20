# Obtenez tous les fichiers du répertoire courant
$files = Get-ChildItem -Path . -File

# Parcourez chaque fichier
foreach ($file in $files) {
    # Vérifiez si le nom du fichier commence par un espace
    if ($file.Name -match '^ +') {
        # Créez un nouveau nom sans les espaces en début
        $newName = $file.Name -replace '^ +', ''
        # Renommez le fichier
        Rename-Item -Path $file.FullName -NewName $newName
        Write-Host "Renamed '$($file.Name)' to '$newName'"
    }
}
