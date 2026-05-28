import io
import pyarrow.csv as pa_csv
import pyarrow.parquet as pq


def csv_to_parquet(csv_bytes: bytes) -> bytes:
    table = pa_csv.read_csv(io.BytesIO(csv_bytes))
    buf = io.BytesIO()
    pq.write_table(table, buf)
    return buf.getvalue()
