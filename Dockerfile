# syntax=docker/dockerfile:1

# Etapa 1: Build del Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
ENV NEXT_DISABLE_ESLINT=1
RUN npm run build

# Etapa 2: Runtime Final
FROM python:3.10-slim
WORKDIR /app

# Instalar Node.js en la imagen de Python para ejecutar el frontend
RUN mkdir -p /app/storage && chmod 777 /app/storage
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias del backend
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el backend
COPY backend/ ./backend/

# Copiar el frontend compilado y sus dependencias desde la etapa 1
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/node_modules ./frontend/node_modules

# Copiar el script de inicio
COPY start.sh ./
RUN chmod +x start.sh

# Exponer los puertos (aunque Render usa $PORT)
EXPOSE 8001
EXPOSE 3000

CMD ["./start.sh"]
