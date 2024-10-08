# Autor: Jonathan Hernández
# Fecha: 23 Septiembre 2024
# Descripción: Código para rutas gps v2.
# GitHub: https://github.com/Jona163

from flask import Flask, render_template, request, jsonify
from math import radians, sin, cos, sqrt, atan2, exp
import random

app = Flask(__name__)

# Coordenadas de las ciudades
coord = {
    'Aguascalientes': [21.87641043660486, -102.26438663286967],
    'BajaCalifornia': [32.5027, -117.00371],
    'BajaCaliforniaSur': [24.14437, -110.3005],
    'Campeche': [19.8301, -90.53491],
    'Chiapas': [16.75, -93.1167],
    'Chihuahua': [28.6353, -106.0889],
    'CDMX': [19.432713075976878, -99.13318344772986],
    'Coahuila': [25.4260, -101.0053],
    'Colima': [19.2452, -103.725],
    'Durango': [24.0277, -104.6532],
    'Guanajuato': [21.0190, -101.2574],
    'Guerrero': [17.5506, -99.5024],
    'Hidalgo': [20.1011, -98.7624],
    'Jalisco': [20.6767, -103.3475],
    'Mexico': [19.285, -99.5496],
    'Michoacan': [19.701400113725654, -101.20829680213464],
    'Morelos': [18.6813, -99.1013],
    'Nayarit': [21.5085, -104.895],
    'NuevoLeon': [25.6714, -100.309],
    'Oaxaca': [17.0732, -96.7266],
    'Puebla': [19.0414, -98.2063],
    'Queretaro': [20.5972, -100.387],
    'QuintanaRoo': [21.1631, -86.8023],
    'SanLuisPotosi': [22.1565, -100.9855],
    'Sinaloa': [24.8091, -107.394],
    'Sonora': [29.0729, -110.9559],
    'Tabasco': [17.9892, -92.9475],
    'Tamaulipas': [25.4348, -99.134],
    'Tlaxcala': [19.3181, -98.2375],
    'Veracruz': [19.1738, -96.1342],
    'Yucatan': [20.967, -89.6237],
    'Zacatecas': [22.7709, -102.5833]
}

def distancia(coord1, coord2):
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distancia = 6371 * c  # Radius of Earth in kilometers

    return distancia

def evalua_ruta(ruta, coord):
    total = 0
    for i in range(len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    return total

def simulated_annealing(ruta, coord):
    T = 20
    T_MIN = 0
    V_enfriamiento = 150 #Le aumente las iteraciones en un punto intermedio , para evitar lentitud en ejecucion.

    if len(ruta) <= 2:  # Verificar que la ruta tiene al menos 2 nodos
        return ruta  # No se necesita optimización si solo hay origen y destino

    while T > T_MIN:
        dist_actual = evalua_ruta(ruta, coord)
        for _ in range(V_enfriamiento):
            if len(ruta) > 2:
                i = random.randint(1, len(ruta) - 2)  # Evitar intercambiar origen y destino
                j = random.randint(1, len(ruta) - 2)
                # Asegurarte de no intercambiar entre el origen y destino
                if i != j:
                    ruta_tmp = ruta[:]
                    ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
                    dist_tmp = evalua_ruta(ruta_tmp, coord)
                    delta = dist_tmp - dist_actual
                    if delta < 0 or random.random() < exp(-delta / T):
                        ruta = ruta_tmp[:]
                        dist_actual = dist_tmp
        T -= 0.005
    return ruta

@app.route('/')
def index():
    return render_template('index.html', ciudades=coord.keys())
def encontrar_nodos_intermedios(coord, origen, destino, umbral_lat, umbral_lon):
    nodos_intermedios = []
    lat_origen, lon_origen = coord[origen]
    lat_destino, lon_destino = coord[destino]

    for ciudad, (lat, lon) in coord.items():
        if ciudad != origen and ciudad != destino:
            if (min(lat_origen, lat_destino) - umbral_lat <= lat <= max(lat_origen, lat_destino) + umbral_lat and
                min(lon_origen, lon_destino) - umbral_lon <= lon <= max(lon_origen, lon_destino) + umbral_lon):
                nodos_intermedios.append(ciudad)

    # Ordenar los nodos intermedios basados en su distancia desde el origen
    nodos_intermedios.sort(key=lambda ciudad: distancia(coord[origen], coord[ciudad]))
    return nodos_intermedios

@app.route('/get_routes', methods=['POST'])
def get_routes():
    data = request.get_json()
    origen = data['start']
    destino = data['end']
    umbral_lat = 0.080000 #Umbral de latitud en punto medio porque se ponia sus moños 
    umbral_lon = 0.080000 #umbral de longitud igual punto medio , coreccion de 0.000005 a jugar con el umbral.

    if origen not in coord or destino not in coord:
        return jsonify({'error': 'Inicio o fin inválidos.'}), 400

    nodos_intermedios = encontrar_nodos_intermedios(coord, origen, destino, umbral_lat, umbral_lon)

    # Imprimir los nodos intermedios encontrados
    print(f"Nodos intermedios encontrados: {nodos_intermedios}")   

    ruta_inicial = [origen] + nodos_intermedios + [destino]
    ruta_optima = simulated_annealing(ruta_inicial, coord)

    # Reordenar la ruta para que coincida en el mapa y en la salida mostrada en pantalla
    ruta_optima_str = " -> ".join(ruta_optima)
    coordenadas_ruta = [coord[ciudad] for ciudad in ruta_optima]

    # Agregar origen y destino a la respuesta
    return jsonify({
        'origen': origen,
        'destino': destino,
        'camino': ruta_optima_str,
        'coordenadas_ruta': coordenadas_ruta,
        'nodos_intermedios_encontrados': nodos_intermedios
    })


if __name__ == '__main__':
    app.run(debug=True)

# © 2024 Jonathan Hernández. Todos los derechos reservados.
# Este software está protegido por leyes de derechos de autor. No está permitido su redistribución o modificación sin autorización previa.
