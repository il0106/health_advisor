import os
import time

import psycopg


def main() -> None:
    host = os.environ.get("POSTGRES_HOST", "db")
    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    dbname = os.environ.get("POSTGRES_DB", "app")
    user = os.environ.get("POSTGRES_USER", "app")
    password = os.environ.get("POSTGRES_PASSWORD", "app")

    deadline = time.time() + 60
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with psycopg.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password,
                connect_timeout=3,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    cur.fetchone()
            print("Database is ready.")
            return
        except Exception as e:
            last_error = e
            time.sleep(1)

    raise RuntimeError(f"Database is not ready after 60s. Last error: {last_error!r}")


if __name__ == "__main__":
    main()

