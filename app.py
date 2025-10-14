from flask import Flask, jsonify, request
import logging
from metro_service import MetroService
from config import get_config

config = get_config()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # Configurar logging
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT
    )

    metro_service = MetroService()

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "service": "metro-api"}), 200

    @app.route('/metro', methods=['GET'])
    def get_metro_status():
        """Endpoint principal - estado de líneas del metro"""
        try:
            status = metro_service.get_lines_status()
            if status is None:
                return jsonify({
                    "error": "No se pudo obtener el estado del metro",
                    "details": "Error al conectar con la API externa"
                }), 503

            return jsonify({"metro": status}), 200

        except Exception as e:
            app.logger.error(f"Error interno en /metro: {e}")
            return jsonify({
                "error": "Error interno del servidor",
                "details": str(e)
            }), 500

    @app.route('/metro/summary', methods=['GET'])
    def get_metro_summary():
        """Endpoint con resumen completo del metro"""
        try:
            summary = metro_service.get_summary()
            if summary is None:
                return jsonify({
                    "error": "No se pudo obtener el resumen del metro"
                }), 503

            return jsonify(summary), 200

        except Exception as e:
            app.logger.error(f"Error interno en /metro/summary: {e}")
            return jsonify({
                "error": "Error interno del servidor"
            }), 500

    @app.route('/metro/display', methods=['GET'])
    def get_metro_display():
        """Endpoint que retorna formato de texto para mostrar"""
        try:
            display_text = metro_service.format_for_display()
            if display_text is None:
                return jsonify({
                    "error": "No se pudo obtener el estado del metro"
                }), 503

            return {"display": display_text, "format": "text"}, 200

        except Exception as e:
            app.logger.error(f"Error interno en /metro/display: {e}")
            return jsonify({
                "error": "Error interno del servidor"
            }), 500

    @app.route('/metro/whatsapp', methods=['GET'])
    def get_metro_whatsapp():
        """Endpoint específico para WhatsApp con emojis - respuesta en texto plano"""
        try:
            whatsapp_text = metro_service.format_for_whatsapp()
            if whatsapp_text is None:
                return "❌ No se pudo obtener el estado del metro", 503

            # Retorna texto plano directamente
            return whatsapp_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

        except Exception as e:
            app.logger.error(f"Error interno en /metro/whatsapp: {e}")
            return "❌ Error interno del servidor", 500, {'Content-Type': 'text/plain; charset=utf-8'}

    @app.route('/metro/problems', methods=['GET'])
    def get_metro_problems():
        """Endpoint que solo muestra problemas - texto plano"""
        try:
            problems_text = metro_service.format_problems_only()
            if problems_text is None:
                return "❌ No se pudo obtener el estado del metro", 503

            # Retorna texto plano directamente
            return problems_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

        except Exception as e:
            app.logger.error(f"Error interno en /metro/problems: {e}")
            return "❌ Error interno del servidor", 500, {'Content-Type': 'text/plain; charset=utf-8'}

    @app.route('/metrics', methods=['GET'])
    def get_prometheus_metrics():
        """Endpoint de métricas Prometheus para Grafana"""
        try:
            metrics_text = metro_service.get_prometheus_metrics()
            if metrics_text is None:
                return "# No metrics available", 503, {'Content-Type': 'text/plain; charset=utf-8'}

            # Retorna métricas en formato Prometheus
            return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

        except Exception as e:
            app.logger.error(f"Error interno en /metrics: {e}")
            return "# Error generating metrics", 500, {'Content-Type': 'text/plain; charset=utf-8'}

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint no encontrado",
            "available_endpoints": [
                "/health",
                "/metro",
                "/metro/summary",
                "/metro/display",
                "/metro/whatsapp",
                "/metro/problems",
                "/metrics"
            ]
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Error 500: {error}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )