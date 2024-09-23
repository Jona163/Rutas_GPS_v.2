# Autor: Jonathan Hernández
# Fecha: 22 Septiembre 2024
# Descripción: Código para rutas gps v2.
# GitHub: https://github.com/Jona163

from flask import Flask, render_template, request, jsonify
from math import radians, sin, cos, sqrt, atan2, exp
import random

app = Flask(__name__)
