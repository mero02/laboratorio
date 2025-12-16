FROM python:3.10-slim

# Instalar herramientas SNMP
RUN apt-get update && apt-get install -y \
    snmp \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar app
COPY app.py .
COPY instrumentation.py .

# Copiar templates y static
COPY templates/ ./templates/
COPY static/ ./static/

EXPOSE 5000

CMD ["python", "app.py"]
