from dataclasses import dataclass
from samla.table.column import SourceColumn, TableType


@dataclass
class Table:
    source_system: str
    server_name: str | None
    catalog: str
    schema: str
    table: str
    table_type: TableType
    columns: list[SourceColumn]
