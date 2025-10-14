import requests
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Optional, List
from config import get_config

config = get_config()
logger = logging.getLogger(__name__)

class MetroService:
    def __init__(self, api_url: str = None):
        self.api_url = api_url or config.METRO_API_URL
        self.timeout = config.REQUEST_TIMEOUT
        self.max_retries = config.MAX_RETRIES

    def get_raw_data(self) -> Optional[Dict]:
        """Obtiene datos raw de la API externa"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Intentando obtener datos del metro (intento {attempt + 1})")
                response = requests.get(self.api_url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {attempt + 1}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Error de conexión en intento {attempt + 1}")
            except requests.exceptions.HTTPError as e:
                logger.error(f"Error HTTP {e.response.status_code}: {e}")
                break
            except json.JSONDecodeError:
                logger.error("Error al decodificar respuesta JSON")
                break
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                break

        logger.error("No se pudieron obtener los datos después de todos los intentos")
        return None

    def get_lines_status(self) -> Optional[Dict[str, str]]:
        """Obtiene el estado de todas las líneas del metro"""
        data = self.get_raw_data()
        if not data or 'lines' not in data:
            return None

        status = {}
        for line in data['lines']:
            line_name = line['name'].replace("Línea ", "L")
            stations = line.get('stations', [])

            # Verificar si todas las estaciones están operativas (status = 0)
            all_operational = all(station.get('status', 1) == 0 for station in stations)
            status[line_name] = "ok" if all_operational else "fail"

            # Log de estaciones con problemas
            failed_stations = [s['name'] for s in stations if s.get('status', 1) != 0]
            if failed_stations:
                logger.info(f"{line_name} - Estaciones con problemas: {failed_stations}")

        return status

    def get_failed_stations(self) -> Optional[Dict[str, List[str]]]:
        """Obtiene las estaciones con problemas por línea"""
        data = self.get_raw_data()
        if not data or 'lines' not in data:
            return None

        failed_by_line = {}
        for line in data['lines']:
            line_name = line['name'].replace("Línea ", "L")
            stations = line.get('stations', [])

            failed_stations = [
                station['name'] for station in stations
                if station.get('status', 1) != 0
            ]

            if failed_stations:
                failed_by_line[line_name] = failed_stations

        return failed_by_line

    def format_for_display(self) -> Optional[str]:
        """Formatea el estado para mostrar en consola con emojis"""
        status = self.get_lines_status()
        if not status:
            return None

        lines = ["Metro de Santiago:"]
        max_line_length = max(len(line) for line in status.keys()) + 1

        for line_name, line_status in status.items():
            emoji = "✅" if line_status == "ok" else "❌"
            lines.append(f"{line_name.ljust(max_line_length)}: {emoji}")

        return "\n".join(lines)

    def format_for_whatsapp(self) -> Optional[str]:
        """Formatea el estado específicamente para WhatsApp con emojis"""
        return self.format_for_display()

    def format_problems_only(self) -> Optional[str]:
        """Formatea solo los problemas - si todo está bien, mensaje corto; si hay problemas, detalle completo"""
        failed_stations = self.get_failed_stations()
        if failed_stations is None:
            return None

        if not failed_stations:
            return "✅ Metro de Santiago: Todas las líneas operativas"

        # Hay problemas - mostrar detalles
        lines = ["⚠️ Metro de Santiago - Problemas detectados:"]

        for line_name, stations in failed_stations.items():
            stations_text = ", ".join(stations)
            lines.append(f"❌ {line_name}: {stations_text}")

        return "\n".join(lines)

    def get_prometheus_metrics(self) -> Optional[str]:
        """Genera métricas en formato Prometheus para Grafana"""
        status = self.get_lines_status()
        failed_stations = self.get_failed_stations()

        if status is None:
            return None

        metrics = []

        # Métricas generales
        total_lines = len(status)
        operational_lines = sum(1 for s in status.values() if s == "ok")
        failed_lines = total_lines - operational_lines
        availability = (operational_lines / total_lines) * 100

        metrics.extend([
            "# HELP metro_total_lines Total number of metro lines",
            "# TYPE metro_total_lines gauge",
            f"metro_total_lines {total_lines}",
            "",
            "# HELP metro_operational_lines Number of operational metro lines",
            "# TYPE metro_operational_lines gauge",
            f"metro_operational_lines {operational_lines}",
            "",
            "# HELP metro_failed_lines Number of failed metro lines",
            "# TYPE metro_failed_lines gauge",
            f"metro_failed_lines {failed_lines}",
            "",
            "# HELP metro_availability_percentage Metro availability percentage",
            "# TYPE metro_availability_percentage gauge",
            f"metro_availability_percentage {availability:.2f}",
            "",
            "# HELP metro_line_status Status of individual metro lines (1=ok, 0=fail)",
            "# TYPE metro_line_status gauge"
        ])

        # Métricas por línea
        for line, line_status in status.items():
            value = 1 if line_status == "ok" else 0
            metrics.append(f'metro_line_status{{line="{line}"}} {value}')

        # Métricas de estaciones con problemas
        if failed_stations:
            metrics.extend([
                "",
                "# HELP metro_failed_stations_count Number of failed stations per line",
                "# TYPE metro_failed_stations_count gauge"
            ])

            for line, stations in failed_stations.items():
                metrics.append(f'metro_failed_stations_count{{line="{line}"}} {len(stations)}')

        return "\n".join(metrics)

    def get_summary(self) -> Optional[Dict]:
        """Obtiene un resumen completo del estado del metro optimizado para Grafana"""
        start_time = time.time()
        status = self.get_lines_status()
        failed_stations = self.get_failed_stations()

        if status is None:
            return None

        total_lines = len(status)
        operational_lines = sum(1 for s in status.values() if s == "ok")
        failed_lines = total_lines - operational_lines

        # Calcular métricas adicionales para Grafana
        availability_percentage = (operational_lines / total_lines) * 100
        response_time = round((time.time() - start_time) * 1000, 2)  # en millisegundos

        # Contar estaciones con problemas
        total_failed_stations = sum(len(stations) for stations in (failed_stations or {}).values())

        # Estado numérico para Grafana (más fácil para alertas)
        status_code = 2 if failed_lines == 0 else 1 if failed_lines < total_lines else 0

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "failed_stations": failed_stations or {},
            "metrics": {
                # Métricas principales para dashboards
                "total_lines": total_lines,
                "operational_lines": operational_lines,
                "failed_lines": failed_lines,
                "availability_percentage": round(availability_percentage, 2),
                "total_failed_stations": total_failed_stations,
                "response_time_ms": response_time,

                # Estados para alertas Grafana
                "status_code": status_code,  # 2=ok, 1=partial, 0=critical
                "overall_status": "ok" if failed_lines == 0 else "partial" if failed_lines < total_lines else "critical",

                # Métricas por línea para paneles individuales
                "lines_status": {
                    line: 1 if state == "ok" else 0
                    for line, state in status.items()
                }
            },
            "summary": {
                "message": f"{operational_lines}/{total_lines} líneas operativas",
                "severity": "success" if failed_lines == 0 else "warning" if failed_lines < 3 else "critical"
            }
        }