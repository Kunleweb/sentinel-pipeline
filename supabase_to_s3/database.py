from contextlib import contextmanager

import psycopg2


@contextmanager
def get_connection(credentials: dict):
    conn = psycopg2.connect(
        host=credentials["host"],
        port=credentials.get("port", 5432),
        dbname=credentials["database"],
        user=credentials["user"],
        password=credentials["password"],
        sslmode="require",
    )
    try:
        yield conn
    finally:
        conn.close()


def extract_table(conn, table_name: str) -> tuple[list, list]:
    """Return (columns, rows) for the given table."""
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM "{table_name}"')
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return columns, rows
