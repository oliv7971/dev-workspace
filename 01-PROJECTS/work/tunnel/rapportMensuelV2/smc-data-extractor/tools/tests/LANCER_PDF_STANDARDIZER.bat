@echo off
chcp 65001 >nul
echo ========================================
echo     PDF STANDARDIZER - Rapports BURE
echo ========================================
echo.

cd /d "C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\smc-data-extractor"

echo Activation de l'environnement Python...
call "C:\data\20-DEVELOPPEMENT\01-PROJECTS\python\projets\rapportMensuelV2\.venv\Scripts\activate.bat"

echo.
echo Lancement du PDF Standardizer...
echo.
python run_pdf_standardizer_windows.py

echo.
echo Appuyez sur une touche pour fermer...
pause >nul