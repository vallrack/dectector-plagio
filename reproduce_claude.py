from backend.app.core.ai_engine import AIEngine

claude_code = """
# Ejercicio: Generador de tabla de multiplicar
# Escribe una función que reciba un número y muestre su tabla de multiplicar del 1 al 10

def tabla_multiplicar(n):
    for i in range(1, 11):
        print(f"{n} x {i} = {n * i}")

numero = int(input("Ingresa un número: "))
tabla_multiplicar(numero)
"""

result = AIEngine.detect_ai_signature(claude_code)
print(f"Entropy: {result['entropy']}")
print(f"Score: {result['score']}%")
print(f"Model: {result['detected_model'] if result['detected_model'] else 'No Identificado'}")
