from flask import Blueprint, request, jsonify
from database.db_config import get_connection
from services.reserva_service import ReservaService
from psycopg2.extras import RealDictCursor 

reserva_bp = Blueprint('reserva', __name__)
service = ReservaService()

@reserva_bp.route('/reservas', methods=['GET'])
def listar():
    conn = get_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "No se pudo conectar a la base de datos"}), 500
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # Casting ::TEXT para evitar error "time is not JSON serializable"
        query = """
            SELECT r.id_reserva, r.fecha::TEXT, r.hora_inicio::TEXT, r.hora_fin::TEXT, r.estado, 
                   COALESCE(u.nombre, 'Admin') as docente, s.nombre as salon, r.id_docente, r.id_salon
            FROM reserva r 
            LEFT JOIN usuario u ON r.id_docente = u.id_usuario 
            LEFT JOIN salon s ON r.id_salon = s.id_salon
            ORDER BY r.fecha DESC, r.hora_inicio DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        if conn: conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

@reserva_bp.route('/reservas', methods=['POST'])
def crear(): return jsonify(service.crear_reserva(request.json))

@reserva_bp.route('/reservas/<int:id>', methods=['PUT'])
def actualizar(id): return jsonify(service.actualizar_reserva(id, request.json))

@reserva_bp.route('/reservas/<int:id>', methods=['DELETE'])
def cancelar(id): return jsonify(service.cancelar_reserva(id))