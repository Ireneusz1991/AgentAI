@echo off
chcp 65001 >nul
echo ========================================================
echo       OPTIDOC AI - AUTOMATYCZNA SYNCHRONIZACJA GITHUB
echo ========================================================
echo.

set GIT="c:\Antigravity\MinGit\cmd\git.exe"

echo [1/3] Sprawdzanie zmian w projekcie...
%GIT% status -s

echo.
echo [2/3] Zapisywanie zmian lokalnie...
%GIT% add -A
set MSG=auto-sync: %date% %time%
%GIT% commit -m "%MSG%" 2>nul
if %errorlevel% neq 0 (
    echo Brak nowych zmian do zatwierdzenia.
) else (
    echo Zmiany zatwierdzone pomyslnie.
)

echo.
echo [3/3] Wysylanie do zdalnego repozytorium GitHub...
%GIT% push origin main

echo.
echo ========================================================
echo   SYNCHRONIZACJA ZAKONCZONA POMYSLNIE!
echo   Repozytorium: https://github.com/Ireneusz1991/AgentAI
echo ========================================================
pause
