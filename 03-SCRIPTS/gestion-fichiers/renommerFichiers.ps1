$repertoire = "C:\chemin\vers\le\dossier"
$ancienMotif = "ancien"
$nouveauMotif = "nouveau"

Get-ChildItem -Path $repertoire -File | ForEach-Object {
    $nouveauNom = $_.Name -replace $ancienMotif, $nouveauMotif
    Rename-Item -Path $_.FullName -NewName $nouveauNom
}
