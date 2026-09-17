from database.db_config import get_connection
from psycopg2.extras import RealDictCursor

class RolService:
    # Cambiamos 'obtener_roles' por 'listar' para que el controlador lo encuentre
    def listar(self): 
        conn = get_connection()
        if conn is None: return []
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Rol")
        res = cursor.fetchall()
        conn.close()
        return res