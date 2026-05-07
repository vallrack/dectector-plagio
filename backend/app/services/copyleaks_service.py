import os
import uuid
import logging
from dotenv import load_dotenv

# Copyleaks SDK
from copyleaks.copyleaks import Copyleaks
from copyleaks.exceptions.command_error import CommandError

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CopyleaksService:
    _auth_token = None

    @classmethod
    def _get_auth_token(cls):
        email = os.getenv("COPYLEAKS_EMAIL")
        api_key = os.getenv("COPYLEAKS_API_KEY")

        if not email or not api_key:
            logger.error("Faltan credenciales de Copyleaks en el archivo .env")
            return None

        # Si ya tenemos un token (en un entorno real deberíamos verificar si expiró tras 48h)
        if cls._auth_token:
            return cls._auth_token

        try:
            cls._auth_token = Copyleaks.login(email, api_key)
            logger.info("Autenticado exitosamente con Copyleaks API")
            return cls._auth_token
        except CommandError as ce:
            logger.error(f"Error al iniciar sesión en Copyleaks: {ce}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado con Copyleaks: {e}")
            return None

    @classmethod
    def analyze_code(cls, code: str) -> dict:
        """
        Analiza el código usando el detector de IA de Copyleaks.
        Retorna un diccionario con score, reasoning y modelo detectado.
        """
        auth_token = cls._get_auth_token()
        if not auth_token:
            return {"error": "No se pudo obtener el token de autenticación"}

        # Generar un ID único para este scan
        scan_id = str(uuid.uuid4())
        
        try:
            # sandbox=True para desarrollo, cambiar a False en producción para usar créditos reales.
            # Nota: Algunos tipos de cuenta requieren pasar el texto plano como diccionario o string directamente,
            # basándonos en la documentación actual del SDK.
            logger.info(f"Enviando código a Copyleaks AI Detector (Scan ID: {scan_id})")
            
            result = Copyleaks.ai_detector(
                auth_token, 
                scan_id, 
                code, 
                sandbox=True # Mantenemos en modo Sandbox mientras desarrollamos
            )
            
            # El resultado típicamente trae un formato como:
            # {'summary': {'human': 0.1, 'ai': 0.9}, 'matches': [...]}
            
            # Extraemos la puntuación (probability of AI)
            ai_probability = 0
            if isinstance(result, dict) and 'summary' in result:
                ai_probability = result['summary'].get('ai', 0)
            elif isinstance(result, dict) and 'probability' in result:
                ai_probability = result.get('probability', 0)
                
            score = ai_probability * 100
            
            return {
                "score": round(score, 2),
                "reasoning": "Analizado mediante Copyleaks AI Detection API.",
                "detected_model": "Copyleaks AI Detector",
                "raw_result": result
            }

        except CommandError as ce:
            logger.error(f"Copyleaks API Error: {ce}")
            return {"error": str(ce)}
        except Exception as e:
            logger.error(f"Error inesperado al llamar a Copyleaks ai_detector: {e}")
            return {"error": str(e)}
