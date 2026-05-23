$out = "D:\20-dvp\github\dev-workspace\01-PROJECTS\personal\midi-DB\audit-midi-v2.txt"
"=== AUDIT MIDI v2 - $(Get-Date) ===" | Out-File $out -Encoding UTF8

function Count-Midi($path) {
    $files = Get-ChildItem -LiteralPath $path -Recurse -File -EA SilentlyContinue |
             Where-Object { $_.Extension -match '^\.mid(i|)$|^\.kar$' }
    $count = $files.Count
    $sizeKB = [math]::Round(($files | Measure-Object -Property Length -Sum -EA SilentlyContinue).Sum / 1KB, 1)
    return [PSCustomObject]@{ Count=$count; SizeKB=$sizeKB }
}

# SOURCE
"" | Out-File $out -Append
"### SOURCE : \\Nas_louhans_2\01-ds420-data\20-MUSIQUE STUDIO ###" | Out-File $out -Append
$src = "\\Nas_louhans_2\01-ds420-data\20-MUSIQUE STUDIO"
foreach ($folder in (Get-ChildItem -LiteralPath $src -Directory -EA SilentlyContinue)) {
    $r = Count-Midi $folder.FullName
    "  $($folder.Name) : $($r.Count) fichiers ($($r.SizeKB) KB)" | Out-File $out -Append
}

# DESTINATION
"" | Out-File $out -Append
"### DESTINATION : \\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR ###" | Out-File $out -Append
$dst = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"
# Fichiers racine
$rootFiles = Get-ChildItem -LiteralPath $dst -File -EA SilentlyContinue |
             Where-Object { $_.Extension -match '^\.mid(i|)$|^\.kar$' }
"  [RACINE] : $($rootFiles.Count) fichiers" | Out-File $out -Append
foreach ($folder in (Get-ChildItem -LiteralPath $dst -Directory -EA SilentlyContinue)) {
    $r = Count-Midi $folder.FullName
    "  $($folder.Name) : $($r.Count) fichiers ($($r.SizeKB) KB)" | Out-File $out -Append
}

"" | Out-File $out -Append
"=== TERMINE ===" | Out-File $out -Append
