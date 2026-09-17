from flask import Blueprint, request, jsonify
from services.docente_service import DocenteService

docente_bp = Blueprint('docente', __name__)
service = DocenteService()

@docente_bp.route('/docentes', methods=['GET'])
def listar():
    data = service.listar()
    return jsonify({"status": "ok", "data": data})

@docente_bp.route('/docentes', methods=['POST'])
def crear():
    return jsonify(service.crear(request.json))