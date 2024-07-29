import requests
import json
import logging

class MetroNetwork:
    def __init__(self, api_url='https://api.xor.cl/red/metro-network'):
        self.api_url = api_url

    def obtener_datos(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error al obtener los datos de la API: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Error al decodificar los datos de la API: {e}")
        return None

    def mostrar_estado_estaciones(self):
        data = self.obtener_datos()
        if data and 'lines' in data:
            mensaje = "Metro de Santiago:\n"
            max_line_length = max(len(line['name']) for line in data['lines']) + 1
            for line in data['lines']:
                line_name = line['name'].replace("Línea ", "L")
                line_status = "✅"
                estaciones_falla = [station['name'] for station in line.get('stations', []) if station['status'] != 0]

                if estaciones_falla:
                    line_status = "❌"
                mensaje += f"{line_name.ljust(max_line_length)}: {line_status}\n"
            return mensaje
        else:
            logging.warning("No se pudieron obtener los datos de la red del metro.")
            return None

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Ejemplo de uso
if __name__ == "__main__":
    metro = MetroNetwork()
    estado_metro = metro.mostrar_estado_estaciones()
    if estado_metro:
        print(estado_metro)
