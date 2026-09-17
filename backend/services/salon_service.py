from database.db_config import get_connection
from psycopg2.extras import RealDictCursor

class SalonService:
    # Tarea 3: Registrar salones
    def crear(self, data):
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Salon (nombre, capacidad, estado, ubicacion) 
            VALUES (%s, %s, %s, %s)
        """, (data['nombre'], data['capacidad'], 'disponible', data['ubicacion']))
        conn.commit()
        conn.close()
        return {"status": "ok", "message": "Salón registrado exitosamente"}

    # Tarea 6, 18, 21: Consultar la lista de salones
    def listar(self):
        conn = get_connection()
        if conn is None: return []
        
        # Usamos RealDictCursor para que Supabase retorne claves-valor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Salon ORDER BY id_salon ASC")
        data = cursor.fetchall()
        conn.close()
        return data

    # Tarea 7: Editar la información de un salón
    def actualizar(self, id_salon, data):
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Salon 
            SET nombre = %s, capacidad = %s, ubicacion = %s 
            WHERE id_salon = %s
        """, (data['nombre'], data['capacidad'], data['ubicacion'], id_salon))
        conn.commit()
        
        # Verificar si se actualizó algo
        filas_afectadas = cursor.rowcount
        conn.close()
        
        if filas_afectadas > 0:
            return {"status": "ok", "message": "Salón actualizado correctamente"}
        else:
            return {"status": "error", "message": "No se encontró el salón para actualizar"}

    # Extra: Eliminar salón (Opcional para completar el CRUD)
    def eliminar(self, id_salon):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Salon WHERE id_salon = %s", (id_salon,))
        conn.commit()
        conn.close()
        return {"status": "ok", "message": "Salón eliminado"}