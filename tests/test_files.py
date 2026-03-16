import pytest
from pathlib import Path
from samla.files.from_file import save_tables_to_file, load_tables_from_file
from samla.table.column import TableType
from fixtures import make_fixtures


@pytest.fixture
def tables():
    return make_fixtures()


@pytest.fixture
def tmp_csv(tmp_path):
    return tmp_path / "tables.csv"


def test_round_trip_table_count(tables, tmp_csv):
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    assert len(loaded) == len(tables)


def test_round_trip_table_fields(tables, tmp_csv):
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    for original, restored in zip(tables, loaded):
        assert restored.source_system == original.source_system
        assert restored.server_name == original.server_name
        assert restored.catalog == original.catalog
        assert restored.schema == original.schema
        assert restored.table == original.table
        assert restored.table_type == original.table_type


def test_round_trip_column_count(tables, tmp_csv):
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    for original, restored in zip(tables, loaded):
        assert len(restored.columns) == len(original.columns)


def test_round_trip_column_fields(tables, tmp_csv):
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    for orig_table, rest_table in zip(tables, loaded):
        for orig_col, rest_col in zip(orig_table.columns, rest_table.columns):
            assert rest_col.column == orig_col.column
            assert rest_col.data_type == orig_col.data_type
            assert rest_col.length == orig_col.length
            assert rest_col.nullable == orig_col.nullable
            assert rest_col.scale == orig_col.scale
            assert rest_col.precision == orig_col.precision
            assert rest_col.is_primary_key == orig_col.is_primary_key
            assert rest_col.source_type == orig_col.source_type


def test_round_trip_nullable_fields(tables, tmp_csv):
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    # Comment column in SalesOrderHeader has length="128" and nullable=True
    sales_table = next(t for t in loaded if t.table == "SalesOrderHeader")
    comment_col = next(c for c in sales_table.columns if c.column == "Comment")
    assert comment_col.nullable is True
    assert comment_col.length == "128"


def test_round_trip_none_server_name(tmp_csv):
    from samla.table.table import Table
    from samla.table.column import SourceColumn

    tables = [
        Table(
            source_system="sys",
            server_name=None,
            catalog="db",
            schema="dbo",
            table="T",
            table_type=TableType.TABLE,
            columns=[
                SourceColumn(
                    column="id",
                    data_type="int",
                    length=None,
                    nullable=False,
                    scale=None,
                    precision=None,
                    is_primary_key=True,
                    source_type=TableType.TABLE,
                )
            ],
        )
    ]
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    assert loaded[0].server_name is None


def test_round_trip_view_type(tmp_csv):
    from samla.table.table import Table
    from samla.table.column import SourceColumn

    tables = [
        Table(
            source_system="sys",
            server_name=None,
            catalog="db",
            schema="dbo",
            table="V",
            table_type=TableType.VIEW,
            columns=[
                SourceColumn(
                    column="id",
                    data_type="int",
                    length=None,
                    nullable=False,
                    scale=None,
                    precision=None,
                    is_primary_key=False,
                    source_type=TableType.VIEW,
                )
            ],
        )
    ]
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    assert loaded[0].table_type == TableType.VIEW
    assert loaded[0].columns[0].source_type == TableType.VIEW


def test_round_trip_decimal_precision_scale(tables, tmp_csv):
    save_tables_to_file(tables, tmp_csv)
    loaded = load_tables_from_file(tmp_csv)
    sales_table = next(t for t in loaded if t.table == "SalesOrderHeader")
    total_due = next(c for c in sales_table.columns if c.column == "TotalDue")
    assert total_due.scale == 4
    assert total_due.precision == 19
