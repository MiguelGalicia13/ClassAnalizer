@echo off
setlocal

set "APP_ROOT=%~dp0"
cd /d "%APP_ROOT%"

if not exist "%APP_ROOT%uv.exe" (
    echo No se encontro uv.exe en la carpeta portable.
    pause
    exit /b 1
)

set "UV_PYTHON=3.12"
set "UV_PROJECT_ENVIRONMENT=%APP_ROOT%.venv"
set "UV_CACHE_DIR=%APP_ROOT%.uv-cache"

"%APP_ROOT%uv.exe" run --directory "%APP_ROOT%" classanalizer gui
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo ClassAnalizer termino con un error. Codigo: %EXIT_CODE%
    pause
)

endlocal & exit /b %EXIT_CODE%
