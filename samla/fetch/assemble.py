from typing import Any
from multiprocessing import Pool
import pyodbc
from samla.table.column import SourceColumn, TableType
from samla.table.table import Table
from samla.fetch.fetch import fetch_rows, split_by_table
from samla.fetch.filter import FilterGroup, filter_tables


def _parse_table_rows(args: tuple[str, str | None, list[dict[str, Any]]]) -> Table:
    source_system, server_name, rows = args
    first = rows[0]
    table_type = TableType(first.get("source_type", "BASE TABLE"))

    columns = [
        SourceColumn(
            column=r["COLUMN_NAME"],
            data_type=r["DATA_TYPE"],
            length=r["length"] if r.get("length") else None,
            nullable=r["IS_NULLABLE"] in ("YES", True, 1),
            scale=int(r["scale"]) if r.get("scale") else None,
            precision=int(r["precision"]) if r.get("precision") else None,
            is_primary_key=r.get("is_primary_key") == "1",
            source_type=table_type,
        )
        for r in rows
    ]

    return Table(
        source_system=source_system,
        server_name=server_name,
        catalog=first["TABLE_CATALOG"],
        schema=first["TABLE_SCHEMA"],
        table=first["TABLE_NAME"],
        table_type=table_type,
        columns=columns,
    )


def get_and_parse_tables(
    conn: pyodbc.Connection,
    source_system: str = "default",
    hostname: str | None = None,
    filters: list[FilterGroup] | None = None,
) -> list[Table]:
    rows = fetch_rows(source_conn=conn)
    groups = split_by_table(rows=rows)

    pool_args = [
        (source_system, hostname, group_rows)
        for _, _, group_rows in groups
    ]

    with Pool() as pool:
        tables = pool.map(_parse_table_rows, pool_args)

    if filters:
        tables = filter_tables(tables=tables, filters=filters)

    return tables
