from flask import Blueprint, request, jsonify
from services.usuario_service import UsuarioService

usuario_bp = Blueprint('usuario', __name__)
service = UsuarioService()

@usuario_bp.route('/login', methods=['POST'])
def login():
    res = service.login(request.json.get('email'), request.json.get('password'))
    if res and res.get('status') == 'ok':
        return jsonify(res)
    return jsonify(res), 401

@usuario_bp.route('/usuarios', methods=['POST'])
def registrar():
    data = request.json
    res = service.crear_usuario(data)
    if res and res.get('status') == 'ok':
        return jsonify(res)
    return jsonify(res), 400