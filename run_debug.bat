@echo off
TITLE LuminaShield - Debug Mode
COLOR 0A
cls

echo ============================================================
echo      MODO DE DEPURACION - LUMINA SHIELD
echo ============================================================
echo.

echo [DEBUG] Iniciando script...
pause

:: 1. Intentar entrar a las carpetas
echo [DEBUG] Verificando carpetas...
if not exist "backend" echo [ERROR] Carpeta backend no encontrada & pause & exit
if not exist "frontend" echo [ERROR] Carpeta frontend no encontrada & pause & exit
echo [+] Carpetas encontradas.
pause

:: 2. Verificando Python
echo [DEBUG] Verificando Python...
python --version
if %errorlevel% neq 0 echo [ERROR] Python no funciona & pause & exit
pause

:: 3. Lanzar servidores sin limpieza de procesos para probar
echo [DEBUG] Lanzando servidores...

cd backend
echo [+] Entrando a backend...
if exist "venv\Scripts\python.exe" (
    echo [+] Usando venv existente...
    start "Lumina-Backend" cmd /c "venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 & pause"
) else (
    echo [ERROR] No existe venv en backend. Por favor ejecuta el instalador.
    pause
    exit
)
cd ..

cd frontend
echo [+] Entrando a frontend...
start "Lumina-Frontend" cmd /c "npm run dev & pause"
cd ..

echo.
echo ============================================================
echo    SERVIDORES LANZADOS EN VENTANAS SEPARADAS (TEMPORAL)
echo ============================================================
echo Si ves este mensaje, el problema era la unificacion.
echo.
pause
