from psycopg2.extras import RealDictCursor
from repositories.i_salon_repository import ISalonRepository


class PostgresSalonRepository(ISalonRepository):
    """LSP: sustituye a ISalonRepository. OCP: se puede agregar otro motor sin cambiar el servicio."""

    def __init__(self, connection_factory):
        self._connection_factory = connection_factory

    def listar(self):
        conn = self._connection_factory()
        if conn is None:
            return []
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM Salon ORDER BY id_salon ASC")
            return cursor.fetchall()
        finally:
            conn.close()

    def crear(self, nombre, capacidad, ubicacion):
        conn = self._connection_factory()
        if conn is None:
            raise ConnectionError("No se pudo conectar a la base de datos")
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Salon (nombre, capacidad, estado, ubicacion)
                VALUES (%s, %s, %s, %s)
                """,
                (nombre, capacidad, "disponible", ubicacion),
            )
            conn.commit()
        finally:
            conn.close()

    def actualizar(self, id_salon, nombre, capacidad, ubicacion):
        conn = self._connection_factory()
        if conn is None:
            raise ConnectionError("No se pudo conectar a la base de datos")
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Salon
                SET nombre = %s, capacidad = %s, ubicacion = %s
                WHERE id_salon = %s
                """,
                (nombre, capacidad, ubicacion, id_salon),
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
