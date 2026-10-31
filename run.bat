@echo off
title OptiDoc AI Enterprise - Launcher
chcp 65001 > nul
echo ========================================================
echo       OPTIDOC AI ENTERPRISE - URUCHAMIANIE APLIKACJI
echo ========================================================
echo.

set PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if not exist "%PYTHON_PATH%" (
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD="%PYTHON_PATH%"
)

:: Sprawdzenie zajętości portu 8501
netstat -ano | findstr /R /C:":8501 .*LISTENING" >nul
if %errorlevel% equ 0 (
    echo [INFO] Port 8501 jest zajęty przez inny projekt (np. Golem XV).
    echo [INFO] Uruchamiam OptiDoc AI na dedykowanym porcie 8502...
    set APP_PORT=8502
) else (
    echo [INFO] Port 8501 jest wolny. Uruchamiam OptiDoc AI na porcie 8501...
    set APP_PORT=8501
)

echo.
echo Adres aplikacji: http://localhost:%APP_PORT%
echo Trwa otwieranie przegladarki...
start http://localhost:%APP_PORT%

%PYTHON_CMD% -m streamlit run app.py --server.port %APP_PORT% --server.headless false --browser.gatherUsageStats false

pause
