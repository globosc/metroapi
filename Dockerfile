# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de la aplicación al contenedor
COPY main.py /app
COPY requirements.txt /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usará la aplicación
EXPOSE 8080

# Define el comando para ejecutar la aplicación
CMD ["python", "main.py"]
