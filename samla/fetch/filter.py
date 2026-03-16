import re
from dataclasses import dataclass
from samla.table.table import Table


@dataclass
class FilterGroup:
    catalog_patterns: list[str] | None = None
    schema_patterns: list[str] | None = None
    table_patterns: list[str] | None = None


def _field_matches(value: str, patterns: list[str]) -> bool:
    return any(re.search(p, value, re.IGNORECASE) for p in patterns)


def _matches(table: Table, group: FilterGroup) -> bool:
    if group.catalog_patterns and not _field_matches(table.catalog, group.catalog_patterns):
        return False
    if group.schema_patterns and not _field_matches(table.schema, group.schema_patterns):
        return False
    if group.table_patterns and not _field_matches(table.table, group.table_patterns):
        return False
    return True


def filter_tables(tables: list[Table], filters: list[FilterGroup]) -> list[Table]:
    return [t for t in tables if any(_matches(t, g) for g in filters)]
