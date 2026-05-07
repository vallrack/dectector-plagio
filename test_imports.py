import os
import sys

# Intentar importar las librerías del "Ejército"
try:
    from openai import AsyncOpenAI
    print("[+] OpenAI: OK")
    import google.generativeai as genai
    print("[+] Google GenAI: OK")
    from groq import AsyncGroq
    print("[+] Groq: OK")
    from dotenv import load_dotenv
    print("[+] Dotenv: OK")
    print("\n[ÉXITO] Todas las librerías están instaladas correctamente.")
except ImportError as e:
    print(f"\n[ERROR] No se pudo encontrar una librería: {e}")
    print(f"Python Path: {sys.executable}")
except Exception as e:
    print(f"\n[ERROR INESPERADO]: {e}")
