import csv
from pathlib import Path
from samla.table.column import SourceColumn, TableType
from samla.table.table import Table

_FIELDNAMES = [
    "source_system",
    "server_name",
    "catalog",
    "schema",
    "table",
    "table_type",
    "column",
    "data_type",
    "length",
    "nullable",
    "scale",
    "precision",
    "is_primary_key",
    "source_type",
]


def save_tables_to_file(tables: list[Table], path: Path) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        for t in tables:
            for col in t.columns:
                writer.writerow(
                    {
                        "source_system": t.source_system,
                        "server_name": t.server_name,
                        "catalog": t.catalog,
                        "schema": t.schema,
                        "table": t.table,
                        "table_type": t.table_type.value,
                        "column": col.column,
                        "data_type": col.data_type,
                        "length": col.length,
                        "nullable": col.nullable,
                        "scale": col.scale,
                        "precision": col.precision,
                        "is_primary_key": col.is_primary_key,
                        "source_type": col.source_type.value,
                    }
                )


def load_tables_from_file(path: Path) -> list[Table]:
    buckets: dict[tuple, dict] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            key = (
                row["source_system"],
                row["server_name"],
                row["catalog"],
                row["schema"],
                row["table"],
                row["table_type"],
            )
            if key not in buckets:
                buckets[key] = {"meta": row, "columns": []}
            buckets[key]["columns"].append(row)

    tables = []
    for key, bucket in buckets.items():
        meta = bucket["meta"]
        columns = [
            SourceColumn(
                column=r["column"],
                data_type=r["data_type"],
                length=r["length"] or None,
                nullable=r["nullable"] == "True",
                scale=int(r["scale"]) if r["scale"] else None,
                precision=int(r["precision"]) if r["precision"] else None,
                is_primary_key=r["is_primary_key"] == "True",
                source_type=TableType(r["source_type"]),
            )
            for r in bucket["columns"]
        ]
        tables.append(
            Table(
                source_system=meta["source_system"],
                server_name=meta["server_name"] or None,
                catalog=meta["catalog"],
                schema=meta["schema"],
                table=meta["table"],
                table_type=TableType(meta["table_type"]),
                columns=columns,
            )
        )
    return tables
