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
            prompt = f"Analiza si este código fue generado por una IA. Responde UNICAMENTE con un JSON: {{'probability': float (0-100), 'reason': 'explicación corta', 'detected_model': '{name}'}}\n\nCÓDIGO:\n{code}"
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                # Algunos proveedores no soportan response_format json_object todavia
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
            model = genai.GenerativeModel('gemini-1.5-flash') # Flash es más rápido para esto
            prompt = f"Analiza este código. ¿Fue generado por IA? Responde solo con un JSON: {{'probability': valor_0_100, 'reason': 'explicación corta', 'detected_model': 'Gemini'}}\n\nCÓDIGO:\n{code}"
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
            prompt = f"Analiza si este código es IA. Responde solo JSON: {{'probability': 0-100, 'reason': '...', 'detected_model': 'Llama-3'}}\n\nCÓDIGO:\n{code}"
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
