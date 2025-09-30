# Définir les noms des répertoires dans une variable
$repertoires = @("Rep1", "Rep2", "Rep3", "Rep4")

# Parcourir chaque nom de répertoire et le créer
foreach ($rep in $repertoires) {
    # Vérifier si le répertoire existe déjà
    if (-Not (Test-Path -Path $rep)) {
        # Créer le répertoire
        New-Item -ItemType Directory -Path $rep
        Write-Output "Répertoire '$rep' créé avec succès."
    } else {
        Write-Output "Répertoire '$rep' existe déjà."
    }
}
