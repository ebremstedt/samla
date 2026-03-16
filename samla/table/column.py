from dataclasses import dataclass
from enum import Enum


class TableType(Enum):
    TABLE = "BASE TABLE"
    VIEW = "VIEW"


@dataclass
class SourceColumn:
    column: str
    data_type: str
    length: str | None
    nullable: bool
    scale: int | None
    precision: int | None
    is_primary_key: bool
    source_type: TableType
