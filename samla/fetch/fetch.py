from typing import Any
import pyodbc
from samla.fetch.query import QUERY


def fetch_rows(source_conn: pyodbc.Connection) -> list[dict[str, Any]]:
    cursor = source_conn.cursor()
    cursor.execute(QUERY)
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def split_by_table(
    rows: list[dict[str, Any]],
) -> list[tuple[str, str, list[dict[str, Any]]]]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["TABLE_SCHEMA"], row["TABLE_NAME"])
        buckets.setdefault(key, []).append(row)
    return [
        (schema, table, table_rows) for (schema, table), table_rows in buckets.items()
    ]
