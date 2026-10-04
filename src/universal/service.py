from __future__ import annotations
import tempfile
from pathlib import Path
from src.universal.io import read_table
from src.universal.profile import profile_dataframe, rank_target_candidates


def profile_uploaded_file(contents: bytes, filename: str) -> dict:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".pq"}:
        raise ValueError("Supported files: CSV, TSV, XLSX, XLS, Parquet")
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(contents); path = f.name
    try:
        df = read_table(path)
        result = profile_dataframe(df)
        result["target_candidates"] = rank_target_candidates(df)
        return result
    finally:
        Path(path).unlink(missing_ok=True)
