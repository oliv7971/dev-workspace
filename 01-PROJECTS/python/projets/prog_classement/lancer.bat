@echo off
echo 🚀 LANCEUR DU SYSTÈME DE CLASSEMENT BURE
echo ========================================
echo.

:menu
echo ============================================
echo 🗂️  SYSTÈME DE CLASSEMENT BURE 
echo ============================================
echo [1] 🧪 Test et diagnostic du système
echo [2] ⚙️  Vérifier la configuration
echo [3] 🚀 Lancer le programme principal
echo [4] 📊 Voir les backups existants
echo [5] 📝 Aide et documentation
echo [0] ❌ Quitter
echo ============================================
echo.

set /p choix="Votre choix: "

if "%choix%"=="1" (
    echo.
    echo 🧪 LANCEMENT DU DIAGNOSTIC...
    py demo.py
    pause
    goto menu
)

if "%choix%"=="2" (
    echo.
    echo ⚙️  VÉRIFICATION DE LA CONFIGURATION...
    py diagnostic.py
    pause
    goto menu
)

if "%choix%"=="3" (
    echo.
    echo 🚀 LANCEMENT DU PROGRAMME PRINCIPAL...
    py src/main.py
    pause
    goto menu
)

if "%choix%"=="4" (
    echo.
    echo 📊 AFFICHAGE DES BACKUPS...
    if exist "C:\Backup\classement" (
        explorer "C:\Backup\classement"
        echo ✅ Dossier de backup ouvert dans l'explorateur
    ) else (
        echo ❌ Aucun backup trouvé
        echo Le dossier C:\Backup\classement n'existe pas encore
    )
    pause
    goto menu
)

if "%choix%"=="5" (
    echo.
    echo 📝 AIDE ET DOCUMENTATION
    echo ========================
    echo.
    echo 🎯 UTILISATION RECOMMANDÉE:
    echo 1. Commencer par [1] Test et diagnostic
    echo 2. Vérifier avec [2] Configuration  
    echo 3. Si tout est OK, utiliser [3] Programme principal
    echo.
    echo 📁 FICHIERS IMPORTANTS:
    echo • config/config.json        ← Configuration principale
    echo • config/categories.json    ← Types d'activités
    echo • config/correspondances.json ← Codes galeries
    echo.
    echo 💾 BACKUPS:
    echo • Localisation: C:\Backup\classement
    echo • Automatiques avant chaque opération
    echo • Gestion via menu [5] dans le programme principal
    echo.
    echo 📊 LOGS:
    echo • Localisation: C:\Temp\logs\classement
    echo • Trace de toutes les opérations
    echo.
    pause
    goto menu
)

if "%choix%"=="0" (
    echo.
    echo 👋 Au revoir !
    goto fin
)

echo ❌ Choix invalide
pause
goto menu

:fin