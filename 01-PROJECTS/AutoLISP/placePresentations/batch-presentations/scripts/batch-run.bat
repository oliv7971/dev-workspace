@echo off
REM Batch script to run the AutoLISP batch processing application

REM Set the path to the AutoLISP executable
set AUTOLISP_PATH="C:\Path\To\AutoLISP\Executable"

REM Set the path to the main AutoLISP script
set MAIN_SCRIPT="C:\Path\To\Your\Project\src\main.lsp"

REM Run the AutoLISP batch processing application
%AUTOLISP_PATH% %MAIN_SCRIPT%

REM Check if the execution was successful
if %errorlevel% neq 0 (
    echo Batch processing encountered an error.
    exit /b %errorlevel%
)

echo Batch processing completed successfully.