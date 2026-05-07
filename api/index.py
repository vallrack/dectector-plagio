import sys
import os

# Añadir la carpeta backend al path para que Python encuentre 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app

# Vercel espera que la aplicacion este en una variable llamada 'app'
# pero opcionalmente podemos exponerla como handler
handler = app
