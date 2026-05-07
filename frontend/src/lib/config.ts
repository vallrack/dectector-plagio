/**
 * Configuración dinámica del backend.
 */
const getBaseUrl = () => {
  const envUrl = process.env.NEXT_PUBLIC_API_URL;

  if (typeof window !== 'undefined') {
    // Si hay una variable de entorno definida (como en Render), usarla prioritariamente
    if (envUrl) {
      // Asegurarse de que tenga el protocolo
      return envUrl.startsWith('http') ? envUrl : `https://${envUrl}`;
    }

    // Si es localhost (desarrollo local)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
       return `http://${window.location.hostname}:8001`;
    }
    
    // Fallback: En la misma URL bajo /api (estilo Vercel Proxy)
    return `${window.location.protocol}//${window.location.host}/api`;
  }
  
  // SSR (Server Side Rendering)
  return envUrl || 'http://127.0.0.1:8001';
};

export const API_BASE_URL = getBaseUrl();

/**
 * Helper para obtener la URL completa de un endpoint.
 */
export const getApiUrl = (endpoint: string) => {
  const base = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Si estamos en Vercel, el endpoint ya incluye /api en el base, 
  // pero si el endpoint tambien empieza por /api, evitamos duplicarlo
  if (base.endsWith('/api') && path.startsWith('/api')) {
      return `${base}${path.substring(4)}`;
  }
  
  return `${base}${path}`;
};
