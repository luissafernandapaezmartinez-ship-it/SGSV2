import os
import psycopg2


def get_connection():
    params = {
        "host": os.getenv("DB_HOST", "aws-1-us-east-2.pooler.supabase.com"),
        "hostaddr": os.getenv("DB_HOSTADDR", "13.58.13.125"),
        "port": int(os.getenv("DB_PORT", "6543")),
        "database": os.getenv("DB_NAME", "postgres"),
        "user": os.getenv("DB_USER", "postgres.qgwpttpknrevnbdsjnrx"),
        "password": os.getenv("DB_PASSWORD", "Sgs_Proyecto_2026"),
        "sslmode": os.getenv("DB_SSLMODE", "require"),
        "connect_timeout": 5,
    }

    try:
        return psycopg2.connect(**params)
    except Exception as e:
        print(f"\n[ms-salones] Connection failed: {e}\n")
        return None
