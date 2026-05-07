"""Test de nuevas marcas: Grok, Groq, Qwen, DeepSeek"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.core.ai_engine import AIEngine

GROK_CODE = """
def fibonacci(n):
    # Let's generate the Fibonacci sequence up to n
    # Note: this works for positive integers only
    assert n > 0, 'n must be positive'
    sequence = [0, 1]
    while sequence[-1] < n:
        sequence.append(sequence[-2] + sequence[-1])
    # Example usage:
    # fibonacci(100) -> [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    return sequence

if __name__ == '__main__':
    print(fibonacci(100))
"""

GROQ_CODE = """
def process_student_grades(students, grades):
    # Initialize results container
    results = {}
    # Validate input lengths match
    if len(students) != len(grades):
        return None
    # Process each student-grade pair
    for idx, (student, grade) in enumerate(zip(students, grades)):
        # Calculate letter grade
        if grade >= 90:
            letter = 'A'
        elif grade >= 80:
            letter = 'B'
        else:
            letter = 'C'
        results[student] = letter
    # Return processed results
    return results
"""

QWEN_CODE = """
from typing import List, Optional

def buscar_maximo(lista: List[int]) -> Optional[int]:
    # 初始化结果变量
    result = None
    for idx, item in enumerate(lista):
        if result is None or item > result:
            result = item
    return result
"""

DEEPSEEK_CODE = """
import numpy as np
import pandas as pd

def normalize_matrix(X):
    mu = np.mean(X, axis=0)
    sigma = np.std(X, axis=0)
    sigma[sigma == 0] = 1
    X_norm = (X - mu) / sigma
    loss = np.sum((X_norm**2 + np.log(sigma**2)) * 0.5)
    grad = np.dot(X_norm.T, X_norm) / X.shape[0]
    return X_norm, loss, grad
"""

BLACKBOX_CODE = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<script>
// Step 1: Get elements
const btn = document.getElementById('btn');
const output = document.getElementById('output');
// Step 2: Add event listener
btn.addEventListener('click', function() {
  output.textContent = 'Clicked!';
});
// Step 3: Initialize
document.querySelector('.container').style.display = 'block';
</script>
</body>
</html>
"""

casos = [
    ("GROK (casual, assert, usage example)",         GROK_CODE),
    ("GROQ/LLAMA (systematic comments, enumerate)",  GROQ_CODE),
    ("QWEN (CJK comment, result=None, type hints)",  QWEN_CODE),
    ("DEEPSEEK (numpy, pandas, dense math)",         DEEPSEEK_CODE),
    ("BLACKBOX (Step 1/2/3, viewport, querySelector)", BLACKBOX_CODE),
]

print("=" * 62)
for label, code in casos:
    r = AIEngine.detect_ai_signature(code)
    print(f"\n[{label}]")
    print(f"  Score     : {r['score']}%")
    print(f"  Marca     : {r['detected_brand']}")
    print(f"  Version   : {r['detected_version']}")
    print(f"  Confianza : {r['attribution_confidence']}%")
    print(f"  Modelo    : {r['detected_model']}")
print("\n" + "=" * 62)
