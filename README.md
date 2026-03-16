# samla

Fetches and parses MSSQL schema metadata (tables, views, columns) into structured Python objects.

## Install

```bash
pip install samla
```

## Usage

### From a database connection

Connects directly to MSSQL and fetches schema metadata:

```python
import pyodbc
from samla import get_and_parse_tables, FilterGroup

filters = [
    FilterGroup(catalog_patterns=["NorthernVault"], schema_patterns=["Reporting"]),
]

conn = pyodbc.connect("<your connection string>")
tables = get_and_parse_tables(conn=conn, source_system="ACME", filters=filters)
```

The SQL query used to fetch metadata from `INFORMATION_SCHEMA` is available [here](samla/fetch/query.py).

### From a CSV file

If you cannot connect to the database directly, load from a pre-exported CSV file instead:

```python
from pathlib import Path
from samla import load_tables_from_file

tables = load_tables_from_file(path=Path("tables.csv"))
```

To produce the CSV, save the output from a database run:

```python
from samla import save_tables_to_file

save_tables_to_file(tables=tables, path=Path("tables.csv"))
```

Or from the command line

```bash
python main.py                        # fetch from database
python main.py --file tables.csv      # load from CSV file
```

## Filtering

`FilterGroup` filters tables by catalog, schema, and/or table name using regex patterns. Multiple patterns within a field are OR'd; multiple `FilterGroup`s are also OR'd between each other.

```python
filters = [
    FilterGroup(schema_patterns=["Sales", "Person"]),
    FilterGroup(catalog_patterns=["AdventureWorks"], table_patterns=["^Product"]),
]
```

## Data model

### Table

| Field | Type | Description |
|---|---|---|
| `source_system` | `str` | Identifier for the source system |
| `server_name` | `str \| None` | Hostname of the server |
| `catalog` | `str` | Database catalog name |
| `schema` | `str` | Schema name |
| `table` | `str` | Table or view name |
| `table_type` | `TableType` | `TABLE` or `VIEW` |
| `columns` | `list[SourceColumn]` | Column definitions |

### SourceColumn

| Field | Type | Description |
|---|---|---|
| `column` | `str` | Column name |
| `data_type` | `str` | SQL data type |
| `length` | `str \| None` | Character max length |
| `nullable` | `bool` | Whether the column is nullable |
| `scale` | `int \| None` | Numeric scale |
| `precision` | `int \| None` | Numeric precision |
| `is_primary_key` | `bool` | Whether the column is a primary key |
| `source_type` | `TableType` | `TABLE` or `VIEW` |

## Development

```bash
pip install -e ".[dev]"
pytest
```
