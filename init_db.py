import os
import psycopg2

def init_db():
    ddl_path = os.path.join(os.path.dirname(__file__), "ddl.sql")
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl = f.read()

    conn = psycopg2.connect(os.environ["SQLALCHEMY_DATABASE_URI"])
    conn.autocommit = True
    cur = conn.cursor()

    # Ejecuta todo el bloque DDL de una vez (incluye CREATE EXTENSION y FKs)
    cur.execute(ddl)
    print("✅ Tablas creadas con éxito")

    cur.close()
    conn.close()

if __name__ == "__main__":
    init_db()
