QUERY = """
SELECT
    c.TABLE_CATALOG,
    c.TABLE_SCHEMA,
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    COALESCE(CAST(c.CHARACTER_MAXIMUM_LENGTH AS VARCHAR), '') AS length,
    c.IS_NULLABLE,
    'TABLE' AS source_type,
    COALESCE(CAST(pk.is_primary_key AS VARCHAR), '0') AS is_primary_key,
    CASE
        WHEN c.DATA_TYPE IN ('decimal', 'numeric') THEN COALESCE(CAST(c.NUMERIC_PRECISION AS VARCHAR), '')
        ELSE ''
    END AS precision,
    CASE
        WHEN c.DATA_TYPE IN ('decimal', 'numeric') THEN COALESCE(CAST(c.NUMERIC_SCALE AS VARCHAR), '')
        ELSE ''
    END AS scale
FROM
    INFORMATION_SCHEMA.COLUMNS AS c
LEFT JOIN (
    SELECT
        t.name AS table_name,
        c.name AS column_name,
        i.is_primary_key
    FROM
        sys.tables AS t
    INNER JOIN sys.indexes AS i ON t.object_id = i.object_id
    INNER JOIN sys.index_columns AS ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    INNER JOIN sys.columns AS c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    WHERE
        i.is_primary_key = 1
) AS pk ON c.TABLE_NAME = pk.table_name AND c.COLUMN_NAME = pk.column_name
ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME
"""
