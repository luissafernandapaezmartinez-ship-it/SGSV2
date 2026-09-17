import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from db_config import get_connection
from repositories.postgres_salon_repository import PostgresSalonRepository
from salon_service import SalonService


def create_app(service=None):
    """Composition root: aquí se elige la implementación concreta del repositorio."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    if service is None:
        service = SalonService(PostgresSalonRepository(get_connection))

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "ms-salones"})

    @app.route("/api/salones", methods=["GET"])
    def get_salones():
        return jsonify({"status": "ok", "data": service.listar()})

    @app.route("/api/salones", methods=["POST"])
    def crear():
        return jsonify(service.crear(request.json))

    @app.route("/api/salones/<int:id_salon>", methods=["PUT"])
    def editar(id_salon):
        return jsonify(service.actualizar(id_salon, request.json))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)), debug=True)
