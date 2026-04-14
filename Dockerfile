FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema (mínimas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copiar código fuente
COPY . .

# Usuario sin privilegios (buena práctica)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Puerto interno de la app
EXPOSE 5000

# Gunicorn para producción (4 workers)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "app:app"]
