# Définir le chemin de base où les répertoires seront créés
$basePath = "C:\Chemin\Vers\Dossier"

# Définir les noms des répertoires dans une variable
$repertoires = @("Rep1", "Rep2", "Rep3", "Rep4")

# Parcourir chaque nom de répertoire et le créer
foreach ($rep in $repertoires) {
    # Construire le chemin complet du répertoire
    $fullPath = Join-Path -Path $basePath -ChildPath $rep

    # Vérifier si le répertoire existe déjà
    if (-Not (Test-Path -Path $fullPath)) {
        # Créer le répertoire
        New-Item -ItemType Directory -Path $fullPath
        Write-Output "Répertoire '$fullPath' créé avec succès."
    } else {
        Write-Output "Répertoire '$fullPath' existe déjà."
    }
}
