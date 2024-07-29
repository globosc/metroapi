import requests
import json

class MetroNetwork:
    def __init__(self, api_url='https://api.xor.cl/red/metro-network'):
        self.api_url = api_url

    def obtener_datos(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"No se pudo obtener los datos de la API: {e}")
            return None

    def mostrar_estado_estaciones(self):
        data = self.obtener_datos()
        if data:
            mensaje = "Metro de Santiago:\n"
            max_line_length = max(len(line['name']) for line in data.get('lines', [])) + 1
            for line in data.get('lines', []):
                line_name = line['name'].replace("Línea ", "L")
                line_status = "✅"
                estaciones_falla = [station['name'] for station in line.get('stations', []) if station['status'] != 0]

                if estaciones_falla:
                    line_status = "❌"
                mensaje += f"{line_name.ljust(max_line_length)}: {line_status}\n"
            return mensaje
        else:
            print("No se pudieron obtener los datos de la red del metro.")
            return None

# Ejemplo de uso
if __name__ == "__main__":
    metro = MetroNetwork()
    estado_metro = metro.mostrar_estado_estaciones()
    if estado_metro:
        print(estado_metro)
