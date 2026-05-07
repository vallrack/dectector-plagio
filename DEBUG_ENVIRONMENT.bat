@echo off
TITLE LuminaShield - Diagnostico de Entorno
COLOR 0D
cls

echo ============================================================
echo      DIAGNOSTICO DE SISTEMA - LUMINA SHIELD
echo ============================================================
echo.

echo [1] VERIFICACION DE HERRAMIENTAS GLOBALES
echo ------------------------------------------
echo | Python: 
python --version 2>&1 || echo NO INSTALADO
echo | Node:
node -v 2>&1 || echo NO INSTALADO
echo | NPM:
call npm -v 2>&1 || echo NO INSTALADO
echo.

echo [2] ESTRUCTURA DEL PROYECTO
echo ------------------------------------------
if exist "backend\" (echo [+] Carpeta Backend encontrada) else (echo [!] Carpeta Backend NO ENCONTRADA)
if exist "frontend\" (echo [+] Carpeta Frontend encontrada) else (echo [!] Carpeta Frontend NO ENCONTRADA)
if exist "backend\venv\" (echo [+] VENV encontrado) else (echo [!] VENV NO ENCONTRADO)
if exist "frontend\node_modules\" (echo [+] Node Modules encontrados) else (echo [!] Node Modules NO ENCONTRADOS)
echo.

echo [3] VERIFICACION DE INTEGRIDAD VENV
echo ------------------------------------------
if exist "backend\venv\Scripts\python.exe" (
    backend\venv\Scripts\python.exe --version 2>&1
    if %errorlevel% neq 0 (echo [!] ERROR: El VENV no funciona en este PC) else (echo [+] VENV es funcional)
) else (
    echo [!] ERROR: No existe el ejecutable de Python en el VENV
)
echo.

echo [4] ESTADO DE PUERTOS
echo ------------------------------------------
netstat -aon | findstr :3000 && echo [!] Puerto 3000 OCUPADO || echo [+] Puerto 3000 LIBRE
netstat -aon | findstr :8001 && echo [!] Puerto 8001 OCUPADO || echo [+] Puerto 8001 LIBRE
echo.

echo ============================================================
echo      FIN DEL DIAGNOSTICO
echo ============================================================
echo.
echo Presiona una tecla para salir...
pause >nul
