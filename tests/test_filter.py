import pytest
from samla.fetch.filter import FilterGroup, filter_tables
from fixtures import make_fixtures


@pytest.fixture
def tables():
    return make_fixtures()


def test_filter_by_schema(tables):
    result = filter_tables(tables, [FilterGroup(schema_patterns=["Sales"])])
    assert len(result) == 1
    assert result[0].schema == "Sales"


def test_filter_by_table(tables):
    result = filter_tables(tables, [FilterGroup(table_patterns=["Customer"])])
    assert len(result) == 1
    assert result[0].table == "Customer"


def test_filter_by_catalog(tables):
    result = filter_tables(tables, [FilterGroup(catalog_patterns=["AdventureWorks"])])
    assert len(result) == 2


def test_filter_case_insensitive(tables):
    result = filter_tables(tables, [FilterGroup(schema_patterns=["sales"])])
    assert len(result) == 1
    assert result[0].schema == "Sales"


def test_filter_partial_match(tables):
    result = filter_tables(tables, [FilterGroup(table_patterns=["Order"])])
    assert len(result) == 1
    assert result[0].table == "SalesOrderHeader"


def test_filter_no_match(tables):
    result = filter_tables(tables, [FilterGroup(schema_patterns=["NonExistent"])])
    assert result == []


def test_filter_multiple_patterns_are_ored(tables):
    result = filter_tables(tables, [FilterGroup(schema_patterns=["Sales", "Person"])])
    assert len(result) == 2


def test_filter_multiple_groups_are_ored(tables):
    result = filter_tables(
        tables,
        [
            FilterGroup(schema_patterns=["Sales"]),
            FilterGroup(schema_patterns=["Person"]),
        ],
    )
    assert len(result) == 2


def test_filter_combined_fields_all_must_match(tables):
    result = filter_tables(
        tables,
        [FilterGroup(schema_patterns=["Sales"], table_patterns=["Customer"])],
    )
    assert result == []


def test_filter_none_patterns_match_all(tables):
    result = filter_tables(tables, [FilterGroup()])
    assert len(result) == 2
