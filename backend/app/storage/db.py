import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ..core.config import BACKEND_ROOT
from .models import INDEXES_SQL, TABLES_SQL


def resolve_db_path(db_path: str) -> Path:
    path = Path(db_path).expanduser()
    if not path.is_absolute():
        path = (BACKEND_ROOT / path).resolve()
    return path


def ensure_db_directory(db_path: str) -> Path:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def get_connection(db_path: str) -> Iterator[sqlite3.Connection]:
    resolved = ensure_db_directory(db_path)
    connection = sqlite3.connect(resolved)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
    finally:
        connection.close()


def initialize_database(db_path: str) -> Path:
    resolved = ensure_db_directory(db_path)
    with sqlite3.connect(resolved) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for statement in TABLES_SQL:
            connection.execute(statement)
        for statement in INDEXES_SQL:
            connection.execute(statement)
    return resolved
