from database.db_config import get_connection
from psycopg2.extras import RealDictCursor # IMPORTANTE para Supabase
from datetime import datetime

class ReservaService:
    def existe_cruce(self, id_salon, fecha, h_ini, h_fin):
        conn = get_connection()
        if conn is None: return False
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = """SELECT * FROM reserva WHERE id_salon = %s AND fecha = %s 
                       AND estado != 'cancelada' AND (hora_inicio < %s AND hora_fin > %s)"""
            cursor.execute(query, (id_salon, fecha, h_fin, h_ini))
            res = cursor.fetchone()
            conn.close()
            return res is not None
        except Exception as e:
            if conn: conn.close()
            return False

    def crear_reserva(self, data):
        # Fallback de seguridad por si no viene hora_fin
        h_ini = data['hora_inicio']
        h_fin = data.get('hora_fin')
        if not h_fin:
            # Asignar 2 horas de duración por defecto
            try:
                from datetime import datetime, timedelta
                t_ini = datetime.strptime(h_ini, "%H:%M")
                t_fin = t_ini + timedelta(hours=2)
                h_fin = t_fin.strftime("%H:%M")
            except Exception:
                h_fin = "22:00" # fallback absoluto
        
        if self.existe_cruce(data['id_salon'], data['fecha'], h_ini, h_fin):
            return self._suscribir_a_cola(data['id_salon'], data['id_docente'])
        
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        try:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO reserva (fecha, hora_inicio, hora_fin, estado, id_docente, id_salon) 
                              VALUES (%s, %s, %s, 'confirmada', %s, %s)""", 
                           (data['fecha'], h_ini, h_fin, data['id_docente'], data['id_salon']))
            conn.commit()
            conn.close()
            return {"status": "ok", "message": "Reserva confirmada en Supabase"}
        except Exception as e:
            if conn: conn.close()
            return {"status": "error", "message": f"Error al crear reserva: {str(e)}"}

    def actualizar_reserva(self, id_reserva, data):
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reserva 
                SET fecha = %s, hora_inicio = %s, hora_fin = %s, id_salon = %s, id_docente = %s
                WHERE id_reserva = %s
            """, (data['fecha'], data['hora_inicio'], data['hora_fin'], data['id_salon'], data['id_docente'], id_reserva))
            conn.commit()
            conn.close()
            return {"status": "ok", "message": "Reserva actualizada con éxito"}
        except Exception as e:
            if conn: conn.close()
            return {"status": "error", "message": f"Error al actualizar reserva: {str(e)}"}

    def _suscribir_a_cola(self, id_salon, id_docente):
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cola_espera (id_salon, id_docente) VALUES (%s, %s)", (id_salon, id_docente))
            conn.commit()
            conn.close()
            return {"status": "cola", "message": "Añadido a lista de espera FIFO"}
        except Exception as e:
            if conn: conn.close()
            return {"status": "error", "message": f"Error al ingresar a cola: {str(e)}"}

    def cancelar_reserva(self, id_reserva):
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT id_salon FROM reserva WHERE id_reserva = %s", (id_reserva,))
            res = cursor.fetchone()
            
            if res:
                id_salon = res['id_salon']
                cursor.execute("UPDATE reserva SET estado = 'cancelada' WHERE id_reserva = %s", (id_reserva,))
                conn.commit()
                self._notificar_siguiente(id_salon)
            conn.close()
            return {"status": "ok"}
        except Exception as e:
            if conn: conn.close()
            return {"status": "error", "message": str(e)}

    def _notificar_siguiente(self, id_salon):
        conn = get_connection()
        if conn is None: return
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM cola_espera WHERE id_salon = %s ORDER BY fecha_registro ASC LIMIT 1", (id_salon,))
            siguiente = cursor.fetchone()
            if siguiente:
                cursor.execute("""INSERT INTO reserva (fecha, estado, id_docente, id_salon, fecha_notificacion) 
                                  VALUES (CURRENT_DATE, 'pendiente_confirmacion', %s, %s, CURRENT_TIMESTAMP)""", 
                               (siguiente['id_docente'], id_salon))
                cursor.execute("DELETE FROM cola_espera WHERE id_cola = %s", (siguiente['id_cola'],))
                conn.commit()
            conn.close()
        except Exception as e:
            if conn: conn.close()