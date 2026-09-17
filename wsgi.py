import os
import sys

# Agregar la carpeta backend al PATH para que Gunicorn encuentre
# todos los módulos internos (controllers, services, database)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# Importar main directamente (backend/ ya está en sys.path)
from main import app
