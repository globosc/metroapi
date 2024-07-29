import requests
import json
from flask import Flask, jsonify

class MetroNetwork:
    def __init__(self, api_url='https://api.xor.cl/red/metro-network'):
        self.api_url = api_url

    def obtener_datos(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error al obtener los datos de la API: {e}")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar los datos de la API: {e}")
        return None

    def obtener_estado_estaciones(self):
        data = self.obtener_datos()
        if data and 'lines' in data:
            resultado = {}
            for line in data['lines']:
                line_name = line['name'].replace("Línea ", "L")
                line_status = "ok" if all(station['status'] == 0 for station in line.get('stations', [])) else "fail"
                resultado[line_name] = line_status
            return resultado
        else:
            print("No se pudieron obtener los datos de la red del metro.")
            return None

app = Flask(__name__)

@app.route('/metro', methods=['GET'])
def estado_metro():
    metro = MetroNetwork()
    estado = metro.obtener_estado_estaciones()
    if estado:
        return jsonify({"metro": estado})
    else:
        return jsonify({"error": "No se pudo obtener el estado del metro"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)

