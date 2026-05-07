@echo off
TITLE LuminaShield - Instalador y Reparador Universal
COLOR 0B
cls

echo ============================================================
echo      LUMINA SHIELD - INSTALADOR / REPARADOR v2.1
echo ============================================================
echo.
echo Este script configurara el entorno en esta nueva PC.
echo.

:: 1. Verificacion de Python
echo [*] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo.
    echo Por favor descarga e instala Python 3.10 o superior:
    echo URL: https://www.python.org/downloads/
    echo IMPORTANTE: Marca la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b
)
echo [+] Python detectado.

:: 2. Verificacion de Node
echo [*] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no esta instalado.
    echo.
    echo Por favor descarga e instala Node.js (Version LTS):
    echo URL: https://nodejs.org/
    echo.
    pause
    exit /b
)
echo [+] Node.js detectado.

:: 3. Reconfiguracion de Backend (venv)
echo.
echo [*] Configurando Backend (Python)...
cd backend

if exist "venv\" (
    echo [!] Verificando integridad del entorno virtual...
    venv\Scripts\python.exe --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] El entorno virtual esta corrupto o fue copiado de otro PC.
        echo [!] Recreando entorno para esta PC...
        rmdir /s /q venv
    ) else (
        echo [+] Entorno virtual OK.
    )
)

if not exist "venv\" (
    echo [+] Creando nuevo entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el venv. Asegurate de tener permisos.
        pause
        exit /b
    )
)

echo [+] Instalando/Actualizando dependencias del Backend...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar dependencias de Python.
    pause
    exit /b
)
cd ..

:: 4. Reconfiguracion de Frontend (node_modules)
echo.
echo [*] Configurando Frontend (Node)...
cd frontend

if not exist "node_modules\" (
    echo [+] Instalando dependencias del Frontend (esto tardara unos minutos)...
    call npm install
) else (
    echo [+] Modulos detectados. Verificando...
    :: Opcional: npm install es rapido si no hay cambios
    call npm install
)

if %errorlevel% neq 0 (
    echo [ERROR] Error al ejecutar npm install.
    pause
    exit /b
)
cd ..

echo.
echo ============================================================
echo    INSTALACION / REPARACION COMPLETADA
echo ============================================================
echo.
echo Ya puedes cerrar esta ventana y usar 'SUPREMO_LAUNCHER.bat'.
echo.
pause
