@echo off
setlocal enabledelayedexpansion

set "APP_ROOT=%~dp0"
if "%APP_ROOT:~-1%"=="\" set "APP_ROOT=%APP_ROOT:~0,-1%"
cd /d "%APP_ROOT%"

set "UV_BIN=%APP_ROOT%\uv.exe"

if not exist "!UV_BIN!" (
    where.exe uv >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        set "UV_BIN=uv"
    ) else (
        echo [ClassAnalizer] uv.exe no fue encontrado en la carpeta del proyecto.
        echo [ClassAnalizer] Descargando uv para Windows...
        curl.exe -fL --retry 3 "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" -o "%TEMP%\uv-windows.zip"
        if !ERRORLEVEL! NEQ 0 (
            powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip' -OutFile '%TEMP%\uv-windows.zip'"
        )
        if exist "%TEMP%\uv-windows.zip" (
            tar.exe -xf "%TEMP%\uv-windows.zip" -C "%APP_ROOT%" uv.exe
            del "%TEMP%\uv-windows.zip"
        )
        if not exist "!UV_BIN!" (
            echo [ClassAnalizer] Error: No se pudo obtener uv.exe automaticamente.
            pause
            exit /b 1
        )
        echo [ClassAnalizer] uv.exe descargado correctamente.
    )
)

chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "UV_PYTHON=3.12"
set "UV_PROJECT_ENVIRONMENT=%APP_ROOT%\.venv"
set "UV_CACHE_DIR=%APP_ROOT%\.uv-cache"

if "%~1"=="" (
    "!UV_BIN!" run --directory "%APP_ROOT%" classanalizer gui
) else (
    "!UV_BIN!" run --directory "%APP_ROOT%" classanalizer %*
)
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo ClassAnalizer termino con un error. Codigo: %EXIT_CODE%
    pause
)

endlocal & exit /b %EXIT_CODE%

