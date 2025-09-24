import os
import psycopg  # ✅ psycopg3 (no psycopg2)

def init_db():
    ddl_path = os.path.join(os.path.dirname(__file__), "ddl.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()

    # Con psycopg3 usamos psycopg.connect
    with psycopg.connect(os.environ["SQLALCHEMY_DATABASE_URI"]) as conn:
        conn.autocommit = True  # necesario para CREATE EXTENSION y DDL en bloque
        with conn.cursor() as cur:
            cur.execute(ddl)
            print("✅ Tablas creadas con éxito")

if __name__ == "__main__":
    init_db()
