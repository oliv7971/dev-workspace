# Script PowerShell pour créer l'ossature de développement
# Auteur: Assistant GitHub Copilot
# Date: 30 septembre 2025

param(
    [string]$BasePath = "C:\data\20-DEVELOPPEMENT",
    [switch]$WhatIf = $false
)

Write-Host "Creation de l'ossature de developpement" -ForegroundColor Green
Write-Host "Repertoire de base: $BasePath" -ForegroundColor Cyan

# Définition de la structure
$structure = @{
    "01-PROJECTS" = @(
        "python",
        "javascript", 
        "csharp",
        "java",
        "cpp",
        "cross-platform",
        "web"
    )
    "02-TOOLS" = @(
        "scripts",
        "configs", 
        "templates",
        "automation"
    )
    "03-SANDBOX" = @(
        "experiments",
        "learning",
        "prototypes", 
        "temp",
        "poc"
    )
    "04-EXTERNAL" = @(
        "libraries",
        "samples",
        "forks",
        "references",
        "documentation"
    )
    "05-ARCHIVE" = @(
        "old-projects",
        "deprecated",
        "to-classify",
        "backup"
    )
    "10-INSTALL" = @(
        "software",
        "drivers", 
        "patches"
    )
    "11-UTILS" = @(
        "portable",
        "system-tools",
        "development-tools"
    )
}

# Fonction pour créer les dossiers
function New-DirectoryStructure {
    param(
        [string]$Path,
        [hashtable]$Structure,
        [bool]$WhatIfMode
    )
    
    foreach ($mainFolder in $Structure.Keys) {
        $mainPath = Join-Path $Path $mainFolder
        
        if ($WhatIfMode) {
            Write-Host "WHAT-IF: Creation du dossier $mainPath" -ForegroundColor Yellow
        } else {
            if (-not (Test-Path $mainPath)) {
                New-Item -ItemType Directory -Path $mainPath -Force | Out-Null
                Write-Host "Cree: $mainPath" -ForegroundColor Green
            } else {
                Write-Host "Existe deja: $mainPath" -ForegroundColor Yellow
            }
        }
        
        # Créer les sous-dossiers
        foreach ($subFolder in $Structure[$mainFolder]) {
            $subPath = Join-Path $mainPath $subFolder
            
            if ($WhatIfMode) {
                Write-Host "WHAT-IF: Creation du sous-dossier $subPath" -ForegroundColor Yellow
            } else {
                if (-not (Test-Path $subPath)) {
                    New-Item -ItemType Directory -Path $subPath -Force | Out-Null
                    Write-Host "  Cree: $subPath" -ForegroundColor Green
                } else {
                    Write-Host "  Existe deja: $subPath" -ForegroundColor Yellow
                }
            }
        }
    }
}

# Fonction pour créer les fichiers README
function New-ReadmeFiles {
    param(
        [string]$Path,
        [bool]$WhatIfMode
    )
    
    $readmeContent = @{
        "01-PROJECTS" = @'
# PROJECTS - Projets de développement

Ce dossier contient vos projets de développement finalisés et en cours.

## Structure par langage :
* python/ - Projets Python
* javascript/ - Projets JavaScript/Node.js  
* csharp/ - Projets C#/.NET
* java/ - Projets Java
* cpp/ - Projets C/C++
* cross-platform/ - Projets multi-langages
* web/ - Projets web frontend

## Versioning Git :
* Chaque projet = 1 repository Git séparé
* OU 1 monorepo par langage selon préférence

## Convention de nommage :
* Noms en minuscules avec tirets : mon-super-projet
* Pas d'espaces ni de caractères spéciaux
'@

        "02-TOOLS" = @'
# TOOLS - Outils de développement

Vos outils, scripts et configurations personnels.

## Structure :
* scripts/ - Scripts utilitaires (PowerShell, Bash, Python...)
* configs/ - Configurations (VS Code, Git, IDE...)
* templates/ - Templates de projets et boilerplates
* automation/ - Scripts d'automatisation

## Versioning Git :
* Repository unique "my-dev-tools"
* Versioning recommandé pour traçabilité

## Idées de contenu :
* Scripts de déploiement
* Configurations IDE partagées
* Templates de projets
* Outils de build personnalisés
'@

        "03-SANDBOX" = @'
# SANDBOX - Expérimentations

Zone d'expérimentation et d'apprentissage.

## Structure :
* experiments/ - Tests et expérimentations rapides
* learning/ - Code d'apprentissage (tutoriels, formations)
* prototypes/ - Prototypes et proof-of-concepts
* temp/ - Fichiers temporaires
* poc/ - Proof of Concepts structurés

## PAS de versioning Git :
* Code temporaire et expérimental
* Nettoyage régulier recommandé
* Migrer vers PROJECTS si ça devient sérieux

## Maintenance :
* Nettoyage mensuel recommandé
* Archiver ou supprimer l'ancien contenu
'@

        "04-EXTERNAL" = @'
# EXTERNAL - Code externe

Code provenant de sources externes.

## Structure :
* libraries/ - Librairies téléchargées
* samples/ - Exemples de code trouvés
* forks/ - Vos forks de projets externes
* references/ - Code de référence
* documentation/ - Documentation externe

## Versioning Git partiel :
* forks/ - OUI si vous modifiez
* samples/ - NON sauf si vous annotez
* libraries/ - NON (utiliser gestionnaires de paquets)

## Documentation :
* Noter la source originale
* Inclure les licences
* Dater les téléchargements
'@

        "05-ARCHIVE" = @'
# ARCHIVE - Archives et anciens projets

Stockage des anciens projets et fichiers à classer.

## Structure :
* old-projects/ - Anciens projets terminés
* deprecated/ - Code obsolète mais à conserver
* to-classify/ - En attente de classification
* backup/ - Sauvegardes diverses

## Versioning Git optionnel :
* Pour l'historique uniquement
* Pas de développement actif

## Maintenance :
* Révision annuelle
* Suppression définitive après 2-3 ans
* Compression des gros dossiers
'@

        "10-INSTALL" = @'
# INSTALL - Logiciels d'installation

Fichiers d'installation de logiciels.

## Structure :
* software/ - Installeurs de logiciels
* drivers/ - Pilotes matériels
* patches/ - Mises à jour et correctifs

## PAS de versioning Git :
* Fichiers binaires volumineux
* Utiliser un stockage cloud si besoin

## Organisation :
* Créer des sous-dossiers par logiciel
* Noter les versions et dates
* Nettoyer les anciennes versions
'@

        "11-UTILS" = @'
# UTILS - Utilitaires

Utilitaires et outils portables.

## Structure :
* portable/ - Logiciels portables
* system-tools/ - Outils système
* development-tools/ - Outils de développement

## PAS de versioning Git :
* Outils externes
* Mise à jour manuelle

## Conseils :
* Privilégier les versions portables
* Organiser par catégorie
* Maintenir une liste des outils installés
'@
    }
    
    foreach ($folder in $readmeContent.Keys) {
        $readmePath = Join-Path (Join-Path $Path $folder) "README.md"
        
        if ($WhatIfMode) {
            Write-Host "WHAT-IF: Creation du README $readmePath" -ForegroundColor Yellow
        } else {
            if (-not (Test-Path $readmePath)) {
                $readmeContent[$folder] | Out-File -FilePath $readmePath -Encoding UTF8
                Write-Host "README cree: $readmePath" -ForegroundColor Green
            } else {
                Write-Host "README existe deja: $readmePath" -ForegroundColor Yellow
            }
        }
    }
}

# Fonction pour créer le .gitignore global
function New-GlobalGitignore {
    param(
        [string]$Path,
        [bool]$WhatIfMode
    )
    
    $gitignoreContent = @'
# ===================================
# .gitignore global pour développement
# ===================================

# Dossiers sans versioning
/03-SANDBOX/
/10-INSTALL/
/11-UTILS/
/05-ARCHIVE/to-classify/

# Fichiers temporaires Windows
Thumbs.db
Desktop.ini
*.lnk

# Fichiers temporaires système
*.tmp
*.temp
*.log
*.bak
*.swp
*.swo
*~

# Fichiers d'installation
*.exe
*.msi
*.dmg
*.pkg
*.deb
*.rpm

# Archives
*.zip
*.rar
*.7z
*.tar
*.gz

# Fichiers IDE et éditeurs
.vscode/settings.json
.vscode/launch.json
.idea/
*.suo
*.user
*.cache

# Dossiers de build génériques
bin/
obj/
build/
dist/
out/

# Dossiers de dépendances
node_modules/
vendor/
packages/

# Fichiers de configuration locaux
.env
.env.local
config.local.*

# Fichiers de cache
.cache/
*.cache
.DS_Store
'@

    $gitignorePath = Join-Path $Path ".gitignore"
    
    if ($WhatIfMode) {
        Write-Host "WHAT-IF: Creation du .gitignore global $gitignorePath" -ForegroundColor Yellow
    } else {
        if (-not (Test-Path $gitignorePath)) {
            $gitignoreContent | Out-File -FilePath $gitignorePath -Encoding UTF8
            Write-Host ".gitignore global cree: $gitignorePath" -ForegroundColor Green
        } else {
            Write-Host ".gitignore global existe deja: $gitignorePath" -ForegroundColor Yellow
        }
    }
}

# Exécution principale
try {
    if ($WhatIf) {
        Write-Host "`nMODE SIMULATION - Aucun fichier ne sera cree" -ForegroundColor Magenta
    }
    
    # Vérifier que le répertoire de base existe
    if (-not (Test-Path $BasePath)) {
        if ($WhatIf) {
            Write-Host "WHAT-IF: Creation du repertoire de base $BasePath" -ForegroundColor Yellow
        } else {
            New-Item -ItemType Directory -Path $BasePath -Force | Out-Null
            Write-Host "Repertoire de base cree: $BasePath" -ForegroundColor Green
        }
    }
    
    Write-Host "`nCreation de la structure des dossiers..." -ForegroundColor Cyan
    New-DirectoryStructure -Path $BasePath -Structure $structure -WhatIfMode $WhatIf
    
    Write-Host "`nCreation des fichiers README..." -ForegroundColor Cyan
    New-ReadmeFiles -Path $BasePath -WhatIfMode $WhatIf
    
    Write-Host "`nCreation du .gitignore global..." -ForegroundColor Cyan
    New-GlobalGitignore -Path $BasePath -WhatIfMode $WhatIf
    
    if ($WhatIf) {
        Write-Host "`nSIMULATION TERMINEE" -ForegroundColor Green
        Write-Host "Pour creer reellement la structure, relancez sans le parametre -WhatIf" -ForegroundColor Yellow
    } else {
        Write-Host "`nSTRUCTURE CREEE AVEC SUCCES !" -ForegroundColor Green
        Write-Host "Emplacement: $BasePath" -ForegroundColor Cyan
        Write-Host "`nProchaines etapes recommandees:" -ForegroundColor Yellow
        Write-Host "  1. Deplacer vos projets existants dans les bons dossiers" -ForegroundColor White
        Write-Host "  2. Initialiser Git dans 01-PROJECTS/ et 02-TOOLS/" -ForegroundColor White
        Write-Host "  3. Configurer vos outils de developpement" -ForegroundColor White
        Write-Host "  4. Commencer a utiliser la nouvelle structure !" -ForegroundColor White
    }
    
} catch {
    Write-Error "Erreur lors de la creation: $($_.Exception.Message)"
    exit 1
}

Write-Host "`nScript termine avec succes !" -ForegroundColor Green