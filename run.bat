@echo off
TITLE LuminaShield Launcher
COLOR 0A
cls

echo [+] Iniciando LuminaShield...

:: Validacion de existencia de entornos
if not exist "backend\venv\" (
    echo [ERROR] No se encontro el entorno virtual en 'backend\venv'.
    echo Por favor, ejecuta primero 'installer.bat' para configurar esta PC.
    pause
    exit /b
)

if not exist "frontend\node_modules\" (
    echo [ERROR] No se encontraron los modulos de Node en 'frontend\node_modules'.
    echo Por favor, ejecuta primero 'installer.bat' para configurar esta PC.
    pause
    exit /b
)

:: 1. Backend
echo [+] Iniciando Backend en puerto 8001...
cd backend
start "Lumina-Backend" cmd /c "venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
cd ..

:: 2. Frontend
echo [+] Iniciando Frontend en puerto 3000...
cd frontend
echo [INFO] La aplicacion se abrira en una nueva ventana.
start "Lumina-Frontend" cmd /c "npm run dev"
cd ..

echo.
echo ==========================================
echo    SISTEMA INICIADO CORRECTAMENTE
echo ==========================================
echo.
echo Se han abierto dos ventanas adicionales con los servidores.
echo Puedes cerrar esta ventana.
echo.
pause
