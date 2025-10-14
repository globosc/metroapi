# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requirements primero (para cache de Docker)
COPY requirements.txt /app/

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos los archivos de la aplicación
COPY *.py /app/

# Crea un usuario no-root para seguridad
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Cambia al usuario no-root
USER appuser

# Expone el puerto que usará la aplicación
EXPOSE 8080

# Variables de entorno para producción
ENV FLASK_ENV=production
ENV DEBUG=False

# Define el comando para ejecutar la aplicación
CMD ["python", "app.py"]
