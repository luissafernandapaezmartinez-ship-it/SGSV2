import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Agregar la raíz del backend al path para evitar problemas de importación
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/static')),
    static_url_path='/static'
)

# Configurar CORS para permitir peticiones locales
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Importar y Registrar Controladores (Blueprints)
from controllers.usuario_controller import usuario_bp
from controllers.reserva_controller import reserva_bp
from controllers.docente_controller import docente_bp
from controllers.rol_controller import rol_bp

app.register_blueprint(usuario_bp, url_prefix='/api')
app.register_blueprint(reserva_bp, url_prefix='/api')
app.register_blueprint(docente_bp, url_prefix='/api')
app.register_blueprint(rol_bp, url_prefix='/api')

# ms-salones ya no vive aquí: el API Gateway rutea /api/salones al microservicio.

# --- SERVICIO DE PÁGINAS FRONTEND ---
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/index.html')
def index_page():
    return render_template('index.html')

if __name__ == '__main__':
    # Ejecutamos el servidor Flask en el puerto 5000 en todas las interfaces para permitir acceso desde otros dispositivos
    app.run(host='0.0.0.0', port=5000, debug=True)
