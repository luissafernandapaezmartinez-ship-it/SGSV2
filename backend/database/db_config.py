import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    # Conexión ultra-robusta diseñada para saltar:
    # 1. Bloqueos de firewall locales en puerto 5432 (usando puerto alternativo 6543)
    # 2. Errores de DNS locales (utilizando la IP directa de AWS-1 Pooler)
    # 3. Fallas de enrutamiento IPv6 de tu ISP (forzando IPv4)
    params = {
        "host": "aws-1-us-east-2.pooler.supabase.com",
        "hostaddr": "13.58.13.125",
        "port": 6543,
        "database": "postgres",
        "user": "postgres.qgwpttpknrevnbdsjnrx",
        "password": "Sgs_Proyecto_2026",
        "sslmode": "require",
        "connect_timeout": 5
    }
    
    try:
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print(f"\n[ERROR] Connection failed completely: {e}\n")
        return None