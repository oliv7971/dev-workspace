$out = "D:\20-dvp\github\dev-workspace\01-PROJECTS\personal\midi-DB\audit-midi.txt"
"=== AUDIT MIDI - $(Get-Date) ===" | Out-File $out -Encoding UTF8

# SOURCE : 20-MUSIQUE STUDIO
"" | Out-File $out -Append
"### SOURCE : \\Nas_louhans_2\01-ds420-data\20-MUSIQUE STUDIO ###" | Out-File $out -Append
$src = "\\Nas_louhans_2\01-ds420-data\20-MUSIQUE STUDIO"
foreach ($folder in (Get-ChildItem $src -Directory -EA SilentlyContinue)) {
    $files = Get-ChildItem $folder.FullName -Recurse -Include "*.mid","*.midi","*.kar" -EA SilentlyContinue
    $count = $files.Count
    $size  = [math]::Round(($files | Measure-Object Length -Sum -EA SilentlyContinue).Sum / 1MB, 2)
    "  $($folder.Name) : $count fichiers ($size MB)" | Out-File $out -Append
}

# DEST : 22-MUSIQUE MIDI KAR
"" | Out-File $out -Append
"### DESTINATION : \\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR ###" | Out-File $out -Append
$dst = "\\Nas_louhans_2\01-ds420-data\22-MUSIQUE MIDI KAR"
# Fichiers à la racine
$root = Get-ChildItem $dst -File -Include "*.mid","*.midi","*.kar" -EA SilentlyContinue
"  [RACINE] : $($root.Count) fichiers" | Out-File $out -Append
foreach ($folder in (Get-ChildItem $dst -Directory -EA SilentlyContinue)) {
    $files = Get-ChildItem $folder.FullName -Recurse -Include "*.mid","*.midi","*.kar" -EA SilentlyContinue
    $count = $files.Count
    $size  = [math]::Round(($files | Measure-Object Length -Sum -EA SilentlyContinue).Sum / 1MB, 2)
    "  $($folder.Name) : $count fichiers ($size MB)" | Out-File $out -Append
}

"" | Out-File $out -Append
"=== TERMINE ===" | Out-File $out -Append
