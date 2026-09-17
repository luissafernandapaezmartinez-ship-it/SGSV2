from repositories.i_salon_repository import ISalonRepository


class MemorySalonRepository(ISalonRepository):
    """LSP: misma interfaz que Postgres, útil para pruebas sin base de datos."""

    def __init__(self):
        self._salones = []
        self._next_id = 1

    def listar(self):
        return list(self._salones)

    def crear(self, nombre, capacidad, ubicacion):
        self._salones.append(
            {
                "id_salon": self._next_id,
                "nombre": nombre,
                "capacidad": capacidad,
                "estado": "disponible",
                "ubicacion": ubicacion,
            }
        )
        self._next_id += 1

    def actualizar(self, id_salon, nombre, capacidad, ubicacion):
        for salon in self._salones:
            if salon["id_salon"] == id_salon:
                salon["nombre"] = nombre
                salon["capacidad"] = capacidad
                salon["ubicacion"] = ubicacion
                return 1
        return 0
