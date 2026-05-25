from __future__ import annotations

import os
import sys

import psycopg2
from sqlalchemy.engine import make_url


def normalize_postgres_url(raw_url: str) -> str:
    url = make_url(raw_url)
    if url.drivername.startswith("postgresql+"):
        url = url.set(drivername="postgresql")
    return str(url)


def get_connection_args(raw_url: str) -> dict:
    url = make_url(raw_url)
    if url.drivername.startswith("postgresql+" ):
        url = url.set(drivername="postgresql")
    return url.translate_connect_args(username="user", password="password")


def ensure_database_exists() -> None:
    raw_url = os.environ.get("DATABASE_URL")
    if not raw_url:
        raise RuntimeError("DATABASE_URL environment variable is required")

    url = make_url(raw_url)
    if url.drivername.startswith("postgresql+" ):
        url = url.set(drivername="postgresql")

    target_db = url.database
    if not target_db:
        raise RuntimeError("DATABASE_URL must include a database name")

    if target_db in {"postgres", "template1", "template0"}:
        print(f"Skipping creation for default database '{target_db}'")
        return

    default_url = url.set(database="postgres")
    connect_args = default_url.translate_connect_args(username="user", password="password")
    connect_args.update(default_url.query)

    print(f"Ensuring PostgreSQL database '{target_db}' exists...")

    with psycopg2.connect(**connect_args) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (target_db,),
            )
            if cursor.fetchone() is None:
                print(f"Database '{target_db}' not found. Creating...")
                cursor.execute(f'CREATE DATABASE "{target_db}"')
            else:
                print(f"Database '{target_db}' already exists.")


if __name__ == "__main__":
    try:
        ensure_database_exists()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
