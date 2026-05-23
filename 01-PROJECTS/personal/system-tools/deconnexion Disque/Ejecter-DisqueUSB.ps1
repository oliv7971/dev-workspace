#Requires -Version 5.1
<#
.SYNOPSIS
    Identifie les processus qui bloquent un disque USB et l'éjecte proprement.
.DESCRIPTION
    Ce script détecte les processus qui utilisent un disque,
    permet de les fermer, puis éjecte le disque en toute sécurité.
.PARAMETER Lettre
    Lettre du disque à éjecter (ex: P:). Par défaut : P:
.EXAMPLE
    .\Ejecter-DisqueUSB.ps1
    .\Ejecter-DisqueUSB.ps1 -Lettre E:
.NOTES
    Lancer de préférence en tant qu'Administrateur pour plus de détails.
#>
param(
    [string]$Lettre = "P:"
)

# ─────────────────────────────────────────────
# Couleurs et helpers
# ─────────────────────────────────────────────
function Write-Title  { param($t) Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Write-Ok     { param($t) Write-Host "  [OK]  $t" -ForegroundColor Green }
function Write-Warn   { param($t) Write-Host "  [!]   $t" -ForegroundColor Yellow }
function Write-Err    { param($t) Write-Host "  [ERR] $t" -ForegroundColor Red }
function Write-Info   { param($t) Write-Host "        $t" -ForegroundColor Gray }

# ─────────────────────────────────────────────
# 1. Vérifier que le disque est présent
# ─────────────────────────────────────────────
# Normaliser : s'assurer que la lettre finit par ":"
if ($Lettre -notmatch ':$') { $Lettre = "$Lettre:" }
$Lettre = $Lettre.ToUpper()

Write-Title "Vérification du disque $Lettre"

$disque = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $Lettre }

if (-not $disque) {
    Write-Err "Le disque $Lettre n'est pas détecté."
    Write-Info "Vérifiez qu'il est bien branché ou changez la lettre avec : .\Ejecter-DisqueUSB.ps1 -Lettre X:"
    exit 1
}

$taille = if ($disque.Size) { "{0:N1} Go" -f ($disque.Size / 1GB) } else { "inconnu" }
$nom    = if ($disque.VolumeName) { $disque.VolumeName } else { "(sans nom)" }
Write-Ok "Disque trouvé : $Lettre  |  $nom  |  $taille"

$lettre = $Lettre

# ─────────────────────────────────────────────
# 2. Détecter les processus qui utilisent ce disque
# ─────────────────────────────────────────────
Write-Title "Recherche des processus qui utilisent $lettre"

$bloquants = [System.Collections.Generic.List[PSObject]]::new()

Get-Process | ForEach-Object {
    $proc = $_
    # Vérifier les modules chargés
    try {
        $proc.Modules | Where-Object { $_.FileName -like "$lettre\*" } | ForEach-Object {
            $bloquants.Add([PSCustomObject]@{
                PID         = $proc.Id
                Nom         = $proc.Name
                Type        = "Module"
                Fichier     = $_.FileName
            })
        }
    } catch { }
    # Vérifier le répertoire de travail
    try {
        if ($proc.MainModule.FileName -like "$lettre\*") {
            $bloquants.Add([PSCustomObject]@{
                PID         = $proc.Id
                Nom         = $proc.Name
                Type        = "Exécutable"
                Fichier     = $proc.MainModule.FileName
            })
        }
    } catch { }
}

# Chercher aussi via les handles ouverts (nécessite handle.exe de Sysinternals si dispo)
$handleExe = Get-Command "handle.exe" -ErrorAction SilentlyContinue
if ($handleExe) {
    Write-Info "Utilisation de handle.exe (Sysinternals) pour une détection complète..."
    $handleOutput = & handle.exe $lettre -nobanner 2>$null
    $handleOutput | Where-Object { $_ -match "pid: (\d+)" } | ForEach-Object {
        if ($_ -match "(\S+)\s+pid:\s+(\d+).*?(.+)$") {
            $bloquants.Add([PSCustomObject]@{
                PID         = [int]$Matches[2]
                Nom         = $Matches[1]
                Type        = "Handle"
                Fichier     = $Matches[3].Trim()
            })
        }
    }
}

# Dédoublonner par PID
$bloquants = $bloquants | Sort-Object PID -Unique

if ($bloquants.Count -eq 0) {
    Write-Ok "Aucun processus bloquant détecté."
} else {
    Write-Warn "$($bloquants.Count) processus utilisent ce disque :"
    $bloquants | Format-Table PID, Nom, Type, Fichier -AutoSize
}

# ─────────────────────────────────────────────
# 3. Fermer l'Explorateur Windows si nécessaire
# ─────────────────────────────────────────────
Write-Title "Vérification de l'Explorateur Windows"

# Vérifier si explorer a des fenêtres ouvertes sur ce disque via Shell.Application
try {
    $shell = New-Object -ComObject Shell.Application
    $fenetresAFermer = $shell.Windows() | Where-Object {
        try { $_.LocationURL -like "*$($lettre -replace ':','%3A')*" } catch { $false }
    }
    if ($fenetresAFermer) {
        Write-Warn "L'Explorateur Windows a des fenêtres ouvertes sur $lettre"
        $rep = Read-Host "Fermer ces fenêtres ? (O/N)"
        if ($rep -match '^[Oo]') {
            $fenetresAFermer | ForEach-Object { $_.Quit() }
            Start-Sleep -Milliseconds 500
            Write-Ok "Fenêtres de l'Explorateur fermées."
        }
    } else {
        Write-Ok "Aucune fenêtre de l'Explorateur sur ce disque."
    }
} catch {
    Write-Info "Impossible de vérifier les fenêtres de l'Explorateur."
}

# ─────────────────────────────────────────────
# 4. Proposer de fermer les processus bloquants
# ─────────────────────────────────────────────
if ($bloquants.Count -gt 0) {
    Write-Title "Fermeture des processus bloquants"
    $rep = Read-Host "Voulez-vous fermer ces processus pour libérer le disque ? (O/N)"
    if ($rep -match '^[Oo]') {
        foreach ($p in $bloquants) {
            # Ne jamais tuer les processus système critiques
            $exclus = @('System', 'svchost', 'csrss', 'wininit', 'winlogon', 'services', 'lsass', 'smss')
            if ($p.Nom -in $exclus) {
                Write-Warn "Processus système ignoré : $($p.Nom) (PID $($p.PID))"
                continue
            }
            try {
                Stop-Process -Id $p.PID -Force -ErrorAction Stop
                Write-Ok "Processus arrêté : $($p.Nom) (PID $($p.PID))"
            } catch {
                Write-Err "Impossible d'arrêter $($p.Nom) (PID $($p.PID)) : $_"
            }
        }
        Start-Sleep -Seconds 1
    }
}

# ─────────────────────────────────────────────
# 5. Éjection du disque
# ─────────────────────────────────────────────
Write-Title "Éjection de $lettre"

$rep = Read-Host "Prêt à éjecter $lettre ($nom) ? (O/N)"
if ($rep -notmatch '^[Oo]') {
    Write-Info "Éjection annulée."
    exit 0
}

# Méthode 1 : via Shell (la plus propre)
try {
    $shell2 = New-Object -ComObject Shell.Application
    $shell2.NameSpace(17).ParseName($lettre).InvokeVerb("Eject")
    Start-Sleep -Seconds 2

    # Vérifier si le disque est toujours là
    $encore = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $lettre }
    if (-not $encore) {
        Write-Ok "Disque $lettre éjecté avec succès !"
        Write-Info "Vous pouvez maintenant débrancher le disque en toute sécurité."
        exit 0
    } else {
        Write-Warn "Le disque est toujours monté. Tentative alternative..."
    }
} catch {
    Write-Warn "Méthode Shell échouée : $_"
}

# Méthode 2 : via diskpart (silencieux)
try {
    $numDisque = (Get-WmiObject -Class Win32_LogicalDiskToPartition |
        Where-Object { $_.Dependent -like "*$($lettre -replace ':','')*" } |
        Select-Object -First 1 |
        ForEach-Object { $_.Antecedent }) -replace '.*Disk #(\d+).*','$1'

    if ($numDisque -match '^\d+$') {
        $diskpartScript = "select disk $numDisque`r`noffline disk`r`nexit"
        $diskpartScript | diskpart | Out-Null
        Write-Ok "Disque mis hors ligne via diskpart. Vous pouvez le débrancher."
    }
} catch {
    Write-Err "Impossible d'éjecter via diskpart : $_"
    Write-Warn "Essayez manuellement : clic droit sur le disque → Éjecter"
}

Write-Host ""
Write-Host "─────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  Script terminé." -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────" -ForegroundColor DarkGray
