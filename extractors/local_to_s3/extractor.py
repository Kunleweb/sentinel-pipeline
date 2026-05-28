import os
from local_to_s3.config import DATA_DIR, FILES


def get_local_files() -> list[dict]:
    """Return list of {path, source, file_name} for each configured file."""
    result = []
    for filename, (source, s3_name) in FILES.items():
        path = os.path.normpath(os.path.join(DATA_DIR, filename))
        if not os.path.exists(path):
            raise FileNotFoundError(f"Expected file not found: {path}")
        result.append({"path": path, "source": source, "file_name": s3_name})
    return result


def read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
