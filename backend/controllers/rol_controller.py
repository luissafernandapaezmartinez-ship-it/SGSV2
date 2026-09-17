from flask import Blueprint, jsonify
from services.rol_service import RolService

rol_bp = Blueprint('rol', __name__)
service = RolService()

@rol_bp.route('/roles', methods=['GET'])
def get_roles():
    return jsonify(service.listar())