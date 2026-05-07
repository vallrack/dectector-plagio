#!/bin/bash

# Iniciar el Backend en segundo plano (puerto 8001)
echo "Iniciando Backend en puerto 8001..."
cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port 8001 &

# Esperar un poco para que el backend inicie
sleep 5

# Iniciar el Frontend en primer plano (puerto $PORT de Render)
echo "Iniciando Frontend en puerto $PORT..."
cd /app/frontend && npm start -- -p $PORT
