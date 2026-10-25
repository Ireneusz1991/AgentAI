@echo off
title Wdrozenie AI MSP - Piaskownica
chcp 65001 > nul
echo ========================================================
echo   Uruchamianie Piaskownicy Wdrozeniowej AI dla MSP
echo ========================================================
echo.

set PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

if not exist "%PYTHON_PATH%" (
    python -m streamlit run app.py
) else (
    "%PYTHON_PATH%" -m streamlit run app.py
)

pause
