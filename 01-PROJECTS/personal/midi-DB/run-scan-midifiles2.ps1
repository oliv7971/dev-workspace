$out = "D:\20-dvp\github\dev-workspace\01-PROJECTS\personal\midi-DB\scan-midifiles2.txt"
$path = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR\midifiles 2"

"=== SCAN midifiles 2 - $(Get-Date) ===" | Out-File $out -Encoding UTF8

$all = Get-ChildItem -LiteralPath $path -Recurse -File -EA SilentlyContinue

# Stats globales
"" | Out-File $out -Append
"--- Stats globales ---" | Out-File $out -Append
"Nb total fichiers : $($all.Count)" | Out-File $out -Append
$totalBytes = ($all | Measure-Object Length -Sum -EA SilentlyContinue).Sum
"Taille totale reelle : $([math]::Round($totalBytes/1GB,2)) GB" | Out-File $out -Append

# Top 30 fichiers les plus gros
"" | Out-File $out -Append
"--- TOP 30 FICHIERS LES PLUS GROS ---" | Out-File $out -Append
$all | Sort-Object Length -Descending | Select-Object -First 30 | ForEach-Object {
    "$([math]::Round($_.Length/1MB,2)) MB | $($_.Extension) | $($_.FullName)"
} | Out-File $out -Append

# Répartition par extension
"" | Out-File $out -Append
"--- REPARTITION PAR EXTENSION ---" | Out-File $out -Append
$all | Group-Object Extension | Sort-Object Count -Descending | ForEach-Object {
    $sz = [math]::Round(($_.Group | Measure-Object Length -Sum).Sum/1MB,2)
    "$($_.Name.PadRight(10)) : $($_.Count) fichiers ($sz MB)"
} | Out-File $out -Append

# Fichiers > 100 MB (suspects)
"" | Out-File $out -Append
"--- FICHIERS > 100 MB (SUSPECTS) ---" | Out-File $out -Append
$all | Where-Object { $_.Length -gt 100MB } | Sort-Object Length -Descending | ForEach-Object {
    "$([math]::Round($_.Length/1MB,2)) MB | $($_.Extension) | $($_.FullName)"
} | Out-File $out -Append

"" | Out-File $out -Append
"=== TERMINE ===" | Out-File $out -Append
