from __future__ import annotations

from pathlib import Path
from typing import Iterable
import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".parquet", ".pq"}


def _read_excel(path: Path, sheet_name=0) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name)


def read_table(path: str | Path, sheet_name: str | int | None = 0) -> pd.DataFrame:
    """Read one tabular dataset from CSV/TSV/XLSX/XLS/Parquet."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    ext = p.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type {ext!r}. Supported: {sorted(SUPPORTED_EXTENSIONS)}")
    if ext in {".csv", ".tsv"}:
        sep = "," if ext == ".csv" else "\t"
        try:
            return pd.read_csv(p, sep=sep, low_memory=False, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(p, sep=sep, low_memory=False, encoding="cp1252")
    if ext in {".xlsx", ".xls"}:
        return _read_excel(p, sheet_name=0 if sheet_name is None else sheet_name)
    try:
        return pd.read_parquet(p)
    except ImportError as exc:
        raise ImportError("Parquet support requires pyarrow or fastparquet; install the project requirements.") from exc


def list_excel_sheets(path: str | Path) -> list[str]:
    p = Path(path)
    if p.suffix.lower() not in {".xlsx", ".xls"}:
        return []
    return pd.ExcelFile(p).sheet_names


def read_workbook(path: str | Path) -> dict[str, pd.DataFrame]:
    """Read every sheet from an Excel workbook as a named table."""
    sheets = pd.read_excel(path, sheet_name=None)
    return {str(k): v for k, v in sheets.items()}


def read_many(paths: Iterable[str | Path]) -> dict[str, pd.DataFrame]:
    """Read multiple supported files; keys are stable file stems."""
    result = {}
    for path in paths:
        p = Path(path)
        key = p.stem
        if key in result:
            raise ValueError(f'Duplicate table name derived from filenames: {key!r}')
        result[key] = read_table(p)
    return result
