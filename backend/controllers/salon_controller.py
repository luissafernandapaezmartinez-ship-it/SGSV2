# Extraído a services/salones. El monolito ya no registra este blueprint.
from flask import Blueprint, request, jsonify
from services.salon_service import SalonService

salon_bp = Blueprint('salon', __name__)
service = SalonService()

@salon_bp.route('/salones', methods=['GET'])
def get_salones():
    return jsonify({"status": "ok", "data": service.listar()})

@salon_bp.route('/salones', methods=['POST'])
def crear():
    return jsonify(service.crear(request.json))
@salon_bp.route('/salones/<int:id>', methods=['PUT'])
def editar(id):
    return jsonify(service.actualizar(id, request.json))
