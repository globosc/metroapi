import requests
import json
import logging
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

    def get_summary(self) -> Optional[Dict]:
        """Obtiene un resumen completo del estado del metro"""
        status = self.get_lines_status()
        failed_stations = self.get_failed_stations()

        if status is None:
            return None

        total_lines = len(status)
        operational_lines = sum(1 for s in status.values() if s == "ok")

        return {
            "status": status,
            "failed_stations": failed_stations or {},
            "summary": {
                "total_lines": total_lines,
                "operational_lines": operational_lines,
                "failed_lines": total_lines - operational_lines,
                "overall_status": "ok" if operational_lines == total_lines else "partial"
            }
        }