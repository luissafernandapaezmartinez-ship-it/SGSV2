from repositories.i_salon_repository import ISalonRepository


class SalonService:
    """SRP: solo reglas de negocio de salones. DIP: recibe un ISalonRepository, no Postgres."""

    def __init__(self, repository: ISalonRepository):
        self._repository = repository

    def listar(self):
        return self._repository.listar()

    def crear(self, data):
        error = self._validar(data)
        if error:
            return error

        try:
            self._repository.crear(data["nombre"].strip(), int(data["capacidad"]), data["ubicacion"].strip())
        except ConnectionError:
            return {"status": "error", "message": "Error de conexión"}

        return {"status": "ok", "message": "Salón registrado exitosamente"}

    def actualizar(self, id_salon, data):
        error = self._validar(data)
        if error:
            return error

        try:
            filas = self._repository.actualizar(
                id_salon,
                data["nombre"].strip(),
                int(data["capacidad"]),
                data["ubicacion"].strip(),
            )
        except ConnectionError:
            return {"status": "error", "message": "Error de conexión"}

        if filas > 0:
            return {"status": "ok", "message": "Salón actualizado correctamente"}
        return {"status": "error", "message": "No se encontró el salón para actualizar"}

    def _validar(self, data):
        if not data:
            return {"status": "error", "message": "Datos de salón requeridos"}

        nombre = (data.get("nombre") or "").strip()
        ubicacion = (data.get("ubicacion") or "").strip()
        if not nombre:
            return {"status": "error", "message": "El nombre del salón es obligatorio"}
        if not ubicacion:
            return {"status": "error", "message": "La ubicación del salón es obligatoria"}

        try:
            capacidad = int(data.get("capacidad"))
        except (TypeError, ValueError):
            return {"status": "error", "message": "La capacidad debe ser un número entero"}

        if capacidad <= 0:
            return {"status": "error", "message": "La capacidad debe ser mayor a 0"}

        return None
