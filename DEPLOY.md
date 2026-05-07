# Guía de Despliegue en Vercel - Lumina Shield

He preparado el proyecto para que pueda funcionar tanto en tu PC localmente como en la nube usando Vercel.

## Requisitos Previos

1.  **Cuenta en Vercel**: [vercel.com](https://vercel.com/)
2.  **Base de Datos en la Nube (CRÍTICO)**: 
    Vercel no permite guardar archivos locales como `plagiarism_detector.db`. Necesitas una base de datos PostgreSQL.
    - Opción recomendada: **Supabase** (Gratis y fácil).
    - Crea un proyecto en Supabase, ve a **Settings > Database** y copia la **Connection String** (formato `postgresql://...`).

## Pasos para Desplegar

### 1. Preparar el Repositorio
Sube tu carpeta `detector-plagio-ia` a un repositorio de GitHub (privado o público).

### 2. Importar en Vercel
1. Ve a tu Dashboard de Vercel y dale a **"Add New > Project"**.
2. Selecciona tu repositorio de GitHub.
3. Vercel detectará el proyecto. Asegúrate de que el **Root Directory** sea la carpeta raíz (donde ahora están `vercel.json` y `api/`).

### 3. Configurar Variables de Entorno (Environment Variables)
Antes de darle a Deploy, añade estas variables en la configuración de Vercel:

| Variable | Valor |
| :--- | :--- |
| `DATABASE_URL` | La URL de tu base de datos de Supabase. |
| `COPYLEAKS_EMAIL` | Tu email de Copyleaks. |
| `COPYLEAKS_API_KEY` | Tu API Key de Copyleaks. |

### 4. Deploy
Dale al botón **Deploy**. Vercel instalará las dependencias de Python y de Node.js automáticamente.

---

## Cómo seguir trabajando localmente

No te preocupes, **nada ha cambiado para tu PC**.
- Puedes seguir usando **`SUPREMO_LAUNCHER.bat`**.
- El código es inteligente: si no detecta la variable `DATABASE_URL`, seguirá usando tu archivo local `plagiarism_detector.db`.

## Estructura de Archivos para Vercel (Creados por mí)
- `/api/index.py`: El puente para que el servidor de Python corra en Vercel.
- `vercel.json`: La configuración de rutas y despliegue.
- `requirements.txt` (en la raíz): Lista de librerías para que Vercel las instale.
