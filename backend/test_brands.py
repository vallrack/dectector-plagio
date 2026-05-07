"""
Test de detección de marcas de IA.
Ejecutar desde: backend/  con  venv\Scripts\python.exe test_brands.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.ai_engine import AIEngine

# ── Muestras de código ────────────────────────────────────────────────────────

GEMINI_CODE = """
import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('App')
        self.lbl = tk.Label(self, text=f'Hola')
        self.lbl.pack()
        self.btn = tk.Button(self, text='Click', command=self.on_click)
        self.btn.pack()
    def on_click(self): self.lbl.config(text=f'Clicked {len(self.lbl.cget("text"))}')

app = App(); app.mainloop()
"""

CHATGPT_CODE = """
def calculate_average(numbers):
    \"\"\"
    Calculate the average of a list of numbers.
    Returns the mean value as a float.
    \"\"\"
    # Ensure the list is not empty
    if not numbers:
        return 0.0
    total = sum(numbers)
    count = len(numbers)
    result = total / count
    return result

if __name__ == '__main__':
    data = [10, 20, 30, 40, 50]
    output = calculate_average(data)
    print(f'Average: {output}')
"""

CLAUDE_CODE = """
from typing import Optional, List

def find_maximum_subarray(
    numbers: List[float],
    allow_empty: bool = False,
) -> Optional[float]:
    \"\"\"
    Find the maximum contiguous subarray sum using Kadane's algorithm.
    This approach works because we only carry forward a running sum
    when it is positive — negative prefixes are never beneficial.
    \"\"\"
    if not numbers:
        return None if not allow_empty else 0.0

    maximum_ending_here: float = numbers[0]
    global_maximum: float = numbers[0]

    for current_value in numbers[1:]:
        maximum_ending_here = max(current_value, maximum_ending_here + current_value)
        global_maximum = max(global_maximum, maximum_ending_here)

    return global_maximum
"""

# Código Gemini con 4 variables renombradas por el humano
HUMAN_MODIFIED = """
import tkinter as tk

class Ventana(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mi app')
        self.etiqueta = tk.Label(self, text=f'Hola mundo')
        self.etiqueta.pack()
        self.boton = tk.Button(self, text='Presionar', command=self.al_hacer_click)
        self.boton.pack()
    def al_hacer_click(self): self.etiqueta.config(text=f'Presionado')

ventana = Ventana(); ventana.mainloop()
"""

HUMAN_CODE = """
# Mi solución al ejercicio de burbuja
numeros = [5, 3, 8, 1, 9, 2]
for i in range(len(numeros)):
    for j in range(i+1, len(numeros)):
        if numeros[i] > numeros[j]:
            # intercambio manual
            aux = numeros[i]
            numeros[i] = numeros[j]
            numeros[j] = aux
print("Ordenados:", numeros)
"""

# ── Ejecutar ──────────────────────────────────────────────────────────────────

casos = [
    ("GEMINI (condensado, tk/self, sin comentarios)", GEMINI_CODE),
    ("CHATGPT (docstring, main, vars en inglés)",      CHATGPT_CODE),
    ("CLAUDE (Optional, verbose vars, narrativo)",     CLAUDE_CODE),
    ("HUMANO MODIFICADO (4 vars renombradas)",         HUMAN_MODIFIED),
    ("HUMANO REAL (bubble sort manual)",               HUMAN_CODE),
]

print("=" * 65)
for label, code in casos:
    r = AIEngine.detect_ai_signature(code)
    print(f"\n[{label}]")
    print(f"  Score        : {r['score']}%")
    print(f"  Entropia     : {r['entropy']}")
    print(f"  Marca        : {r['detected_brand']}")
    print(f"  Version      : {r['detected_version']}")
    print(f"  Confianza    : {r['attribution_confidence']}%")
    print(f"  Modelo final : {r['detected_model']}")
    print(f"  Color        : {r['brand_color']}")
print("\n" + "=" * 65)
