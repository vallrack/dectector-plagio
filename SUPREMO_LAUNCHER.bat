@echo off
SETLOCAL EnableDelayedExpansion
TITLE LUMINA SHIELD - ULTRA LAUNCHER v3.1
cls

echo ============================================================
echo      LUMINA SHIELD - SISTEMA DE ARRANQUE v3.1
echo ============================================================
echo.

:: 1. VERIFICACION DE INTEGRIDAD
echo [!] FASE 1: VERIFICACION DE INTEGRIDAD
echo ------------------------------------------------------------

set NEEDS_REPAIR=0

:: Verificar Backend
if not exist "backend\venv\Scripts\python.exe" (
    echo [!] Backend: Entorno virtual no encontrado o roto.
    set NEEDS_REPAIR=1
) else (
    "backend\venv\Scripts\python.exe" --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [!] Backend: Entorno virtual incompatible con este PC.
        set NEEDS_REPAIR=1
    ) else (
        echo [+] Backend: Entorno OK.
    )
)

:: Verificar Frontend
if not exist "frontend\node_modules\" (
    echo [!] Frontend: Dependencias de Node no encontradas.
    set NEEDS_REPAIR=1
) else (
    echo [+] Frontend: Entorno OK.
)

if "%NEEDS_REPAIR%"=="1" (
    echo.
    echo [!] Se detectaron problemas en el entorno. Iniciando Reparador...
    timeout /t 3 >nul
    call installer.bat
    echo.
    echo [+] Reparacion finalizada. Reintentando arranque...
)

:: 2. LIBERAR PUERTOS
echo.
echo [!] FASE 2: LIMPIEZA DE PUERTOS
echo ------------------------------------------------------------

:: Matar procesos por puerto 3000 (Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    echo [*] Liberando puerto 3000 (PID %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

:: Matar procesos por puerto 8001 (Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
    echo [*] Liberando puerto 8001 (PID %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

echo [+] Puertos listos.

:: 3. ARRANQUE DE SERVIDORES
echo.
echo [!] FASE 3: DESPLIEGUE DE SERVICIOS
echo ------------------------------------------------------------

:: Iniciar Backend
echo [*] Lanzando Backend en puerto 8001...
cd backend
start "LUMINA-BACKEND" cmd /c "title BACKEND-CONSOLE && venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
cd ..

:: Iniciar Frontend
echo [*] Lanzando Frontend en puerto 3000...
cd frontend
start "LUMINA-FRONTEND" cmd /c "title FRONTEND-CONSOLE && npm run dev"
cd ..

:: 4. PORT POLLING (ESPERA INTELIGENTE)
echo.
echo [*] Esperando a que el servidor este listo...
echo (Esto puede tardar unos segundos segun la potencia de tu PC)

set MAX_RETRIES=30
set RETRY_COUNT=0

:POLL_LOOP
set /a RETRY_COUNT+=1
if %RETRY_COUNT% gtr %MAX_RETRIES% (
    echo.
    echo [ERROR] El servidor tardo demasiado en arrancar.
    echo [!] Por favor revisa las ventanas de consola que se abrieron.
    pause
    exit /b
)

:: Intentar conectar al puerto 3000 usando powershell
powershell -Command "$c = New-Object System.Net.Sockets.TcpClient; $c.Connect('127.0.0.1', 3000); if($c.Connected){$c.Close(); exit 0} else {exit 1}" >nul 2>&1

if %errorlevel% neq 0 (
    set /p "=[.]" <nul
    timeout /t 2 >nul
    goto POLL_LOOP
)

echo.
echo [+] Servidor detectado y respondiendo!

:: 5. FINALIZACION
echo.
echo ============================================================
echo      LUMINA SHIELD ESTA EN LINEA - ABRIENDO NAVEGADOR
echo ============================================================
echo.

start http://localhost:3000

echo Puedes cerrar este monitor. Las consolas de los servidores
echo deben permanecer abiertas mientras uses el sistema.
echo.
pause
exit
