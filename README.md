# Metro Santiago API

API moderna y escalable para consultar el estado del Metro de Santiago en tiempo real.

## 🚀 Características

- **API REST** con múltiples endpoints
- **CLI completa** con diferentes formatos de salida
- **Manejo robusto de errores** con reintentos automáticos
- **Logging estructurado** configurable
- **Arquitectura modular** fácil de extender

## 📡 Endpoints API

```bash
GET /health          # Health check
GET /metro           # Estado básico de líneas
GET /metro/summary   # Resumen completo con estadísticas
GET /metro/display   # Formato texto para mostrar
```

## 🖥️ Uso CLI

```bash
# Estado básico
python3 cli.py

# Resumen completo
python3 cli.py --summary

# Solo líneas con problemas
python3 cli.py --failed-only

# Formato JSON
python3 cli.py --format json

# Ayuda completa
python3 cli.py --help
```

## ⚙️ Instalación

```bash
pip install -r requirements.txt
python3 app.py
```

## 🔧 Configuración

Variables de entorno disponibles:
- `PORT` - Puerto del servidor (default: 8080)
- `DEBUG` - Modo debug (default: True)
- `FLASK_ENV` - Entorno (development/production)

## 🏗️ Arquitectura

```
├── config.py         # Configuración centralizada
├── metro_service.py  # Lógica de negocio
├── app.py           # API Flask
├── cli.py           # Interfaz CLI
└── requirements.txt # Dependencias
```

## 💡 Ideas de Expansión

- **Buses RED**: Agregar estado de buses de Santiago
- **Trenes EFE**: Estado de trenes regionales
- **Alertas**: Notificaciones push/email
- **Histórico**: Base de datos con tendencias
- **Mapas**: Visualización interactiva
- **API Premium**: Límites de rate, analytics