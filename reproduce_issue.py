from backend.app.core.ai_engine import AIEngine

chatgpt_code = """
<!DOCTYPE html>
<html>
<head>
    <title>Ejercicio ChatGPT</title>
</head>
<body>
    <input type="number" id="numeroInput" placeholder="Ingresa un número">
    <button onclick="agregarNumero()">Agregar</button>
    <ul id="lista"></ul>

    <p id="suma"></p>
    <p id="maximo"></p>
    <p id="pares"></p>

    <script>
        let numeros = [];

        function agregarNumero() {
            const input = document.getElementById("numeroInput");
            const valor = Number(input.value);
            
            if (!isNaN(valor)) {
                numeros.push(valor);
                actualizarInterfaz();
                input.value = "";
            }
        }

        function actualizarInterfaz() {
            const lista = document.getElementById("lista");
            lista.innerHTML = "";
            
            let suma = 0;
            let max = -Infinity;
            let pares = [];

            numeros.forEach(n => {
                const li = document.createElement("li");
                li.textContent = n;
                lista.appendChild(li);
                
                suma += n;
                if (n > max) max = n;
                if (n % 2 === 0) pares.push(n);
            });

            document.getElementById("suma").textContent = "Suma: " + suma;
            document.getElementById("maximo").textContent = "Máximo: " + max;
            document.getElementById("pares").textContent = "Pares: " + pares.join(", ");
        }
    </script>
</body>
</html>
"""

result = AIEngine.detect_ai_signature(chatgpt_code)
print(f"Entropy: {result['entropy']}")
print(f"Score: {result['score']}%")
print(f"Model: {result['detected_model'] if result['detected_model'] else 'No Identificado'}")
