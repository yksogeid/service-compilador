# Etapa de construcción
FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependencias de sistema necesarias para matplotlib
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Etapa de producción
FROM python:3.10-slim

WORKDIR /app

# Copiar dependencias instaladas desde la etapa de construcción
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "api_service.py"]