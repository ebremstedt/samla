import pytest
from samla.fetch.fetch import split_by_table
from samla.fetch.assemble import _parse_table_rows
from samla.table.column import TableType


def _make_row(**kwargs):
    defaults = {
        "TABLE_CATALOG": "db",
        "TABLE_SCHEMA": "dbo",
        "TABLE_NAME": "MyTable",
        "COLUMN_NAME": "id",
        "DATA_TYPE": "int",
        "length": None,
        "IS_NULLABLE": "NO",
        "scale": None,
        "precision": None,
        "is_primary_key": "1",
        "source_type": "BASE TABLE",
    }
    return {**defaults, **kwargs}


class TestSplitByTable:
    def test_single_table(self):
        rows = [_make_row(), _make_row(COLUMN_NAME="name", DATA_TYPE="nvarchar")]
        result = split_by_table(rows)
        assert len(result) == 1
        schema, table, table_rows = result[0]
        assert schema == "dbo"
        assert table == "MyTable"
        assert len(table_rows) == 2

    def test_multiple_tables(self):
        rows = [
            _make_row(TABLE_SCHEMA="Sales", TABLE_NAME="Orders"),
            _make_row(TABLE_SCHEMA="Person", TABLE_NAME="Customer"),
            _make_row(TABLE_SCHEMA="Sales", TABLE_NAME="Orders", COLUMN_NAME="name"),
        ]
        result = split_by_table(rows)
        assert len(result) == 2
        tables = {(s, t): r for s, t, r in result}
        assert len(tables[("Sales", "Orders")]) == 2
        assert len(tables[("Person", "Customer")]) == 1

    def test_empty_input(self):
        assert split_by_table([]) == []


class TestParseTableRows:
    def test_basic_table(self):
        rows = [_make_row()]
        table = _parse_table_rows(("mysys", "myhost", rows))
        assert table.source_system == "mysys"
        assert table.server_name == "myhost"
        assert table.catalog == "db"
        assert table.schema == "dbo"
        assert table.table == "MyTable"
        assert table.table_type == TableType.TABLE

    def test_column_parsed(self):
        rows = [_make_row()]
        table = _parse_table_rows(("sys", None, rows))
        assert len(table.columns) == 1
        col = table.columns[0]
        assert col.column == "id"
        assert col.data_type == "int"
        assert col.is_primary_key is True
        assert col.nullable is False

    def test_nullable_yes(self):
        rows = [_make_row(IS_NULLABLE="YES", is_primary_key="0")]
        table = _parse_table_rows(("sys", None, rows))
        assert table.columns[0].nullable is True
        assert table.columns[0].is_primary_key is False

    def test_length_none_when_empty(self):
        rows = [_make_row(length=None)]
        table = _parse_table_rows(("sys", None, rows))
        assert table.columns[0].length is None

    def test_length_set(self):
        rows = [_make_row(DATA_TYPE="nvarchar", length="50")]
        table = _parse_table_rows(("sys", None, rows))
        assert table.columns[0].length == "50"

    def test_scale_and_precision(self):
        rows = [_make_row(DATA_TYPE="decimal", scale="4", precision="19")]
        table = _parse_table_rows(("sys", None, rows))
        col = table.columns[0]
        assert col.scale == 4
        assert col.precision == 19

    def test_view_source_type(self):
        rows = [_make_row(source_type="VIEW")]
        table = _parse_table_rows(("sys", None, rows))
        assert table.table_type == TableType.VIEW
        assert table.columns[0].source_type == TableType.VIEW

    def test_multiple_columns(self):
        rows = [
            _make_row(COLUMN_NAME="id", DATA_TYPE="int"),
            _make_row(
                COLUMN_NAME="name",
                DATA_TYPE="nvarchar",
                length="50",
                is_primary_key="0",
            ),
        ]
        table = _parse_table_rows(("sys", None, rows))
        assert len(table.columns) == 2
        assert table.columns[1].column == "name"

    def test_none_hostname(self):
        rows = [_make_row()]
        table = _parse_table_rows(("sys", None, rows))
        assert table.server_name is None
