from database.db_config import get_connection
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

class DocenteService:
    def listar(self):
        conn = get_connection()
        if conn is None: return []
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id_usuario as id_docente, nombre, email as correo, 'Sin Teléfono' as telefono
                FROM usuario 
                WHERE id_rol = 3 
                ORDER BY nombre ASC
            """)
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            if conn: conn.close()
            return []

    def crear(self, data):
        conn = get_connection()
        if conn is None: return {"status": "error", "message": "Error de conexión"}
        
        email = data.get('correo', '').lower()
        if '@' in email:
            dominio_completo = email.split('@')[-1]
            dominio_base = dominio_completo.split('.')[0]
            
            typos_base = {
                'gmal': 'gmail', 'gmai': 'gmail', 'gamil': 'gmail', 'gmaill': 'gmail',
                'hotml': 'hotmail', 'hotmal': 'hotmail', 'hormail': 'hotmail', 'homail': 'hotmail',
                'outlok': 'outlook', 'outloo': 'outlook', 'oulook': 'outlook',
                'yaho': 'yahoo', 'yahhoo': 'yahoo'
            }
            
            if dominio_base in typos_base:
                correccion = dominio_completo.replace(dominio_base, typos_base[dominio_base], 1)
                return {"status": "error", "message": f"Dominio de correo inválido. ¿Quisiste escribir @{correccion}?"}
            
            if dominio_completo.endswith(('.con', '.c', '.om', '.o')):
                correccion = dominio_completo.rsplit('.', 1)[0] + '.com'
                return {"status": "error", "message": f"Dominio de correo inválido. ¿Quisiste escribir @{correccion}?"}
                
        try:
            cursor = conn.cursor()
            password_defecto = generate_password_hash("docente123")
            cursor.execute("""
                INSERT INTO usuario (nombre, email, password, id_rol) 
                VALUES (%s, %s, %s, 3)
            """, (data['nombre'], data['correo'], password_defecto))
            conn.commit()
            conn.close()
            return {"status": "ok", "message": "Docente registrado con éxito. Contraseña por defecto: docente123"}
        except Exception as e:
            if conn: conn.close()
            return {"status": "error", "message": f"Error al registrar docente: {str(e)}"}