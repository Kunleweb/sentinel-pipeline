import _bootstrap  # noqa: F401
import pyarrow as pa
import pyarrow.compute as pc


def drop_duplicates(table: pa.Table, pk: list[str]) -> pa.Table:
    pk_cols = [table.column(col).to_pylist() for col in pk]
    seen, keep = set(), []
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
    for field in fields:
        idx = table.schema.get_field_index(field)
        col = pc.cast(table.column(field), pa.decimal128(21, 2))
        table = table.set_column(idx, field, col)
    return table


def parse_date_fields(table: pa.Table, fields: list[str]) -> pa.Table:
    for field in fields:
        idx = table.schema.get_field_index(field)
        col = table.column(field)
        if pa.types.is_date(col.type):
            continue
        date_col = pc.cast(pc.strptime(col, format="%Y-%m-%d", unit="s"), pa.date32())
        table = table.set_column(idx, field, date_col)
    return table


def normalize_casing(
    table: pa.Table,
    upper_fields: list[str],
    title_fields: list[str],
    lower_fields: list[str],
) -> pa.Table:
    for field in upper_fields:
        idx = table.schema.get_field_index(field)
        table = table.set_column(idx, field, pc.utf8_upper(table.column(field)))

    for field in title_fields:
        idx = table.schema.get_field_index(field)
        raw = table.column(field).to_pylist()
        titled = pa.array([s.title() if s else None for s in raw], type=pa.string())
        table = table.set_column(idx, field, titled)

    for field in lower_fields:
        idx = table.schema.get_field_index(field)
        table = table.set_column(idx, field, pc.utf8_lower(table.column(field)))

    return table


def clean(table: pa.Table, cfg: dict) -> pa.Table:
    table = drop_duplicates(table, cfg["pk"])
    table = parse_date_fields(table, cfg["date_fields"])
    table = cast_money_fields(table, cfg["money_fields"])
    table = normalize_casing(table, cfg["upper_fields"], cfg["title_fields"], cfg["lower_fields"])
    return table
