import os
import json
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
import google.generativeai as genai
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

class ArmyService:
    """
    Servicio 'Ejército de IA' que utiliza múltiples modelos para 
    identificar si un código fue generado por IA.
    """

    @staticmethod
    async def _query_openai_compatible(client: AsyncOpenAI, model: str, code: str, name: str) -> Dict[str, Any]:
        """Helper para consultas a APIs compatibles con OpenAI."""
        try:
            prompt = (
                f"Actúa como un experto forense en código y detección de IA. Analiza si este código fue generado por un modelo de lenguaje.\n"
                f"CÓDIGO A ANALIZAR:\n{code}\n\n"
                f"RESPONDE UNICAMENTE CON UN JSON que tenga esta estructura exacta (Usa doble comillas, no comillas simples):\n"
                f"{{\n"
                f"  \"probability\": 95.5,\n"
                f"  \"reason\": \"explicación ejecutiva muy corta\",\n"
                f"  \"detected_model\": \"{name}\",\n"
                f"  \"evidence\": [\"lista de 3-5 evidencias técnicas detalladas como estructura, comentarios, patrones típicos de IA, etc\"],\n"
                f"  \"points_of_interest\": [\"puntos específicos o bloques de código que confirman la sospecha\"]\n"
                f"}}\n"
            )
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": "Eres un experto en seguridad y análisis de código IA."},
                          {"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error en {name}: {e}")
            return None

    @classmethod
    async def consult_openai(cls, code: str) -> Dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: return None
        client = AsyncOpenAI(api_key=api_key)
        return await cls._query_openai_compatible(client, "gpt-4o", code, "OpenAI GPT-4o")

    @classmethod
    async def consult_deepseek(cls, code: str) -> Dict[str, Any]:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key: return None
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        return await cls._query_openai_compatible(client, "deepseek-chat", code, "DeepSeek-V3")

    @classmethod
    async def consult_xai(cls, code: str) -> Dict[str, Any]:
        api_key = os.getenv("XAI_API_KEY")
        if not api_key: return None
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        return await cls._query_openai_compatible(client, "grok-2-latest", code, "xAI Grok-2")

    @classmethod
    async def consult_qwen(cls, code: str) -> Dict[str, Any]:
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key: return None
        # Qwen suele usarse via DashScope o proveedores como OpenRouter, 
        # asumiremos que es el API directo de Alibaba compatible
        client = AsyncOpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        return await cls._query_openai_compatible(client, "qwen-turbo", code, "Alibaba Qwen")

    @staticmethod
    async def consult_gemini(code: str) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
        if not api_key: return None
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = (
                f"Analiza este código forensemente. ¿Es IA? Responde solo JSON válido con doble comillas:\n"
                f"{{\n"
                f"  \"probability\": 85,\n"
                f"  \"reason\": \"resumen corto\",\n"
                f"  \"detected_model\": \"Gemini\",\n"
                f"  \"evidence\": [\"evidencia 1\", \"evidencia 2\", \"...\"],\n"
                f"  \"points_of_interest\": [\"bloque 1\", \"bloque 2\"]\n"
                f"}}\n\nCÓDIGO:\n{code}"
            )
            response = model.generate_content(prompt)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error Gemini: {e}")
            return None

    @staticmethod
    async def consult_groq(code: str) -> Dict[str, Any]:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key: return None
        try:
            client = AsyncGroq(api_key=api_key)
            prompt = (
                f"Expert AI Detection. Analyze this code. Response must be valid JSON only (use double quotes):\n"
                f"{{\n"
                f"  \"probability\": 80,\n"
                f"  \"reason\": \"brief explanation\",\n"
                f"  \"detected_model\": \"Llama-3-Groq\",\n"
                f"  \"evidence\": [\"technical evidence list\"],\n"
                f"  \"points_of_interest\": [\"specific code parts\"]\n"
                f"}}\n\nCODE:\n{code}"
            )
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error Groq: {e}")
            return None

    @classmethod
    async def get_consensus(cls, code: str) -> Dict[str, Any]:
        """
        Ejecuta las consultas disponibles en paralelo.
        """
        tasks = []
        # Añadir solo las que tengan llave configurada
        if os.getenv("OPENAI_API_KEY"): tasks.append(cls.consult_openai(code))
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY"): tasks.append(cls.consult_gemini(code))
        if os.getenv("GROQ_API_KEY"): tasks.append(cls.consult_groq(code))
        if os.getenv("DEEPSEEK_API_KEY"): tasks.append(cls.consult_deepseek(code))
        if os.getenv("XAI_API_KEY"): tasks.append(cls.consult_xai(code))
        if os.getenv("QWEN_API_KEY"): tasks.append(cls.consult_qwen(code))
        
        if not tasks:
            return {"army_score": 0, "army_verdict": "Sin llaves configuradas", "army_details": []}
            
        results = await asyncio.gather(*tasks)
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            return {"army_score": 0, "army_verdict": "Error en consultas", "army_details": []}
            
        avg_score = sum(r.get("probability", 0) for r in valid_results) / len(valid_results)
        
        return {
            "army_score": round(avg_score, 2),
            "army_verdict": "Plagio detectado por Ejército" if avg_score > 60 else "Parece Humano",
            "army_details": valid_results
        }
