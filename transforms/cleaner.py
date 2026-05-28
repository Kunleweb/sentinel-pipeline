"""
Pure pyarrow transform functions. No pandas/numpy dependency.
Each function accepts a pyarrow Table and returns a cleaned pyarrow Table.
"""

import pyarrow as pa
import pyarrow.compute as pc


def drop_duplicates(table: pa.Table, pk: list[str]) -> pa.Table:
    """Keep the first occurrence of each unique PK combination."""
    pk_cols = [table.column(col).to_pylist() for col in pk]
    seen = set()
    keep = []
    for i in range(len(table)):
        key = tuple(col[i] for col in pk_cols)
        if key not in seen:
            seen.add(key)
            keep.append(i)
    dupes = len(table) - len(keep)
    if dupes:
        print(f"    dropped {dupes} duplicate row(s)")
    return table.take(keep)


def cast_money_fields(table: pa.Table, fields: list[str]) -> pa.Table:
    """Cast numeric columns to Decimal(18, 2)."""
    for field in fields:
        idx = table.schema.get_field_index(field)
        col = pc.cast(table.column(field), pa.decimal128(21, 2))
        table = table.set_column(idx, field, col)
    return table


def parse_date_fields(table: pa.Table, fields: list[str]) -> pa.Table:
    """Parse string columns into proper date32 types (expects YYYY-MM-DD format)."""
    for field in fields:
        idx = table.schema.get_field_index(field)
        col = table.column(field)
        if pa.types.is_date(col.type):
            continue
        # string → timestamp → date32
        ts_col = pc.strptime(col, format="%Y-%m-%d", unit="s")
        date_col = pc.cast(ts_col, pa.date32())
        table = table.set_column(idx, field, date_col)
    return table


def normalize_casing(
    table: pa.Table,
    upper_fields: list[str],
    title_fields: list[str],
    lower_fields: list[str],
) -> pa.Table:
    """Normalize string column casing."""
    for field in upper_fields:
        idx = table.schema.get_field_index(field)
        col = pc.utf8_upper(table.column(field))
        table = table.set_column(idx, field, col)

    for field in title_fields:
        idx = table.schema.get_field_index(field)
        # pyarrow has no utf8_title — apply via Python, acceptable for these sizes
        raw = table.column(field).to_pylist()
        titled = pa.array(
            [s.title() if s is not None else None for s in raw],
            type=pa.string(),
        )
        table = table.set_column(idx, field, titled)

    for field in lower_fields:
        idx = table.schema.get_field_index(field)
        col = pc.utf8_lower(table.column(field))
        table = table.set_column(idx, field, col)

    return table


def clean(table: pa.Table, cfg: dict) -> pa.Table:
    """Apply all configured transforms in order."""
    table = drop_duplicates(table, cfg["pk"])
    table = parse_date_fields(table, cfg["date_fields"])
    table = cast_money_fields(table, cfg["money_fields"])
    table = normalize_casing(
        table,
        cfg["upper_fields"],
        cfg["title_fields"],
        cfg["lower_fields"],
    )
    return table
