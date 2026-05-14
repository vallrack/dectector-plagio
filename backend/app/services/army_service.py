import os
import json
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
import google.generativeai as genai
from groq import AsyncGroq
from anthropic import AsyncAnthropic
import cohere
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
                f"INSTRUCCIÓN CRÍTICA: Actúa como un experto forense de ÉLITE en detección de código generado por LLMs.\n"
                f"Tu misión es encontrar huellas sintéticas inconfundibles que un humano normalmente omitiría.\n\n"
                f"REGLA ESTRICTA ANTI-FALSO POSITIVO: NO asumas que un código es IA solo porque está ordenado, usa variables comunes (i, result, count) o sigue un tutorial de 'libro de texto'. Los estudiantes escriben así.\n"
                f"Para emitir una probabilidad mayor a 60%, DEBES identificar la FIRMA EXACTA de un modelo (ej. comentarios de pasos narrativos de ChatGPT, estilo hiper-condensado de Gemini, o verbosidad extrema de Claude). Si no hay una firma clara, asume que es HUMANO.\n\n"
                f"CÓDIGO A ANALIZAR:\n{code}\n\n"
                f"RESPONDE UNICAMENTE CON UN JSON (Doble comillas obligatorias):\n"
                f"{{\n"
                f"  \"probability\": 95.5,\n"
                f"  \"reason\": \"explicación técnica detallada en español\",\n"
                f"  \"detected_model\": \"{name}\",\n"
                f"  \"evidence\": [\"mínimo 3 evidencias forenses muy detalladas en español\"],\n"
                f"  \"points_of_interest\": [\"bloques de código específicos sospechosos\"]\n"
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
                f"ANÁLISIS FORENSE DE CÓDIGO: Tu objetivo es detectar si este código es producto de una IA (como tú).\n"
                f"REGLA ESTRICTA: NO marques un código como IA solo porque es ordenado o usa variables genéricas. Los estudiantes escriben así. Para una alta probabilidad, DEBES encontrar la FIRMA EXACTA de un modelo IA (ej. tu estilo, el de GPT, Claude). Si no ves una firma clara, asume que es Humano.\n"
                f"Responde SOLO JSON válido (doble comillas):\n"
                f"{{\n"
                f"  \"probability\": 90,\n"
                f"  \"reason\": \"por qué es IA\",\n"
                f"  \"detected_model\": \"Gemini\",\n"
                f"  \"evidence\": [\"evidencia 1\", \"evidencia 2\"],\n"
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
                f"Expert AI Detection. Analyze this code. STRICT RULE: Do not flag as AI just because it's clean, uses textbook patterns, or simple variables (like 'i', 'result'). Students code like this. To give >60% probability, you MUST identify an EXACT AI model signature (like ChatGPT narrative steps, Gemini condensed style). Otherwise, assume Human. Response must be valid JSON only (use double quotes):\n"
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

    @staticmethod
    async def consult_claude(code: str) -> Dict[str, Any]:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key: return None
        try:
            client = AsyncAnthropic(api_key=api_key)
            prompt = (
                f"Actúa como analista forense de IA. Analiza este código y determina si fue generado por un modelo de lenguaje.\n"
                f"REGLA ESTRICTA ANTI-FALSOS POSITIVOS: Los estudiantes humanos a menudo escriben código genérico, ordenado o 'de libro de texto'. NO marques esto como IA solo por eso. Para una probabilidad alta (>60%), DEBES identificar una FIRMA EXACTA e inconfundible de IA (ej. verbosidad típica tuya, o estilo de GPT). Si no, es Humano.\n"
                f"CÓDIGO:\n{code}\n\n"
                f"Responde SOLO con un JSON válido (usa doble comillas):\n"
                f"{{\n"
                f"  \"probability\": 90,\n"
                f"  \"reason\": \"explicación breve\",\n"
                f"  \"detected_model\": \"Claude-3\",\n"
                f"  \"evidence\": [\"evidencia 1\", \"...\"],\n"
                f"  \"points_of_interest\": [\"bloque 1\", \"...\"]\n"
                f"}}\n"
            )
            response = await client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error Claude: {e}")
            return None

    @staticmethod
    async def consult_cohere(code: str) -> Dict[str, Any]:
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key: return None
        try:
            co = cohere.AsyncClient(api_key=api_key)
            prompt = (
                f"Analiza si este código es generado por IA. REGLA ESTRICTA: No lo marques como IA solo porque esté bien indentado o use variables comunes. Exige encontrar una firma exacta de un LLM (estilo narrativo, comentarios excesivos). Si no, asume Humano. Responde solo JSON:\n"
                f"{{\n"
                f"  \"probability\": 80,\n"
                f"  \"reason\": \"resumen\",\n"
                f"  \"detected_model\": \"Cohere Command\",\n"
                f"  \"evidence\": [\"...\"],\n"
                f"  \"points_of_interest\": [\"...\"]\n"
                f"}}\n\nCÓDIGO:\n{code}"
            )
            response = await co.chat(
                message=prompt,
                model="command-r-plus"
            )
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Error Cohere: {e}")
            return None

    @classmethod
    async def _get_judge_verdict(cls, opinions: List[Dict[str, Any]], code: str) -> Dict[str, Any]:
        """
        Un modelo principal actúa de juez leyendo el código y el veredicto de los demás.
        Intentará usar OpenAI primero, luego Anthropic, luego Gemini, el que esté disponible.
        """
        opinions_text = "\n\n".join([
            f"Modelo del Jurado: {op.get('detected_model', 'Desconocido')}\n"
            f"Probabilidad de IA: {op.get('probability', 0)}%\n"
            f"Razonamiento: {op.get('reason', '')}\n"
            f"Evidencias: {', '.join(op.get('evidence', []))}"
            for op in opinions
        ])

        prompt = (
            f"INSTRUCCIÓN CRÍTICA: Eres el JUEZ FINAL de la Corte Suprema de IA forense.\n"
            f"Varios expertos (el Jurado) han analizado un código o texto sospechoso. Tu misión es leer sus opiniones, revisar el contenido original tú mismo, "
            f"y emitir un veredicto FINAL y DEFINITIVO sobre si el texto fue generado por IA o por un Humano.\n\n"
            f"OPINIONES DEL JURADO:\n{opinions_text}\n\n"
            f"CONTENIDO ORIGINAL A ANALIZAR:\n{code}\n\n"
            f"REGLA DE ORO ANTI-FALSO POSITIVO: Los estudiantes humanos a menudo escriben código 'de libro de texto' con variables genéricas (i, x, result). Si el jurado condenó el código basándose solo en que 'es muy ordenado' o 'no tiene errores humanos', DEBES CONTRADECIRLOS y bajar la probabilidad drásticamente. Para confirmar que es IA, debes poder identificar la FIRMA EXACTA de un LLM específico (ej. los comentarios narrativos de GPT, la verbosidad de Claude).\n"
            f"RESPONDE UNICAMENTE CON UN JSON VÁLIDO EN ESPAÑOL (Doble comillas obligatorias):\n"
            f"{{\n"
            f"  \"probability\": 90,\n"
            f"  \"reason\": \"Resumen del veredicto final del juez tras analizar el dictamen de los demás...\",\n"
            f"  \"detected_model\": \"Nombre del modelo responsable (o 'Humano')\",\n"
            f"  \"evidence\": [\"Evidencia clave confirmada\"]\n"
            f"}}\n"
        )

        try:
            # Seleccionar Juez por disponibilidad de llave
            if os.getenv("OPENAI_API_KEY"):
                client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Eres el Juez Supremo Forense."},
                              {"role": "user", "content": prompt}],
                )
                text = response.choices[0].message.content
            elif os.getenv("ANTHROPIC_API_KEY"):
                client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                response = await client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                text = response.content[0].text
            elif os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY"):
                api_k = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
                genai.configure(api_key=api_k)
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = await model.generate_content_async(prompt)
                text = response.text
            else:
                return None

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Error en Juez Final: {e}")
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
        if os.getenv("ANTHROPIC_API_KEY"): tasks.append(cls.consult_claude(code))
        if os.getenv("COHERE_API_KEY"): tasks.append(cls.consult_cohere(code))
        
        if not tasks:
            return {"army_score": 0, "army_verdict": "Sin llaves configuradas", "army_details": []}
            
        # Ejecutar con timeout de 20 segundos por archivo para no colgar el sistema
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=20.0)
        except asyncio.TimeoutError:
            print("Timeout en consultas del ejército")
            results = []
            
        valid_results = [r for r in results if r is not None]
        
        if not valid_results:
            return {"army_score": 0, "army_verdict": "Error en consultas", "army_details": []}

        # --- FASE 2: EL JUEZ ---
        # Si solo hay 1 modelo, el juez es redundante
        if len(valid_results) == 1:
            avg_score = valid_results[0].get("probability", 0)
            return {
                "army_score": round(avg_score, 2),
                "army_verdict": valid_results[0].get("reason", "Dictamen único"),
                "army_details": valid_results
            }

        judge_result = await cls._get_judge_verdict(valid_results, code)

        if judge_result:
            final_score = judge_result.get("probability", 0)
            # Agregar el dictamen del juez al principio de los detalles
            judge_result["detected_model"] = f"⚖️ JUEZ SUPREMO ({judge_result.get('detected_model', 'IA')})"
            judge_result["points_of_interest"] = ["Veredicto basado en consenso"]
            valid_results.insert(0, judge_result)

            return {
                "army_score": round(final_score, 2),
                "army_verdict": judge_result.get("reason", "Veredicto Conjunto"),
                "army_details": valid_results
            }
        else:
            # Fallback al promedio si el juez falla por timeout/error
            avg_score = sum(r.get("probability", 0) for r in valid_results) / len(valid_results)
            return {
                "army_score": round(avg_score, 2),
                "army_verdict": "Plagio detectado por Ejército (Promedio)" if avg_score > 60 else "Parece Humano",
                "army_details": valid_results
            }
