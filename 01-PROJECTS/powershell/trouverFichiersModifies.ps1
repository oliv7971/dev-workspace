Get-ChildItem -Path "C:\chemin\du\dossier" -Recurse | 
Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-1) } | 
Select-Object FullName, LastWriteTime | 
Out-File "C:\chemin\vers\log_fichiers_modifies.txt"
