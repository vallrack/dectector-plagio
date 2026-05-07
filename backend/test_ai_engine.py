from app.core.ai_engine import AIEngine

test_code = """
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test</title>
</head>
<body>
    <script>
        const items = [1, 2, 3];
        items.forEach(i => console.log(i));
    </script>
</body>
</html>
```
"""

result = AIEngine.detect_ai_signature(test_code)
print(f"Score: {result['score']}")
print(f"Model: {result['detected_model']}")
